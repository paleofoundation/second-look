"""Adapted from the preserved SL-F01/F02 staged importer and preflight.

Only explicit apply/recover --rollback changes canonical files. Per-file replace
is atomic; the store-wide lock and durable journal make multi-file interruption
visible and recoverable. This module does not acquire or interpret research.
"""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import uuid
import zipfile

from .contracts import KINDS, SCHEMAS


class Hold(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Hold(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                       allow_nan=False) + "\n").encode()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def decode(data):
    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(Hold("Invalid JSON constant: " + value)))


def load(path):
    return decode(Path(path).read_bytes())


def pinned_load(path, pins, expected=None):
    path = Path(path).resolve()
    data = path.read_bytes()
    actual = digest(data)
    require(expected is None or actual == expected, "Pinned artifact changed: " + str(path))
    pins[str(path)] = actual
    return decode(data)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate_shape(kind, value):
    try:
        from jsonschema import Draft202012Validator
    except ImportError as error:
        raise Hold("Install scripts/research_ingest/requirements.txt in a Python environment.") from error
    errors = sorted(Draft202012Validator(SCHEMAS[kind]).iter_errors(value), key=lambda e: str(e.path))
    require(not errors, kind + " schema: " + "; ".join(e.message for e in errors[:8]))


def safe_path(root, relative):
    require(isinstance(relative, str) and relative and "\\" not in relative and "\0" not in relative,
            "Unsafe relative path")
    parts = relative.split("/")
    require(not PurePosixPath(relative).is_absolute() and all(p not in ("", ".", "..") for p in parts),
            "Unsafe relative path: " + relative)
    path = Path(root)
    for part in parts:
        path = path / part
        require(not path.is_symlink(), "Symlink is not allowed: " + str(path))
    require(path.resolve().is_relative_to(Path(root).resolve()), "Path escapes root: " + relative)
    return path


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(parsed.tzinfo is not None, "Timestamp needs an explicit timezone")
    except (ValueError, AttributeError) as error:
        raise Hold("Invalid dated checkpoint") from error


def current_hash(path):
    require(not path.exists() or path.is_file(), "Expected regular file: " + str(path))
    return sha(path) if path.exists() else None


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".ingest-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def state_directory(root):
    return safe_path(root, ".research-ingest")


def pending_journals(root):
    folder = safe_path(root, ".research-ingest/journals")
    if not folder.exists():
        return []
    result = []
    for path in folder.iterdir():
        require(path.is_file() and not path.is_symlink() and path.suffix == ".json", "Unexpected journal directory entry")
        journal = load(path)
        validate_journal(root, journal, path)
        if journal["status"] in ("INTENT", "HOLD_MANUAL_RECOVERY"):
            result.append(path)
    return result


def valid_target(root, relative):
    path = safe_path(root, relative)
    require(relative.split("/")[0] not in (".git", ".research-ingest"), "Reserved target")
    require(path.suffix in (".json", ".jsonl"), "Research targets must be JSON/JSONL")
    return path


def validate_journal(root, journal, journal_path=None):
    validate_shape("journal", journal)
    require(journal["root"] == str(Path(root).resolve()), "Journal root mismatch")
    run_id = journal["runId"]
    if journal_path is not None:
        require(Path(journal_path).name == run_id + ".json", "Journal filename/run identity mismatch")
    prefix = ".research-ingest/backups/" + run_id + "/"
    require(journal["planBackup"] == prefix + "plan.json", "Journal plan backup is outside run subtree")
    plan_path = safe_path(root, journal["planBackup"])
    plan = pinned_load(plan_path, {}, journal["planSha256"])
    validate_shape("plan", plan)
    require(plan["planId"] == journal["planId"], "Journal plan identity mismatch")
    targets = set()
    for index, item in enumerate(journal["files"]):
        valid_target(root, item["target"])
        require(item["target"] in plan["allowedTargets"] and item["target"] not in targets,
                "Journal target is duplicate or outside approved plan")
        targets.add(item["target"])
        require(item["before"] != item["after"], "Journal contains unchanged target")
        require(item["backup"] == (prefix + str(index) + ".bin" if item["before"] is not None else None),
                "Journal backup is outside exact run subtree")


