#!/usr/bin/env python3
"""Inventory existing research bytes/metadata; never extract science or mutate inputs.

Only --output is written. Logical roots may be remapped on another host. All joins
are exact identifier/hash candidate joins, never fuzzy identity or efficacy merges.
Run with --check to compare a fresh, read-only inventory with the saved inventory.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


VERSION = "remaprx-research-inventory-v1"
HISTORICAL_ROOTS = {
    "APP": Path("/Users/kmfp/Documents/ChatGPT/Drug Repurposing/second-look-navigation"),
    "RESEARCH": Path("/Users/kmfp/Documents/Codex/2026-10-08/one-match-drug-repurposing"),
    "WORK": Path("/Users/kmfp/Documents/ChatGPT/One Match Rule/work"),
    "RETURNS": Path("/Users/kmfp/Desktop/papers-for-chatgpt/second-look-return"),
}
EXPECTED = {"app_sources": 281, "acquisition_sources": 2765,
            "report_identities": 1990, "assets": 1930, "draft_results": 570,
            "draft_claims": 525, "draft_reviews": 1152,
            "mechanism_sources": 13, "moa_rows": 1272,
            "moa_full_pdf": 1049, "moa_existing_held": 223}
MISSING = {"", "none", "null", "not in corpus", "doi not printed", "not reported"}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def fingerprint(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def stream_hash(stream):
    digest = hashlib.sha256()
    size = 0
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
        size += len(chunk)
    return digest.hexdigest(), size


def file_hash(path):
    with path.open("rb") as stream:
        return stream_hash(stream)


def doi(value):
    if not isinstance(value, str) or value.lower().strip() in MISSING:
        return None
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I)
    return value.lower() if re.match(r"^10\.\d{4,9}/\S+$", value) else None


def pmid(value):
    value = str(value or "").strip()
    return value if re.fullmatch(r"\d+", value) else None


def read_json(path):
    return json.loads(path.read_text())


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def rows(value):
    return list(value.values()) if isinstance(value, dict) else value


class Inventory:
    def __init__(self, args):
        self.args = args
        self.declared_roots = {"APP": args.app.absolute(), "RESEARCH": args.research_root.absolute(),
                               "WORK": args.work_root.absolute(), "RETURNS": args.returns_root.absolute()}
        self.roots = {key: path.resolve() for key, path in self.declared_roots.items()}
        self.files = {}
        self.members = []
        self.inputs = {}
        self.sources = []
        self.lineage = []
        self.bindings = []
        self.gaps = []
        self.return_rows = []
        self.errors = []
        self.hash_cache = {}

    def location(self, path):
        path = self.resolve_input_path(path)
        # Longest root first makes nested APP/WORK dependencies unambiguous.
        for key, root in sorted(self.roots.items(), key=lambda x: -len(str(x[1]))):
            if path.is_relative_to(root):
                return {"rootId": key, "path": path.relative_to(root).as_posix()}
        raise ValueError(f"No declared logical root for {path}")

    def resolve_input_path(self, path):
        """Remap immutable historical locations before reading any bytes.

        Source metadata stays unchanged. Configured roots are the authority on
        this host; a historical path must never silently read from the old host
        location when that root has been remapped. Symlinks must remain inside
        their selected logical root.
        """
        path = Path(path)
        if not path.is_absolute():
            raise ValueError("Research input must have a declared absolute root")
        candidates = [(key, root, priority)
                      for priority, mapping in enumerate([self.declared_roots, self.roots, HISTORICAL_ROOTS])
                      for key, root in mapping.items() if path.is_relative_to(root)]
        for key, root, _ in sorted(candidates, key=lambda x: (-len(str(x[1])), x[2])):
            relative = path.relative_to(root)
            if ".." in relative.parts:
                raise ValueError("Parent traversal in research input")
            configured_root = self.roots[key]
            resolved = (configured_root / relative).resolve()
            if not resolved.is_relative_to(configured_root):
                raise ValueError(f"Research input escapes logical root {key}")
            return resolved
        raise ValueError(f"No declared logical root for {path}")

    def observe_file(self, path, file_id=None, expected_sha=None, expected_bytes=None, kind="metadata"):
        path = self.resolve_input_path(path)
        loc = self.location(path)
        file_id = file_id or f"{loc['rootId']}:{loc['path']}"
        record = {"id": file_id, **loc, "kind": kind, "expectedSha256": expected_sha,
                  "expectedBytes": expected_bytes, "exists": path.is_file()}
        if path.is_file():
            if str(path) not in self.hash_cache:
                self.hash_cache[str(path)] = file_hash(path)
            sha, size = self.hash_cache[str(path)]
            matches = (not expected_sha or sha == expected_sha) and (expected_bytes is None or size == expected_bytes)
            record.update(sha256=sha, bytes=size,
                          verificationState=("verified" if expected_sha else "observed") if matches else "mismatch")
            if record["verificationState"] == "mismatch":
                self.errors.append({"kind": "file_mismatch", "fileId": file_id})
        else:
            record.update(sha256=None, bytes=None, verificationState="not_accessible")
        if file_id in self.files and self.files[file_id] != record:
            raise ValueError(f"Conflicting resolver ID {file_id}")
        self.files[file_id] = record
        return file_id

    def load(self, root, rel, jsonl=False):
        path = self.roots[root] / rel
        file_id = self.observe_file(path)
        if not path.exists():
            raise FileNotFoundError(path)
        self.inputs[file_id] = self.files[file_id]
        return (read_jsonl(path) if jsonl else read_json(path)), file_id

    def preserve(self, kind, record, file_id, pointer, record_id=None, **extra):
        self.lineage.append({"kind": kind, "id": str(record_id or record.get("id") or pointer),
                             "sourceFileId": file_id, "pointer": pointer,
                             "recordSha256": fingerprint(record), "disposition": "preserve_existing",
                             "acceptance": "metadata_inventory_only", **extra})

    def source(self, origin, record, file_id, pointer, canonical=None, asset_ids=None, **extra):
        underlying = record.get("source_record", record)
        source_id = underlying.get("source_id") or record.get("sourceId") or record.get("id")
        identity = underlying.get("sourceIdentity", {})
        source_id = source_id or record["sourceId"]
        result = {"id": f"{origin}:{source_id}", "origin": origin, "sourceId": source_id,
                  "canonicalId": canonical, "doi": doi(underlying.get("doi_verified") or
                  underlying.get("doi") or identity.get("doi")),
                  "pmid": pmid(underlying.get("pmid") or identity.get("pmid")),
                  "sha256": record.get("asset_sha256") or underlying.get("sha256") or record.get("sourceHash"),
                  "title": underlying.get("title") or identity.get("title"),
                  "sourceLocation": {"fileId": file_id, "pointer": pointer},
                  "recordSha256": fingerprint(record), "assetIds": asset_ids or [],
                  "acquisitionTags": {k: underlying[k] for k in ["drug_ids", "condition_ids", "demand_ids", "request_ids", "drugs", "mechanism_themes"] if k in underlying},
                  "identityMetadata": {k: underlying[k] for k in ["identity_status", "doi_verification_source", "version_of", "duplicate_of", "related_source_ids", "study_family_id", "family_identity_status", "report_role"] if k in underlying},
                  "states": {k: record[k] for k in ["access_state", "publication_state", "verification_state", "human_review_status", "quarantined", "reviewState", "publicationState", "status", "extractionStatus", "appraisalStatus"] if k in record},
                  "disposition": "preserve_existing_metadata", "scientificApproval": False, **extra}
        self.sources.append(result)
        self.preserve("source", record, file_id, pointer, source_id, origin=origin)
        return result

    def run(self):
        app = self.roots["APP"]
        content, content_file = self.load("APP", "data/content.json")
        for index, item in enumerate(content["sources"]):
            self.source("app", item, content_file, f"/sources/{index}", canonical=item["id"])
        for index, guide in enumerate(content["guides"]):
            self.preserve("guide", guide, content_file, f"/guides/{index}")
            for source_id in guide.get("sourceIds", []):
                self.bindings.append({"kind": "existing_editorial_usage", "sourceId": source_id,
                                      "guideId": guide["id"], "entityId": guide.get("entityId"),
                                      "path": guide.get("slug"), "scientificAcceptanceInferred": False,
                                      "provenance": {"fileId": content_file, "pointer": f"/guides/{index}/sourceIds"}})
        preserved_aliases = {}
        for rel in ["editorial/reader-source-aliases.json", "editorial/reader-source-corrections.json",
                    "editorial/retired-background-outcome-rows.json", "data/review-envelopes.json",
                    "data/private-reviews.json", "editorial/evidence-assessments.json",
                    "data/reader-evidence.json", "data/ingestion-status.json", "data/acquisition-status.json"]:
            value, file_id = self.load("APP", rel)
            if rel.endswith("reader-source-aliases.json"):
                preserved_aliases["app"] = {"fileId": file_id, "aliases": value}
            if rel.endswith("reader-evidence.json"):
                groups = [("synthesisRows", value["synthesisRows"]), ("quarantine", value["quarantine"])]
            elif "evidence-assessments" in rel:
                groups = [("records", value["records"])]
            elif rel.endswith("-status.json"):
                groups = [("pages", value["pages"])]
            else:
                groups = [("", value)]
            for prefix, group in groups:
                for key, record in (group.items() if isinstance(group, dict) else enumerate(group)):
                    self.preserve(Path(rel).stem, record if isinstance(record, dict) else {"value": record},
                                  file_id, f"/{prefix}/{key}" if prefix else f"/{key}", str(key))

        acquisition = "outputs/research/evidence/acquisition/"
        acq, acq_file = self.load("RESEARCH", acquisition + "sources.jsonl", True)
        assets, asset_file = self.load("RESEARCH", acquisition + "assets.jsonl", True)
        reports, report_file = self.load("RESEARCH", acquisition + "reports.jsonl", True)
        source_asset_ids = defaultdict(list)
        for line, asset in enumerate(assets, 1):
            asset_id = self.observe_file(asset["storage_path"], asset["id"], asset["sha256"], asset["bytes"], "research_asset")
            self.files[asset_id]["historicalStoragePath"] = asset["storage_path"]
            for source_id in asset["source_ids"]:
                source_asset_ids[source_id].append(asset_id)
            self.preserve("asset", asset, asset_file, f"line:{line}", asset["id"], resolverId=asset_id)
        for line, source in enumerate(acq, 1):
            self.source("acquisition", source, acq_file, f"line:{line}",
                        canonical=source.get("canonical_report_id"), asset_ids=source_asset_ids[source["source_id"]])
        for line, report in enumerate(reports, 1):
            self.preserve("report_identity", report, report_file, f"line:{line}", report["id"])
        # Preserve all metadata-store files, including screening/search/coverage/gap
        # histories, by exact file hash; no destructive reset or lossy rewrite.
        for path in sorted((self.roots["RESEARCH"] / acquisition).iterdir()):
            if path.is_file():
                fid = self.observe_file(path)
                self.inputs[fid] = self.files[fid]
        aliases, alias_file = self.load("RESEARCH", acquisition + "report-aliases.json")
        preserved_aliases["acquisition"] = {"fileId": alias_file, "aliases": aliases}

        # The original corpus is a separate protected baseline. Draft records
        # reuse some of it, but that is not permission to overwrite the baseline.
        original_root = self.roots["RESEARCH"] / "outputs/research/evidence"
        for path in sorted(original_root.iterdir()):
            if not path.is_file() or path.suffix not in {".json", ".jsonl", ".md"}:
                continue
            fid = self.observe_file(path)
            self.inputs[fid] = self.files[fid]
            if path.suffix == ".jsonl" and path.stem in {"papers", "studies", "results", "claims", "reviews", "pages", "topics", "context"}:
                for line, record in enumerate(read_jsonl(path), 1):
                    self.preserve("original_baseline_" + path.stem, record, fid, f"line:{line}",
                                  originalStoreRemainsSeparate=True)

        draft_prefix = "outputs/research/evidence/draft-science/"
        draft_counts = {}
        for entity in ["results", "claims", "reviews"]:
            values, fid = self.load("RESEARCH", draft_prefix + entity + ".jsonl", True)
            draft_counts[entity] = len(values)
            for line, record in enumerate(values, 1):
                self.preserve(entity, record, fid, f"line:{line}", sourceId=record.get("source_id") or record.get("paper_id"),
                              scientificCompletion=record.get("full_review_complete", False))
        for name in ["manifest", "source-dispositions", "result-dispositions", "source-integrity-notices", "integration-holds", "mechanism-duplicate-dispositions", "mechanisms"]:
            value, fid = self.load("RESEARCH", draft_prefix + name + ".json")
            if isinstance(value, list):
                for index, record in enumerate(value):
                    self.preserve(name, record, fid, f"/{index}", record.get("id") or record.get("source_id") or record.get("result_id"))
            if name == "source-dispositions":
                disposition_by_source = {record["source_id"]: record for record in value}
                for source in self.sources:
                    if source["origin"] == "acquisition" and source["sourceId"] in disposition_by_source:
                        source["priorScientificDisposition"] = disposition_by_source[source["sourceId"]]
        bindings, binding_file = self.load("RESEARCH", draft_prefix + "result-bindings.json")
        for index, binding in enumerate(bindings):
            self.bindings.append({"kind": "existing_source_located_draft_binding", **binding,
                                  "scientificAcceptanceInferred": False,
                                  "provenance": {"fileId": binding_file, "pointer": f"/{index}", "recordSha256": fingerprint(binding)}})

        # These dated executed receipts supersede historical NOT_DISPATCHED state
        # only for their own scope. They do not grant fresh scientific approval.
        checkpoint_specs = [
            "outputs/ingest/FETCH30-B-20261009T101312Z/source-receipt.json",
            "outputs/ingest/FETCH30-B-20261009T101312Z/import-report.json",
            "outputs/ingest/SL-SCIENTIFIC-20261010/final/final-draft-verified/completion-report.json",
            "outputs/ingest/SL-F01-F02-20261011/completion-report.json",
            "outputs/ingest/SL-F01-F02-20261011/governance/candidate-acceptance.json",
            "outputs/ingest/SL-F01-F02-20261011/receipt/archive-verification.json"]
        checkpoints = []
        for rel in checkpoint_specs:
            value, fid = self.load("RESEARCH", rel)
            checkpoints.append({"fileId": fid, "sha256": self.files[fid]["sha256"],
                                "planId": value.get("plan_id"), "planSha256": value.get("plan_sha256"),
                                "publicationPerformed": value.get("publication_performed", value.get("published", False)),
                                "acceptanceScope": "historical private draft/receipt only"})

        acquisition_projection, _ = self.load("APP", "data/acquisition-pages.json")
        returns = []
        for batch in range(9):
            name = f"F{batch:02d}"
            base = "ingest/SL-F01-F02-20261011/receipt/input" if batch < 3 else "ingest/FETCH30-B-20261009T101312Z/input"
            rel = f"{base}/return/{name}/acquisition-return.json"
            value, fid = self.load("WORK", rel)
            observed = self.files[fid]["sha256"]
            projection_hash = acquisition_projection["inputs"].get(f"return/{name}/acquisition-return.json")
            returns.append({"batchId": name, "fileId": fid, "sha256": observed,
                            "currentProjectionHash": projection_hash,
                            "projectionMatches": observed == projection_hash if projection_hash else None,
                            "sourceAppearances": len(value["sources"]), "requestIds": value["scope_request_ids"],
                            "scientificAcceptance": "not_inferred_from_acquisition"})
            if projection_hash and observed != projection_hash:
                self.errors.append({"kind": "projection_input_mismatch", "batchId": name})
            for index, source in enumerate(value["sources"]):
                self.return_rows.append({"batchId": name, "sourceId": source["source_id"],
                                         "reportId": source.get("report_id"), "sha256": source.get("sha256"),
                                         "fileId": fid, "pointer": f"/sources/{index}",
                                         "recordSha256": fingerprint(source), "filePresentInPacket": bool(source.get("filename")),
                                         "acquisitionTags": {k: source.get(k, []) for k in ["drug_ids", "condition_ids", "demand_ids", "request_ids"]},
                                         "disposition": "preserve_appearance_not_independent_source"})

        archive_specs = [
            ("fetch30-A-20261009T100524Z.zip", "59968e4e65cf1338d7a6be6614c250d426c8170e715b69561c5f758f60316ee6"),
            ("fetch30-B-20261009T101312Z.zip", "54f7c76acac994c4d218c1c948d2715384e6dea5807b990371956e7341bc48bd"),
            ("moa-01-20261011T055323Z.zip", None)]
        for name, expected in archive_specs:
            self.observe_file(self.roots["RETURNS"] / name, f"ARCHIVE:{name}", expected_sha=expected, kind="received_archive")

        mechanisms, mfid = self.load("APP", "editorial/mechanism-expansion/source-extraction-ledger.json")
        manifest, _ = self.load("APP", "editorial/mechanism-expansion/fulltext-manifest.json")
        mechanism_assets = {}
        for entry in manifest:
            p = app / "editorial/mechanism-expansion" / entry["path"]
            aid = self.observe_file(p, f"MECHANISM:{entry['sourceId']}", entry["sha256"], entry["bytes"], "existing_mechanism_asset")
            mechanism_assets[entry["sourceId"]] = aid
        for index, record in enumerate(mechanisms["records"]):
            self.source("mechanism", record, mfid, f"/records/{index}", canonical=record["sourceId"],
                        asset_ids=[mechanism_assets[record["sourceId"]]], disposition="preserve_bounded_prior_extraction")

        targets = self.targets(content)
        allowed_names = {x["name"].lower(): x["id"] for x in targets["drugs"]}
        allowed_names.update({"sirolimus": "D06", "rapamycin": "D06", "nirmatrelvir": "D03"})
        moa_path = self.roots["RETURNS"] / archive_specs[-1][0]
        moa_id = f"ARCHIVE:{moa_path.name}"
        with zipfile.ZipFile(moa_path) as archive:
            meta = archive.read("moa-manifest.csv")
            moa_rows = list(csv.DictReader(io.StringIO(meta.decode("utf-8-sig"))))
            moa_names = list(csv.DictReader(io.StringIO(archive.read("drug-universe.csv").decode("utf-8-sig"))))
            for member_name in ["moa-manifest.csv", "drug-universe.csv", "coverage.json", "gaps.csv", "README.md", "search-log.csv"]:
                payload = archive.read(member_name)
                self.members.append({"id": f"MOA-METADATA:{member_name}", "archiveFileId": moa_id,
                                     "path": member_name, "sha256": hashlib.sha256(payload).hexdigest(),
                                     "bytes": len(payload), "verificationState": "observed", "kind": "metadata"})
            names = set(archive.namelist())
            for index, record in enumerate(moa_rows):
                asset_ids = []
                if record["filename"]:
                    member_name = record["filename"]
                    if member_name.startswith("/") or ".." in Path(member_name).parts:
                        raise ValueError("Unsafe MOA archive member")
                    member_id = f"MOA-ASSET:{record['source_id']}"
                    member = {"id": member_id, "archiveFileId": moa_id, "path": member_name,
                              "expectedSha256": record["sha256"], "expectedBytes": int(record["bytes"]),
                              "kind": "research_asset", "verificationState": "not_accessible"}
                    if member_name in names:
                        with archive.open(member_name) as stream:
                            sha, size = stream_hash(stream)
                        member.update(sha256=sha, bytes=size,
                                      verificationState="verified" if sha == record["sha256"] and size == int(record["bytes"]) else "mismatch")
                    if member["verificationState"] != "verified":
                        self.errors.append({"kind": "moa_member_verification_failed", "id": member_id})
                    self.members.append(member)
                    asset_ids.append(member_id)
                named_drugs = [x.strip().lower() for x in re.split(r"[;|]", record["drugs"]) if x.strip()]
                existing = sorted({allowed_names[x] for x in named_drugs if x in allowed_names})
                extra = sorted({x for x in named_drugs if x not in allowed_names})
                inventory_record = self.source("moa", record, "MOA-METADATA:moa-manifest.csv", f"csv-row:{index + 2}",
                            asset_ids=asset_ids, existingTargetIds=existing, additionalNames=extra,
                            disposition="eligible_for_existing_target_screening" if existing else "lead_only_outside_existing_targets",
                            classificationAuthority="unverified_acquisition_regex_tags", existingDuplicateOf=record.get("existing_duplicate_of"))
                # EXIST-* cross-reference IDs repeat in the received CSV. Retain
                # every occurrence without manufacturing canonical paper IDs.
                inventory_record["id"] += f"@row-{index + 2}"

        identity_groups = self.identity_groups()
        counts = {"app_sources": len(content["sources"]), "acquisition_sources": len(acq),
                  "report_identities": len(reports), "assets": len(assets),
                  **{f"draft_{k}": v for k, v in draft_counts.items()},
                  "mechanism_sources": len(mechanisms["records"]), "moa_rows": len(moa_rows),
                  "moa_full_pdf": sum(x["access_state"] == "full_pdf" for x in moa_rows),
                  "moa_existing_held": sum(x["access_state"] == "existing_held" for x in moa_rows)}
        for key, expected in EXPECTED.items():
            if counts[key] != expected:
                self.errors.append({"kind": "baseline_changed", "count": key, "expected": expected, "observed": counts[key]})
        ids = [s["id"] for s in self.sources]
        if len(ids) != len(set(ids)):
            self.errors.append({"kind": "duplicate_inventory_record_ids"})
        missing = [f["id"] for f in self.files.values() if not f["exists"]]
        for file_id in missing:
            self.gaps.append({"kind": "source_access", "fileId": file_id, "state": "not_accessible", "nextAction": "Relocate matching bytes using declared source hash; do not infer source inspection."})
        summary = {"schemaVersion": VERSION, "batchId": "RRX-INGEST-001", "operation": "existing_metadata_and_bytes_inventory_only",
                   "scientificExtractionPerformed": False, "canonicalImportPerformed": False, "publicationPerformed": False,
                   "counts": counts, "expectedBaseline": EXPECTED, "errors": self.errors,
                   "status": "PASS_INVENTORY_ONLY" if not self.errors else "HOLD_RECONCILIATION",
                   "sourceAccessGaps": len(missing), "checkpoints": checkpoints, "returns": returns,
                   "appCountsAreNotExternalStoreCounts": True, "independentStudies": None,
                   "identityPolicy": "Exact DOI/PMID/hash candidates only. No identity or report-version merge; no independence inferred.",
                   "sourceRestrictions": {"F01_F02": "closed_packet_no_web_no_new_acquisition", "MOA": "existing_target_screening_only_extra_names_leads_only", "future_gap_acquisition": "separate_prospective_GP_packet"},
                   "moaAdditionalNames": [x["generic_name"] for x in moa_names if x["generic_name"].lower() not in allowed_names],
                   "claim": "Hashes prove byte continuity, not scientific correctness or approval."}
        ownership = self.ownership(targets)
        source_locations = {"schemaVersion": "remaprx-source-locations-v1", "roots": {
            key: {"path": str(path), "portable": False, "remapOption": {"APP": "--app", "RESEARCH": "--research-root", "WORK": "--work-root", "RETURNS": "--returns-root"}[key]}
            for key, path in self.roots.items()}, "files": sorted(self.files.values(), key=lambda x: x["id"]),
            "archiveMembers": sorted(self.members, key=lambda x: x["id"]),
            "portability": "Remap logical roots; identity remains source/report IDs plus exact hashes. No raw file is copied into Git."}
        return {"summary.json": summary, "source-locations.json": source_locations,
                "input-manifest.json": {"schemaVersion": VERSION, "files": sorted(self.inputs.values(), key=lambda x: x["id"])},
                "source-records.jsonl": sorted(self.sources, key=lambda x: x["id"]),
                "lineage.jsonl": self.lineage, "bindings.jsonl": self.bindings,
                "return-appearances.jsonl": self.return_rows, "identity-groups.jsonl": identity_groups,
                "preserved-aliases.json": preserved_aliases,
                "target-registry.json": targets, "ownership.json": ownership,
                "calibration-candidates.json": self.calibration(), "gaps.jsonl": self.gaps,
                "README.md": self.readme(summary)}

    def targets(self, content):
        prefix = self.roots["APP"] / "research/prior-pilot/outputs/handoff/fetch-30x30"
        target = {"schemaVersion": VERSION, "drugs": [], "conditions": [], "questions": [], "goals": []}
        for category, file_name in [("drugs", "30-drugs.csv"), ("conditions", "30-conditions.csv")]:
            path = prefix / file_name
            fid = self.observe_file(path)
            self.inputs[fid] = self.files[fid]
            for entry in csv.DictReader(path.open()):
                target[category].append({"id": entry["id"], "name": entry["name"], "path": entry["page"],
                                         "requestId": entry["request_id"], "scope": "initial_portfolio", "source": file_name})
        discovery, _ = self.load("APP", "data/discovery-pages.json")
        for guide in content["guides"] + discovery:
            entity_id = guide.get("entityId")
            if not entity_id:
                continue
            category = "drugs" if entity_id.startswith("D") else "conditions" if entity_id.startswith("C") else "goals"
            if entity_id not in {x["id"] for x in target[category]}:
                target[category].append({"id": entity_id, "name": guide["title"], "path": guide["slug"],
                                         "scope": "existing_addition_preserve", "guideId": guide["id"]})
        questions, _ = self.load("APP", "data/topics.json")
        target["questions"] = questions
        target["priorityMechanismDrugIds"] = ["D01", "D06", "D07", "D08", "D10", "D26", "D31", "D34"]
        target["newGuideCreation"] = False
        return target

    def identity_groups(self):
        indexes = {field: defaultdict(list) for field in ["doi", "pmid", "sha256"]}
        for source in self.sources:
            for field in indexes:
                if source.get(field):
                    indexes[field][source[field]].append(source)
        groups = []
        for field, index in indexes.items():
            for value, entries in sorted(index.items()):
                if len(entries) < 2:
                    continue
                dois = sorted({entry["doi"] for entry in entries if entry.get("doi")})
                conflict = field != "doi" and len(dois) > 1
                groups.append({"matchField": field, "value": value, "recordIds": [e["id"] for e in entries],
                               "distinctDois": dois, "disposition": "conflicting_report_identity_preserve_separate" if conflict else "exact_match_candidate_review_required",
                               "autoMerge": False, "independentStudyCount": None})
        return groups

    def ownership(self, targets):
        packets, _ = self.load("APP", "research/prior-pilot/outputs/handoff/fetch-30x30/worker-packets.json")
        return {"schemaVersion": VERSION, "integrator": "RRX-INGEST-001 integrator",
                "sourceOwnership": "One extraction owner per canonical source version; requests share accepted findings by explicit scope bindings.",
                "waves": [
                    {"id": "R0", "work": "Reconcile metadata, byte access, identities and preserved draft checkpoints", "scope": "all existing records"},
                    {"id": "R1", "work": "Source integrity and compatibility repair", "drugIds": ["D01", "D02", "D03"], "conditionIds": ["C01", "C02"], "questionIds": [f"DR{i:03d}" for i in [1, 2, 3, 4, 5, 13, 14, 15, 16, 17, 18]]},
                    {"id": "R2", "work": "Current cited reviews and existing-target mechanism completion", "drugIds": targets["priorityMechanismDrugIds"]},
                    {"id": "R3", "work": "Delta breadth after repair; existing holdings first, separate Grok gap packets"}],
                "historicalPartitions": [{"id": p["id"], "requestIds": p["request_ids"], "status": "ownership_reference_not_dispatch_authority"} for p in packets["packets"]],
                "acquisitionTagsNeverAuthorizeFindingFanout": True}

    def calibration(self):
        desired = ["B-R0071-F01", "B-R0016-F01", "B-R0092-F01", "A-F01-R029-F01", "P-REVIVE-2026", "MECH-D07-HEDGEHOG-2010", "MECH-D31-PASTIS-2022"]
        reasons = ["Randomized report and distinct treatment arm", "Observational design and confounding", "Clinical outcome numerical extraction", "Journal/preprint same-byte identity conflict; HOLD must survive", "Retraction/replacement quarantine; no favorable claim reactivation", "Preclinical mechanistic model and exposure", "Human mechanistic null finding and surrogate boundary"]
        return {"schemaVersion": VERSION, "status": "selection_only_not_extraction_authorization", "records": [
            {"sourceId": sid, "recordIds": [s["id"] for s in self.sources if s["sourceId"] == sid], "purpose": purpose}
            for sid, purpose in zip(desired, reasons)]}

    def readme(self, summary):
        count = summary["counts"]
        return f"""# RRX-INGEST-001 continuity inventory

