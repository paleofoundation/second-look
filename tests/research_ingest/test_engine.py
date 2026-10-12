import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts.research_ingest import cli


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "app"
        self.packet = Path(self.temp.name) / "packet"
        self.root.mkdir()
        self.packet.mkdir()
        self.put(self.root / "inputs/context.json", {"protected": "original"})
        self.put(self.root / "corpus/sources.json", {"old": True})
        self.put(self.packet / "candidate/sources.json", {"old": True, "added": ["source-a"]})
        self.put(self.packet / "candidate/results.json", {"results": []})
        self.plan = {"schemaVersion": "remaprx-ingest-plan-v1", "planId": "TEST-1",
                     "operations": ["validate", "stage", "diff", "apply"],
                     "allowedTargets": ["corpus/sources.json", "corpus/results.json"],
                     "inputs": [{"path": "inputs/context.json", "sha256": cli.sha(self.root / "inputs/context.json")}],
                     "contract": {"scope": "synthetic test fixture only"}}
        self.plan_path = self.packet / "plan.json"
        self.put(self.plan_path, self.plan)
        self.manifest = {"schemaVersion": "remaprx-candidate-v1", "planId": "TEST-1",
                         "planSha256": cli.sha(self.plan_path), "batchId": "T01", "author": "extractor",
                         "files": [{"target": "corpus/" + name, "path": "candidate/" + name,
                                    "sha256": cli.sha(self.packet / "candidate" / name),
                                    "baseSha256": cli.current_hash(self.root / "corpus" / name)}
                                   for name in ["sources.json", "results.json"]]}
        self.manifest_path = self.packet / "manifest.json"
        self.readiness_path = self.packet / "readiness.json"
        self.acceptance_path = self.packet / "acceptance.json"
        self.put(self.readiness_path, {"schemaVersion": "remaprx-gp-readiness-v1", "status": "PASS",
                                      "scope": "GP_PLAN", "planId": "TEST-1", "planSha256": self.manifest["planSha256"],
                                      "checkedAt": "2026-10-12T00:00:00Z"})
        self.seal()

    def put(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(cli.canonical(value))

    def seal(self):
        self.put(self.manifest_path, self.manifest)
        self.candidate_digest = cli.digest(cli.canonical(self.manifest))
        evidence = self.packet / "audit/evidence.json"
        self.put(evidence, {"fixture": "two-file synthetic integration", "candidateDigest": self.candidate_digest})
        reports = []
        for kind in cli.KINDS:
            path = self.packet / f"audit/{kind}.json"
            report = {"status": "PASS", "candidateDigest": self.candidate_digest,
                      "targets": sorted(f["target"] for f in self.manifest["files"]),
                      "inputHashes": {f["path"]: f["sha256"] for f in self.manifest["files"]},
                      "checks": {"fixture_check": True}}
            if kind == "independent_audit":
                report.update(author="extractor", auditor="auditor",
                              evidence=[{"path": "audit/evidence.json", "sha256": cli.sha(evidence)}])
            self.put(path, report)
            reports.append({"kind": kind, "path": f"audit/{kind}.json", "sha256": cli.sha(path)})
        self.acceptance = {"schemaVersion": "remaprx-acceptance-v1", "status": "PASS",
                           "scope": "technical_candidate_integration", "planId": "TEST-1",
                           "planSha256": self.manifest["planSha256"], "batchId": "T01",
                           "candidateDigest": self.candidate_digest, "author": "extractor", "auditor": "auditor",
                           "reviewedAt": "2026-10-12T00:01:00Z", "reports": reports}
        self.put(self.acceptance_path, self.acceptance)

    def context(self, operation="apply", **overrides):
        args = dict(root=self.root, packet=self.packet, plan_path=self.plan_path,
                    manifest_path=self.manifest_path, operation=operation,
                    readiness=self.readiness_path, acceptance=self.acceptance_path)
        args.update(overrides)
        return cli.preflight(**args)

    def apply(self):
        with cli.store_lock(self.root):
            return cli.apply_context(self.context())

    def test_apply_and_repeat_are_exact_noop(self):
        protected = cli.sha(self.root / "inputs/context.json")
        result = self.apply()
        self.assertEqual(result["changedFiles"], 2)
        self.assertEqual(cli.load(result["journal"])["status"], "COMMITTED")
        second = self.apply()
        self.assertEqual(second["status"], "UNCHANGED")
        self.assertEqual(second["changedFiles"], 0)
        self.assertEqual(cli.sha(self.root / "inputs/context.json"), protected)

    def test_stage_does_not_import(self):
        output = Path(self.temp.name) / "staged"
        before = cli.sha(self.root / "corpus/sources.json")
        result = cli.stage(self.context("stage"), output)
        self.assertFalse(result["performedImport"])
        self.assertEqual(cli.sha(self.root / "corpus/sources.json"), before)
        self.assertEqual(cli.load(output / "candidate-manifest.json"), self.manifest)
        for relative in ["public/research", "dist/drafts", "research/corpus/staging"]:
            with self.assertRaisesRegex(cli.Hold, "Staging destination"):
                cli.stage(self.context("stage"), self.root / relative)

    def test_gp_required_and_wrong_plan_rejected(self):
        with self.assertRaisesRegex(cli.Hold, "readiness"):
            self.context("stage", readiness=None)
        ready = cli.load(self.readiness_path)
        ready["planSha256"] = "f" * 64
        self.put(self.readiness_path, ready)
        with self.assertRaisesRegex(cli.Hold, "stale"):
            self.context()

    def test_candidate_hash_and_plan_change_rejected(self):
        self.put(self.packet / "candidate/results.json", {"changed": True})
        with self.assertRaisesRegex(cli.Hold, "payload hash"):
            self.context()
        self.put(self.plan_path, {**self.plan, "newScope": "changed"})
        with self.assertRaisesRegex(cli.Hold, "plan mismatch"):
            self.context()

    def test_duplicate_target_and_json_keys_rejected(self):
        self.manifest["files"].append(self.manifest["files"][0])
        self.seal()
        with self.assertRaisesRegex((cli.Hold,), "Duplicate|schema"):
            self.context("validate")
        with self.assertRaisesRegex(cli.Hold, "Duplicate JSON key"):
            cli.decode(b'{"value":1,"value":2}')

    def test_wrong_current_base_and_protected_input_rejected(self):
        self.put(self.root / "corpus/sources.json", {"concurrent": True})
        with self.assertRaisesRegex(cli.Hold, "Concurrent/base"):
            self.context()
        self.put(self.root / "inputs/context.json", {"new": True})
        with self.assertRaisesRegex(cli.Hold, "Pinned input"):
            self.context()

    def test_unknown_target_and_symlink_rejected(self):
        self.manifest["files"][0]["target"] = "data/unapproved.json"
        self.seal()
        with self.assertRaisesRegex(cli.Hold, "allowlisted"):
            self.context()
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / "alias").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(cli.Hold, "Symlink"):
            cli.safe_path(self.root, "alias/file.json")
        for relative in ("../escape", "/absolute", "a/../escape", "a//b", "a\\b"):
            with self.assertRaises(cli.Hold):
                cli.safe_path(self.root, relative)

    def test_self_audit_stale_digest_and_scope_rejected(self):
        self.acceptance["auditor"] = " EXTRACTOR "
        self.put(self.acceptance_path, self.acceptance)
        with self.assertRaisesRegex(cli.Hold, "own candidate"):
            self.context()
        self.acceptance["auditor"] = "auditor"
        self.acceptance["candidateDigest"] = "0" * 64
        self.put(self.acceptance_path, self.acceptance)
        with self.assertRaisesRegex(cli.Hold, "candidateDigest"):
            self.context()

    def test_missing_independent_evidence_rejected(self):
        pin = next(p for p in self.acceptance["reports"] if p["kind"] == "independent_audit")
        path = self.packet / pin["path"]
        report = cli.load(path)
        report["evidence"] = []
        self.put(path, report)
        pin["sha256"] = cli.sha(path)
        self.put(self.acceptance_path, self.acceptance)
        with self.assertRaisesRegex(cli.Hold, "supporting evidence"):
            self.context()

    def test_store_wide_lock_blocks_another_batch(self):
        with cli.store_lock(self.root):
            with self.assertRaisesRegex(cli.Hold, "Store lock"):
                with cli.store_lock(self.root):
                    pass

    def test_caught_error_rolls_back_all_files(self):
        before = cli.sha(self.root / "corpus/sources.json")
        def fail(index):
            if index == 1:
                raise OSError("simulated write failure")
        with cli.store_lock(self.root), self.assertRaises(OSError):
            cli.apply_context(self.context(), fail)
        self.assertEqual(cli.sha(self.root / "corpus/sources.json"), before)
        self.assertFalse((self.root / "corpus/results.json").exists())
        self.assertEqual(cli.recover(self.root)["status"], "CLEAR")

    def test_interruption_holds_until_explicit_recovery(self):
        before = cli.sha(self.root / "corpus/sources.json")
        def interrupt(index):
            raise KeyboardInterrupt()
        with cli.store_lock(self.root), self.assertRaises(KeyboardInterrupt):
            cli.apply_context(self.context(), interrupt)
        pending = cli.recover(self.root)
        self.assertEqual(pending["status"], "HOLD")
        with self.assertRaisesRegex(cli.Hold, "interrupted"):
            self.context()
        result = cli.recover(self.root, pending["pendingJournals"][0], True)
        self.assertEqual(result["status"], "ROLLED_BACK")
        self.assertEqual(cli.sha(self.root / "corpus/sources.json"), before)
        self.assertEqual(self.apply()["changedFiles"], 2)

    def test_recovery_preserves_concurrent_edits(self):
        def interrupt(index):
            raise KeyboardInterrupt()
        with cli.store_lock(self.root), self.assertRaises(KeyboardInterrupt):
            cli.apply_context(self.context(), interrupt)
        self.put(self.root / "corpus/sources.json", {"external": "keep"})
        journal = cli.recover(self.root)["pendingJournals"][0]
        with self.assertRaisesRegex(cli.Hold, "Concurrent change"):
            cli.recover(self.root, journal, True)
        self.assertEqual(cli.load(self.root / "corpus/sources.json"), {"external": "keep"})

    def test_changed_approval_during_write_rolls_back(self):
        before = cli.sha(self.root / "corpus/sources.json")
        def change_control(index):
            self.put(self.acceptance_path, {"replaced": True})
        with cli.store_lock(self.root), self.assertRaisesRegex(cli.Hold, "Control artifact changed"):
            cli.apply_context(self.context(), change_control)
        self.assertEqual(cli.sha(self.root / "corpus/sources.json"), before)

    def test_unknown_journal_status_holds_all_imports(self):
        self.put(self.root / ".research-ingest/journals/broken.json", {"status": "INTNET", "files": []})
        with self.assertRaisesRegex(cli.Hold, "journal schema"):
            cli.recover(self.root)
        with self.assertRaisesRegex(cli.Hold, "journal schema"):
            self.context()

    def test_corrupted_journal_targets_and_backup_paths_cannot_restore(self):
        def interrupt(index):
            raise KeyboardInterrupt()
        with cli.store_lock(self.root), self.assertRaises(KeyboardInterrupt):
            cli.apply_context(self.context(), interrupt)
        path = Path(cli.recover(self.root)["pendingJournals"][0])
        journal = cli.load(path)
        original = journal["files"][0]["target"]
        journal["files"][0]["target"] = ".git/config.json"
        self.put(path, journal)
        with self.assertRaisesRegex(cli.Hold, "Reserved target"):
            cli.recover(self.root, path, True)
        journal["files"][0]["target"] = original
        journal["files"][0]["backup"] = "inputs/context.json"
        self.put(path, journal)
        with self.assertRaisesRegex(cli.Hold, "backup is outside"):
            cli.recover(self.root, path, True)

    def test_explicit_stale_lock_recovery_without_journal(self):
        lock = self.root / ".research-ingest/lock.json"
        self.put(lock, {"pid": 123456789, "root": str(self.root), "token": "fixture"})
        with patch("scripts.research_ingest.cli.os.kill", side_effect=ProcessLookupError):
            self.assertEqual(cli.recover(self.root, clear_lock=True)["status"], "STALE_LOCK_CLEARED")
        self.put(lock, {"pid": os.getpid(), "root": str(self.root), "token": "fixture"})
        with self.assertRaisesRegex(cli.Hold, "still alive"):
            cli.recover(self.root, clear_lock=True)

    def test_identity_conflicts_and_shared_file_do_not_merge(self):
        old = [{"id": "P1", "doi": "10.1000/a", "pmid": "1", "sha256": "f" * 64}]
        result = cli.resolve_identities(old, [{"id": "X", "doi": "10.1000/b", "pmid": "1"}])
        self.assertEqual(result["records"][0]["state"], "conflict")
        result = cli.resolve_identities(old, [{"id": "Y", "doi": "https://doi.org/10.1000/A"}])
        self.assertEqual(result["records"][0]["canonicalId"], "P1")
        result = cli.resolve_identities(old, [{"id": "Z", "sha256": "f" * 64}])
        self.assertEqual(result["records"][0]["state"], "new")
        self.assertEqual(result["records"][0]["sameAssetIds"], ["P1"])

    def test_source_resolver_hashes_real_bytes(self):
        source_map = self.packet / "source-locations.json"
        path = self.root / "inputs/context.json"
        self.put(source_map, {"roots": {"APP": {"path": str(self.root)}}, "files": [
            {"id": "S1", "rootId": "APP", "path": "inputs/context.json",
             "sha256": cli.sha(path), "bytes": path.stat().st_size}]})
        self.assertFalse(cli.resolve_source(source_map, "S1")["sourceInspected"])
        path.write_bytes(b"changed")
        with self.assertRaisesRegex(cli.Hold, "bytes/hash"):
            cli.resolve_source(source_map, "S1")

    def test_archive_resolver_streams_manifested_member(self):
        archive = self.packet / "papers.zip"
        payload = b"synthetic source bytes"
        with zipfile.ZipFile(archive, "w") as stream:
            stream.writestr("sources/report.txt", payload)
        source_map = self.packet / "source-locations.json"
        self.put(source_map, {"roots": {"PACKET": {"path": str(self.packet)}}, "files": [
            {"id": "ZIP", "rootId": "PACKET", "path": "papers.zip", "sha256": cli.sha(archive), "bytes": archive.stat().st_size}],
            "archiveMembers": [{"archiveFileId": "ZIP", "path": "sources/report.txt", "sha256": cli.digest(payload), "bytes": len(payload)}]})
        result = cli.resolve_source(source_map, "ZIP", "sources/report.txt")
        self.assertFalse(result["extracted"])
        self.assertFalse((self.packet / "sources").exists())
        with self.assertRaisesRegex(cli.Hold, "resolve exactly once"):
            cli.resolve_source(source_map, "ZIP", "sources/absent.txt")

    def test_cli_diff_is_read_only(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            result = cli.main(["diff", "--root", str(self.root), "--packet", str(self.packet),
                               "--plan", str(self.plan_path), "--manifest", str(self.manifest_path)])
        self.assertEqual(result, 0)
        self.assertFalse(json.loads(output.getvalue())["performedImport"])
        self.assertFalse((self.root / ".research-ingest").exists())


if __name__ == "__main__":
    unittest.main()