@contextlib.contextmanager
def store_lock(root):
    root = Path(root).resolve()
    state = state_directory(root)
    state.mkdir(parents=True, exist_ok=True)
    lock = safe_path(root, ".research-ingest/lock.json")
    token = uuid.uuid4().hex
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise Hold("Store lock exists; inspect recover before retrying: " + str(lock)) from error
    with os.fdopen(fd, "wb") as stream:
        stream.write(canonical({"pid": os.getpid(), "token": token, "root": str(root)}))
        stream.flush()
        os.fsync(stream.fileno())
    try:
        yield
    finally:
        if lock.exists() and load(lock).get("token") == token:
            lock.unlink()


def check_inputs(root, plan):
    pins = {}
    for item in plan["inputs"]:
        require(item["path"] not in pins, "Duplicate pinned input")
        path = safe_path(root, item["path"])
        require(path.is_file() and sha(path) == item["sha256"], "Pinned input changed: " + item["path"])
        pins[item["path"]] = item["sha256"]
    return pins


def check_readiness(path, plan, plan_hash, pins=None):
    require(path is not None, "GP Plan readiness file is required")
    value = pinned_load(path, pins if pins is not None else {})
    validate_shape("readiness", value)
    require(value["planId"] == plan["planId"] and value["planSha256"] == plan_hash,
            "GP Plan readiness is stale or belongs to a different plan")
    timestamp(value["checkedAt"])


def acceptance_check(path, packet, plan, manifest, candidate_digest, control_pins=None):
    require(path is not None, "Reviewed candidate acceptance is required")
    control_pins = control_pins if control_pins is not None else {}
    value = pinned_load(path, control_pins)
    validate_shape("acceptance", value)
    for key, expected in {"planId": plan["planId"], "planSha256": manifest["planSha256"],
                          "batchId": manifest["batchId"], "candidateDigest": candidate_digest,
                          "author": manifest["author"]}.items():
        require(value[key] == expected, "Acceptance mismatch: " + key)
    require(value["auditor"].strip().casefold() != value["author"].strip().casefold(),
            "The candidate author cannot independently audit their own candidate")
    timestamp(value["reviewedAt"])
    require(sorted(r["kind"] for r in value["reports"]) == sorted(KINDS), "Every audit kind is required exactly once")
    targets = sorted(f["target"] for f in manifest["files"])
    hashes = {f["path"]: f["sha256"] for f in manifest["files"]}
    for pin in value["reports"]:
        report_path = safe_path(packet, pin["path"])
        report = pinned_load(report_path, control_pins, pin["sha256"])
        validate_shape("report", report)
        require(report["candidateDigest"] == candidate_digest and sorted(report["targets"]) == targets
                and report["inputHashes"] == hashes, "Audit report scope mismatch: " + pin["kind"])
        if pin["kind"] == "independent_audit":
            require(report.get("author") == value["author"] and report.get("auditor") == value["auditor"]
                    and bool(report.get("evidence")), "Independent audit requires matching people and supporting evidence")
        for evidence in report.get("evidence", []):
            source = safe_path(packet, evidence["path"])
            raw = source.read_bytes()
            require(digest(raw) == evidence["sha256"], "Audit supporting evidence changed")
            control_pins[str(source.resolve())] = evidence["sha256"]
    return value


