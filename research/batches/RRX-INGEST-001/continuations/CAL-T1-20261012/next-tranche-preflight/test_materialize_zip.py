import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('gated_zip_materializer', HERE / 'materialize_zip.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def pdf(label):
    """A real, synthetic one-page PDF; exercises the actual pdfinfo counter."""
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
               b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] /Contents 4 0 R >>',
               b'<< /Length 0 >>\nstream\n\nendstream']
    data = b'%PDF-1.4\n% synthetic ' + label.encode() + b'\n'; offsets = [0]
    for i, body in enumerate(objects, 1):
        offsets.append(len(data)); data += str(i).encode() + b' 0 obj\n' + body + b'\nendobj\n'
    start = len(data)
    data += b'xref\n0 5\n0000000000 65535 f \n'
    data += b''.join(f'{offset:010d} 00000 n \n'.encode() for offset in offsets[1:])
    return data + b'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n' + str(start).encode() + b'\n%%EOF\n'


class MaterializerTests(unittest.TestCase):
    def setUp(self):
        self.controls_tmp = tempfile.TemporaryDirectory(prefix='synthetic-zip-test-', dir=HERE)
        self.external_tmp = tempfile.TemporaryDirectory(prefix='synthetic-zip-private-')
        self.addCleanup(self.controls_tmp.cleanup); self.addCleanup(self.external_tmp.cleanup)
        self.control_dir = Path(self.controls_tmp.name).resolve()
        self.external = Path(self.external_tmp.name).resolve()
        self.output = self.external / 'raw'
        self.archive = self.external / 'fixture.zip'
        self.plan_path = self.control_dir / 'plan.json'
        self.readiness = self.control_dir / 'readiness.json'
        self.manifest_path = self.control_dir / 'manifest.json'
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as archive:
            archive.writestr('Original supplement.pdf', pdf('first'))
            archive.writestr('nested/Analysis plan.pdf', pdf('second'))
        self.archive.write_bytes(data.getvalue())
        self.members = tool.inventory.archive_inventory(data.getvalue())
        rows = []
        for i, member in enumerate(self.members):
            rows.append({'sourceId': 'SYNTHETIC-S' + str(i), 'canonicalReportId': 'SYNTHETIC-REPORT',
                         'archiveSourceId': 'SYNTHETIC-ZIP', 'archiveSha256': tool.sha(self.archive),
                         'member': member, 'expectedUnits': [{'id': 'page-1', 'kind': 'pdf_page', 'locator': '1'}],
                         'proposedMaterializationRelativePath': 'CAL-01/archive-members/' + member['sha256'] + '.pdf'})
        self.manifest = {'schemaVersion': 'remaprx-prospective-archive-members-v1', 'members': rows}
        self.plan = {'schemaVersion': 'remaprx-zip-materialization-plan-v1', 'planId': 'SYNTHETIC-NOT-REAL-GP',
                     'operations': ['materialize-zip'], 'preparer': 'synthetic-test', 'canonicalReportId': 'SYNTHETIC-REPORT',
                     'archive': {'sourceId': 'SYNTHETIC-ZIP', 'sha256': tool.sha(self.archive), 'bytes': self.archive.stat().st_size},
                     'manifestPath': self.manifest_path.relative_to(tool.APP).as_posix(),
                     'privateOutputRoot': str(self.output), 'memberDirectory': 'CAL-01/archive-members',
                     'allowedDestinations': [r['proposedMaterializationRelativePath'] for r in rows],
                     'receiptRelativePath': 'CAL-01/materialization-receipt.json', 'inputs': [],
                     'scopeLimits': {'scientificReading': False, 'canonicalWrites': False, 'humanApproval': False, 'released': False}}
        self.write_controls()

    def write_controls(self):
        self.manifest_path.write_bytes(tool.canonical(self.manifest))
        files = [HERE/'materialize_zip.py', HERE/'inventory.py', tool.SCHEMA, HERE/'ZIP-MEMBER-CONTRACT-DRAFT.md',
                 HERE/'test_materialize_zip.py', tool.APP/'scripts/research_ingest/cli.py', tool.APP/'scripts/research_ingest/contracts.py',
                 tool.APP/'AGENTS.md', tool.APP/'docs/PROJECT-RULES.md', tool.APP/'docs/RULE-CHANGELOG.md',
                 tool.APP/'docs/RESEARCH-INGEST.md', self.manifest_path]
        self.plan['inputs'] = [{'path': f.relative_to(tool.APP).as_posix(), 'sha256': tool.sha(f)} for f in files]
        self.plan_path.write_bytes(tool.canonical(self.plan))
        self.readiness.write_bytes(tool.canonical({'schemaVersion': 'remaprx-gp-readiness-v1', 'status': 'PASS', 'scope': 'GP_PLAN',
                        'planId': self.plan['planId'], 'planSha256': tool.sha(self.plan_path), 'checkedAt': '2026-10-12T00:00:00Z'}))

    def run_tool(self):
        return tool.materialize(tool.APP, self.plan_path, self.readiness, self.manifest_path, self.archive, self.output)

    def test_actual_pdf_counts_complete_receipt_and_zero_change_repeat(self):
        first = self.run_tool()
        self.assertEqual(first['changedFiles'], 3)
        receipt_path = Path(first['receiptPath']); original = receipt_path.read_bytes()
        receipt = json.loads(original)
        self.assertEqual([r['pages'] for r in receipt['members']], [1, 1])
        self.assertTrue(all(r['result'] == 'created' for r in receipt['members']))
        self.assertFalse(receipt['scientificInspectionPerformed'])
        self.assertFalse(receipt['sourceReadinessGranted'])
        snapshots = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.output.rglob('*') if p.is_file()}
        second = self.run_tool()
        self.assertEqual(second['changedFiles'], 0)
        self.assertEqual(first['receiptSha256'], second['receiptSha256'])
        self.assertEqual(snapshots, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.output.rglob('*') if p.is_file()})

    def test_missing_stale_readiness_and_changed_controls_write_nothing(self):
        original = self.readiness.read_bytes()
        self.readiness.unlink()
        with self.assertRaises(OSError): self.run_tool()
        self.readiness.write_bytes(original)
        self.plan['preparer'] = 'changed-plan'; self.plan_path.write_bytes(tool.canonical(self.plan))
        with self.assertRaisesRegex(tool.Hold, 'stale'): self.run_tool()
        self.write_controls()
        self.manifest_path.write_text(self.manifest_path.read_text() + '\n')
        with self.assertRaisesRegex(tool.Hold, 'Pinned input changed'): self.run_tool()
        self.assertFalse(self.output.exists())

    def test_whole_archive_member_set_pages_and_duplicate_identity(self):
        original = self.archive.read_bytes()
        self.archive.write_bytes(original[:-1] + b'x')
        with self.assertRaisesRegex(tool.Hold, 'archive hash'): self.run_tool()
        self.archive.write_bytes(original)
        baseline = copy.deepcopy(self.manifest)
        for change in ['pages', 'missing', 'identity', 'destination']:
            with self.subTest(change=change):
                self.manifest = copy.deepcopy(baseline)
                if change == 'pages': self.manifest['members'][0]['member']['pages'] = 2
                elif change == 'missing': self.manifest['members'].pop()
                elif change == 'identity': self.manifest['members'][1]['sourceId'] = self.manifest['members'][0]['sourceId'].lower()
                else: self.manifest['members'][0]['proposedMaterializationRelativePath'] = '../outside.pdf'
                self.write_controls()
                with self.assertRaises(ValueError): self.run_tool()
                self.assertFalse(self.output.exists())

    def test_unknown_unsafe_member_rejected_even_with_correct_archive_hash(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as archive:
            archive.writestr('../escape.pdf', pdf('unsafe'))
        self.archive.write_bytes(data.getvalue())
        self.plan['archive'].update(sha256=tool.sha(self.archive), bytes=len(data.getvalue()))
        self.write_controls()
        with self.assertRaisesRegex(ValueError, 'Unsafe'): self.run_tool()
        self.assertFalse(self.output.exists())

    def test_no_clobber_symlink_boundary_and_concurrent_lock(self):
        dest = self.output / self.plan['allowedDestinations'][1]
        dest.parent.mkdir(parents=True); dest.write_bytes(b'unrelated private file')
        with self.assertRaisesRegex(tool.Hold, 'different bytes'): self.run_tool()
        self.assertEqual(dest.read_bytes(), b'unrelated private file')
        self.assertFalse((self.output / self.plan['allowedDestinations'][0]).exists())
        dest.unlink(); dest.symlink_to(self.archive)
        with self.assertRaisesRegex(tool.Hold, 'Symlink'): self.run_tool()
        dest.unlink()
        lock = self.output / '.rrx-materialization.lock'; lock.write_bytes(b'other owner')
        with self.assertRaisesRegex(tool.Hold, 'locked'): self.run_tool()
        self.assertEqual(lock.read_bytes(), b'other owner')

    def test_partial_interruption_retry_and_receipt_conflict(self):
        original = tool.install_exclusive
        calls = []
        def interrupted(*args):
            calls.append(args[1])
            if len(calls) == 2: raise OSError('simulated second-member failure')
            return original(*args)
        with patch.object(tool, 'install_exclusive', interrupted), self.assertRaisesRegex(tool.Hold, 'simulated') as caught:
            self.run_tool()
        self.assertEqual(len(caught.exception.receipt['changedPaths']), 1)
        self.assertFalse((self.output / self.plan['receiptRelativePath']).exists())
        self.assertFalse((self.output / '.rrx-materialization.lock').exists())
        completed = self.run_tool()
        self.assertEqual(completed['changedFiles'], 2)
        receipt_path = Path(completed['receiptPath'])
        receipt = json.loads(receipt_path.read_bytes())
        self.assertEqual([r['result'] for r in receipt['members']], ['reused_exact', 'created'])
        receipt['preparer'] = 'different'; receipt_path.write_bytes(tool.canonical(receipt))
        with self.assertRaisesRegex(tool.Hold, 'different controls'): self.run_tool()

    def test_archive_drift_during_write_holds_without_success_receipt(self):
        original = tool.install_exclusive
        def mutated(*args):
            result = original(*args)
            self.archive.write_bytes(self.archive.read_bytes() + b'changed')
            return result
        with patch.object(tool, 'install_exclusive', mutated), self.assertRaisesRegex(tool.Hold, 'archive changed'):
            self.run_tool()
        self.assertFalse((self.output / self.plan['receiptRelativePath']).exists())

    def test_output_must_be_external_ignored_and_untracked(self):
        with self.assertRaisesRegex(tool.Hold, 'outside'): tool.private_root(tool.APP, HERE / 'raw', ['x.pdf'])
        with self.assertRaisesRegex(tool.Hold, 'contain'): tool.private_root(tool.APP, tool.APP.parent, ['x.pdf'])
        git_root = self.external / 'enclosing'; git_root.mkdir()
        subprocess.run(['git', 'init', '-q', str(git_root)], check=True)
        output = git_root / 'raw'
        with self.assertRaisesRegex(tool.Hold, 'ignored'): tool.private_root(tool.APP, output, ['x.pdf'])
        (git_root / '.gitignore').write_text('/raw/\n')
        self.assertTrue(tool.private_root(tool.APP, output, ['x.pdf'])['ignored'])
        output.mkdir(); (output / 'x.pdf').write_bytes(pdf('tracked'))
        subprocess.run(['git', '-C', str(git_root), 'add', '-f', 'raw/x.pdf'], check=True)
        with self.assertRaisesRegex(tool.Hold, 'tracked'): tool.private_root(tool.APP, output, ['x.pdf'])

    def test_receipt_cannot_be_a_member_ancestor(self):
        self.plan['memberDirectory'] = 'receipt.json/members'
        for row in self.manifest['members']:
            row['proposedMaterializationRelativePath'] = self.plan['memberDirectory'] + '/' + row['member']['sha256'] + '.pdf'
        self.plan['allowedDestinations'] = [r['proposedMaterializationRelativePath'] for r in self.manifest['members']]
        self.plan['receiptRelativePath'] = 'receipt.json'
        self.write_controls()
        with self.assertRaisesRegex(tool.Hold, 'File/directory'): self.run_tool()
        self.assertFalse(self.output.exists())


if __name__ == '__main__': unittest.main()
