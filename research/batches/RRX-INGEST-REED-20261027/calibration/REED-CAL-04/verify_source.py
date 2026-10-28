"""Check source lineage and observational interpretation boundaries."""
from pathlib import Path
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 schema=read(B/'SCHEMA.json');assert set(schema['required'])<=c.keys() and c['schemaVersion']==schema['schemaVersion']
 assert c['paper']['id']=='B-R0586' and not c['paper']['newReportIdentity'] and c['paper']['newRandomizedTrials']==0
 d=c['design'];assert d['type']=='pooled_prospective_observational_cohorts' and not d['randomized'] and not d['causalIdentificationEstablished']
 assert not d['postExposureRepeatedlyUpdated'] and d['preDiagnosisLagYears']==2 and not d['sampleFlowReconciled']
 assert c['inspection']['textualPagesRead']==list(range(1,17)) and not c['inspection']['fullScientificReviewComplete']
 assert c['source']['sha256']==read(B/'READINESS.json')['sourceSha256']
 assert not c['scientificAcceptance'] and not c['humanApproval'] and not c['released']
 assert len(c['results'])==2 and len(c['claims'])==2
 for r in c['results']:
  assert set(schema['resultRequired'])<=r.keys() and r['estimate']['type']=='adjusted_hazard_ratio'
  assert r['estimate']['unit']=='relative hazard' and not r['estimate']['causalEffect']
  assert r['estimate']['absoluteRiskReduction'] is None and r['estimate']['NNT'] is None
  assert r['timepoint']['fixedOutcomeVisit'] is None and r['timepoint']['overallMedianFollowupMonths']==43
  assert not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None
  n=r['denominatorBasis'];assert not n['flowReconciled'] and n['derivedTableTotals']=={'userAtRisk':185,'nonuserAtRisk':251,'allAtRisk':436}
  for arm in ['user','nonuser']:assert sum(row[arm]['atRisk'] for row in n['rawCohortRows'])==n['derivedTableTotals'][arm+'AtRisk']
  assert r['adjustment']['stratification']=='cohort(sex)' and r['uncertainty']['pValue'] is None
  for l in r['sourceLocators']:assert 1<=l['physicalPage']<=16 and l['sourceSha256']==c['source']['sha256']
 assert c['exposures'][0]['prescribedDailyDose'] is None and not c['exposures'][0]['repeatedlyUpdated']
 assert not c['exposures'][0]['81mgSpecificEffectEstablished']
 assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
 assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for cl in c['claims']:assert not cl['acceptedSupport'] and set(cl['resultIds'])<={r['id'] for r in c['results']}
 return True
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for f,h in read(B/'AUDIT-MANIFEST.json')['files'].items():assert sha(B/f)==h
for f,h in read(B/'READINESS.json')['hashes'].items():assert sha(B/f)==h
root=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(root/'aspirin-myeloma/pdfs/34862208-marinac-2022.pdf')==c['source']['sha256'];assert sha(root/'aspirin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');entries=[json.loads(x) for x in (B/'review-inputs.jsonl').read_text().splitlines()]
assert len(entries)==67 and {(e['questionId'],e['field']) for e in entries}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in entries:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,mutate):
 x=copy.deepcopy(c);mutate(x)
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' unexpectedlyaccepted')
reject('hazard_ratio_cannot_be_risk_ratio',lambda x:x['results'][0]['estimate'].update(type='risk_ratio'))
reject('association_cannot_be_causal_effect',lambda x:x['results'][0]['estimate'].update(causalEffect=True))
reject('median_followup_cannot_be_fixed_risk_horizon',lambda x:x['results'][0]['timepoint'].update(fixedOutcomeVisit='43months'))
reject('fixed_first_post_exposure_cannot_be_time_varying',lambda x:x['design'].update(postExposureRepeatedlyUpdated=True))
reject('unresolved_flow_cannot_be_silently_accepted',lambda x:x['results'][0]['denominatorBasis'].update(flowReconciled=True))
reject('do_not_replace_printed436_with_inferred357',lambda x:x['results'][0]['denominatorBasis']['derivedTableTotals'].update(allAtRisk=357))
reject('weekly_equivalent_quantity_not_daily_prescription',lambda x:x['exposures'][0].update(prescribedDailyDose='325mg/day'))
reject('quantity_trend_p_not_binary_use_p',lambda x:x['results'][0]['uncertainty'].update(pValue=.0005))
r={'status':'PASS','candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceSha256':c['source']['sha256'],'observationalHRResults':2,'claims':2,'questions':15,'typedFields':67,'regressions':checks,'sampleFlow':'unresolved','independentAudit':'pending','fullScientificReviewComplete':False,'scientificAcceptance':False};(B/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
