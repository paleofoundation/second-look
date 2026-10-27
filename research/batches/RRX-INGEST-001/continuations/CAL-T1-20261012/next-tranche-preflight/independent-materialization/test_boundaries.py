"""Independent synthetic boundary checks. Never reads the real source archive."""
import importlib.util
import os
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("author_materializer_tests", HERE.parent / "test_materialize_zip.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)

class IndependentBoundaries(unittest.TestCase):
    def setUp(self):
        self.case = fixture.MaterializerTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)

    def test_existing_hard_link_is_held_without_writes(self):
        c = self.case
        destination = c.output / c.plan["allowedDestinations"][0]
        destination.parent.mkdir(parents=True)
        source = c.external / "unrelated.pdf"
        source.write_bytes(fixture.pdf("first"))
        os.link(source, destination)
        before = source.read_bytes()
        with self.assertRaisesRegex(fixture.tool.Hold, "regular unlinked file"):
            c.run_tool()
        self.assertEqual(source.read_bytes(), before)
        self.assertFalse((c.output / c.plan["receiptRelativePath"]).exists())
        self.assertFalse((c.output / c.plan["allowedDestinations"][1]).exists())
        self.assertFalse((c.output / ".rrx-materialization.lock").exists())

    def test_existing_fifo_is_held_without_blocking(self):
        c = self.case
        destination = c.output / c.plan["allowedDestinations"][0]
        destination.parent.mkdir(parents=True)
        os.mkfifo(destination)
        with self.assertRaisesRegex(fixture.tool.Hold, "regular unlinked file"):
            c.run_tool()
        self.assertFalse((c.output / c.plan["receiptRelativePath"]).exists())
        self.assertFalse((c.output / c.plan["allowedDestinations"][1]).exists())

    def test_receipt_with_missing_member_does_not_repair_silently(self):
        c = self.case
        first = c.run_tool()
        receipt = Path(first["receiptPath"])
        original = receipt.read_bytes()
        member = c.output / c.plan["allowedDestinations"][0]
        member.unlink()
        with self.assertRaisesRegex(fixture.tool.Hold, "members are missing"):
            c.run_tool()
        self.assertFalse(member.exists())
        self.assertEqual(receipt.read_bytes(), original)

if __name__ == "__main__":
    unittest.main(verbosity=2)