def preflight(root, packet, plan_path, manifest_path, operation, readiness=None, acceptance=None):
    root, packet = Path(root).resolve(), Path(packet).resolve()
    require(root.is_dir() and packet.is_dir(), "Project root and packet must exist")
    controls = {}
    plan = pinned_load(plan_path, controls)
    manifest = pinned_load(manifest_path, controls)
    validate_shape("plan", plan)
    validate_shape("manifest", manifest)
    plan_hash = controls[str(Path(plan_path).resolve())]
    require(operation in plan["operations"], "Operation is outside the plan: " + operation)
    require(manifest["planId"] == plan["planId"] and manifest["planSha256"] == plan_hash, "Candidate plan mismatch")
    allowed = set(plan["allowedTargets"])
    for relative in allowed:
        valid_target(root, relative)
    pins = check_inputs(root, plan)
    require(not (allowed & set(pins)), "Pinned inputs cannot also be mutation targets")
    if operation in ("stage", "apply"):
        check_readiness(readiness, plan, plan_hash, controls)
    candidate_digest = digest(canonical(manifest))
    if operation == "apply":
        acceptance_check(acceptance, packet, plan, manifest, candidate_digest, controls)
        require(not pending_journals(root), "An interrupted import requires recovery")
    writes, targets, payloads = [], set(), set()
    for item in manifest["files"]:
        require(item["target"] in allowed, "Target not allowlisted: " + item["target"])
        require(item["target"] not in targets and item["path"] not in payloads, "Duplicate target or candidate payload")
        targets.add(item["target"])
        payloads.add(item["path"])
        source, target = safe_path(packet, item["path"]), safe_path(root, item["target"])
        require(source != target, "Candidate payload cannot be a canonical target")
        data = source.read_bytes()
        require(digest(data) == item["sha256"], "Candidate payload hash mismatch: " + item["path"])
        if target.suffix == ".json":
            decode(data)
        else:
            for line in data.splitlines():
                if line.strip():
                    decode(line)
        require(not target.exists() or target.is_file(), "Target is not a regular file")
        before_data = target.read_bytes() if target.exists() else None
        before = digest(before_data) if before_data is not None else None
        require(before in (item["baseSha256"], item["sha256"]), "Concurrent/base change: " + item["target"])
        writes.append({**item, "before": before, "data": data, "beforeData": before_data})
    return {"root": root, "packet": packet, "plan": plan, "manifest": manifest,
            "planHash": plan_hash, "candidateDigest": candidate_digest, "writes": writes,
            "pins": pins, "controlPins": controls, "planPath": str(Path(plan_path).resolve())}


def check_controls(context):
    for path, expected in context["controlPins"].items():
        require(Path(path).is_file() and sha(path) == expected, "Control artifact changed: " + path)


def summary(context):
    files = [{"target": w["target"], "before": w["before"], "after": w["sha256"],
              "action": "unchanged" if w["before"] == w["sha256"] else "create" if w["before"] is None else "replace"}
             for w in context["writes"]]
    return {"status": "PASS", "planId": context["plan"]["planId"],
            "batchId": context["manifest"]["batchId"], "candidateDigest": context["candidateDigest"],
            "files": files, "changedFiles": sum(f["action"] != "unchanged" for f in files),
            "scientificApproval": False, "publicationPerformed": False}


def stage(context, output):
    output = Path(output).resolve()
    if output.is_relative_to(context["root"]):
        relative = output.relative_to(context["root"])
        require(relative.parts and relative.parts[0] not in ("public", "dist", ".next", ".git", ".research-ingest", "data")
                and relative.parts[:2] != ("research", "corpus"), "Staging destination is a public, canonical or reserved directory")
    canonical_targets = {safe_path(context["root"], w["target"]) for w in context["writes"]}
    protected = canonical_targets | {safe_path(context["root"], p) for p in context["pins"]}
    protected |= {Path(p) for p in context["controlPins"]}
    destinations = [safe_path(output, w["path"]) for w in context["writes"]]
    destinations.append(safe_path(output, "candidate-manifest.json"))
    require(not (set(destinations) & protected), "Staging would overwrite canonical or protected inputs")
    require("candidate-manifest.json" not in {w["path"] for w in context["writes"]}, "Reserved staged manifest filename")
    for path, write in zip(destinations, context["writes"]):
        require(not path.exists() or path.read_bytes() == write["data"], "Staging destination already contains different bytes")
    manifest_data = canonical(context["manifest"])
    require(not destinations[-1].exists() or destinations[-1].read_bytes() == manifest_data, "Staged manifest differs")
    for path, write in zip(destinations, context["writes"]):
        atomic(path, write["data"])
    atomic(destinations[-1], manifest_data)
    check_inputs(context["root"], context["plan"])
    check_controls(context)
    return {**summary(context), "stagedAt": str(output), "performedImport": False}


