"""Independent recovery auditor probes using a small isolated fixture checkpoint."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/audit-research-recovery.py'
SPEC = importlib.util.spec_from_file_location('recovery_audit', SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class RecoveryAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'app'
        self.batch = self.root / 'research/batches/RRX-INGEST-001'
        self.packet = self.root / 'work/research-ingest/fixture'
        self.historical = Path(self.temp.name) / 'historical'
        self.saved = (audit.ROOT, audit.BATCH, audit.EXPECTED_FILES, audit.EXPECTED_COLLECTIONS)
        self.addCleanup(self.restore)
        audit.ROOT, audit.BATCH = self.root, self.batch
        audit.EXPECTED_FILES = len(audit.EXPECTED_COLLECTIONS)
        audit.EXPECTED_COLLECTIONS = {key: (field, 1) for key, (field, _) in audit.EXPECTED_COLLECTIONS.items()}
        recovery, payloads = [], []
        for relative, (identity_key, _) in audit.EXPECTED_COLLECTIONS.items():
            row = {identity_key: relative, 'human_review_status': 'pending', 'publication_state': 'draft'}
            if relative == 'draft-science/reviews.jsonl':
                row['full_review_complete'] = False
            data = audit.canonical(row)
            source = self.historical / relative
            source.parent.mkdir(parents=True, exist_ok=True); source.write_bytes(data)
            target = 'research/corpus/RRX-INGEST-001/' + relative
            candidate = 'candidate/' + target
            destination = self.packet / candidate
            destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(data)
            recovery.append({'rootId': 'HISTORY', 'path': relative, 'sha256': audit.digest(data), 'bytes': len(data), 'target': target})
            payloads.append({'target': target, 'path': candidate, 'sha256': audit.digest(data), 'baseSha256': None})
        self.put(self.batch / 'recovery-inputs.json', {'files': recovery})
        self.put(self.batch / 'inventory/source-locations.json', {'roots': {'HISTORY': {'path': str(self.historical)}}})
        plan = {'schemaVersion': 'remaprx-ingest-plan-v1', 'planId': 'fixture-plan', 'operations': ['apply'],
                'allowedTargets': [entry['target'] for entry in recovery],
                'inputs': [{'path': path.relative_to(self.root).as_posix(), 'sha256': audit.digest(path.read_bytes())}
                           for path in [self.batch / 'recovery-inputs.json', self.batch / 'inventory/source-locations.json']]}
        self.put(self.batch / 'plan.json', plan)
        plan_hash = audit.digest((self.batch / 'plan.json').read_bytes())
        self.put(self.batch / 'readiness.json', {'schemaVersion': 'remaprx-gp-readiness-v1', 'status': 'PASS', 'scope': 'GP_PLAN',
                                               'planId': plan['planId'], 'planSha256': plan_hash})
        self.manifest = {'schemaVersion': 'remaprx-candidate-v1', 'planId': plan['planId'], 'planSha256': plan_hash,
                         'batchId': 'RRX-INGEST-001-RECOVERY', 'author': 'codex/root', 'files': payloads}
        self.put(self.packet / 'manifest.json', self.manifest)

    def restore(self):
        audit.ROOT, audit.BATCH, audit.EXPECTED_FILES, audit.EXPECTED_COLLECTIONS = self.saved

    def put(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audit.canonical(value))

    def test_exact_private_candidate_passes_without_writing_targets(self):
        evidence, report = audit.audit(self.packet)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['candidateDigest'], audit.digest(audit.canonical(self.manifest)))
        self.assertEqual(evidence['collections']['draft-science/reviews.jsonl']['completedFullReviews'], 0)
        self.assertFalse((self.root / 'research/corpus').exists())
        self.assertFalse((self.packet / 'audit').exists())

    def test_source_or_candidate_byte_change_holds(self):
        file = self.packet / self.manifest['files'][0]['path']
        file.write_bytes(b'{}\n')
        with self.assertRaisesRegex(ValueError, 'Pinned artifact changed'):
            audit.audit(self.packet)

    def test_concurrent_target_is_preserved_and_rejected(self):
        target = self.root / self.manifest['files'][0]['target']
        self.put(target, {'concurrent': True})
        before = target.read_bytes()
        with self.assertRaisesRegex(ValueError, 'declared base'):
            audit.audit(self.packet)
        self.assertEqual(target.read_bytes(), before)

    def test_self_audit_and_path_escape_are_rejected(self):
        self.manifest['author'] = audit.AUDITOR
        self.put(self.packet / 'manifest.json', self.manifest)
        with self.assertRaisesRegex(ValueError, 'independent'):
            audit.audit(self.packet)
        for relative in ['../escape', '/absolute', 'candidate/../escape', 'a\\b']:
            with self.assertRaises(ValueError):
                audit.safe(self.packet, relative)

    def test_changed_readiness_holds_and_public_packet_rejected(self):
        self.put(self.batch / 'readiness.json', {'status': 'PASS', 'scope': 'GP_PLAN', 'planSha256': '0' * 64})
        with self.assertRaisesRegex(ValueError, 'matching prospective'):
            audit.audit(self.packet)
        with self.assertRaisesRegex(ValueError, 'dedicated private'):
            audit.audit(self.root / 'public')


if __name__ == '__main__':
    unittest.main()
