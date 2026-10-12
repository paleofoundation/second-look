import copy
import importlib.util
from pathlib import Path
import unittest
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('checkpoint_audit', ROOT / 'scripts/audit-research-checkpoint.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def fixture():
    candidate = {'inspection': {'scope': 'partial_source'}, 'human_review_status': 'pending',
                 'excluded_from_accepted_support': True, 'mechanism_payload': None,
                 'results': [{'id': f'R{i}'} for i in range(3)], 'claims': [{'id': f'C{i}'} for i in range(4)],
                 'questions': [{'id': f'Q{i:02}', 'status': 'located_candidate' if i <= 5 else 'partial'} for i in range(1, 16)]}
    mechanism = {'publicationState': 'private_ai_draft', 'humanApproval': 'pending', 'scientificAssessment': 'pending', 'clinicalBenefitEstablished': False}
    proposals = {'performedImport': False, 'humanApproval': False, 'releaseChanged': False, 'synthesisProposals': [],
                 'mechanismProposals': [copy.deepcopy(mechanism), copy.deepcopy(mechanism)],
                 'pageProposals': [{'guideId': 'G-DRUG-D07'}, {'guideId': 'G-DRUG-D07'},
                                  {'guideId': 'G-CONDITION-C19', 'sections': [{'id': 'interventions', 'label': 'Interventions'}],
                                   'destinationStatus': 'private_proposal', 'renderedTargetVerified': False, 'layoutStatus': 'pending_layout'}],
                 'historyProposals': [{}, {}, {}], 'reviewProposal': {'reviewCompletion': 'pending', 'humanApproval': 'pending', 'release': 'pending', 'accessPolicy': 'free_authenticated'},
                 'invalidations': {'applyAutomatically': False}}
    return candidate, {'binding': 'exact'}, {'receipt': 'exact'}, proposals


class CheckpointAuditTests(unittest.TestCase):
    def verify(self, values):
        return audit.verify_bundle(audit.canonical(audit.expected_bundle(*values)), *values)

    def test_exact_bounded_bundle(self):
        self.assertFalse(self.verify(fixture())['fullScientificReviewComplete'])

    def test_changed_candidate_bytes_or_extra_field(self):
        values = fixture(); bundle = audit.expected_bundle(*values)
        bundle['candidate'] = copy.deepcopy(bundle['candidate']); bundle['candidate']['results'][0]['text'] = 'unverified edit'
        with self.assertRaisesRegex(ValueError, 'exactly preserve'):
            audit.verify_bundle(audit.canonical(bundle), *values)
        bundle = audit.expected_bundle(*values); bundle['unreviewed_payload'] = {'newClaim': True}
        with self.assertRaisesRegex(ValueError, 'exactly preserve'):
            audit.verify_bundle(audit.canonical(bundle), *values)

    def test_source_scope_or_missingness_cannot_be_promoted(self):
        for mutation in ['scope', 'question']:
            values = fixture()
            if mutation == 'scope': values[0]['inspection']['scope'] = 'full_source'
            else: values[0]['questions'][5]['status'] = 'located_candidate'
            with self.assertRaises(ValueError): self.verify(values)

    def test_clinical_synthesis_or_approval_cannot_be_added(self):
        for mutation in ['clinical', 'approval']:
            values = fixture()
            if mutation == 'clinical': values[3]['synthesisProposals'] = [{'humanEfficacy': True}]
            else: values[3]['reviewProposal']['humanApproval'] = 'approved'
            with self.assertRaises(ValueError): self.verify(values)

    def test_condition_layout_cannot_claim_rendered_or_generic_mechanism(self):
        for mutation in ['rendered', 'section']:
            values = fixture(); condition = values[3]['pageProposals'][2]
            if mutation == 'rendered': condition['renderedTargetVerified'] = True
            else: condition['sections'] = [{'id': 'mechanisms', 'label': 'Mechanism of Action'}]
            with self.assertRaises(ValueError): self.verify(values)

    def test_noncanonical_or_duplicate_key_json_is_rejected(self):
        values = fixture(); data = audit.canonical(audit.expected_bundle(*values))
        with self.assertRaisesRegex(ValueError, 'exactly preserve'):
            audit.verify_bundle(b' ' + data, *values)
        with self.assertRaisesRegex(ValueError, 'Duplicate JSON key'):
            audit.decode('{"status":"PASS","status":"HOLD"}')


class IsolatedReplayTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(); self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.name = 'docs/PROJECT-RULES.md'; self.snapshot = 'research/snapshots/PROJECT-RULES.md'
        self.old = b'Existing scientific contract.\n'; self.current = self.old + b'Append-only blue illustration requirement.\n'
        for name, value in [(self.name, self.current), (self.snapshot, self.old), ('data/current.json', b'{}\n')]:
            path = self.root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(value)
        self.history = {self.name: audit.digest(self.old), 'data/current.json': audit.digest(b'{}\n')}
        self.override = {'path': self.name, 'historicalSha256': audit.digest(self.old), 'snapshotPath': self.snapshot,
                         'currentSha256': audit.digest(self.current), 'reason': 'Append-only illustration rules from another task; isolate archived private proposal replay.'}
        self.plan = {'inputs': [{'path': self.name, 'sha256': audit.digest(self.current)}, {'path': self.snapshot, 'sha256': audit.digest(self.old)},
                                {'path': 'data/current.json', 'sha256': audit.digest(b'{}\n')}], 'contract': {'isolatedReplayOverrides': [self.override]}}
    def read(self, path, checksum=None):
        value = Path(path).read_bytes()
        audit.require(checksum is None or audit.digest(value) == checksum, 'hash mismatch')
        return value
    def select(self): return audit.select_replay_inputs(self.root, self.history, self.plan, self.read)
    def test_exact_snapshot_selected_without_touching_current(self):
        selected, receipt = self.select()
        self.assertEqual(selected[self.name], self.old)
        self.assertEqual((self.root/self.name).read_bytes(), self.current)
        self.assertTrue(receipt[0]['currentDocumentPreserved'])
    def test_unlisted_current_change_holds(self):
        (self.root/'data/current.json').write_text('{"changed":true}')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'): self.select()
    def test_non_doc_override_rejected(self):
        self.override['path'] = 'data/current.json'
        with self.assertRaisesRegex(ValueError, 'Only distinct'): self.select()
    def test_current_and_snapshot_both_must_be_pinned(self):
        self.plan['inputs'] = [x for x in self.plan['inputs'] if x['path'] != self.snapshot]
        with self.assertRaisesRegex(ValueError, 'Both current'): self.select()
    def test_changed_snapshot_rejected(self):
        (self.root/self.snapshot).write_text('different contract')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'): self.select()
    def test_replacement_of_old_contract_rejected(self):
        data = b'Changed scientific contract.\n'
        (self.root/self.name).write_bytes(data); self.override['currentSha256'] = audit.digest(data)
        self.plan['inputs'][0]['sha256'] = audit.digest(data)
        with self.assertRaisesRegex(ValueError, 'append-only'): self.select()
    def test_duplicate_override_rejected(self):
        self.plan['contract']['isolatedReplayOverrides'].append(dict(self.override))
        with self.assertRaisesRegex(ValueError, 'Only distinct'): self.select()
    def test_snapshot_symlink_escape_rejected(self):
        path = self.root/self.snapshot; path.unlink(); path.symlink_to(self.root/self.name)
        with self.assertRaisesRegex(ValueError, 'Symlink'): self.select()


if __name__ == '__main__': unittest.main()