def rollback(root, journal):
    """First verify every file, then reverse only exact proposed bytes."""
    validate_journal(root, journal)
    for item in journal["files"]:
        path = safe_path(root, item["target"])
        require(current_hash(path) in (item["before"], item["after"]), "Concurrent change prevents rollback: " + item["target"])
        if item["before"] is not None:
            backup = safe_path(root, item["backup"])
            require(backup.is_file() and sha(backup) == item["before"], "Rollback backup changed")
    for item in reversed(journal["files"]):
        path = safe_path(root, item["target"])
        if current_hash(path) == item["before"]:
            continue
        require(current_hash(path) == item["after"], "Concurrent change during rollback")
        if item["before"] is None:
            path.unlink()
        else:
            atomic(path, safe_path(root, item["backup"]).read_bytes())


def apply_context(context, after_write=None):
    """Caller holds store lock and has recomputed preflight inside that lock."""
    root = context["root"]
    check_controls(context)
    check_inputs(root, context["plan"])
    writes = [w for w in context["writes"] if w["before"] != w["sha256"]]
    if not writes:
        return {**summary(context), "performedImport": True, "status": "UNCHANGED"}
    run_id = uuid.uuid4().hex
    journal_path = safe_path(root, ".research-ingest/journals/" + run_id + ".json")
    plan_backup = f".research-ingest/backups/{run_id}/plan.json"
    plan_bytes = Path(context["planPath"]).read_bytes()
    require(digest(plan_bytes) == context["planHash"], "Plan changed before intent journal")
    atomic(safe_path(root, plan_backup), plan_bytes)
    records = []
    for i, write in enumerate(writes):
        backup = f".research-ingest/backups/{run_id}/{i}.bin"
        if write["beforeData"] is not None:
            atomic(safe_path(root, backup), write["beforeData"])
        records.append({"target": write["target"], "before": write["before"],
                        "after": write["sha256"], "backup": backup if write["before"] is not None else None})
    journal = {"schemaVersion": "remaprx-import-journal-v1", "status": "INTENT", "root": str(root),
               "runId": run_id, "planBackup": plan_backup,
               "candidateDigest": context["candidateDigest"], "planId": context["plan"]["planId"],
               "planSha256": context["planHash"], "files": records,
               "perFileAtomic": True, "crossFileAtomic": False}
    atomic(journal_path, canonical(journal))
    try:
        check_inputs(root, context["plan"])
        check_controls(context)
        for i, write in enumerate(writes):
            destination = safe_path(root, write["target"])
            require(current_hash(destination) == write["before"], "Destination changed after preflight")
            atomic(destination, write["data"])
            if after_write is not None:
                after_write(i)
        for write in writes:
            require(current_hash(safe_path(root, write["target"])) == write["sha256"], "Post-import byte mismatch")
        check_inputs(root, context["plan"])
        check_controls(context)
    except Exception as error:
        journal["error"] = str(error)
        try:
            rollback(root, journal)
            journal["status"] = "ROLLED_BACK"
        except Exception as recovery_error:
            journal["status"] = "HOLD_MANUAL_RECOVERY"
            journal["recoveryError"] = str(recovery_error)
        atomic(journal_path, canonical(journal))
        raise
    journal["status"] = "COMMITTED"
    atomic(journal_path, canonical(journal))
    return {**summary(context), "performedImport": True, "status": "IMPORTED_PRIVATE_CANDIDATE",
            "journal": str(journal_path), "crossFileAtomic": False}


