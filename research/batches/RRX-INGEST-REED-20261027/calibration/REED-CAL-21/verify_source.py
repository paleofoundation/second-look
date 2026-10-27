"""Guard single-case coexposure, lab thresholds and causality limits."""
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
    assert c['paper']['sourceType']=='primary_single_human_adverse_event_case'
    assert c['inspection']['textualPagesRead']==[1,2,3] and not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
    s=c['study'];assert (s['patients'],s['age'],s['sex'])==(1,55,'female')
    assert s['indication']=='self_directed_parasite_cleanse_without_confirmed_infection' and not s['cancerPresentReported']
    assert (s['fenbendazoleMgDailySelfReported'],s['TUDCAMgDailySelfReported'],s['exposureWeeks'],s['lastDoseDaysBeforeAdmission'])==(222,500,4,3)
    assert s['comparisonGroup'] is None and s['RUCAMReported']==9 and s['RValueReported']=='>=5'
    for k in ['formulationPurityAssayed','RUCAMComponentsAvailable','acuteLiverFailureReported','biopsyReported','rechallengeReported','soleFenbendazoleCausalityIndependentlyEstablished','populationIncidenceEstimated','TUDCAProtectionOrHarmEstablished','NACEfficacyEstablished','cancerEfficacyAssessed','clinicalDoseRecommendationAdopted']:assert not s[k]
    assert len(c['results'])==len(c['claims'])==3
    a,b,d=[r['estimate'] for r in c['results']]
    assert (a['ALTText'],a['ALTTableDay1'],a['ALPText_U_L'],a['ALPTableDay1_U_L'])==('>3300',3300,255,245)
    assert a['AST_U_L']==1854 and a['bilirubin_mg_dL']==1.7 and a['INR']==1.11 and a['populationRate'] is None
    assert b['days']==[1,2,3,4,5,10,26]
    assert b['ALT_U_L']==[3300,3300,2578,2318,2201,1077,37]
    assert b['AST_U_L']==[1854,1357,1097,937,876,328,19]
    assert b['ALP_U_L']==[245,231,193,186,195,177,108]
    assert b['bilirubin_mg_dL']==[1.7,1.6,1.5,1.4,1.6,1.3,.8]
    assert b['INRLiteral']==[1.11,1.12,1.08,1.08,.96,'<0.9',None]
    assert b['NACHours']==72 and b['dischargeDayTable']==5 and not b['NACDurationEqualsHospitalStay']
    assert b['day26MeasuredINR'] is None and b['recoveryNotRandomizedNACEffect']
    assert d['RUCAMReported']==9 and not d['RUCAMRecalculated'] and not d['soleDrugCausalityEstablished']
    assert not d['TUDCAProtectiveEffectMeasured'] and not d['TUDCAHarmContributionExcluded'] and not d['currentGlobalTrialAbsenceVerified']
    assert d['comparativeRisk'] is None
    for r in c['results']:
        assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:assert 1 <= loc['physicalPage'] <= 3 and loc['sourceSha256']==c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']}=={'C21-ALP','C21-ALT','C21-EXPOSURE','C21-CAUSALITY','C21-MANAGEMENT','C21-INR','C21-PRIOR-LITERATURE'}
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
assert sha(reed / 'fenbendazole-cancer/pdfs/42383214-satinskya-2026.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
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

reject('one_case_not_population_risk', lambda x:x['study'].update(populationIncidenceEstimated=True))
reject('not_cancer_treatment_case', lambda x:x['study'].update(cancerPresentReported=True))
reject('coexposure_TUDCA_not_erased', lambda x:x['study'].update(TUDCAMgDailySelfReported=0))
reject('selfreport_not_purity_assay', lambda x:x['study'].update(formulationPurityAssayed=True))
reject('ALP_text_table_difference_not_repaired', lambda x:x['results'][0]['estimate'].update(ALPText_U_L=245))
reject('ALT_text_threshold_not_exact3300', lambda x:x['results'][0]['estimate'].update(ALTText='3300'))
reject('INR_day10_threshold_not_exact', lambda x:x['results'][1]['estimate']['INRLiteral'].__setitem__(5,.9))
reject('INR_day26_blank_not_zero', lambda x:x['results'][1]['estimate'].update(day26MeasuredINR=0))
reject('72h_NAC_not_exact_stay', lambda x:x['results'][1]['estimate'].update(NACDurationEqualsHospitalStay=True))
reject('RUCAM_not_independently_recalculated', lambda x:x['results'][2]['estimate'].update(RUCAMRecalculated=True))
reject('not_sole_drug_proof', lambda x:x['results'][2]['estimate'].update(soleDrugCausalityEstablished=True))
reject('no_TUDCA_protective_effect_estimate', lambda x:x['results'][2]['estimate'].update(TUDCAProtectiveEffectMeasured=True))
reject('no_NAC_causal_efficacy', lambda x:x['study'].update(NACEfficacyEstablished=True))
reject('no_current_global_trial_absence', lambda x:x['results'][2]['estimate'].update(currentGlobalTrialAbsenceVerified=True))
reject('source_qualifications_preserved', lambda x:x.update(sourceQualifications=[]))

result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedCaseFindings': 3, 'claims': 3, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
