"""Validate secondary-source provenance and known unsafe reinterpretations."""
import copy,hashlib,json,os
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 schema=read(B/'SCHEMA.json');assert set(schema['required'])<=c.keys()
 assert c['schemaVersion']==schema['schemaVersion']
 assert c['paper']['sourceType']=='secondary_systematic_review_meta_analysis' and c['paper']['tier']=='CONTEXT'
 assert c['paper']['newOriginalTrialCount']==c['paper']['newIndependentParticipants']==0
 assert c['source']['sha256']==read(B/'READINESS.json')['sourceSha256']
 assert not c['scientificAcceptance'] and not c['humanApproval'] and not c['released'] and not c['inspection']['fullScientificReviewComplete']
 assert c['inspection']['textualPagesRead']==list(range(1,29))
 obs=c['observations'];assert len(obs)==3
 for o in obs:
  assert set(schema['observationRequired'])<=o.keys()
  assert not o['originalDataVerified'] and not o['acceptedSupport'] and o['independentTrialCountContribution']==0 and o['grade'] is None
  for l in o['sourceLocators']:assert set(schema['locatorRequired'])<=l.keys() and 1<=l['physicalPage']<=28 and l['sourceSha256']==c['source']['sha256']
 assert obs[0]['values']['abstractALSStudyCount']==2 and obs[0]['values']['bodyALSStudyCount']==1 and obs[0]['values']['adjudicatedIndependentALSTrialCount'] is None
 assert obs[1]['values']['comparatorLiteral']=='TAU' and obs[1]['values']['originalTrialDenominatorVerified']==False
 for k in ['ALSArmEffectEstimates','ALSBetweenGroupEffect','ALSConfidenceInterval','ALSPValue','ALSPooledEffect']:assert obs[2]['values'][k] is None
 assert c['includedPrimaryReportLinks'][0]['originalAccess']=='not_accessible' and not c['includedPrimaryReportLinks'][0]['originalDataVerified']
 assert len(c['claims'])==3
 for cl in c['claims']:assert not cl['acceptedSupport'] and set(cl['observationIds'])<={o['id'] for o in obs}
 assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
 assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 assert c['methods']['cutoff']['intro']=='June2022' and c['methods']['cutoff']['methods']=='May2022' and c['methods']['cutoff']['resolution']=='unresolved'
 return True
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for f,h in read(B/'AUDIT-MANIFEST.json')['files'].items():assert sha(B/f)==h
for f,h in read(B/'READINESS.json')['hashes'].items():assert sha(B/f)==h
root=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));source=root/'minocycline-als/pdfs/36982324-panizzutti-2023.pdf';assert sha(source)==c['source']['sha256'] and sha(root/'minocycline-als/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');entries=[json.loads(x) for x in (B/'review-inputs.jsonl').read_text().splitlines()]
assert len(entries)==67 and {(x['questionId'],x['field']) for x in entries}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in entries:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,mutate):
 x=copy.deepcopy(c);mutate(x)
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError('Unsafe reinterpretation accepted: '+name)
reject('review_cannot_add_an_original_trial',lambda x:x['paper'].update(newOriginalTrialCount=1))
reject('review_cannot_add_twenty_new_participants',lambda x:x['paper'].update(newIndependentParticipants=20))
reject('abstract_two_cannot_silently_resolve_body_one',lambda x:x['observations'][0]['values'].update(adjudicatedIndependentALSTrialCount=2))
reject('unreported_effect_cannot_be_zero',lambda x:x['observations'][2]['values'].update(ALSBetweenGroupEffect=0))
reject('TAU_cannot_be_reclassified_placebo',lambda x:x['observations'][1]['values'].update(comparatorLiteral='placebo'))
reject('unavailable_primary_cannot_be_verified',lambda x:x['includedPrimaryReportLinks'][0].update(originalDataVerified=True))
reject('authors_high_risk_cannot_be_new_GRADE',lambda x:x['observations'][1].update(grade='High'))
r={'status':'PASS','candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceSha256':c['source']['sha256'],'secondaryObservations':3,'claims':3,'newOriginalTrials':0,'newParticipants':0,'questions':15,'typedFields':67,'regressions':checks,'independentAudit':'pending','fullScientificReviewComplete':False,'scientificAcceptance':False};(B/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