This is a metadata and byte-continuity inventory, not a scientific ingest, review or release.

The app has {count['app_sources']} source records. The separate private research store has
{count['acquisition_sources']} acquisition source records, {count['report_identities']} report identities,
{count['assets']} assets and {count['draft_results']} draft results. These populations overlap and
must not be added together. No independent-study count is asserted.

The MOA archive has {count['moa_full_pdf']} full-PDF entries and {count['moa_existing_held']} prior-holding
cross-references. Its automatic tags do not prove eligibility. Existing targets may be screened;
additional names remain leads and do not create guides.

`source-records.jsonl` preserves separate origin records; `lineage.jsonl` gives exact source
file/pointer and record hashes. `return-appearances.jsonl` retains batch appearances without
counting duplicate appearances as new sources. `identity-groups.jsonl` proposes exact matching
candidates and conflicts; it never merges DOI reports. `bindings.jsonl` separates current editorial
usage and source-located private draft bindings from acquisition tags. No new findings are generated.

`source-locations.json` resolves logical roots, relative files and archive members with byte/hash
verification. Remap the four CLI roots on another host; host paths alone are not source identity.
Raw papers stay outside Git and public assets. Historical checkpoint receipts preserve their scope;
latest stored draft records do not imply acceptance into the current app or human scientific approval.

