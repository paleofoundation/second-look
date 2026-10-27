"""Guard protocol units, no-result status and reuse of prior review identity."""
from pathlib import Path
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 s=read(B/'SCHEMA.json');assert set(s['required'])<=c.keys() and c['schemaVersion']==s['schemaVersion']
 assert c['paper']['id']=='B-R0187' and c['paper']['sourceId']=='B-R0187-F01' and c['paper']['existingReviewId']=='DRAFT-REVIEW-B-R0187-F01' and not c['paper']['newCanonicalIdentity']
 assert c['paper']['sourceType']=='trial_protocol' and c['clinicalResults']==[]
 assert not c['scientificAcceptance'] and not c['humanApproval'] and not c['released'] and not c['inspection']['fullScientificReviewComplete']
 assert c['inspection']['textualPagesRead']==[1,2,3,4,5,6,7]
 t=c['trialPlan'];assert t['plannedN']==120 and t['plannedNPerArm']==60 and t['actualEnrolledTotal'] is None and t['actualAnalyzedN'] is None
 assert not t['actualOutcomeDataPresent'] and not t['currentRegistryStatusVerified'] and not t['memantineComponentEffectIsolated']
 assert len(c['observations'])==len(c['claims'])==3
 for o in c['observations']:
  assert not o['acceptedSupport'] and o['grade'] is None
  for l in o['sourceLocators']:assert 1<=l['physicalPage']<=7 and l['sourceSha256']==c['source']['sha256']
 v=c['observations'][0]['values'];assert v['actualTotalEnrollmentReported'] is None and v['actualAnalyzedN'] is None
 assert v['powerAssumptions']['controlPFS6']==.50 and v['powerAssumptions']['experimentalPFS6']==.70 and v['powerAssumptions']['plannedDropoutAllowance']==.10
 v=c['observations'][1]['values'];assert v['memantinePlannedDailyMg']==[5,10,15,20] and v['plannedInterimSafetyExperimentalN']==20 and not v['actualInterimSafetyDataReported'] and not v['standaloneMemantineEffectIdentifiable']
 assert c['observations'][2]['values']['clinicalResultsInThisReport']==0 and not c['observations'][2]['values']['currentStatusExternallyVerified']
 assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
 assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for cl in c['claims']:assert not cl['acceptedSupport'] and set(cl['observationIds'])<={o['id'] for o in c['observations']}
 return True
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for f,h in read(B/'AUDIT-MANIFEST.json')['files'].items():assert sha(B/f)==h
for f,h in read(B/'READINESS.json')['hashes'].items():assert sha(B/f)==h
prior=read(B/'PRIOR-REVIEW-RECONCILIATION.json');assert sha(ROOT/prior['sourceFile'])==prior['sha256'] and prior['existingReviewId']==c['paper']['existingReviewId']
root=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(root/'memantine-glioblastoma/pdfs/38225589-mastall-2024.pdf')==c['source']['sha256']==read(B/'READINESS.json')['sourceSha256'];assert sha(root/'memantine-glioblastoma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(x) for x in (B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field']) for e in es}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in es:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,mutate):
 x=copy.deepcopy(c);mutate(x)
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError('Unsafe protocol interpretation accepted: '+name)
reject('planned120_cannot_be_actual_enrollment',lambda x:x['trialPlan'].update(actualEnrolledTotal=120))
reject('planned60_cannot_be_analyzed_armN',lambda x:x['trialPlan'].update(actualAnalyzedN=60))
reject('protocol_assumptions_cannot_be_results',lambda x:x['clinicalResults'].append({'PFS6':.70}))
reject('combination_cannot_isolate_memantine',lambda x:x['trialPlan'].update(memantineComponentEffectIsolated=True))
reject('historical_status_not_current_registry_verification',lambda x:x['trialPlan'].update(currentRegistryStatusVerified=True))
reject('planned_safety_trigger_not_safety_data',lambda x:x['observations'][1]['values'].update(actualInterimSafetyDataReported=True))
reject('prior_review_identity_not_duplicated',lambda x:x['paper'].update(existingReviewId='NEW-PROTOCOL-REVIEW'))
reject('protocol_not_automatic_grade',lambda x:x['observations'][0].update(grade='High'))
r={'status':'PASS','candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceSha256':c['source']['sha256'],'protocolObservations':3,'claims':3,'clinicalResults':0,'questions':15,'typedFields':67,'regressions':checks,'independentAudit':'pending','fullScientificReviewComplete':False,'scientificAcceptance':False};(B/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
