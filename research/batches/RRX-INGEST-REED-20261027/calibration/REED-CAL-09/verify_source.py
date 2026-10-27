"""Validate safety-series units, compounds, case denominators and attribution limits."""
from pathlib import Path
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 s=read(B/'SCHEMA.json');assert set(s['required'])<=c.keys() and c['schemaVersion']==s['schemaVersion']
 assert c['paper']['sourceType']=='primary_early_pilot_safety_case_series'
 assert c['inspection']['textualPagesRead']==list(range(1,13)) and not c['inspection']['fullScientificReviewComplete']
 assert not c['scientificAcceptance'] and not c['humanApproval'] and not c['released']
 st=c['study'];assert st['agents']==['metforminXR','ritonavir'] and st['reportedN']==3 and st['lacticAcidemiaCases']==2
 assert st['populationIncidenceRate'] is None and not st['soleMetforminCausationEstablished'] and st['currentRegimenObjectivePRCR'] is None
 assert [p['metforminLeadInWeeks'] for p in c['cases']]==[2,3,2] and all(p['metforminSpecificActualDose'] is None for p in c['cases'])
 assert len(c['results'])==len(c['claims'])==len(c['cases'])==3
 for r in c['results']:
  assert r['comparator'] is None and r['populationRate'] is None and not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None
  for l in r['sourceLocators']:assert 1<=l['physicalPage']<=12 and l['sourceSha256']==c['source']['sha256']
 r=c['results'][0]['estimate'];assert r['lactate']['unit']=='mmol/L' and r['lactate']['event']==4.6 and r['creatinine']['unit']=='mg/dL'
 assert not r['definitiveMetforminAloneCausation']
 r=c['results'][1]['estimate'];assert r['lacticAcidemia']=='not_reported_for_this_case_not_verified_absent' and r['currentDiseaseResponse']=='stable disease asreported' and r['voluntaryWithdrawal'] and not r['unacceptableToxicityByStudyDefinition']
 r=c['results'][2]['estimate'];assert r['lactate']['value']==3.74 and r['lactate']['unit']=='mmol/L'
 assert r['creatinine']['valueAsPrinted']==1.4 and r['creatinine']['unitAsPrinted']=='mmol/L' and r['creatinine']['normalizedValue'] is None and not r['definitiveMetforminAloneCausation']
 pk=c['pharmacokineticContext'];assert pk['day1N']==3 and pk['day15N']==2 and pk['day15CmaxRangeLiteral']==[1043,1011] and not pk['absenceOfDrugInteractionProven']
 assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
 assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for cl in c['claims']:assert not cl['acceptedSupport'] and set(cl['resultIds'])<={r['id'] for r in c['results']}
 return True
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for f,h in read(B/'AUDIT-MANIFEST.json')['files'].items():assert sha(B/f)==h
for f,h in read(B/'READINESS.json')['hashes'].items():assert sha(B/f)==h
assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json')
root=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(root/'metformin-myeloma/pdfs/32631779-nathwani-2020.pdf')==c['source']['sha256']==read(B/'READINESS.json')['sourceSha256'];assert sha(root/'metformin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(x) for x in (B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field']) for e in es}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in es:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,mutate):
 x=copy.deepcopy(c);mutate(x)
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' unexpectedlyaccepted')
reject('ritonavir_not_nelfinavir',lambda x:x['study'].update(agents=['metforminXR','nelfinavir']))
reject('three_cases_not_twelve_pooled_with_CAL07',lambda x:x['study'].update(reportedN=12))
reject('two_cases_not_population_risk',lambda x:x['study'].update(populationIncidenceRate=2/3))
reject('printed_creatinine_unit_not_silently_mg_dL',lambda x:x['results'][2]['estimate']['creatinine'].update(unitAsPrinted='mg/dL'))
reject('unreported_lactate_not_proven_normal',lambda x:x['results'][1]['estimate'].update(lacticAcidemia='absent_normal'))
reject('later_therapy_CR_not_current_regimen_response',lambda x:x['study'].update(currentRegimenObjectivePRCR=1))
reject('different_PK_N_not_proof_no_interaction',lambda x:x['pharmacokineticContext'].update(absenceOfDrugInteractionProven=True))
reject('protocol_maximum_not_individual_actual_metformin_dose',lambda x:x['cases'][0].update(metforminSpecificActualDose=1000))
reject('regimen_signal_not_metformin_alone_cause',lambda x:x['study'].update(soleMetforminCausationEstablished=True))
r={'status':'PASS','candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceSha256':c['source']['sha256'],'boundedCaseFindings':3,'claims':3,'questions':15,'typedFields':67,'regressions':checks,'unitPKAttributionQualifications':'held','independentAudit':'pending','fullScientificReviewComplete':False,'scientificAcceptance':False};(B/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
