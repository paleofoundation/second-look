from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from scripts.research_full_review import AUDIT_CHECKS, INTEGRITY_KINDS, QUESTION_MAP, SCHEMA_DIR, SCHEMAS, make_template, validate, validate_review
from scripts.research_ingest.cli import Hold, canonical, sha


class FullReviewTests(unittest.TestCase):
    def setUp(self):
        self.repo = Path(__file__).resolve().parents[2]
        self.question_map = json.loads((self.repo / QUESTION_MAP).read_text())
        self.assignment = dict(schemaVersion='remaprx-full-review-assignment-v1', assignmentId='A1', planId='P1', canonicalReportId='REPORT1', reviewId='REVIEW1', assets=[])
        specs = [('MAIN','primary','text/html',[('methods','html_section','#methods'),('results','html_section','#results')]),
                 ('SUP','companion','application/pdf',[('p1','pdf_page','1'),('p2','pdf_page','2')]),
                 ('FIG1','companion','image/jpeg',[('figure1','image','figure1.jpg')])]
        inspection=[]
        for sid,role,media,units in specs:
            self.assignment['assets'].append(dict(sourceId=sid,role=role,required=True,mediaType=media,availability='available',sha256='a'*64,bytes=100,path=sid,
                expectedUnits=[dict(id=i,kind=k,locator=l) for i,k,l in units],reason='This assigned asset contributes required report methods or measured results.'))
            visual=[i for i,k,l in units if k=='image']
            inspection.append(dict(sourceId=sid,sourceSha256='a'*64,status='full',unitIdsRead=[i for i,k,l in units],visualUnitIds=visual,
                readLog=[dict(unitId=i,inspectedAt='2026-10-12T12:00:00Z',method='visual_read' if i in visual else 'native_read',notes='Synthetic fixture inspection of this complete assigned source unit.') for i,k,l in units], limitations=[],nextAction=None))
        self.locator=dict(sourceId='MAIN',sourceSha256='a'*64,unitId='methods',kind='html_section',locator='#methods',quote='The synthetic source reports 12 observations.',figureTable=None)
        inputs=[];answers=[]
        for q in self.question_map['questions']:
            for field in q['inputFields']:
                inputs.append(dict(questionId=q['id'],field=field,status='reported',value='Synthetic source-reported input for this required review field.',reason='The synthetic assigned source provides the specified information directly.',basis='reported',sourceLocators=[deepcopy(self.locator)],assessedAssetIds=['MAIN','SUP','FIG1'],experimentIds=['E1'],numericClaimIds=[],nextAction=None))
            answers.append(dict(questionId=q['id'],status='answered',answer='The synthetic experiment supports only the measured population and comparison described in this report.',appraisalRationale='This fixture appraisal distinguishes the recorded observation from broader untested clinical conclusions.',inputFields=q['inputFields'],experimentIds=['E1'],sourceLocators=[deepcopy(self.locator)],limitations=[]))
        self.candidate=dict(schemaVersion='remaprx-full-review-v1',reviewId='REVIEW1',canonicalReportId='REPORT1',assignmentId='A1',assignmentSha256='b'*64,planId='P1',planSha256='c'*64,questionMapSha256='d'*64,questionSetVersion=self.question_map['questionSetVersion'],author='source author',processingState='candidate_complete',inspection=inspection,studyIds=['STUDY1'],familyIds=[],experiments=[dict(id='E1',label='Synthetic experiment',design='Synthetic controlled comparison',experimentalUnit='Individual experimental unit',studyIds=['STUDY1'],sourceLocators=[deepcopy(self.locator)])],identityRationale='One assigned report contains this explicitly identified synthetic experiment.',relatedReports=[],inputs=inputs,answers=answers,sourceIntegrity=[dict(kind=k,status='checked',checkedAt='2026-10-12T12:00:00Z',scope='Only this fixture version and its assigned companion source bytes were checked.',rationale='The synthetic fixture records a scoped integrity check without claiming an external search.',sourceLocators=[deepcopy(self.locator)],limitations=['Synthetic scope; no external integrity search.'],nextAction=None) for k in INTEGRITY_KINDS],numericClaims=[],sourceLimitations=[],humanApproval=False,released=False)
        self.candidate['results']=[dict(id='R1',experimentId='E1',endpoint='Observed event count',population='Synthetic experiment population',comparison='Intervention versus control',arms=[dict(id='A1',label='Experimental arm',role='intervention',sampleSizeNumericClaimId=None)],timepoint='Day 10',outcomeType='binary',numericClaimIds=[],sourceLocators=[deepcopy(self.locator)],interpretation='The synthetic measured events support only this experimental comparison.',limitations=[])]
        self.candidate['claims']=[dict(id='CL1',text='The synthetic experiment reports the specified events within its bounded comparison.',basis='observed_result',resultIds=['R1'],sourceLocators=[deepcopy(self.locator)])]
        self.candidate['resultCoverage']=[]
        for asset in self.assignment['assets']:
            for unit in asset['expectedUnits']:
                recorded=asset['sourceId']=='MAIN' and unit['id']=='methods'
                locator=dict(sourceId=asset['sourceId'],sourceSha256=asset['sha256'],unitId=unit['id'],kind=unit['kind'],locator=unit['locator'],quote='Synthetic unit content inspected for result accounting.',figureTable=None)
                self.candidate['resultCoverage'].append(dict(sourceId=asset['sourceId'],unitId=unit['id'],disposition='results_recorded' if recorded else 'no_applicable_result',resultIds=['R1'] if recorded else [],rationale='This synthetic unit is explicitly accounted for within the report review.',sourceLocators=[locator]))

    def inspect(self):
        return validate_review(self.candidate,self.assignment,self.question_map)

    def test_complete_one_report_includes_companions_and_all_fields(self):
        result=self.inspect()
        self.assertEqual(result,{'errors':[],'gaps':[]})
        self.assertEqual(len(self.candidate['inputs']),67)
        self.assertEqual(len(self.candidate['answers']),15)

    def test_fresh_template_is_honest_draft_and_cannot_claim_complete(self):
        template=make_template(self.assignment,'b'*64,'c'*64,self.question_map,'d'*64,'source author')
        self.assertEqual(validate_review(template,self.assignment,self.question_map)['errors'],[])
        self.assertTrue(validate_review(template,self.assignment,self.question_map)['gaps'])
        template['processingState']='candidate_complete'
        self.assertTrue(validate_review(template,self.assignment,self.question_map)['errors'])

    def test_result_claim_graph_and_each_source_unit_accounting(self):
        for key,value in [('results',[]),('claims',[]),('resultCoverage',[])]:
            c=deepcopy(self.candidate);c[key]=value
            self.assertTrue(validate_review(c,self.assignment,self.question_map)['errors'])
        self.candidate['claims'][0]['resultIds']=['ABSENT']
        self.assertTrue(any('unknown result' in e for e in self.inspect()['errors']))

    def test_duplicate_field_question_experiment_and_wrong_report_fail(self):
        for mutation in [lambda c:c['inputs'].__setitem__(1,deepcopy(c['inputs'][0])),
                         lambda c:c['answers'].__setitem__(1,deepcopy(c['answers'][0])),
                         lambda c:c['experiments'].append(deepcopy(c['experiments'][0])),
                         lambda c:c.update(canonicalReportId='OTHER')]:
            with self.subTest(mutation=mutation):
                c=deepcopy(self.candidate);mutation(c)
                self.assertTrue(validate_review(c,self.assignment,self.question_map)['errors'])

    def test_uninspected_companion_page_or_image_blocks_completion(self):
        self.candidate['inspection'][1]['unitIdsRead']=['p1']
        self.candidate['inspection'][1]['readLog']=self.candidate['inspection'][1]['readLog'][:1]
        self.assertTrue(any('every expected unit' in e for e in self.inspect()['errors']))
        self.candidate['inspection'][1]['status']='partial'
        self.candidate['inspection'][1]['nextAction']='Inspect the missing second supplement page.'
        result=self.inspect()
        self.assertTrue(result['gaps'])
        self.assertTrue(any('claims completeness' in e for e in result['errors']))

    def test_not_reported_and_inapplicable_are_closed_after_full_reading(self):
        for state,basis in [('not_reported','absence_check'),('not_applicable','design_applicability')]:
            self.candidate['inputs'][0].update(status=state,basis=basis,value=None)
            self.assertEqual(self.inspect()['errors'],[])
        self.candidate['inputs'][0].update(status='not_reported',basis='absence_check',assessedAssetIds=['MAIN'])
        self.assertTrue(any('every required asset' in e for e in self.inspect()['errors']))

    def test_written_answers_do_not_close_conflicting_or_unchecked_inputs(self):
        for state in ['conflicting','not_checked','not_accessible','not_identifiable']:
            self.candidate['inputs'][0].update(status=state,basis='unfinished',nextAction='Resolve the declared missing or conflicting input from the assigned sources.')
            self.assertTrue(any('claims completeness' in e for e in self.inspect()['errors']))
            self.candidate['processingState']='draft'
            self.assertEqual(self.inspect()['errors'],[])
            self.assertTrue(self.inspect()['gaps'])
            self.candidate['processingState']='candidate_complete'

    def test_optional_missing_asset_does_not_block_complete_native_report(self):
        self.assignment['assets'].append(dict(sourceId='ALTERNATE_PDF',role='other',required=False,mediaType='application/pdf',availability='not_accessible',sha256=None,bytes=None,path=None,expectedUnits=[],reason='Optional alternate representation is unavailable; the complete native report is assigned.'))
        self.candidate['inspection'].append(dict(sourceId='ALTERNATE_PDF',sourceSha256=None,status='not_accessible',unitIdsRead=[],visualUnitIds=[],readLog=[],limitations=['Unavailable alternate representation.'],nextAction=None))
        self.assertEqual(self.inspect(),{'errors':[],'gaps':[]})
        self.assignment['assets'][-1]['required']=True
        self.assertTrue(self.inspect()['errors'])

    def test_reported_main_fact_survives_pending_required_companion_in_draft(self):
        self.candidate['processingState']='draft'
        asset=self.assignment['assets'][1];asset.update(availability='not_accessible',sha256=None,bytes=None,path=None,expectedUnits=[])
        self.candidate['inspection'][1].update(sourceSha256=None,status='not_accessible',unitIdsRead=[],readLog=[],nextAction='Acquire and inspect the required companion before completing this review.')
        self.candidate['resultCoverage']=[c for c in self.candidate['resultCoverage'] if c['sourceId']!='SUP']
        for field in self.candidate['inputs']:field['assessedAssetIds']=['MAIN','FIG1']
        result=self.inspect()
        self.assertEqual(result['errors'],[])
        self.assertTrue(result['gaps'])

    def test_wrong_locator_hash_media_unit_and_unknown_experiment_fail(self):
        for key,value in [('sourceSha256','f'*64),('kind','pdf_page'),('locator','#absent'),('sourceId','UNKNOWN')]:
            candidate=deepcopy(self.candidate);candidate['inputs'][0]['sourceLocators'][0][key]=value
            self.assertTrue(validate_review(candidate,self.assignment,self.question_map)['errors'])
        self.candidate['answers'][0]['experimentIds']=['E-ABSENT']
        self.assertTrue(self.inspect()['errors'])

    def test_numeric_exactness_and_visual_requirement(self):
        number=dict(id='N1',questionId='Q06',field='arm_results',value=12,units='events',basis='exact_reported',reportedText='12',precision='The source reports this exact integer count without derived precision.',sourceLocators=[deepcopy(self.locator)],calculationProvenance=None,limitation=None)
        self.candidate['numericClaims']=[number]
        self.candidate['results'][0]['numericClaimIds']=['N1']
        next(f for f in self.candidate['inputs'] if (f['questionId'],f['field'])==('Q06','arm_results'))['numericClaimIds']=['N1']
        self.assertEqual(self.inspect()['errors'],[])
        number['value']=999
        self.assertTrue(any('exact reported scalar' in e for e in self.inspect()['errors']))
        number['value']=12;number['sourceLocators'][0]['figureTable']='Table 1'
        self.assertTrue(any('visual inspection' in e for e in self.inspect()['errors']))
        number['basis']='graph_estimate';number['value']=11.7;number['limitation']='A precise graph estimate is not supported by this first contract.'
        self.assertTrue(any('not supported by this contract' in e for e in self.inspect()['errors']))
        number.update(basis='exact_reported',value=None,reportedText='approximately 800 nM',limitation='The reported value is qualified; no exact scalar or graph estimate is asserted.')
        number['sourceLocators']=[{**self.locator,'quote':'The source describes approximately 800 nM.'}]
        self.assertEqual(self.inspect()['errors'],[])

    def test_integrity_dates_scope_and_release_cannot_be_faked(self):
        self.candidate['sourceIntegrity'][0]['checkedAt']='yesterday'
        self.assertTrue(any('needs date' in e for e in self.inspect()['errors']))
        self.candidate['humanApproval']=True
        self.assertTrue(any(e.startswith('schema:') for e in self.inspect()['errors']))

    def prepare(self,directory):
        root=Path(directory)
        def save(name,value):
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(canonical(value));return p
        for name in ['scripts/research_full_review.py','scripts/research_ingest/cli.py','scripts/research_ingest/source_validation.py']:
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((self.repo/name).read_bytes())
        for name,schema in SCHEMAS.items():save(SCHEMA_DIR+'/'+name,schema)
        qmap=save(QUESTION_MAP,self.question_map)
        assignment=deepcopy(self.assignment);candidate=deepcopy(self.candidate)
        for asset,data in zip(assignment['assets'],[b'<html><section id="methods">12</section><section id="results">12</section></html>',b'%PDF-1.4 synthetic two-page fixture',b'\xff\xd8\xffsynthetic figure fixture']):
            p=root/asset['path'];p.write_bytes(data);asset.update(sha256=sha(p),bytes=p.stat().st_size)
        def hashes(value):
            if isinstance(value,dict):
                if 'sourceId' in value and 'sourceSha256' in value:value['sourceSha256']=next(a['sha256'] for a in assignment['assets'] if a['sourceId']==value['sourceId'])
                for child in value.values():hashes(child)
            elif isinstance(value,list):
                for child in value:hashes(child)
        hashes(candidate)
        apath=save('assignment.json',assignment)
        pins=['assignment.json',QUESTION_MAP]+[SCHEMA_DIR+'/'+n for n in SCHEMAS]+['scripts/research_full_review.py','scripts/research_ingest/cli.py','scripts/research_ingest/source_validation.py']
        plan=save('plan.json',dict(planId='P1',operations=['full-review-validate'],inputs=[dict(path=p,sha256=sha(root/p)) for p in pins]))
        gp=save('gp.json',dict(schemaVersion='remaprx-gp-readiness-v1',status='PASS',scope='GP_PLAN',planId='P1',planSha256=sha(plan),checkedAt='2026-10-12T12:00:00Z'))
        candidate.update(planSha256=sha(plan),assignmentSha256=sha(apath),questionMapSha256=sha(qmap))
        cpath=save('candidate.json',candidate)
        return SimpleNamespace(root=root,plan=plan,readiness=gp,assignment=apath,candidate=cpath,schema=root/SCHEMA_DIR/'full-review.schema.json',question_map=qmap,audit=None)

    def test_end_to_end_read_only_source_hash_and_candidate_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            args=self.prepare(directory)
            before={p:sha(p) for p in Path(directory).rglob('*') if p.is_file()}
            result=validate(args)
            self.assertEqual(result['completionState'],'candidate_complete')
            self.assertFalse(result['independentAuditAccepted'])
            self.assertFalse(result['performedImport'])
            self.assertTrue(all(sha(p)==expected for p,expected in before.items()))
            (Path(directory)/'SUP').write_bytes(b'%PDF-1.4 changed source')
            with self.assertRaisesRegex(Hold,'source bytes/hash'):validate(args)

    def test_independent_audit_exact_candidate_and_author_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            args=self.prepare(directory);root=Path(directory)
            evidence=root/'audit-evidence.json';evidence.write_text('{"synthetic":true}')
            assignment=json.loads(args.assignment.read_text())
            audit=dict(schemaVersion='remaprx-full-review-audit-v1',status='PASS',scope='independent_full_report_review',author='source author',auditor='independent auditor',reviewedAt='2026-10-12T13:00:00Z',candidateSha256=sha(args.candidate),planSha256=sha(args.plan),assignmentSha256=sha(args.assignment),questionMapSha256=sha(args.question_map),sourceHashes=[dict(sourceId=a['sourceId'],sha256=a['sha256']) for a in assignment['assets']],checks={k:True for k in AUDIT_CHECKS},evidence=[dict(path='audit-evidence.json',sha256=sha(evidence))],limitations=[],humanApproval=False,released=False)
            args.audit=root/'audit.json';args.audit.write_bytes(canonical(audit))
            self.assertEqual(validate(args)['completionState'],'accepted_private')
            audit['auditor']='SOURCE AUTHOR';args.audit.write_bytes(canonical(audit))
            with self.assertRaisesRegex(Hold,'must differ'):validate(args)
            audit['auditor']='independent auditor';audit['candidateSha256']='f'*64;args.audit.write_bytes(canonical(audit))
            with self.assertRaisesRegex(Hold,'audit hash mismatch'):validate(args)

    def test_source_root_remap_preserves_assignment_and_candidate_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            args=self.prepare(directory);root=Path(directory);relocated=root/'new-host';relocated.mkdir()
            assignment=json.loads(args.assignment.read_text())
            before=(sha(args.assignment),sha(args.candidate),sha(args.plan))
            files=[]
            for asset in assignment['assets']:
                (root/asset['path']).rename(relocated/asset['path'])
                files.append(dict(id=asset['sourceId'],rootId='HOST',path=asset['path'],sha256=asset['sha256'],bytes=asset['bytes']))
            args.source_map=root/'local-source-map.json';args.source_map.write_bytes(canonical(dict(roots={'HOST':{'path':str(relocated)}},files=files)))
            self.assertEqual(validate(args)['completionState'],'candidate_complete')
            self.assertEqual(before,(sha(args.assignment),sha(args.candidate),sha(args.plan)))


if __name__=='__main__':
    unittest.main()
