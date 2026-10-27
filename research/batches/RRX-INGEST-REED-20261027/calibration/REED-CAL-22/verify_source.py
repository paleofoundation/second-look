"""Guard alternating estimated coexposure, endpoint recovery and qualified causality."""
from pathlib import Path
import copy
import hashlib
import json
import os

B = Path(__file__).resolve().parent
ROOT = B.parents[4]

def read(p):
    return json.loads(p.read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def validate(c):
    schema=read(B/'SCHEMA.json');assert set(schema['required']) <= c.keys() and c['schemaVersion']==schema['schemaVersion']
    assert c['paper']['sourceType']=='primary_single_human_coingestion_adverse_event_case'
    assert c['paper']['existingReportId']=='A-F02-R1249' and c['paper']['existingSourceId']=='A-F02-R1249-F01'
    assert c['inspection']['textualPagesRead']==list(range(1,8)) and not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
    s=c['study'];assert (s['patients'],s['age'],s['sex'])==(1,65,'male')
    assert s['cancer']=='prostate_cancer_active_surveillance' and not s['oncologyResponseAssessed']
    assert s['exposure']=='alternating_daily_veterinary_fenbendazole_and_ivermectin'
    assert (s['estimatedFenbendazoleMgPerKgPerAdministration'],s['estimatedIvermectinMgPerKgPerAdministration'])==(.98,.18)
    for k in ['doseOrPurityAssayed','bothDrugsEveryDayEstablished','RUCAMIndependentAcceptance','encephalopathyReported','formalAcuteLiverFailureEstablished','biopsyPerformed','rechallengePerformed','genotypingPerformed','pharmacologicalTreatmentInitiated','NACGiven','singleDrugCausalityEstablished','synergisticHepatotoxicityEstablished','populationIncidenceEstimated','currentDoseRecommendationAdopted','pooledWithCAL21']:assert not s[k]
    assert s['RUCAMReported']==9 and s['reportedRValue']==37.50 and s['inpatientObservationDays']==3
    prior=s['priorIdentity'];assert prior==read(B/'PRIOR-RECONCILIATION.json')
    assert not prior['sameBytesAsPriorAsset'] and not prior['priorAcceptanceTransferred'] and prior['canonicalChanges']==0
    assert prior['priorAssetSha256']=='91b05e5e2bc5e7339daa552dcf75939b0361673e5af3c78de80b4f91b4e9c6b8'
    assert len(c['results'])==len(c['claims'])==3
    a,b,d=[r['estimate'] for r in c['results']]
    assert (a['ALT_U_L'],a['AST_U_L'],a['ALP_U_L'],a['bilirubin_mg_dL'],a['INR'])==(1764,1132,148,12.9,1.7)
    assert a['PTUnitReported'] is None and a['cancerResponseOutcome'] is None and a['populationRisk'] is None
    assert b['postCessationDays']==['baseline',0,1,2,3,6,9,22,42,143]
    assert b['bilirubin_mg_dL']==[.8,12.9,15.2,16.7,18.3,23.1,16.5,4.3,2.3,.8]
    assert b['ALP_U_L']==[61,148,141,147,146,155,151,98,78,63]
    assert b['AST_U_L']==[18,1132,739,666,698,488,387,61,28,20]
    assert b['ALT_U_L']==[21,1764,1373,1248,1201,899,741,111,25,17]
    assert b['transaminasesNormalDay42'] and not b['allShownLabsNormalDay42'] and not b['bilirubinNormalDay42']
    assert b['allShownLabsNormalDay143'] and b['bilirubinPeakDay']==6 and not b['pharmacologicalTreatmentInitiated']
    assert d['reportedRUCAM']==9 and sum(d['componentsReported'].values())==9
    assert d['courseReported']=='58percent_ALT_decline_within9days' and d['criterionCitedInDiscussion']=='50percent_drop_within8days'
    assert not d['day7Or8ALTMeasured'] and not d['criterionWithin8DaysEstablished'] and not d['independentlyAcceptedOrRecalculatedScore']
    for k in ['biopsyOrRechallenge','HLAOrCYPMechanismTested','combinedToxicityVersusSingleAgentCompared','individualMortalityRiskCalculated']:assert not d[k]
    for r in c['results']:
        assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:assert 1 <= loc['physicalPage'] <= 7 and loc['sourceSha256']==c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']}=={'C22-DOSE','C22-RUCAM','C22-RECOVERY','C22-COEXPOSURE','C22-REGULATORY-MECHANISM','C22-RUCAM-ALCOHOL'}
    assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
    assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
    for claim in c['claims']:assert not claim['acceptedSupport'] and set(claim['resultIds']) <= {r['id'] for r in c['results']}

c = read(B / 'SOURCE-CANDIDATE.json')
validate(c)
for f, h in read(B / 'AUDIT-MANIFEST.json')['files'].items():
    assert sha(B / f) == h
for f, h in read(B / 'READINESS.json')['hashes'].items():
    assert sha(B / f) == h
assert c['sourceQualifications'] == read(B / 'SOURCE-QUALIFICATIONS.json')
reed = Path(os.environ.get('REMAPRX_REED_ROOT', '/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed / 'fenbendazole-cancer/pdfs/42299164-powderlyge-2026.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
assert sha(reed / 'fenbendazole-cancer/index.csv') == read(B / 'READINESS.json')['indexSha256']
inventory = read(ROOT / 'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json')
entries = [json.loads(line) for line in (B / 'review-inputs.jsonl').read_text().splitlines()]
assert len(entries) == 67
assert {(e['questionId'], e['field']) for e in entries} == {(q['id'], f) for q in inventory['questions'] for f in q['inputFields']}
for entry in entries:
    assert set(inventory['requiredReviewInputEntryFields']) <= entry.keys()
    assert entry['status'] in inventory['answerStatuses'] and entry['sourceHash'] == c['source']['sha256']

checks = []
def reject(name, mutate):
    altered = copy.deepcopy(c)
    mutate(altered)
    try:
        validate(altered)
    except AssertionError:
        checks.append(name)
        return
    raise AssertionError(name + ' unexpectedly accepted')

reject('onecase_not_population_incidence', lambda x:x['study'].update(populationIncidenceEstimated=True))
reject('estimated_not_assayed_dose', lambda x:x['study'].update(doseOrPurityAssayed=True))
reject('alternating_not_each_drug_daily', lambda x:x['study'].update(bothDrugsEveryDayEstablished=True))
reject('prostate_background_not_cancer_response', lambda x:x['study'].update(oncologyResponseAssessed=True))
reject('INR_without_encephalopathy_not_formal_ALF', lambda x:x['study'].update(formalAcuteLiverFailureEstablished=True))
reject('no_NAC_or_pharmacotherapy', lambda x:x['study'].update(NACGiven=True))
reject('day42_bilirubin_not_normal', lambda x:x['results'][1]['estimate'].update(bilirubinNormalDay42=True))
reject('sixweeks_not_all_lab_normalization', lambda x:x['results'][1]['estimate'].update(allShownLabsNormalDay42=True))
reject('bilirubin_peaks_day6', lambda x:x['results'][1]['estimate'].update(bilirubinPeakDay=0))
reject('nine_day_decline_not_proved_within_eight', lambda x:x['results'][2]['estimate'].update(criterionWithin8DaysEstablished=True))
reject('reported_RUCAM_not_independent_acceptance', lambda x:x['results'][2]['estimate'].update(independentlyAcceptedOrRecalculatedScore=True))
reject('no_single_drug_causal_isolation', lambda x:x['study'].update(singleDrugCausalityEstablished=True))
reject('no_synergistic_toxicity_comparison', lambda x:x['study'].update(synergisticHepatotoxicityEstablished=True))
reject('no_individual_mortality_probability', lambda x:x['results'][2]['estimate'].update(individualMortalityRiskCalculated=True))
reject('old_new_source_bytes_distinct', lambda x:x['study']['priorIdentity'].update(sameBytesAsPriorAsset=True))
reject('no_prior_acceptance_transfer', lambda x:x['study']['priorIdentity'].update(priorAcceptanceTransferred=True))
reject('no_CAL21_case_pool', lambda x:x['study'].update(pooledWithCAL21=True))
reject('source_qualifications_retained', lambda x:x.update(sourceQualifications=[]))

result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedCaseFindings': 3, 'claims': 3, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
