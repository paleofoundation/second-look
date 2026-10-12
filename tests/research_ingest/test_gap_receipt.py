import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from copy import deepcopy
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[2]
PACKET = REPO / 'research/batches/RRX-INGEST-001/grok/RRX-GAP-001'
spec = importlib.util.spec_from_file_location('gap_receipt', REPO / 'scripts/verify-research-gap-return.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = (self.base / 'app').resolve()
        self.root.mkdir()
        self.old = m.ROOT
        m.ROOT = self.root
        self.plan = json.loads((PACKET / 'plan.json').read_text())
        self.schema = self.root / 'return.schema.json'
        names = ['return.schema.json', 'review-inputs.schema.json', 'review-questions-and-inputs.json']
        for name in names:
            (self.root / name).write_bytes((PACKET / name).read_bytes())
        self.plan['inputs'] = [{'path': name, 'sha256': m.sha(self.root / name)} for name in names]
        self.pp = self.root / 'plan.json'
        self.pp.write_text(json.dumps(self.plan))
        self.ph = m.sha(self.pp)
        self.gp = self.root / 'readiness.json'
        self.gp.write_text(json.dumps(dict(schemaVersion='remaprx-gp-readiness-v1', status='PASS', scope='GP_PLAN', planId=self.plan['planId'], planSha256=self.ph, checkedAt=datetime.now(timezone.utc).isoformat())))
        self.logs = [dict(query=q['query'], location=q['location'], executedAt='2026-10-12T00:00:00Z', resultCount=0, limits='Synthetic no-source fixture.') for g in self.plan['gaps'] for q in g['queries']]
        self.man = dict(schemaVersion='remaprx-gap-return-v1', planId=self.plan['planId'], planSha256=self.ph, batchId='RRX-GAP-001', files=[], fileCount=0, searchLog='search-log.json', screeningLog='screening-log.json', gaps='gaps.json', reviewInputs='review-inputs.jsonl', ingestPrompt='CHATGPT-INGEST-PROMPT.txt')
        self.members = {'search-log.json': json.dumps(self.logs), 'screening-log.json': '[]', 'gaps.json': json.dumps([dict(gapId=g['id'], reason='Synthetic unavailable full text', nextAction='Recheck lawful access') for g in self.plan['gaps']])}
        self.rows = []
        self.prompt_override = None

    def tearDown(self):
        m.ROOT = self.old
        self.tmp.cleanup()

    def prompt(self):
        prompt = (PACKET / 'CHATGPT-INGEST-PROMPT.template.txt').read_text()
        values = {
            '[actual downloadable filename and link]': 'return.zip (synthetic local fixture)',
            '[hash of manifest.json]': hashlib.sha256(self.members['manifest.json'].encode()).hexdigest(),
            '[actual return schema SHA-256]': m.sha(self.schema),
            '[actual review-input schema SHA-256]': m.sha(self.root / 'review-inputs.schema.json'),
            '[exact input plan]': self.plan['planId'] + ' ' + self.ph,
            '[actual count]': str(self.man['fileCount']),
            '[actual timestamps]': '2026-10-12T00:00:00Z; synthetic query fixture only',
            '[actual list]': 'Synthetic unavailability only; no genuine acquisition or scientific approval.',
        }
        for token, value in values.items():
            prompt = prompt.replace(token, value)
        return prompt

    def verify(self, extra=None):
        self.members['manifest.json'] = json.dumps(self.man)
        self.members['review-inputs.jsonl'] = ''.join(json.dumps(row) + '\n' for row in self.rows)
        self.members['CHATGPT-INGEST-PROMPT.txt'] = self.prompt_override or self.prompt()
        archive = self.base / 'return.zip'
        with zipfile.ZipFile(archive, 'w') as z:
            for name, value in self.members.items():
                z.writestr(name, value)
            if extra:
                z.writestr(*extra)
        return m.verify(archive, self.pp, self.gp, self.schema)

    def full_report(self):
        body = '<html><section id="methods">This synthetic randomized trial compared A with B in adults for fourteen days.</section><section id="results">There were twelve events in arm A.</section></html>'
        file = dict(id='asset1', path='files/report.html', sha256=hashlib.sha256(body.encode()).hexdigest(), bytes=len(body.encode()), mediaType='text/html', sourceId='SYNTHETIC-V1', canonicalReportId='SYNTHETIC-REPORT', role='original_report', downloadUrl='https://example.invalid/fixture', rightsOrAccessBasis='Synthetic fixture authored for a unit test', retrievedAt='2026-10-12T00:00:00Z', gapIds=['GAP-JOURNAL-ACTIV6'])
        self.man['files'] = [file]
        self.man['fileCount'] = 1
        self.members[file['path']] = body
        questions = m.load(self.root / 'review-questions-and-inputs.json')
        answers = {('Q01', 'objective'): 'Compare A with B over fourteen days.', ('Q02', 'population_species'): 'Adults', ('Q04', 'comparator'): 'B', ('Q06', 'arm_results'): 'Twelve events in arm A.'}
        for question in questions['questions']:
            for field in question['inputFields']:
                answer = answers.get((question['id'], field))
                self.rows.append(dict(paperId=file['canonicalReportId'], questionId=question['id'], questionSetVersion=questions['questionSetVersion'], field=field, value_or_null=answer, status='answered' if answer else 'not_extracted', reason=None if answer else 'Not extracted from this bounded synthetic fixture.', sourceId=file['sourceId'], sourceHash=file['sha256'], nativeLocator=dict(kind='html', location='#results' if question['id']=='Q06' else '#methods', quotedText='There were twelve events in arm A.' if question['id']=='Q06' else 'This synthetic randomized trial compared A with B in adults for fourteen days.') if answer else None, extractionBasis='Synthetic full-text fixture; extraction assertions remain pending verification.', verificationState='pending', nextAction=None if answer else 'Inspect the requested field before review completion.'))
        return file

    def companion(self, source_id='SYNTHETIC-COMPANION'):
        file = deepcopy(self.man['files'][0])
        file.update(id='asset2', path='files/companion.html', sourceId=source_id, role='supplement')
        self.members[file['path']] = self.members[self.man['files'][0]['path']]
        self.man['files'].append(file)
        self.man['fileCount'] += 1
        return file

    def test_honest_empty_with_explicit_gaps(self):
        self.assertEqual(self.verify()['sourceFiles'], 0)

    def test_nonempty_report_has_exact_full_question_field_coverage(self):
        self.full_report()
        result = self.verify()
        self.assertEqual(result['sourceFiles'], 1)
        self.assertFalse(result['scientificApproval'])
        self.assertEqual({row['questionId'] for row in self.rows}, {f'Q{i:02d}' for i in range(1, 16)})
        self.assertEqual(sum(row['status']=='answered' for row in self.rows), 4)
        self.assertNotIn('[actual', self.members['CHATGPT-INGEST-PROMPT.txt'])
        self.assertIn('separate reply or sidecar', self.members['CHATGPT-INGEST-PROMPT.txt'])

    def test_companion_mapping_is_explicit_and_one_field_not_duplicated(self):
        self.full_report()
        companion = self.companion()
        self.rows[-1].update(sourceId=companion['sourceId'], sourceHash=companion['sha256'])
        self.assertEqual(self.verify()['sourceFiles'], 2)
        duplicate = deepcopy(self.rows[0])
        duplicate.update(sourceId=companion['sourceId'], sourceHash=companion['sha256'])
        self.rows.append(duplicate)
        with self.assertRaisesRegex(ValueError, 'Duplicate paper/question/field'):
            self.verify()

    def test_missing_and_duplicate_required_fields_rejected(self):
        self.full_report()
        removed = self.rows.pop()
        with self.assertRaisesRegex(ValueError, 'Missing exact Q01-Q15'):
            self.verify()
        self.rows.append(removed)
        self.rows.append(deepcopy(self.rows[0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate paper/question/field'):
            self.verify()

    def test_malformed_answered_and_missing_fields_rejected(self):
        self.full_report()
        baseline = deepcopy(self.rows)
        cases = [(0, 'field', 'wrong_field'), (0, 'value_or_null', ' '), (0, 'nativeLocator', None),
                 (1, 'reason', ''), (1, 'nextAction', None), (1, 'value_or_null', 'Contradicts missingness'),
                 (0, 'questionSetVersion', 'wrong_version')]
        for index, key, value in cases:
            with self.subTest(key=key, value=value):
                self.rows = deepcopy(baseline)
                self.rows[index][key] = value
                with self.assertRaisesRegex(ValueError, 'Review-input schema'):
                    self.verify()
        self.rows = deepcopy(baseline)
        self.rows[0].pop('nativeLocator')
        with self.assertRaisesRegex(ValueError, 'Review-input schema'):
            self.verify()

    def test_source_version_hash_and_duplicate_source_ids_rejected(self):
        self.full_report()
        self.rows[0]['sourceHash'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'source/report/hash mismatch'):
            self.verify()
        self.rows[0]['sourceHash'] = self.man['files'][0]['sha256']
        self.companion(source_id=self.man['files'][0]['sourceId'])
        with self.assertRaisesRegex(ValueError, 'Duplicate source IDs'):
            self.verify()

    def test_partial_value_requires_a_locator_and_preserves_unfinished_state(self):
        self.full_report()
        self.rows[0].update(status='partial', reason='Only a bounded part was located.', nextAction='Inspect the remaining objectives.', nativeLocator=None)
        with self.assertRaisesRegex(ValueError, 'Review-input schema'):
            self.verify()
        self.rows[0]['value_or_null'] = None
        self.assertEqual(self.verify()['status'], 'PASS_RECEIPT_ONLY')

    def test_manifest_prompt_hash_count_and_template_tokens_rejected(self):
        self.full_report()
        self.verify()
        correct = self.members['CHATGPT-INGEST-PROMPT.txt']
        manifest_hash = hashlib.sha256(self.members['manifest.json'].encode()).hexdigest()
        for prompt, expected in [(correct.replace(manifest_hash, '0'*64), 'manifest hash'),
                                 (correct.replace('Manifest source file count: 1', 'Manifest source file count: 2'), 'file count'),
                                 (correct+'\n[hash of manifest.json]', 'template tokens')]:
            with self.subTest(expected=expected):
                self.prompt_override = prompt
                with self.assertRaisesRegex(ValueError, expected):
                    self.verify()

    def test_unaccounted_gap_rejected(self):
        self.members['gaps.json'] = '[]'
        with self.assertRaisesRegex(ValueError, 'Unaccounted requested gap'):
            self.verify()

    def test_missing_queries_rejected(self):
        self.members['search-log.json'] = '[]'
        with self.assertRaisesRegex(ValueError, 'Missing planned search'):
            self.verify()

    def test_traversal_and_unlisted_members_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe archive member'):
            self.verify(('../outside.pdf', 'x'))

    def test_stale_plan_rejected(self):
        self.man['planSha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'Returned plan identity'):
            self.verify()

    def test_hash_mismatch_rejected(self):
        self.full_report()
        self.man['files'][0]['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'Source hash mismatch'):
            self.verify()


if __name__ == '__main__':
    unittest.main()
