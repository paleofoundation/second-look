"""Synthesis identities and legacy projection safety, using temporary fixture stores only."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reader_outcomes', ROOT / 'scripts/apply-reader-outcomes.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.fact = dict(drugId='D01', conditionId='C01', sourceId='P1', endpoint='Outcome A',
                         population='Adults', comparison='Placebo', timepoint='Week 12',
                         route='Oral', formulation='Tablet', finding='No difference',
                         magnitude='0 units', limits='Small trial', N=20)

    def test_each_scope_dimension_has_distinct_identity(self):
        baseline = module.resolve_synthesis_identity(self.fact, [])
        for field in module.DIMENSIONS:
            variant = {**self.fact, field: self.fact[field] + ' other'}
            self.assertNotEqual(baseline, module.resolve_synthesis_identity(variant, []), field)
        self.assertEqual(baseline, module.resolve_synthesis_identity(self.fact, []))

    def test_old_id_outcome_result_and_route_preserved(self):
        legacy = {**self.fact, 'id': 'SYN-LEGACY', 'sourceIds': ['P1'], 'resultIds': ['R-ORIGINAL'], 'answerRoutes': ['/answers/old']}
        registry = {'rowOutcomeMap': {'SYN-LEGACY': 'OUT-ORIGINAL'}}
        mapping = module.build_identity_map([legacy], registry)
        self.assertEqual(module.resolve_synthesis_identity(self.fact, [legacy], mapping=mapping), 'SYN-LEGACY')
        self.assertEqual(mapping['entries'][0]['outcomeId'], 'OUT-ORIGINAL')
        self.assertEqual(mapping['entries'][0]['resultIds'], ['R-ORIGINAL'])
        self.assertEqual(mapping['entries'][0]['answerRoutes'], ['/answers/old'])

    def test_two_endpoints_survive_a_source_alias(self):
        first = {**self.fact, 'id': 'SYN-OLD-PAPER-A', 'sourceIds': ['OLD']}
        second = {**self.fact, 'endpoint': 'Outcome B', 'id': 'SYN-PAPER-B', 'sourceIds': ['P1']}
        self.assertEqual(module.resolve_synthesis_identity(self.fact, [first, second], {'OLD': 'P1'}), first['id'])
        self.assertEqual(module.resolve_synthesis_identity({**self.fact, 'endpoint': 'Outcome B'}, [first, second], {'OLD': 'P1'}), second['id'])

    def test_ambiguous_and_unknown_scopes_hold(self):
        row = {**self.fact, 'id': 'ONE', 'sourceIds': ['P1']}
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            module.resolve_synthesis_identity(self.fact, [row, {**row, 'id': 'TWO'}])
        with self.assertRaisesRegex(ValueError, 'incomplete scope'):
            module.resolve_synthesis_identity(self.fact, [{**row, 'route': None}])
        with self.assertRaisesRegex(ValueError, 'alias cycle'):
            module.resolve_synthesis_identity(self.fact, [], {'P1': 'P2', 'P2': 'P1'})

    def test_duplicate_import_is_byte_identical_and_conflict_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            originals = module.ROOT
            module.ROOT = root
            try:
                (root / 'data').mkdir(); (root / 'editorial').mkdir()
                content = {'sources': [{'id': 'P1', 'design': 'Trial', 'locators': []}],
                           'guides': [{'id': 'G1', 'entityId': 'D01', 'sourceIds': [], 'synthesisIds': []}]}
                values = {'data/content.json': content, 'data/public-content.json': content,
                          'data/reader-evidence.json': {'synthesisRows': []}, 'data/public-reader-evidence.json': {'synthesisRows': []},
                          'data/outcome-registry.json': {'outcomes': [], 'rowOutcomeMap': {}},
                          'editorial/parent-guide-scopes.json': {'parents': []}, 'editorial/reader-source-aliases.json': {}}
                for name, value in values.items(): (root / name).write_text(json.dumps(value))
                batch = root / 'batch.json'
                batch.write_text(json.dumps({'evidenceRecords': [self.fact, {**self.fact, 'endpoint': 'Outcome B'}]}))
                with contextlib.redirect_stdout(io.StringIO()): module.apply_batches([batch])
                rows = json.loads((root / 'data/reader-evidence.json').read_text())['synthesisRows']
                self.assertEqual(len(rows), 2)
                self.assertEqual(len({row['id'] for row in rows}), 2)
                def hashes():
                    return {str(file.relative_to(root)): hashlib.sha256(file.read_bytes()).hexdigest()
                            for directory in ['data', 'editorial'] for file in (root / directory).glob('*.json')}
                before = hashes()
                with contextlib.redirect_stdout(io.StringIO()): module.apply_batches([batch])
                self.assertEqual(before, hashes(), 'Repeat import changes no bytes.')
                # A new first row followed by a conflicting update must not partially apply.
                batch.write_text(json.dumps({'evidenceRecords': [{**self.fact, 'endpoint': 'Outcome C'}, {**self.fact, 'finding': 'Conflicting claim'}]}))
                with self.assertRaisesRegex(ValueError, 'reviewed candidate importer'):
                    module.apply_batches([batch])
                self.assertEqual(before, hashes(), 'A rejected batch changes no canonical files.')
            finally:
                module.ROOT = originals


if __name__ == '__main__':
    unittest.main()
