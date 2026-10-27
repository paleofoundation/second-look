"""Check in-vitro source units and additive/replicate/translation boundaries."""
from pathlib import Path
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 s=read(B/'SCHEMA.json');assert set(s['required'])<=c.keys() and c['schemaVersion']==s['schemaVersion']
 assert c['paper']['sourceType']=='primary_invitro' and not c['paper']['humanClinicalEvidence']
 assert c['inspection']['textualPagesRead']==list(range(1,9)) and not c['inspection']['fullScientificReviewComplete']
 assert not c['scientificAcceptance'] and not c['humanApproval'] and not c['released']
 assert len(c['models'])==2 and all(m['mutationAssignment']=='unresolved_abstract_vs_Methods' for m in c['models'])
 e=c['exposures'][0];assert e['ASA']=={'value':2.5,'unit':'mM'} and e['BTZ']=={'value':10,'unit':'nM'} and e['clinicalDose'] is None and not e['humanPKEquivalenceVerified']
 assert len(c['results'])==len(c['claims'])==3
 for r in c['results']:
  assert not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None and r['estimate']['humanEffect'] is None
  assert r['uncertainty']['numericCI'] is None and r['uncertainty']['numericSD'] is None
  for l in r['sourceLocators']:assert l['sourceSha256']==c['source']['sha256'] and l['printedPage']==646+l['physicalPage']
 assert c['results'][0]['estimate']['reportedInteraction']=='additive' and c['results'][0]['estimate']['reportedRInterval']==[.8,1.2]
 a=c['results'][1]['estimate'];assert a['authorsReportedIndependentExperiments']==3 and a['flowEventsPerAnalysis']==10000 and not a['biologicalReplicateNIndependentlyVerified']
 assert a['MM1S']==[2.73,44.8,45.4,64.3] and a['RPMI8226']==[3.43,36.1,57.9,77.2] and a['unit']=='percent'
 a=c['results'][2]['estimate'];assert a['numericIOD'] is None and not a['directSelectiveBindingDemonstrated'] and not a['causalMediationEstablished']
 assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
 assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for cl in c['claims']:assert not cl['acceptedSupport'] and set(cl['resultIds'])<={r['id'] for r in c['results']}
 return True
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for f,h in read(B/'AUDIT-MANIFEST.json')['files'].items():assert sha(B/f)==h
for f,h in read(B/'READINESS.json')['hashes'].items():assert sha(B/f)==h
assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json')
root=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(root/'aspirin-myeloma/pdfs/28356941-ding-2017.pdf')==c['source']['sha256']==read(B/'READINESS.json')['sourceSha256'];assert sha(root/'aspirin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(x) for x in (B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field']) for e in es}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in es:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,mutate):
 x=copy.deepcopy(c);mutate(x)
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' unexpectedlyaccepted')
reject('additive_not_synergistic',lambda x:x['results'][0]['estimate'].update(reportedInteraction='synergistic'))
reject('culture_mM_not_human_mg_per_day',lambda x:x['exposures'][0]['ASA'].update(unit='mg/day'))
reject('BTZ_nM_not_mM',lambda x:x['exposures'][0]['BTZ'].update(unit='mM'))
reject('flow_events_not_experiment_replicates',lambda x:x['results'][1]['estimate'].update(authorsReportedIndependentExperiments=10000))
reject('cellline_finding_not_human_clinical_evidence',lambda x:x['paper'].update(humanClinicalEvidence=True))
reject('marker_pattern_not_direct_binding',lambda x:x['results'][2]['estimate'].update(directSelectiveBindingDemonstrated=True))
reject('unresolved_Ras_assignment_not_guessed',lambda x:x['models'][0].update(mutationAssignment='K-Ras_verified'))
reject('no_SD_from_bar_pixels',lambda x:x['results'][1]['uncertainty'].update(numericSD=1.2))
r={'status':'PASS','candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceSha256':c['source']['sha256'],'boundedInVitroFindings':3,'claims':3,'questions':15,'typedFields':67,'regressions':checks,'modelMarkerPKQualifications':'held','independentAudit':'pending','fullScientificReviewComplete':False,'scientificAcceptance':False};(B/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
