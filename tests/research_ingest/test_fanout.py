from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from scripts.research_ingest.cli import Hold, canonical, sha
from scripts.research_fanout import APP_INPUTS, AUDIT_CHECKS, build_proposals, fanout, identity_module, object_hash
import test_source_validation as source_fixture


class FanoutTests(unittest.TestCase):
    def setUp(self):
        fixture = source_fixture.SourceCandidateTests()
        fixture.setUp()
        self.candidate, self.schema, self.assignment = fixture.candidate, fixture.schema, fixture.assignment
        self.repo = Path(__file__).resolve().parents[2]
        self.identities = identity_module(self.repo)
        self.current = {
            'data/content.json': {'sources': [{'id': 'P1'}], 'guides': [
                {'id': 'GD', 'entityId': 'D01', 'slug': '/drugs/test', 'type':'Drug'},
                {'id': 'GC', 'entityId': 'C01', 'slug': '/conditions/test', 'type':'Condition', 'sections':[{'id':'c01-options','label':'Options'}]},
                {'id': 'GQ', 'slug': '/answers/test'}]},
            'data/reader-evidence.json': {'synthesisRows': [], 'sources': [], 'quarantine': []},
            'data/private-reviews.json': {'P1': {'version': 'old', 'questions': []}},
            'data/review-envelopes.json': {'P1': {'release': {'state': 'approved'}}},
            'data/article-updates.json': {'entries': []}, 'data/outcome-registry.json': {},
            'data/public-mechanisms.json': {'drugs': [
                {'drugId':'D01','originalAction':'Existing drug action.','questions':[],'summary':'Existing drug summary.'},
                {'conditionId':'C01','guideIds':['GC'],'questions':[],'summary':'Existing condition summary.'},
            ], 'contexts': []},
            'editorial/evidence-assessments.json': {'records': []},
            'editorial/reader-source-aliases.json': {},
            'editorial/synthesis-identity-map.json': {'entries': []},
        }
        scope = dict(drugId='D01', conditionId='C01', population='Synthetic participants', comparison='A versus B', endpoint='Events', formulation=None, route=None, timepoint='Day 10')
        self.bindings = dict(schemaVersion='remaprx-scientific-bindings-v1', author='extractor', sourceId='S1', canonicalReportId='P1', appSourceId='P1', candidateSha256='c'*64, sourceSha256='a'*64, familyIds=[], familyIdentityStatus='unknown', identityRationale='The assigned report is the same existing canonical source.', bindings=[dict(
            id='B1', kind='clinical_result', scope=scope, resultIds=['R1'], claimIds=['CL1'], rationale='The report directly measures the bound population and endpoint.',
            summary='The source reports twelve events in the specified comparison.', magnitude='12 events', limits='This synthetic comparison does not support other populations.', mechanismState=None, questionRoutes=[], pageHistory=[
                {'guideId':'GD','title':'Trial result proposed','summary':'The drug guide would gain the reported event count and its limits.'},
                {'guideId':'GC','title':'Condition finding proposed','summary':'The condition guide would identify this specific population comparison.'}])])

    def build(self):
        return build_proposals(self.candidate, self.bindings, self.current, self.identities, '2026-10-12')

    def test_parents_share_identity_and_review_approvals_are_invalidated(self):
        before = deepcopy(self.current)
        out = self.build()
        self.assertEqual(len(out['synthesisProposals']), 1)
        self.assertEqual({p['sharedRecordId'] for p in out['pageProposals']}, {out['synthesisProposals'][0]['id']})
        self.assertEqual(out['reviewProposal']['questionInputs'], self.candidate['questions'])
        self.assertEqual(out['reviewProposal']['release'], 'pending')
        self.assertEqual(out['synthesisProposals'][0]['provenance']['claimIds'], ['CL1'])
        self.assertEqual(out['synthesisProposals'][0]['scopedClaimRecords'][0]['text'], self.candidate['claims'][0]['text'])
        self.assertIn('approvedSha256', out['invalidations']['reviewApprovalFields'])
        self.assertEqual(self.current, before)

    def test_mechanism_stays_out_of_clinical_evidence_rows(self):
        self.bindings['bindings'][0].update(kind='mechanism', mechanismState='tested')
        out = self.build()
        self.assertFalse(out['synthesisProposals'])
        self.assertFalse(out['mechanismProposals'][0]['clinicalBenefitEstablished'])
        pages={p['guideId']:p for p in out['pageProposals']}
        self.assertEqual(pages['GD']['sections'],[{'id':'mechanisms','label':'Mechanism of Action'}])
        self.assertEqual(pages['GC']['sections'],[{'id':'interventions','label':'Interventions'}])
        self.assertEqual(pages['GD']['sharedRecordId'],pages['GC']['sharedRecordId'])
        self.assertEqual(pages['GC']['destinationStatus'],'private_proposal')
        self.assertEqual(pages['GC']['layoutStatus'],'pending_layout')
        self.assertFalse(pages['GC']['currentDataTargetAvailable'])
        self.assertFalse(pages['GC']['renderedTargetVerified'])
        histories={h['pagePaths'][0]:h for h in out['historyProposals']}
        for page in pages.values():
            self.assertEqual(histories[page['route']]['affectedSections'],page['sections'])
        self.assertEqual(histories['/conditions/test']['layoutStatus'],'pending_layout')

    def test_condition_data_target_does_not_claim_rendered_availability(self):
        self.bindings['bindings'][0].update(kind='mechanism',mechanismState='tested')
        condition=self.current['data/content.json']['guides'][1]
        condition['sections'].append({'id':'c01-interventions','label':'Interventions'})
        page=next(p for p in self.build()['pageProposals'] if p['guideId']=='GC')
        self.assertEqual(page['currentGuideSectionIds'],['c01-interventions'])
        self.assertTrue(page['currentDataTargetAvailable'])
        self.assertFalse(page['renderedTargetVerified'])
        self.assertEqual(page['layoutStatus'],'pending_rendered_verification')
        condition['type']='Drug'
        with self.assertRaisesRegex(Hold,'identity/type mismatch'):
            self.build()

    def test_mixed_drug_and_condition_mechanism_records_end_to_end(self):
        self.bindings['bindings'][0].update(kind='mechanism',mechanismState='tested')
        records=self.current['data/public-mechanisms.json']['drugs']
        with tempfile.TemporaryDirectory() as directory:
            out=fanout(self.prepare(directory))
            self.assertEqual(out['status'],'PASS')
            self.assertEqual(out['mechanismProposals'][0]['currentMechanismDrugSha256'],object_hash(records[0]))
            self.assertEqual(next(p for p in out['pageProposals'] if p['guideId']=='GC')['layoutStatus'],'pending_layout')
        records.append(deepcopy(records[0]))
        with self.assertRaisesRegex(Hold,'Ambiguous existing mechanism drug records'):
            self.build()

    def test_mechanism_only_question_is_not_mistaken_for_condition_parent(self):
        binding=self.bindings['bindings'][0]
        binding.update(kind='mechanism',mechanismState='tested')
        binding['scope']['conditionId']=None
        binding['questionRoutes']=[dict(guideId='GQ',route='/answers/test',rationale='The exact mechanism question and model scope were explicitly checked.',verifiedScope=deepcopy(binding['scope']))]
        binding['pageHistory']=[binding['pageHistory'][0],dict(guideId='GQ',title='Mechanism question proposal',summary='The mechanism question would gain this source-bound model observation.')]
        pages={p['guideId']:p for p in self.build()['pageProposals']}
        self.assertEqual(set(pages),{'GD','GQ'})
        self.assertEqual(pages['GQ']['sections'],[{'id':'mechanisms','label':'Mechanism of Action'}])
        self.assertNotIn('layoutStatus',pages['GQ'])

    def test_result_scope_and_missing_parent_fail(self):
        self.bindings['bindings'][0]['scope']['endpoint'] = 'Different endpoint'
        with self.assertRaisesRegex(Hold, 'scope differs'):
            self.build()
        self.bindings['bindings'][0]['scope']['endpoint'] = 'Events'
        self.bindings['bindings'][0]['scope']['drugId'] = 'D999'
        with self.assertRaisesRegex(Hold, 'parent guide'):
            self.build()

    def test_question_routes_need_exact_verified_scope(self):
        binding = self.bindings['bindings'][0]
        binding['questionRoutes'] = [dict(guideId='GQ', route='/answers/test', rationale='An independent reader checked the exact question against the source.', verifiedScope=deepcopy(binding['scope']))]
        binding['pageHistory'].append(dict(guideId='GQ',title='Question answer proposal',summary='The specific question would gain its measured event finding.'))
        self.assertEqual(len(self.build()['pageProposals']), 3)
        binding['questionRoutes'][0]['verifiedScope']['conditionId'] = 'C99'
        with self.assertRaisesRegex(Hold, 'verified scope'):
            self.build()

    def test_family_id_not_in_established_records_fails(self):
        self.bindings.update(familyIds=['INVENTED'], familyIdentityStatus='preserved')
        with self.assertRaisesRegex(Hold, 'Family identities'):
            self.build()

    def add_cross_scope_claim(self):
        other = deepcopy(self.candidate['results'][0])
        other.update(id='R2',population='A different experimental model')
        other['numbers'][0]['id']='N2'
        self.candidate['results'].append(other)
        self.candidate['claims'][0]['result_ids'].append('R2')
        self.candidate['claims'][0]['text']='A broad interpretation combines different experimental models.'

    def add_scoped_restatement(self):
        binding=self.bindings['bindings'][0]
        binding['scopedClaims']=[dict(id='SCOPED-CL1',sourceClaimId='CL1',resultIds=['R1'],text='The selected participants experienced the source-reported events only.',scope=deepcopy(binding['scope']),sourceLocators=deepcopy(self.candidate['results'][0]['source_locators']),scopeExplanation='This restatement excludes the other experimental model and its findings.')]

    def test_cross_scope_claim_needs_explicit_scoped_restatement(self):
        self.add_cross_scope_claim()
        with self.assertRaisesRegex(Hold,'Cross-scope'):
            self.build()
        self.add_scoped_restatement()
        record=self.build()['synthesisProposals'][0]['scopedClaimRecords'][0]
        self.assertEqual(record['resultIds'],['R1'])
        self.assertEqual(record['excludedSourceClaimResultIds'],['R2'])
        self.assertNotEqual(record['text'],self.candidate['claims'][0]['text'])
        self.assertEqual(self.candidate['claims'][0]['result_ids'],['R1','R2'])

    def test_unknown_claim_uncovered_result_and_unrelated_locator_fail(self):
        binding=self.bindings['bindings'][0]
        binding['claimIds']=['ABSENT']
        with self.assertRaisesRegex(Hold,'unvalidated source claims'):
            self.build()
        binding['claimIds']=['CL1']
        self.add_scoped_restatement()
        binding['scopedClaims'][0]['sourceLocators'][0]['source_sha256']='f'*64
        with self.assertRaisesRegex(Hold,'locators must come'):
            self.build()
        binding.pop('scopedClaims')
        other=deepcopy(self.candidate['results'][0]); other['id']='R2'; self.candidate['results'].append(other)
        binding['resultIds'].append('R2')
        with self.assertRaisesRegex(Hold,'Every selected result'):
            self.build()

    def test_generic_repeated_page_history_and_quarantine_fail(self):
        binding = self.bindings['bindings'][0]
        binding['pageHistory'][1]['summary'] = binding['pageHistory'][0]['summary']
        with self.assertRaisesRegex(Hold, 'page specifically'):
            self.build()
        self.current['data/reader-evidence.json']['quarantine'] = [{'sourceId':'P1'}]
        with self.assertRaisesRegex(Hold, 'quarantined'):
            self.build()

    def prepare(self, directory):
        root = Path(directory)
        def save(relative, value):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(canonical(value))
            return path
        for name, value in self.current.items():
            save(name, value)
        for name in ['scripts/apply-reader-outcomes.py', 'scripts/research_fanout.py']:
            target = root / name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((self.repo / name).read_bytes())
        source = root / 'source.pdf'
        source.write_bytes(b'%PDF-1.4\nsynthetic fixture only')
        assignment = {**self.assignment,'sha256':sha(source),'bytes':source.stat().st_size,'path':str(source)}
        assignment_path = save('assignments.json', {'packets':[{'sourceAssignments':[assignment]}]})
        schema_path = save('source-schema.json', self.schema)
        source_plan = save('source-plan.json', {'planId': self.candidate['plan_id'],'operations':['validate'],'inputs':[
            {'path':p.name,'sha256':sha(p)} for p in [assignment_path,schema_path]]})
        candidate = deepcopy(self.candidate)
        candidate['plan_sha256'] = sha(source_plan)
        from scripts.research_ingest.source_validation import walk
        for value in walk(candidate):
            if 'source_sha256' in value:
                value['source_sha256'] = sha(source)
        candidate_path = save('candidate.json', candidate)
        authorship_path = save('authorship.json', dict(schemaVersion='remaprx-source-authorship-v1',candidateSha256=sha(candidate_path),assignmentId=candidate['assignment_id'],author='source extractor',writtenAt='2026-10-12T00:00:00Z'))
        source_gp = save('source-gp.json',dict(schemaVersion='remaprx-gp-readiness-v1',status='PASS',scope='GP_PLAN',planId=candidate['plan_id'],planSha256=sha(source_plan),checkedAt='2026-10-12T00:00:00Z'))
        binding = deepcopy(self.bindings)
        binding.update(candidateSha256=sha(candidate_path),sourceSha256=sha(source))
        for value in walk(binding):
            if 'source_sha256' in value:
                value['source_sha256']=sha(source)
        binding_path = save('bindings.json',binding)
        evidence = save('audit-evidence.json',{'syntheticTest':True})
        audit = dict(schemaVersion='remaprx-source-fanout-audit-v1',status='PASS',scope='independent_source_and_fanout_verification',author='extractor',auditor='independent auditor',reviewedAt='2026-10-12T00:00:00Z',candidateSha256=sha(candidate_path),bindingsSha256=sha(binding_path),sourceSha256=sha(source),auditedResultIds=['R1'],auditedClaimIds=['CL1'],auditedScopedClaimIds=[],checks={k:True for k in AUDIT_CHECKS},evidence=[{'path':evidence.name,'sha256':sha(evidence)}])
        audit_path = save('audit.json',audit)
        paths = list(APP_INPUTS) + ['editorial/synthesis-identity-map.json','scripts/research_fanout.py','assignments.json','source-schema.json','source-plan.json','candidate.json','source-gp.json','bindings.json','audit-evidence.json','audit.json','authorship.json']
        plan_path = save('fanout-plan.json',dict(schemaVersion='remaprx-fanout-plan-v1',planId='FANOUT-TEST',proposalDate='2026-10-12',operations=['fanout'],inputs=[{'path':p,'sha256':sha(root/p)} for p in paths]))
        gp_path = save('fanout-gp.json',dict(schemaVersion='remaprx-gp-readiness-v1',status='PASS',scope='GP_PLAN',planId='FANOUT-TEST',planSha256=sha(plan_path),checkedAt='2026-10-12T00:00:00Z'))
        return SimpleNamespace(root=root,plan=plan_path,readiness=gp_path,candidate=candidate_path,schema=schema_path,assignment=assignment_path,source_plan=source_plan,source_readiness=source_gp,bindings=binding_path,verification=audit_path,authorship=authorship_path,identity_map=root/'editorial/synthesis-identity-map.json',source_file=None,mechanism_schema=None)

    def test_end_to_end_read_only_hash_binding_and_stale_input_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.prepare(directory)
            before = {p.relative_to(directory).as_posix():sha(p) for p in Path(directory).rglob('*') if p.is_file()}
            out = fanout(args)
            self.assertEqual(out['status'],'PASS')
            self.assertFalse(out['performedImport'])
            self.assertFalse(out['humanApproval'])
            self.assertEqual(out,fanout(args))
            self.assertEqual({h['date'] for h in out['historyProposals']},{'2026-10-12'})
            # Import machinery may emit pycache only; all supplied inputs remain exact.
            self.assertTrue(all(sha(Path(directory)/name)==value for name,value in before.items()))
            (Path(directory)/'data/content.json').write_text('{}')
            with self.assertRaisesRegex(Hold,'Pinned input changed'):
                fanout(args)

    def test_plan_requires_canonical_calendar_proposal_date(self):
        from scripts.research_ingest.cli import load
        with tempfile.TemporaryDirectory() as directory:
            args=self.prepare(directory)
            for value in [None,'','20261012','2026-W42-1','2026-02-30']:
                with self.subTest(value=value):
                    plan=load(args.plan); plan['proposalDate']=value; args.plan.write_bytes(canonical(plan))
                    gp=load(args.readiness); gp['planSha256']=sha(args.plan); args.readiness.write_bytes(canonical(gp))
                    with self.assertRaisesRegex(Hold,'canonical ISO calendar date'):
                        fanout(args)

    def test_self_audit_and_stale_candidate_receipt_fail(self):
        from scripts.research_ingest.cli import load
        for field, value, message in [('auditor','extractor','differ'),('auditor','source extractor','source extractor'),('candidateSha256','f'*64,'audit hash'),('auditedClaimIds',[],'source claim needs')]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                args=self.prepare(directory)
                audit=load(args.verification); audit[field]=value; args.verification.write_bytes(canonical(audit))
                plan=load(args.plan)
                for pin in plan['inputs']:
                    if pin['path']=='audit.json': pin['sha256']=sha(args.verification)
                args.plan.write_bytes(canonical(plan))
                gp=load(args.readiness); gp['planSha256']=sha(args.plan); args.readiness.write_bytes(canonical(gp))
                with self.assertRaisesRegex(Hold,message): fanout(args)

    def test_cross_scope_claim_requires_audit_of_dependencies_and_restatement(self):
        from scripts.research_ingest.cli import load
        self.add_cross_scope_claim(); self.add_scoped_restatement()
        with tempfile.TemporaryDirectory() as directory:
            args=self.prepare(directory)
            with self.assertRaisesRegex(Hold,'original claim dependency'):
                fanout(args)
            for audited_scopes in [[],['SCOPED-CL1']]:
                audit=load(args.verification); audit.update(auditedResultIds=['R1','R2'],auditedScopedClaimIds=audited_scopes)
                args.verification.write_bytes(canonical(audit))
                plan=load(args.plan)
                for pin in plan['inputs']:
                    if pin['path']=='audit.json': pin['sha256']=sha(args.verification)
                args.plan.write_bytes(canonical(plan))
                gp=load(args.readiness); gp['planSha256']=sha(args.plan); args.readiness.write_bytes(canonical(gp))
                if not audited_scopes:
                    with self.assertRaisesRegex(Hold,'scoped claim restatement'):
                        fanout(args)
                else:
                    out=fanout(args)
                    self.assertEqual(out['synthesisProposals'][0]['scopedClaimRecords'][0]['excludedSourceClaimResultIds'],['R2'])


if __name__ == '__main__':
    unittest.main()
