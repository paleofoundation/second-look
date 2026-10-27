"""Guard MGUS observational scope, exposure timing and source reporting discrepancies."""
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
    assert c['paper']['sourceType'] == 'primary_retrospective_MGUS_diabetes_cohort_accepted_manuscript'
    assert c['paper']['existingReportId'] == 'B-R0044' and c['paper']['existingSourceId'] == 'B-R0044-F00'
    assert c['inspection']['textualPagesRead'] == list(range(1, 22))
    assert not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance', 'humanApproval', 'released'])
    s = c['study']
    assert s['design'] == 'VHA_retrospective_MGUS_diabetes_cohort' and not s['randomized']
    assert (s['screenedMGUSdiabetesN'], s['excludedN'], s['analyticN'], s['MMcases']) == (3287, 1284, 2003, 87)
    assert s['maleN'] == 1961 and s['deathsBeforeCutoff'] == 938
    assert s['timeOrigin'] == 'MGUSdiagnosis' and s['DMBeforeMGUSRequired']
    assert s['metforminExposureYears'] == 4 and s['singleGapMustBeLessThanMonths'] == 6
    assert not s['timeVaryingMetforminModelEstablished'] and not s['immortalTimeBiasEliminated']
    assert not s['causalPreventionEstablished'] and not s['clinicalDoseRecommendationAdopted']
    assert s['HgbA1cTiming'] == 'averagedafterMGUSdiagnosis'
    assert not s['nonusersNecessarilyNeverExposed'] and not s['metforminDoseAnalyzed']
    assert not s['safetyOutcomesReported'] and not s['biologicalMechanismMeasured']
    prior = s['preexistingIdentity']
    assert prior == read(B / 'PRIOR-RECONCILIATION.json')
    assert prior['priorDisposition']['state'] == 'held' and not prior['priorDisposition']['full_review_complete']
    assert prior['canonicalSourceChanges'] == 0 and prior['canonicalReviewChanges'] == 0
    assert [g['n'] for g in c['cohorts']] == [463, 1540]
    assert [g['MMcases'] for g in c['cohorts']] == [13, 74]
    assert len(c['results']) == len(c['claims']) == 3
    adjusted, counts, sensitivity = c['results']
    e = adjusted['estimate']
    assert e['kind'] == 'hazard_ratio'
    assert (e['fullyAdjustedHR'], e['fullyAdjustedCI95'], e['fullyAdjustedP']) == (.47, [.25, .87], .016)
    assert (e['univariateHR'], e['univariateCI95'], e['univariateP']) == (.52, [.29, .94], .030)
    assert e['partiallyAdjustedA_HR'] == .49 and e['partiallyAdjustedB_HR'] == .49
    assert not e['causalRiskReductionEstablished'] and e['absoluteRiskReduction'] is None and e['NNT'] is None
    e = counts['estimate']
    assert e['cases'] == [13, 74] and e['denominators'] == [463, 1540] and e['reportedPercent'] == [2.8, 4.8]
    assert e['table1PrintedChiSquareP'] == '<0.0001' and e['KMlogrankP'] == .028
    assert e['fixedTimeRiskDifference'] is None and e['wholeCohortMedianTimeToProgression'] is None
    e = sensitivity['estimate']
    assert e['years'] == [2, 3, 5, 6] and e['HRs'] == [.76, .63, .50, .58]
    assert e['CI95'] == [[.48, 1.12], [.38, 1.05], [.23, 1.06], [.24, 1.40]]
    assert e['allCIsInclude1'] and not e['sameAnalyticCohortGuaranteed'] and not e['provenFourYearThreshold']
    assert e['independentReplicationCount'] == 0 and e['exposedN'] == [None, None, 325, 246]
    for r in c['results']:
        assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:
            assert 1 <= loc['physicalPage'] <= 21 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C17-MPROTEIN', 'C17-INCIDENCE-P', 'C17-TEMPORAL-EXPOSURE', 'C17-HGBA1C', 'C17-COMPARATOR', 'C17-SENSITIVITY', 'C17-VERSION', 'C17-PROGRESSION-TIME'}
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
assert sha(reed / 'metformin-myeloma/pdfs/26034780-chang-2015.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
assert sha(reed / 'metformin-myeloma/index.csv') == read(B / 'READINESS.json')['indexSha256']
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

reject('observational_not_randomized', lambda x: x['study'].update(randomized=True))
reject('existing_B_R0044_identity_not_new_canonical_report', lambda x: x['paper'].update(existingReportId='new_report'))
reject('old_abstract_hold_not_silently_scientific_complete', lambda x: x['study']['preexistingIdentity']['priorDisposition'].update(full_review_complete=True))
reject('fouryear_users463_not_firstline461', lambda x: x['cohorts'][0].update(n=461))
reject('nonuser_definition_not_never_exposed', lambda x: x['study'].update(nonusersNecessarilyNeverExposed=True))
reject('HgbA1c_post_MGUS_average_not_baseline', lambda x: x['study'].update(HgbA1cTiming='baseline'))
reject('PH_test_not_timevarying_exposure_proof', lambda x: x['study'].update(timeVaryingMetforminModelEstablished=True))
reject('fouryear_exclusion_not_proof_immortal_time_eliminated', lambda x: x['study'].update(immortalTimeBiasEliminated=True))
reject('adjusted_HR_not_causal_prevention', lambda x: x['study'].update(causalPreventionEstablished=True))
reject('table_P_not_replaced_by_Cox_P', lambda x: x['results'][1]['estimate'].update(table1PrintedChiSquareP='0.016'))
reject('raw_fractions_not_fixed_time_risk_difference', lambda x: x['results'][1]['estimate'].update(fixedTimeRiskDifference=-.02))
reject('reported_progression_times_not_whole_cohort_KM_median', lambda x: x['results'][1]['estimate'].update(wholeCohortMedianTimeToProgression=[71, 47]))
reject('other_windows_not_proven_fouryear_threshold', lambda x: x['results'][2]['estimate'].update(provenFourYearThreshold=True))
reject('overlapping_sensitivities_not_independent_replication', lambda x: x['results'][2]['estimate'].update(independentReplicationCount=4))
reject('no_AE_result_not_safety_proof', lambda x: x['study'].update(safetyOutcomesReported=True))
reject('source_reporting_conflicts_preserved', lambda x: x.update(sourceQualifications=x['sourceQualifications'][1:]))
result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedObservationalFindings': 3, 'claims': 3, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'priorIdentityReusedOldHoldPreserved': True, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
