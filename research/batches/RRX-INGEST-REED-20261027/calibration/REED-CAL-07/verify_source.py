"""Check phase-I source lineage, cohort/response/attribution and uncertainty bounds."""
from pathlib import Path
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 s=read(B/'SCHEMA.json');assert set(s['required'])<=c.keys() and c['schemaVersion']==s['schemaVersion']
 assert c['paper']['id']=='B-R0045' and not c['paper']['newCanonicalIdentity'] and c['paper']['sourceType']=='primary_uncontrolled_phase1'
 assert c['inspection']['textualPagesRead']==list(range(1,16)) and not c['inspection']['fullScientificReviewComplete']
 assert not c['scientificAcceptance'] and not c['humanApproval'] and not c['released']
 st=c['study'];assert st['accruedN']==9 and st['groupN']==[3,6] and st['responseEvaluableN'] is None and st['completeDLTEvaluableN'] is None and not st['MTDEstablished']
 assert st['doseLevelsPlanned']==3 and st['doseLevelsEvaluated']==1 and not st['causalMetforminEffectIsolated']
 assert c['cohorts'][0]['treatment']==['metformin','nelfinavir'] and c['cohorts'][0]['n']==3
 assert c['cohorts'][1]['treatment']==['metformin','nelfinavir','bortezomib'] and c['cohorts'][1]['n']==6
 assert len(c['results'])==len(c['claims'])==4 and len(c['sourceConflicts'])==4
 for r in c['results']:
  assert r['comparator'] is None and not r['causalAttributionToMetforminAlone'] and not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None
  for l in r['sourceLocators']:assert l['sourceSha256']==c['source']['sha256'] and 1<=l['physicalPage']<=15
 r=c['results'][0]['estimate'];assert r['confirmedResponsesReported']==0 and r['reportedORRProportion'] is None and r['responseAnalyzedN'] is None
 r=c['results'][1]['estimate'];assert r['trialN']==9 and r['grade3plusHematologicPatients']==4 and r['grade3plusNonhematologicPatients']==6 and r['uniquePatientsEitherCategory'] is None and r['treatmentCausedEventCount'] is None
 assert r['group2Grade5EventTerms']==[{'term':'encephalopathy','n':1},{'term':'disease progression','n':1}]
 for r in c['results'][2:]:
  e=r['estimate'];assert e['events']==8 and e['total']==9 and e['unit']=='months' and e['CILevel']==.95 and e['upper'] is None and e['upperLiteral']=='NE'
 assert c['results'][2]['estimate']['value']==1.4 and c['results'][3]['estimate']['value']==2.1
 assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
 assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for cl in c['claims']:assert not cl['acceptedSupport'] and set(cl['resultIds'])<={r['id'] for r in c['results']}
 return True
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for f,h in read(B/'AUDIT-MANIFEST.json')['files'].items():assert sha(B/f)==h
for f,h in read(B/'READINESS.json')['hashes'].items():assert sha(B/f)==h
assert c['sourceConflicts']==read(B/'SOURCE-CONFLICTS.json')
root=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(root/'metformin-myeloma/pdfs/38220589-alodhaibi-2024.pdf')==c['source']['sha256']==read(B/'READINESS.json')['sourceSha256'];assert sha(root/'metformin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(x) for x in (B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field']) for e in es}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in es:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,mutate):
 x=copy.deepcopy(c);mutate(x)
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' unexpectedlyaccepted')
reject('first_cohort_dual_not_metformin_monotherapy',lambda x:x['cohorts'][0].update(treatment=['metformin']))
reject('unknown_response_denominator_not_accruedN',lambda x:x['results'][0]['estimate'].update(responseAnalyzedN=9))
reject('unconfirmed_responses_not_confirmedORR',lambda x:x['results'][0]['estimate'].update(confirmedResponsesReported=2))
reject('overlapping_AE_categories_not_ten_unique_patients',lambda x:x['results'][1]['estimate'].update(uniquePatientsEitherCategory=10))
reject('regardless_attribution_events_not_treatment_caused',lambda x:x['results'][1]['estimate'].update(treatmentCausedEventCount=6))
reject('grade5_events_not_erased_by_noDLT',lambda x:x['results'][1]['estimate'].update(group2Grade5EventTerms=[]))
reject('NE_bound_not_zero',lambda x:x['results'][2]['estimate'].update(upper=0))
reject('unevaluable_DLT_windows_not_established_MTD',lambda x:x['study'].update(MTDEstablished=True))
reject('combination_not_metformin_causality',lambda x:x['study'].update(causalMetforminEffectIsolated=True))
r={'status':'PASS','candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceSha256':c['source']['sha256'],'boundedFindings':4,'claims':4,'questions':15,'typedFields':67,'regressions':checks,'doseAttributionFlowConflicts':'held','independentAudit':'pending','fullScientificReviewComplete':False,'scientificAcceptance':False};(B/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
