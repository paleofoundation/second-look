import json,hashlib,copy
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def validate(c):
 schema=read(B/'SCHEMA.json');assert all(k in c for k in schema['requiredTopLevel']);sha=read(B/'READINESS.json')['sourceSha256'];assert c['source']['sha256']==sha and c['source']['pmid']=='18608093'
 assert c['experiment']['randomizedTotal']==86 and c['experiment']['primaryPoolTotal']==60 and c['experiment']['concurrentPlacebo']==False
 assert sorted(c['experiment']['primaryPoolArmN'].values())==[30,30] and sorted(c['experiment']['secondaryAllRandomizedArmN'].values())==[39,47]
 assert len(c['results'])==8 and len({r['id'] for r in c['results']})==8;assert len(c['claims'])==8
 for r in c['results']:
  assert all(k in r for k in schema['resultRequired']);assert r['verificationState']=='pending_independent_source_audit' and r['acceptedSupport']==False and r['grade'] is None and r['benefitGrade'] is None
  assert r['experimentId']==c['experiment']['id'] and set(r['arms'])=={a['id'] for a in c['arms']}
  for l in r['sourceLocators']:assert all(k in l for k in schema['locatorRequired']) and l['sourceSha256']==sha and 1<=l['physicalPage']<=21 and l['journalPrintedPage'] is None
 assert c['results'][0]['estimate']['reportedAbsoluteDifference']==1.2 and c['results'][0]['estimate']['selectionThreshold']==1.035
 m='REED-CAL-01-ARM-MC';cc='REED-CAL-01-ARM-CC'
 assert c['results'][0]['estimate']['values'][m]['n']==c['results'][0]['estimate']['values'][cc]['n']==30
 for r in [c['results'][2],*c['results'][4:]]:assert r['estimate']['values'][m]['denominator']==39 and r['estimate']['values'][cc]['denominator']==47
 ids={r['id'] for r in c['results']}
 for claim in c['claims']:assert set(claim['resultIds'])<=ids and claim['acceptedSupport']==False
 assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
 assert c['inspection']['physicalPagesRead']==list(range(1,22)) and c['inspection']['fullScientificReviewComplete']==False
 assert not c['scientificAcceptance'] and not c['humanApproval'] and not c['released'] and len(c['gaps'])>=4
 return True
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');fields=[json.loads(line) for line in (B/'review-inputs.jsonl').read_text().splitlines()];expected={(q['id'],f) for q in inv['questions'] for f in q['inputFields']};assert {(r['questionId'],r['field']) for r in fields}==expected and len(fields)==len(expected)==67
for r in fields:
 assert set(inv['requiredReviewInputEntryFields'])<=r.keys() and r['status'] in inv['answerStatuses'] and r['sourceHash']==c['source']['sha256'];assert r['verificationState']=='pending_independent_source_audit'
for name,h in read(B/'AUDIT-MANIFEST.json')['files'].items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==h
checks=[]
def reject(name,mutator):
 x=copy.deepcopy(c);mutator(x)
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError('Fixture accepted: '+name)
reject('primary60cannotbe86',lambda x:x['experiment'].update(primaryPoolTotal=86))
reject('noplacebofabrication',lambda x:x['experiment'].update(concurrentPlacebo=True))
reject('noanalysispopulationtransfer',lambda x:x['results'][4]['estimate']['values']['REED-CAL-01-ARM-MC'].update(denominator=30))
reject('noautomaticclinicalgrade',lambda x:x['results'][0].update(grade='High'))
reject('nounauditedscientificapproval',lambda x:x.update(scientificAcceptance=True))
reject('noselectionassuperioritypvalue',lambda x:x['results'][0]['estimate'].update(selectionThreshold=0.05))
result={'status':'PASS','sourceHash':c['source']['sha256'],'candidateSha256':hashlib.sha256((B/'SOURCE-CANDIDATE.json').read_bytes()).hexdigest(),'locatedResultCandidates':8,'claimCandidates':8,'questions':15,'fieldInputs':67,'regressions':checks,'independentAudit':'bounded8resultsourcefidelityPASSonv3;v4Q14followuppending','scientificApproval':False};(B/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
