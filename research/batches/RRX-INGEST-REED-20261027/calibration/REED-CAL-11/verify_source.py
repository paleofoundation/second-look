"""Check incident-disease scope, overlapping analyses and trend/uncertainty limits."""
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
    schema = read(B / 'SCHEMA.json')
    assert set(schema['required']) <= c.keys() and c['schemaVersion'] == schema['schemaVersion']
    assert c['paper']['sourceType'] == 'primary_prospective_incidence_cohort'
    assert c['inspection']['textualPagesRead'] == list(range(1, 16))
    assert not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance', 'humanApproval', 'released'])
    s = c['study']
    assert s['design'] == 'prospective_observational_cohorts' and not s['randomized']
    assert s['endpointPurpose'] == 'incident_multiple_myeloma_risk'
    assert s['exposureLagYears'] == 4 and s['exposureUpdateYears'] == 2
    assert not s['causalPreventionEstablished'] and not s['sexInteractionProven']
    assert not s['doseRecommendationEstablished'] and not s['safetyResultAvailable']
    assert not s['mechanismDirectlyMeasured'] and s['optimalRiskBenefitDoseFrequency'] is None
    assert s['participantCountsNotSummedAcrossAnalysesOrCAL04']
    assert s['exposureMissingHandling'] == 'carry previous exposure one followup interval only, then set missing'
    men, women = c['cohorts']
    assert (men['quantityBaselineN'], men['durationBaselineN'], women['quantityBaselineN'], women['durationBaselineN']) == (30839, 47029, 85942, 85942)
    assert (men['quantityBaselineYear'], men['durationBaselineYear'], women['quantityBaselineYear']) == (1996, 1990, 1984)
    assert len(c['results']) == len(c['claims']) == 2
    quantity, duration = c['results']
    assert (quantity['analysisCases'], quantity['reportedTotalPersonYears']) == (265, 1997506)
    assert (duration['analysisCases'], duration['reportedTotalPersonYears']) == (328, 2395458)
    assert [r['category'] for r in quantity['cohortRows']] == ['Non-users', '<2', '2-<5', '>=5']
    assert [r['category'] for r in duration['cohortRows']] == ['Non-users', '<=5', '6-10', '>=11']
    assert [r['combined']['HR'] for r in quantity['cohortRows']] == [1, .92, 1.04, .61]
    assert [r['combined']['HR'] for r in duration['cohortRows']] == [1, .80, .97, .63]
    assert quantity['cohortRows'][-1]['combined']['CI95'] == [.39, .94]
    assert duration['cohortRows'][-1]['combined']['CI95'] == [.41, .95]
    assert quantity['cohortRows'][-1]['HPFS']['cases'] == 3
    assert duration['cohortRows'][-1]['HPFS']['cases'] == 6
    assert quantity['cohortRows'][-1]['NHS']['CI95'] == [.43, 1.18]
    assert duration['cohortRows'][-1]['NHS']['CI95'] == [.48, 1.37]
    assert quantity['estimate']['trendP'] == {'HPFS': .11, 'NHS': .22, 'combined': .06}
    assert duration['estimate']['trendP'] == {'HPFS': .02, 'NHS': .96, 'combined': .17}
    for result in c['results']:
        e = result['estimate']
        assert e['kind'] == 'hazard_ratio' and e['trendTestNotPairwiseCategoryP']
        assert e['NNT'] is None and e['absoluteRiskReduction'] is None
        assert not result['participantDenominatorIsPersonYears'] and not result['causalPreventionEstablished']
        assert result['grade'] is None and result['benefitGrade'] is None and not result['acceptedSupport']
        for loc in result['sourceLocators']:
            assert 1 <= loc['physicalPage'] <= 15 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C11-NHS-CUTOFF', 'C11-TREND-CODING', 'C11-PERSON-YEAR-SUM', 'C11-OVERLAP', 'C11-DOSE-SAFETY'}
    assert [q['id'] for q in c['reviewInputs']] == ['Q' + str(i).zfill(2) for i in range(1, 16)]
    assert c['reviewInputs'][13]['downstreamMapping'] == read(B / 'DOWNSTREAM-MAPPING.json')
    for claim in c['claims']:
        assert not claim['acceptedSupport'] and set(claim['resultIds']) <= {r['id'] for r in c['results']}

c = read(B / 'SOURCE-CANDIDATE.json')
validate(c)
for f, h in read(B / 'AUDIT-MANIFEST.json')['files'].items():
    assert sha(B / f) == h
for f, h in read(B / 'READINESS.json')['hashes'].items():
    assert sha(B / f) == h
assert c['sourceQualifications'] == read(B / 'SOURCE-QUALIFICATIONS.json')
reed = Path(os.environ.get('REMAPRX_REED_ROOT', '/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed / 'aspirin-myeloma/pdfs/24282256-birmann-2014.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
assert sha(reed / 'aspirin-myeloma/index.csv') == read(B / 'READINESS.json')['indexSha256']
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

reject('incident_disease_not_mortality', lambda x: x['study'].update(endpointPurpose='postdiagnosis_mortality'))
reject('observational_not_randomized', lambda x: x['study'].update(randomized=True))
reject('quantity_265_not_duration_328_cases', lambda x: x['results'][0].update(analysisCases=328))
reject('person_time_not_participant_N', lambda x: x['results'][0].update(participantDenominatorIsPersonYears=True))
reject('no_cross_analysis_or_CAL04_population_sum', lambda x: x['study'].update(participantCountsNotSummedAcrossAnalysesOrCAL04=False))
reject('four_year_lag_retained', lambda x: x['study'].update(exposureLagYears=0))
reject('trend_P_not_category_P', lambda x: x['results'][0]['estimate'].update(trendTestNotPairwiseCategoryP=False))
reject('subgroup_significance_not_sex_interaction', lambda x: x['study'].update(sexInteractionProven=True))
reject('lower_null_categories_not_dropped', lambda x: x['results'][0].update(cohortRows=x['results'][0]['cohortRows'][2:]))
reject('association_not_causal_prevention', lambda x: x['study'].update(causalPreventionEstablished=True))
reject('no_safety_data_not_safe', lambda x: x['study'].update(safetyResultAvailable=True))
reject('source_inconsistencies_not_silently_repaired', lambda x: x.update(sourceQualifications=x['sourceQualifications'][1:]))
result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedMultiCategoryFindings': 2, 'claims': 2, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
