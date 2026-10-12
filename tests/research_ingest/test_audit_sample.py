import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('audit_sample', Path(__file__).resolve().parents[2] / 'scripts/research-audit-sample.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SamplingTests(unittest.TestCase):
    def fixture(self):
        return {'seed': 'RRX-fixture-1', 'records': [
            {'id': f'R{i:03}', 'reportId': f'P{i}', 'sourceSha256': f'{i:064x}',
             'worker': 'a' if i < 21 else 'b', 'design': 'trial', 'format': 'pdf',
             'calibration': False, 'publicNumericalClaim': False, 'launchSupporting': False,
             'fullTextExtraction': True} for i in range(31)]}

    def test_deterministic_order_independent_stratified_ceiling(self):
        data = self.fixture()
        first = m.select(data)
        data['records'].reverse()
        self.assertEqual(first, m.select(data))
        self.assertEqual(first['selectedCount'], 4)
        self.assertEqual([s['required'] for s in first['strata']], [3, 1])
        self.assertFalse(first['auditPerformed'])

    def test_every_mandatory_packet_even_without_fulltext(self):
        data = self.fixture()
        for i, flag in enumerate(('calibration', 'publicNumericalClaim', 'launchSupporting')):
            data['records'][i][flag] = True
            data['records'][i]['fullTextExtraction'] = False
        selected = {r['id'] for r in m.select(data)['selected']}
        self.assertTrue({'R000', 'R001', 'R002'} <= selected)

    def test_material_error_expands_affected_dimensions(self):
        data = self.fixture()
        data['materialErrors'] = [{'recordId': 'R000', 'worker': 'a', 'design': None, 'format': None}]
        rows = m.select(data)['selected']
        expanded = [r for r in rows if 'material_error:R000' in r['reasons']]
        self.assertEqual(len(expanded), 21)
        data['materialErrors'][0]['worker'] = None
        self.assertEqual(m.select(data)['selectedCount'], 31)

    def test_bad_identity_or_invented_error_rejected(self):
        data = self.fixture()
        data['records'].append(dict(data['records'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'): m.select(data)
        data = self.fixture()
        data['materialErrors'] = [{'recordId': 'R000', 'worker': 'b', 'design': None, 'format': None}]
        with self.assertRaisesRegex(ValueError, 'differ'): m.select(data)

    def test_whitespace_cannot_hide_duplicate_or_error_dimension(self):
        for key in ('id', 'reportId', 'worker', 'design', 'format'):
            data = self.fixture()
            data['records'][0][key] += ' '
            with self.subTest(key=key), self.assertRaises(ValueError): m.select(data)
        data = self.fixture()
        data['materialErrors'] = [{'recordId': 'R000', 'worker': 'a ', 'design': None, 'format': None}]
        with self.assertRaisesRegex(ValueError, 'Invalid error'): m.select(data)

    def test_duplicate_report_version_and_nonboolean_flags_rejected(self):
        data = self.fixture()
        data['records'].append({**data['records'][0], 'id': 'other'})
        with self.assertRaisesRegex(ValueError, 'Duplicate report-version'): m.select(data)
        for flag in ('calibration', 'publicNumericalClaim', 'launchSupporting', 'fullTextExtraction'):
            for value in (None, 0, 'false'):
                data = self.fixture()
                data['records'][0][flag] = value
                with self.subTest(flag=flag, value=value), self.assertRaisesRegex(ValueError, 'booleans'): m.select(data)

    def test_mandatory_fulltext_is_outside_sample_denominator(self):
        data = self.fixture()
        data['records'][0]['calibration'] = True
        result = m.select(data)
        self.assertEqual(result['strata'][0]['eligible'], 20)
        self.assertEqual(result['strata'][0]['required'], 2)
        self.assertEqual(result['selectedCount'], 4)

    def test_material_error_expands_any_matching_dimension(self):
        data = self.fixture()
        for i, row in enumerate(data['records']):
            row['worker'] = 'a' if i % 3 == 0 else 'b'
            row['design'] = 'trial' if i % 3 == 1 else 'cohort'
            row['format'] = 'pdf' if i % 3 == 2 else 'html'
        data['materialErrors'] = [{'recordId': 'R000', 'worker': 'a', 'design': 'cohort', 'format': 'html'}]
        self.assertEqual(m.select(data)['selectedCount'], 31)


if __name__ == '__main__': unittest.main()
