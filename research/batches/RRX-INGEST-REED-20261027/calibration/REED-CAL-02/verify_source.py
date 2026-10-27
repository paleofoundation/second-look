import json,hashlib,copy,os
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def validate(c):
 assert c['schemaVersion']=='REED-CAL-02source-extraction-v2' and c['paper']['pmid']=='12657672'
 assert c['paper']['sourceType']=='preclinical_primary_report' and c['paper']['humanEvidence']==False
 assert c['source']['sha256']==read(B/'READINESS-v2.json')['sourceSha256']
 assert c['inspection']['activeReadiness']=='READINESS-v2.json' and c['inspection']['physicalPagesRead']==list(range(1,11))
 assert c['inspection']['fullScientificReviewComplete']==False and not c['scientificAcceptance'] and not c['humanApproval'] and not c['released']
 assert len(c['experiments'])==1 and c['experiments'][0]['animalNPerArm'] is None
 dose=c['arms'][0]['exposure'];assert dose['value']==1 and dose['unit']=='g_minocycline_per_kg_rodent_diet' and dose['startAgeMonths']==9 and dose['bodyWeightDose'] is None
 assert len(c['results'])==2 and len(c['claims'])==2
 for r in c['results']:
  assert r['experimentId']==c['experiments'][0]['id'] and r['estimate']['kind']=='qualitative_histological_observation'
  assert r['estimate']['perArmAnimalN'] is None and r['estimate']['effectSize'] is None and r['uncertainty']['pValue'] is None
  assert not any(x in r['outcome'].lower() for x in ['survival','lifespan','clinical efficacy'])
  assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport'] and r['verificationState']=='pending_independent_source_audit'
  for l in r['sourceLocators']:assert l['sourceSha256']==c['source']['sha256'] and l['journalPrintedPage']==2130+l['physicalPage'] and 1<=l['physicalPage']<=10
 ids={r['id'] for r in c['results']}
 for r in c['claims']:assert set(r['resultIds'])<=ids and not r['acceptedSupport']
 assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
 assert next(q for q in c['reviewInputs'] if q['id']=='Q14')['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 assert c['inspection']['scopeCorrection']=='SCOPE-CORRECTION.json' and read(B/'SCOPE-CORRECTION.json')['initialPlanState']=='held_superseded_scope_error'
 return True
c=read(B/'SOURCE-CANDIDATE.json');validate(c);manifest=read(B/'AUDIT-MANIFEST.json')
for f,h in manifest['files'].items():assert hashlib.sha256((B/f).read_bytes()).hexdigest()==h
for f,h in read(B/'READINESS-v2.json')['hashes'].items():assert hashlib.sha256((B/f).read_bytes()).hexdigest()==h
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');entries=[json.loads(x) for x in (B/'review-inputs.jsonl').read_text().splitlines()];expected={(q['id'],f) for q in inv['questions'] for f in q['inputFields']};assert {(x['questionId'],x['field']) for x in entries}==expected and len(entries)==67
for r in entries:assert set(inv['requiredReviewInputEntryFields'])<=r.keys() and r['status'] in inv['answerStatuses'] and r['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,fn):
 x=copy.deepcopy(c);fn(x)
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' fixture unexpectedly accepted')
reject('rejecthumantrialmisclassification',lambda x:x['paper'].update(humanEvidence=True))
reject('rejectdoseconversiontobodyweight',lambda x:x['arms'][0]['exposure'].update(unit='mg_per_kg_body_weight'))
reject('rejectinferredtreatedN5',lambda x:x['results'][0]['estimate'].update(perArmAnimalN=5))
reject('rejectpriorcitedlifespansasnewendpoint',lambda x:x['results'][0].update(outcome='Survival benefit of three weeks'))
reject('rejectautomaticclinicalgrade',lambda x:x['results'][0].update(grade='High'))
reject('rejectoldwrongscopeGP',lambda x:x['inspection'].update(activeReadiness='READINESS.json'))
result={'status':'PASS','candidateSha256':manifest['candidateSha256'],'sourceSha256':c['source']['sha256'],'directQualitativeResultCandidates':2,'claimCandidates':2,'questions':15,'fieldInputs':67,'regressions':checks,'independentAudit':'pending','scientificApproval':False};(B/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
