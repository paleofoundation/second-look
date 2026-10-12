"""Failure-focused tests for relocating immutable source metadata safely."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/research_inventory.py"
SPEC = importlib.util.spec_from_file_location("research_inventory", SCRIPT)
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


class InventoryLocationsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.args = argparse.Namespace(app=self.base / "app", research_root=self.base / "research",
                                       work_root=self.base / "work", returns_root=self.base / "returns")
        for root in vars(self.args).values():
            root.mkdir()
        self.subject = inventory.Inventory(self.args)

    def test_old_asset_path_reads_relocated_bytes(self):
        rel = Path("work/ingest/FETCH30/source-files/aa/relocated.pdf")
        source = self.args.research_root / rel
        source.parent.mkdir(parents=True)
        source.write_bytes(b"existing source bytes")
        expected = hashlib.sha256(source.read_bytes()).hexdigest()
        original = inventory.HISTORICAL_ROOTS["RESEARCH"] / rel
        self.subject.observe_file(original, "source", expected, source.stat().st_size)
        result = self.subject.files["source"]
        self.assertEqual(result["rootId"], "RESEARCH")
        self.assertEqual(result["path"], rel.as_posix())
        self.assertEqual(result["sha256"], expected)
        self.assertEqual(result["verificationState"], "verified")
        self.assertEqual(source.read_bytes(), b"existing source bytes")

    def test_mismatched_source_hash_is_not_verified(self):
        source = self.args.work_root / "wrong.pdf"
        source.write_bytes(b"wrong source version")
        self.subject.observe_file(source, "wrong", "0" * 64)
        self.assertEqual(self.subject.files["wrong"]["verificationState"], "mismatch")
        self.assertEqual(self.subject.errors, [{"kind": "file_mismatch", "fileId": "wrong"}])

    def test_symlink_cannot_escape_declared_root(self):
        outside = self.base / "outside.pdf"
        outside.write_bytes(b"not an authorized source-root member")
        link = self.args.research_root / "link.pdf"
        link.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "escapes logical root"):
            self.subject.observe_file(inventory.HISTORICAL_ROOTS["RESEARCH"] / "link.pdf")
        self.assertEqual(self.subject.files, {})

    def test_parent_traversal_cannot_select_another_root(self):
        with self.assertRaisesRegex(ValueError, "Parent traversal"):
            self.subject.observe_file(self.args.research_root / ".." / "outside.pdf")

    def test_unknown_root_cannot_be_read(self):
        with self.assertRaisesRegex(ValueError, "No declared logical root"):
            self.subject.observe_file(self.base / "unmapped.pdf")

    def test_missing_relocated_source_is_explicit_gap(self):
        original = inventory.HISTORICAL_ROOTS["WORK"] / "missing.pdf"
        self.subject.observe_file(original, "missing", "0" * 64)
        self.assertFalse(self.subject.files["missing"]["exists"])
        self.assertEqual(self.subject.files["missing"]["verificationState"], "not_accessible")

    def test_relocation_beneath_historical_root_is_idempotent(self):
        historical = self.base / "historical"
        self.args.research_root = historical / "relocated"
        self.args.research_root.mkdir(parents=True)
        with patch.dict(inventory.HISTORICAL_ROOTS, {"RESEARCH": historical}):
            subject = inventory.Inventory(self.args)
            first = subject.resolve_input_path(historical / "source.pdf")
            second = subject.resolve_input_path(first)
            self.assertEqual(first, second)
            self.assertEqual(second, self.args.research_root.resolve() / "source.pdf")


if __name__ == "__main__":
    unittest.main()
