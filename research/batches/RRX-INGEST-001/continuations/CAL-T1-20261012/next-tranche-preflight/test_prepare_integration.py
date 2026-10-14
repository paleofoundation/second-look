"""Independent preparer boundary tests; scientific validation is a mocked gate.

All fixtures and simulated canonical writes live in TemporaryDirectory. These
tests exercise control races, preservation and identity, not source appraisal.
"""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file() and (p/'data').is_dir())
sys.path.insert(0,str(ROOT))
import scripts.research_full_review as full_review
from scripts.research_ingest import cli

HERE='research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012'
CORPUS='research/corpus/RRX-INGEST-001/full-reviews'


class PrepareIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.real_canonical=cli.canonical
        def save(name,value):
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(cli.canonical(value));return p
        self.save=save
        self.candidate=save(HERE+'/CAL-07/candidate.json',{'canonicalReportId':'REPORT1','reviewId':'REPORT1'})
        self.evidence=save(HERE+'/CAL-07/evidence.json',{'fixture':'independent evidence'})
        self.audit=save(HERE+'/CAL-07/audit.json',{'evidence':[{'path':self.evidence.relative_to(self.root).as_posix(),'sha256':cli.sha(self.evidence)}]})
        self.source_map=save(HERE+'/source-map.json',{'roots':{},'files':[]})
        self.assignment=save(HERE+'/CAL-07/assignment.json',{'fixture':'assignment'})
        self.gp=save(HERE+'/CAL-07/readiness.json',{'fixture':'readiness'})
        self.schema=save(HERE+'/schemas/full-review.schema.json',{'fixture':'schema'})
        for name in ['AGENTS.md','docs/PROJECT-RULES.md','docs/RESEARCH-INGEST.md','docs/RULE-CHANGELOG.md','scripts/research_ingest/contracts.py','scripts/research_ingest/__main__.py']:
            save(name,{'fixture':name})
        old=[]
        for n in range(48):
            p=save(f'research/corpus/RRX-INGEST-001/recovered/{n:02}.json',{'preserved':n})
            old.append({'path':p.relative_to(self.root).as_posix(),'sha256':cli.sha(p)})
        self.baseline=save(HERE+'/integration-baseline.json',{'files':old})
        self.plan=save(HERE+'/CAL-07/plan.json',{'planId':'SOURCE-TEST','inputs':[{'path':self.schema.relative_to(self.root).as_posix(),'sha256':cli.sha(self.schema)}]})
        script=self.root/HERE/'prepare-integration.py';script.write_bytes((ROOT/HERE/'prepare-integration.py').read_bytes())
        spec=importlib.util.spec_from_file_location('preparer_fixture',script);self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
        self.index=self.root/CORPUS/'index.json'
        self.baseline_hashes={self.root/x['path']:x['sha256'] for x in old}

    def tearDown(self):
        self.temp.cleanup()

    def run_prepare(self,suffix='1',during_validate=None,packet_path=None,plan_dir=None):
        def accepted(args):
            result={'completionState':'accepted_private','candidateSha256':cli.sha(self.candidate),'planSha256':cli.sha(self.plan),'humanApproval':False,'released':False}
            if during_validate:during_validate()
            return result
        argv=['prepare-integration.py','--root',str(self.root),'--review-dir',HERE+'/CAL-07',
              '--candidate',self.candidate.relative_to(self.root).as_posix(),'--audit',self.audit.relative_to(self.root).as_posix(),
              '--source-map',self.source_map.relative_to(self.root).as_posix(),'--packet',packet_path or 'work/research-ingest/packet-'+suffix,
              '--plan-dir',plan_dir or HERE+'/integration-'+suffix,'--plan-id','INTEGRATION-'+suffix]
        output=io.StringIO()
        with patch.object(sys,'argv',argv),patch.object(sys,'path',list(sys.path)),patch.object(full_review,'validate',side_effect=accepted),redirect_stdout(output):
            self.module.main()
        return json.loads(output.getvalue())

    def assert_baseline(self):
        self.assertTrue(all(cli.sha(path)==value for path,value in self.baseline_hashes.items()))

    def test_insert_prepares_private_only_and_preserves_all48(self):
        result=self.run_prepare()
        self.assertFalse(result['performedImport'])
        self.assertFalse(self.index.exists())
        self.assert_baseline()
        plan=json.loads((self.root/HERE/'integration-1/plan.json').read_text())
        self.assertEqual(set(plan['allowedTargets']),{CORPUS+'/REPORT1.json',CORPUS+'/index.json'})
        self.assertEqual(plan['contract']['historicalFilesPreserved'],48)

    def test_changed_controls_after_validation_are_never_re_pinned(self):
        for name in ['audit','source_map','gp','plan','evidence','schema']:
            with self.subTest(control=name):
                path=getattr(self,name);before=path.read_bytes()
                try:
                    with self.assertRaises(cli.Hold):self.run_prepare(name,lambda:path.write_bytes(before+b'\n'))
                    self.assertFalse((self.root/HERE/('integration-'+name)).exists())
                    self.assertFalse(self.index.exists())
                finally:path.write_bytes(before)
        self.assert_baseline()

    def test_index_race_while_deriving_payload_holds_without_overwrite(self):
        concurrent=self.real_canonical({'schemaVersion':'remaprx-private-full-review-index-v1','reviews':[],'concurrent':'preserve'})
        def interleaved(value):
            if isinstance(value,dict) and value.get('schemaVersion')=='remaprx-private-full-review-index-v1':
                self.index.parent.mkdir(parents=True,exist_ok=True);self.index.write_bytes(concurrent)
            return self.real_canonical(value)
        with patch.object(cli,'canonical',side_effect=interleaved),self.assertRaisesRegex(cli.Hold,'Canonical base changed'):
            self.run_prepare()
        self.assertEqual(self.index.read_bytes(),concurrent)
        self.assertFalse((self.root/HERE/'integration-1').exists())

    def test_index_race_after_packet_write_holds_and_preserves_external_bytes(self):
        real_write=Path.write_bytes
        concurrent=self.real_canonical({'schemaVersion':'remaprx-private-full-review-index-v1','reviews':[],'concurrent':'preserve'})
        def interleaved(path,data):
            result=real_write(path,data)
            if str(path).endswith('/candidate/'+CORPUS+'/index.json'):
                self.index.parent.mkdir(parents=True,exist_ok=True);real_write(self.index,concurrent)
            return result
        with patch.object(Path,'write_bytes',new=interleaved),self.assertRaisesRegex(cli.Hold,'Canonical base changed'):
            self.run_prepare()
        self.assertEqual(self.index.read_bytes(),concurrent)
        self.assert_baseline()

    def test_reserved_and_case_colliding_identities_hold(self):
        self.candidate.write_bytes(self.real_canonical({'canonicalReportId':'INDEX','reviewId':'INDEX'}))
        with self.assertRaisesRegex(cli.Hold,'Reserved'):self.run_prepare()
        self.candidate.write_bytes(self.real_canonical({'canonicalReportId':'REPORT1','reviewId':'REPORT1'}))
        self.save(CORPUS+'/report1.json',{'fixture':'different case'})
        with self.assertRaisesRegex(cli.Hold,'Case-colliding'):self.run_prepare()

    def test_orphan_and_mismatched_indexed_body_hold(self):
        body=self.save(CORPUS+'/REPORT1.json',{'fixture':'orphan'})
        with self.assertRaisesRegex(cli.Hold,'Unindexed'):self.run_prepare()
        self.save(CORPUS+'/index.json',{'schemaVersion':'remaprx-private-full-review-index-v1','reviews':[{'canonicalReportId':'REPORT1','path':CORPUS+'/REPORT1.json','sha256':'f'*64}]})
        with self.assertRaisesRegex(cli.Hold,'approved pin'):self.run_prepare()
        self.assertEqual(json.loads(body.read_text()),{'fixture':'orphan'})

    def test_public_output_and_symlink_escape_are_rejected(self):
        with self.assertRaisesRegex(cli.Hold,'isolated work packet'):self.run_prepare(packet_path='public/packet')
        with self.assertRaisesRegex(cli.Hold,'continuation plan directory'):self.run_prepare(plan_dir='public/plan')
        (self.root/'work').mkdir();(self.root/'public').mkdir()
        (self.root/'work/research-ingest').symlink_to(self.root/'public',target_is_directory=True)
        with self.assertRaises(cli.Hold):self.run_prepare()
        self.assertEqual(list((self.root/'public').iterdir()),[])

    def test_exact_repeat_preserves_index_bytes_and_revision_holds(self):
        self.run_prepare('1')
        packet=self.root/'work/research-ingest/packet-1/candidate'
        for name in [CORPUS+'/REPORT1.json',CORPUS+'/index.json']:
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((packet/name).read_bytes())
        previous=self.index.read_bytes()
        self.run_prepare('2')
        self.assertEqual((self.root/'work/research-ingest/packet-2/candidate'/CORPUS/'index.json').read_bytes(),previous)
        self.candidate.write_bytes(self.real_canonical({'canonicalReportId':'REPORT1','reviewId':'REPORT1','revision':'changed'}))
        with self.assertRaisesRegex(cli.Hold,'separate preservation'):self.run_prepare('3')
        self.assertEqual(self.index.read_bytes(),previous)


if __name__=='__main__':unittest.main()
