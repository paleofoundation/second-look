"""Guard selected maintenance population, endpoint/time origins and safety missingness."""
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
    assert c['paper']['sourceType'] == 'primary_randomized_selected_maintenance'
    assert c['inspection']['textualPagesRead'] == list(range(1, 8))
    assert not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance', 'humanApproval', 'released'])
    s = c['study']
    assert (s['inductionRandomizedN'], s['inductionResponseEvaluableN'], s['nineCycleEligibleN'], s['maintenanceRandomizedN'], s['maintenancePerArm']) == (289, 249, 137, 128, 64)
    assert s['eligibleNotRandomized'] == {'total': 9, 'toxicityOrPoorCondition': 5, 'noConsent': 4}
    assert s['maintenancePowerPlannedN'] == 194 and s['maintenanceActualPowerPercent'] == 69
    assert s['timeOrigin'] == 'maintenance_randomization'
    assert not s['allInductionPatientsInMaintenanceEstimate'] and not s['clinicalDoseRecommendationAdopted']
    assert s['newIndependentTrialFamiliesFromInductionReport'] == 0
    assert [a['randomizedN'] for a in c['arms']] == [64, 64]
    assert [a['safetyAvailableN'] for a in c['arms']] == [61, 63]
    assert c['arms'][0]['thalidomideTargetMgDaily'] == 200 and c['arms'][0]['thalidomideActualMedianMgDaily'] == 75
    assert c['arms'][1]['label'] == 'interferon_alpha2b_alone'
    assert len(c['results']) == len(c['claims']) == 5
    pfs, os_result, conditional, response, ae = c['results']
    e = pfs['estimate']
    assert (e['medianMonths'], e['events'], e['HR'], e['CI95'], e['P']) == ([27.7, 13.2], [38, 49], .55, [.36, .86], .0068)
    assert e['randomizedNs'] == [64, 64] and not e['PFSBenefitIsOSBenefit']
    assert not e['all289InductionPatientsBenefitEstablished']
    e = os_result['estimate']
    assert (e['medianMonths'], e['deaths'], e['HR'], e['CI95'], e['P']) == ([52.6, 51.4], [23, 25], .93, [.53, 1.66], .81)
    assert not e['survivalBenefitEstablished'] and not e['survivalEquivalenceEstablished']
    assert e['observedTotalDeaths'] == 48
    e = conditional['estimate']
    assert e['displayedSubsetN'] == [38, 49] and e['displayedDeaths'] == [23, 25]
    assert (e['medianMonths'], e['HR'], e['CI95'], e['P']) == ([8.1, 25.6], 1.75, [.97, 3.14], .056)
    assert e['timeOrigin'] == 'progression_in_event_selected_subgroup'
    assert not e['fullRandomizedCausalHarmEstablished'] and not e['statisticallySignificantAt05']
    e = response['estimate']
    assert e['upgradePatients'] == [5, 2] and e['reportedPercent'] == [8, 3]
    assert e['baselinePRcounts'] == [11, 12] and e['conditionalPRSubsetRateCalculated'] is None
    assert e['notDeNovoORR'] and e['CI'] is None and e['P'] is None
    e = ae['estimate']
    assert e['availableSafetyNs'] == [61, 63] and e['missingSafetyTotal'] == 4
    assert e['categoryNameAsTable'] == 'Neurological'
    assert e['neurological_G1to2_counts'] == [38, 24] and e['neurological_G3to4_cells'] == [4, '-']
    assert e['constipation_G1to2_counts'] == [27, 11] and e['constipation_G3to4_cells'] == ['-', 1]
    assert e['skin_G1to2_counts'] == [17, 7] and e['skin_G3to4_cells'] == [3, '-']
    assert e['renal_G3to4_cells'] == [5, '-']
    assert (e['neurological_ordinalGradeP'], e['constipation_ordinalGradeP'], e['skin_ordinalGradeP'], e['renal_ordinalGradeP']) == (.0015, .0004, .0041, .026)
    assert not e['PvaluesAreGrade3Only']
    assert e['nonPDnonDeathWithdrawals'] == [18, 10] and e['intoleranceWithdrawals'] == [9, 5] and e['patientDecisionWithdrawals'] == [9, 4]
    assert not e['completeWithdrawalCausesReconciled'] and e['uniqueAEPatientsFromSummedCategories'] is None
    assert not e['soleThalidomideCausationEstablished']
    for r in c['results']:
        assert r['armOrder'] == ['REED-CAL-16-A', 'REED-CAL-16-B']
        assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:
            assert 1 <= loc['physicalPage'] <= 7 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C16-FATIGUE-P', 'C16-WITHDRAWAL', 'C16-SUBGROUP-MEDIAN', 'C16-SAFETY-MISSING', 'C16-CONDITIONAL-SURVIVAL', 'C16-OTHER-DATA'}
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
assert sha(reed / 'thalidomide-myeloma/pdfs/20418244-ludwig-2010.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
assert sha(reed / 'thalidomide-myeloma/index.csv') == read(B / 'READINESS.json')['indexSha256']
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

reject('maintenance128_not_induction289', lambda x: x['study'].update(maintenanceRandomizedN=289))
reject('IFN_control_not_no_treatment', lambda x: x['arms'][1].update(label='no_treatment'))
reject('actual75_not_target200_received', lambda x: x['arms'][0].update(thalidomideActualMedianMgDaily=200))
reject('maintenance_not_induction_time_origin', lambda x: x['study'].update(timeOrigin='induction_randomization'))
reject('PFS_benefit_not_OS_benefit', lambda x: x['results'][0]['estimate'].update(PFSBenefitIsOSBenefit=True))
reject('null_OS_not_equivalence', lambda x: x['results'][1]['estimate'].update(survivalEquivalenceEstablished=True))
reject('conditional_subset_not_all_randomized', lambda x: x['results'][2]['estimate'].update(displayedSubsetN=[64, 64]))
reject('postprogression_trend_not_proven_causal_harm', lambda x: x['results'][2]['estimate'].update(fullRandomizedCausalHarmEstablished=True))
reject('P056_not_significant_at05', lambda x: x['results'][2]['estimate'].update(statisticallySignificantAt05=True))
reject('safety_available_N_not_randomized64', lambda x: x['results'][4]['estimate'].update(availableSafetyNs=[64, 64]))
reject('ordinal_grade_P_not_grade3_only', lambda x: x['results'][4]['estimate'].update(PvaluesAreGrade3Only=True))
reject('literal_dash_not_silently_numeric_zero', lambda x: x['results'][4]['estimate'].update(neurological_G3to4_cells=[4, 0]))
reject('response_upgrade_not_de_novo_ORR', lambda x: x['results'][3]['estimate'].update(notDeNovoORR=False))
reject('one_IFN_withdrawal_cause_not_invented', lambda x: x['results'][4]['estimate'].update(completeWithdrawalCausesReconciled=True))
reject('nested_family_not_new_independent_trial', lambda x: x['study'].update(newIndependentTrialFamiliesFromInductionReport=1))
reject('source_discrepancies_retained', lambda x: x.update(sourceQualifications=x['sourceQualifications'][1:]))
result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedMaintenanceFindings': 5, 'claims': 5, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
