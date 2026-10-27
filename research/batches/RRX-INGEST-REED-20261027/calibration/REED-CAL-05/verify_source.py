"""Case-report lineage and safeguards against population/causal reinterpretation."""
from pathlib import Path
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 s=read(B/'SCHEMA.json');assert set(s['required'])<=c.keys() and c['schemaVersion']==s['schemaVersion']
 assert c['paper']['sourceType']=='primary_case_report' and c['paper']['newRandomizedProphylaxisTrials']==0
 assert c['inspection']['textualPagesRead']==[1,2,3,4] and not c['inspection']['fullScientificReviewComplete']
 assert not c['scientificAcceptance'] and not c['humanApproval'] and not c['released']
 case=c['case'];assert case['reportedN']==1 and case['condition']=='high-risk smoldering myeloma'
 assert not case['clinicalTrialContext']['aspirinRandomized'] and not case['clinicalTrialContext']['externalRegistryChecked']
 assert not case['aspirinScheduleVerified'] and case['diagnosticTimeline']['truePVTOnset'] is None
 assert len(c['results'])==len(c['claims'])==1
 r=c['results'][0];assert set(s['resultRequired'])<=r.keys() and r['caseDenominator']==r['eventCount']==1
 assert r['populationRate'] is None and r['effectSize'] is None and r['comparator'] is None and not r['causalAttributionEstablished']
 assert r['exposure']['reportedDoseMg']==325 and r['exposure']['frequency'] is None and not r['exposure']['adherenceVerified']
 assert r['timing']['exactThrombusOnset'] is None and not r['acceptedSupport'] and r['grade'] is None
 for l in r['sourceLocators']:assert l['sourceSha256']==c['source']['sha256'] and l['printedPage']==72+l['physicalPage']
 m=c['managementContext'];assert not m['aspirinResult'] and not m['causalIsolation'] and not m['clinicalRecommendationAdopted']
 assert not c['claims'][0]['acceptedSupport'] and c['claims'][0]['resultIds']==[r['id']]
 assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
 assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 return True
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for f,h in read(B/'AUDIT-MANIFEST.json')['files'].items():assert sha(B/f)==h
for f,h in read(B/'READINESS.json')['hashes'].items():assert sha(B/f)==h
root=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(root/'aspirin-myeloma/pdfs/34046102-stawiarski-2021.pdf')==c['source']['sha256']==read(B/'READINESS.json')['sourceSha256'];assert sha(root/'aspirin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(x) for x in (B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field']) for e in es}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in es:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,mutate):
 x=copy.deepcopy(c);mutate(x)
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError('Unsafe reinterpretation accepted: '+name)
reject('one_case_is_not_population_failure_rate',lambda x:x['results'][0].update(populationRate=1.0))
reject('dose_without_frequency_not_daily_schedule',lambda x:x['results'][0]['exposure'].update(frequency='daily'))
reject('reported_use_not_verified_adherence',lambda x:x['results'][0]['exposure'].update(adherenceVerified=True))
reject('parent_cancer_randomization_not_aspirin_randomization',lambda x:x['case']['clinicalTrialContext'].update(aspirinRandomized=True))
reject('symptom_onset_not_proven_clot_onset',lambda x:x['results'][0]['timing'].update(exactThrombusOnset='3weeks'))
reject('rivaroxaban_resolution_not_aspirin_result',lambda x:x['managementContext'].update(aspirinResult=True))
reject('authors_learning_point_not_current_recommendation',lambda x:x['managementContext'].update(clinicalRecommendationAdopted=True))
reject('smoldering_subtype_not_general_symptomatic_myeloma',lambda x:x['case'].update(condition='symptomatic multiple myeloma'))
r={'status':'PASS','candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceSha256':c['source']['sha256'],'caseEventCandidates':1,'claims':1,'questions':15,'typedFields':67,'regressions':checks,'independentAudit':'pending','fullScientificReviewComplete':False,'scientificAcceptance':False};(B/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