def clear_stale_lock(root):
    lock = safe_path(root, ".research-ingest/lock.json")
    require(lock.is_file(), "No lock to clear")
    owner = load(lock)
    require(isinstance(owner.get("root"), str) and Path(owner["root"]).resolve() == root, "Lock root mismatch")
    pid = owner.get("pid")
    require(isinstance(pid, int) and pid > 0, "Lock owner PID is invalid")
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        lock.unlink()
    else:
        raise Hold("Lock owner is still alive; recovery refused")


def recover(root, journal_path=None, do_rollback=False, clear_lock=False):
    root = Path(root).resolve()
    lock = safe_path(root, ".research-ingest/lock.json")
    journals = pending_journals(root)
    require(not (do_rollback and clear_lock), "Choose rollback or clear-stale-lock")
    if clear_lock:
        require(not journals, "Pending journal requires rollback/recovery before clearing its lock")
        clear_stale_lock(root)
        return {"status": "STALE_LOCK_CLEARED", "performedRecovery": True}
    if not do_rollback:
        return {"status": "HOLD" if lock.exists() or journals else "CLEAR",
                "lock": load(lock) if lock.exists() else None,
                "pendingJournals": [str(p) for p in journals], "performedRecovery": False}
    require(journal_path is not None, "Explicit journal path is required for rollback")
    path = Path(journal_path).resolve()
    require(path in [p.resolve() for p in journals], "Journal is not a pending journal in this store")
    if lock.exists():
        clear_stale_lock(root)
    with store_lock(root):
        journal = load(path)
        validate_journal(root, journal, path)
        rollback(root, journal)
        journal["status"] = "ROLLED_BACK"
        journal["recoveredAt"] = datetime.now(timezone.utc).isoformat()
        atomic(path, canonical(journal))
    return {"status": "ROLLED_BACK", "performedRecovery": True, "journal": str(path)}


def normalize_doi(value):
    if not value:
        return None
    result = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", str(value).strip(), flags=re.I).lower()
    require(re.fullmatch(r"10\.\d{4,9}/\S+", result) is not None, "Malformed DOI")
    return result


def resolve_identities(existing, incoming):
    """Propose mappings; never merge distinct reports solely by file hash."""
    def normalized(rows):
        require(len({r["id"] for r in rows}) == len(rows), "Duplicate identity ID")
        return [{**r, "doi": normalize_doi(r.get("doi")),
                 "pmid": str(r["pmid"]).strip() if r.get("pmid") else None} for r in rows]
    old, new = normalized(existing), normalized(incoming)
    by_id = {r["id"]: r for r in old}
    output = []
    for row in new:
        exact = by_id.get(row["id"])
        matches = [r for r in old if (row["doi"] and row["doi"] == r["doi"])
                   or (row["pmid"] and row["pmid"] == r["pmid"])]
        if exact and exact not in matches:
            matches.append(exact)
        conflicts = [r for r in matches if (row["doi"] and r["doi"] and row["doi"] != r["doi"])
                     or (row["pmid"] and r["pmid"] and row["pmid"] != r["pmid"])]
        canonical_ids = {r.get("canonicalId") or r["id"] for r in matches}
        state = "conflict" if conflicts else "ambiguous" if len(canonical_ids) > 1 else "matched" if matches else "new"
        output.append({"id": row["id"], "state": state,
                       "canonicalId": next(iter(canonical_ids)) if state == "matched" else None,
                       "matchingIds": sorted(r["id"] for r in matches),
                       "sameAssetIds": sorted(r["id"] for r in old if row.get("sha256") and row.get("sha256") == r.get("sha256"))})
    return {"status": "HOLD" if any(r["state"] in ("conflict", "ambiguous") for r in output) else "PASS",
            "records": output, "performedMerge": False}