Run `python3 scripts/research_inventory.py` to regenerate, or add `--check` for a read-only
reproducibility comparison. The tool writes only this inventory directory. Missing expected inputs
or changed baseline counts are held explicitly. `summary.json` is the machine-readable status.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--research-root", type=Path, default=HISTORICAL_ROOTS["RESEARCH"])
    parser.add_argument("--work-root", type=Path, default=HISTORICAL_ROOTS["WORK"])
    parser.add_argument("--returns-root", type=Path, default=HISTORICAL_ROOTS["RETURNS"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="Compare regenerated inventory; write nothing")
    args = parser.parse_args()
    output = (args.output or args.app / "research/batches/RRX-INGEST-001/inventory").resolve()
    allowed = (args.app / "research/batches/RRX-INGEST-001/inventory").resolve()
    if output != allowed:
        parser.error("Output must be the batch inventory directory; canonical data and external roots are read-only")
    inventory = Inventory(args)
    artifacts = inventory.run()
    differences = []
    if not args.check:
        output.mkdir(parents=True, exist_ok=True)
    for name, value in artifacts.items():
        if name.endswith(".jsonl"):
            data = b"".join(encoded(row) + b"\n" for row in value)
        elif name.endswith(".json"):
            data = (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()
        else:
            data = value.encode()
        path = output / name
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                differences.append(name)
        elif not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
    print(json.dumps({"status": artifacts["summary.json"]["status"], "counts": artifacts["summary.json"]["counts"],
                      "reproducibilityDifferences": differences, "errors": inventory.errors,
                      "mode": "check" if args.check else "write_inventory_only"}, indent=2))
    return 1 if differences or inventory.errors else 0


if __name__ == "__main__":
    sys.exit(main())