def resolve_source(source_map, source_id, archive_member=None):
    mapping = load(source_map)
    rows = [r for r in mapping["files"] if r["id"] == source_id]
    require(len(rows) == 1, "Source location ID must resolve exactly once")
    row = rows[0]
    root = Path(mapping["roots"][row["rootId"]]["path"]).resolve()
    path = safe_path(root, row["path"])
    require(path.is_file() and path.stat().st_size == row["bytes"] and sha(path) == row["sha256"], "Source bytes/hash mismatch")
    if archive_member is not None:
        safe_path(Path("/"), archive_member)
        members = [r for r in mapping.get("archiveMembers", [])
                   if r["archiveFileId"] == source_id and r["path"] == archive_member]
        require(len(members) == 1, "Archive member must resolve exactly once in inventory")
        expected = members[0]
        with zipfile.ZipFile(path) as archive:
            require(archive.namelist().count(archive_member) == 1, "Archive member is missing or duplicated")
            info = archive.getinfo(archive_member)
            require(info.file_size == expected["bytes"], "Archive member byte count differs")
            require((info.external_attr >> 16) & 0o170000 != 0o120000, "Archive member is a symlink")
            checksum, count = hashlib.sha256(), 0
            with archive.open(archive_member) as stream:
                while chunk := stream.read(1024 * 1024):
                    count += len(chunk)
                    require(count <= expected["bytes"], "Archive member exceeds declared byte count")
                    checksum.update(chunk)
            require(count == expected["bytes"] and checksum.hexdigest() == expected["sha256"], "Archive member hash mismatch")
        return {"status": "PASS", "archiveId": source_id, "member": archive_member,
                "sha256": expected["sha256"], "verifiedBytes": count, "extracted": False, "sourceInspected": False}
    return {"status": "PASS", "id": source_id, "path": str(path), "sha256": row["sha256"],
            "verifiedBytes": row["bytes"], "sourceInspected": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "validate-source", "preflight", "stage", "diff", "apply", "recover", "resolve", "schema"])
    for name in ["root", "packet", "plan", "manifest", "readiness", "acceptance", "out", "journal", "existing", "incoming", "source-map", "source-id", "archive-member", "schema", "candidate", "assignment", "source-file", "mechanism-schema"]:
        parser.add_argument("--" + name)
    parser.add_argument("--rollback", action="store_true")
    parser.add_argument("--clear-stale-lock", action="store_true")
    parser.add_argument("--kind", choices=SCHEMAS)
    args = parser.parse_args(argv)
    try:
        if args.command == "schema":
            result = SCHEMAS[args.kind] if args.kind else SCHEMAS
        elif args.command == "validate-source":
            from .source_validation import validate_source
            require(all([args.root, args.schema, args.candidate, args.assignment, args.plan, args.readiness]),
                    "--root --schema --candidate --assignment --plan --readiness are required")
            result = validate_source(args.schema, args.candidate, args.assignment, args.plan,
                                     args.readiness, args.source_file, args.mechanism_schema, args.root)
        elif args.command == "recover":
            require(args.root, "--root is required")
            result = recover(args.root, args.journal, args.rollback, args.clear_stale_lock)
        elif args.command == "resolve":
            if args.source_map:
                result = resolve_source(args.source_map, args.source_id, args.archive_member)
            else:
                require(args.existing and args.incoming, "--existing and --incoming are required")
                result = resolve_identities(load(args.existing), load(args.incoming))
        else:
            require(all([args.root, args.packet, args.plan, args.manifest]), "--root --packet --plan --manifest are required")
            operation = "validate" if args.command == "preflight" else args.command
            options = dict(root=args.root, packet=args.packet, plan_path=args.plan,
                           manifest_path=args.manifest, operation=operation,
                           readiness=args.readiness, acceptance=args.acceptance)
            if args.command == "apply":
                with store_lock(Path(args.root).resolve()):
                    result = apply_context(preflight(**options))
            else:
                context = preflight(**options)
                if args.command == "preflight":
                    check_readiness(args.readiness, context["plan"], context["planHash"])
                if args.command == "stage":
                    require(args.out, "--out is required for stage")
                    result = stage(context, args.out)
                else:
                    result = {**summary(context), "performedImport": False}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1 if result.get("status") == "HOLD" else 0
    except (Hold, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(json.dumps({"status": "HOLD", "error": str(error), "performedImport": False,
                          "scientificApproval": False, "publicationPerformed": False}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
