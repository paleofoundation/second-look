"""Guard case-control referents, distinct duration estimates and source reporting ambiguities."""
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
    assert c['paper']['sourceType'] == 'primary_nested_matched_case_control_with_unmatched_subgroup'
    assert c['inspection']['textualPagesRead'] == list(range(1, 6))
    assert not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance', 'humanApproval', 'released'])
    s = c['study']
    assert s['design'] == 'nested_matched_case_control' and not s['randomized']
    assert (s['primaryCases'], s['primaryControlObservations']) == (124, 760)
    assert s['baselineMetforminDefinition'] == 'atleast2prescriptionsattimeofMGUSdiagnosis'
    assert s['primaryModel'] == 'conditional_logistic' and s['primaryReference'] == 'MGUS_without_diabetes'
    assert s['primaryAdjustment'] == ['obesity_literal_BMI>30mg/m2', 'ever_smoking']
    assert (s['diabetesSubgroupCases'], s['diabetesSubgroupControlObservations']) == (11, 127)
    assert not s['diabetesSubgroupMatched'] and s['diabetesSubgroupModel'] == 'unconditional_logistic'
    assert s['diabetesSubgroupReference'] == 'diabetic_MGUS_never_metformin'
    assert s['diabetesSubgroupFootnoteAdjustment'] == ['age', 'sex', 'obesity', 'smoking']
    for key in ['metforminDoseReported', 'causalPreventionEstablished', 'glycemicControlMechanismEstablished', 'safetyOutcomesReported', 'clinicalRecommendationAdopted', 'CAL17patientDataPooled', 'uniqueTotalPopulationRiskDenominatorEstablished']:
        assert not s[key]
    assert len(c['results']) == len(c['claims']) == 3
    primary, sensitivity, subgroup = [r['estimate'] for r in c['results']]
    assert primary['kind'] == 'conditional_logistic_odds_ratios' and primary['reference'] == 'MGUS_without_diabetes'
    assert primary['referenceCaseControlCounts'] == [113, 633]
    assert [r['caseControlCounts'] for r in primary['rows']] == [[6,38],[4,65],[1,24]]
    assert [r['adjustedOR'] for r in primary['rows']] == [.96,.39,.17]
    assert [r['adjustedCI95'] for r in primary['rows']] == [[.38,2.38],[.14,1.13],[.02,1.28]]
    assert primary['allAdjustedCIsInclude1'] and not primary['caseCountsArePopulationRisks'] and not primary['metforminSpecificCausalBenefitEstablished']
    assert sensitivity['kind'] == 'text_reported_sensitivity_odds_ratio'
    assert sensitivity['duration'] == 'strictly_more_than_2_years' and sensitivity['OR'] == .19 and sensitivity['CI95'] == [.04,.99]
    assert sensitivity['glucoseAdjustmentReported'] and sensitivity['notDiabetesOnlyTableB']
    assert sensitivity['exactCaseControlCells'] is None and sensitivity['analysisN'] is None
    assert not sensitivity['primaryAnalysisReplaced'] and not sensitivity['causalTwoYearThresholdEstablished']
    assert subgroup['kind'] == 'unconditional_logistic_odds_ratios' and not subgroup['matched']
    assert subgroup['reference'] == 'diabetic_MGUS_never_metformin' and subgroup['referenceCaseControlCounts'] == [7,62]
    assert [r['caseControlCounts'] for r in subgroup['rows']] == [[2,17],[2,48]]
    assert [r['duration'] for r in subgroup['rows']] == ['strictly_less_than_24_months','strictly_more_than_24_months']
    assert [r['adjustedOR'] for r in subgroup['rows']] == [1.01,.40]
    assert [r['adjustedCI95'] for r in subgroup['rows']] == [[.18,5.65],[.08,2.04]]
    assert not subgroup['glucoseListedInTableFootnote'] and not subgroup['exact24MonthAssignmentKnown'] and not subgroup['equivalenceEstablished']
    assert subgroup['bothAdjustedCIsInclude1']
    for e in [primary,sensitivity,subgroup]:assert e['P'] is None
    for r in c['results']:
        assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:
            assert 1 <= loc['physicalPage'] <= 5 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C18-REFERENTS','C18-DURATION-SENSITIVITY','C18-GLUCOSE','C18-BOUNDARY','C18-BMI-UNIT','C18-COUNT-UNIT'}
    assert [q['id'] for q in c['reviewInputs']] == ['Q' + str(i).zfill(2) for i in range(1,16)]
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
assert sha(reed / 'metformin-myeloma/pdfs/27701912-boursi-2017.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
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

reject('not_randomized', lambda x: x['study'].update(randomized=True))
reject('case_control_counts_not_population_risk', lambda x: x['study'].update(uniqueTotalPopulationRiskDenominatorEstablished=True))
reject('two_prescriptions_not_four_years', lambda x: x['study'].update(baselineMetforminDefinition='fouryears'))
reject('primary_conditional_model', lambda x: x['study'].update(primaryModel='cox_hazard'))
reject('primary_nondiabetic_reference', lambda x: x['study'].update(primaryReference='diabetic_never'))
reject('subgroup_unmatched', lambda x: x['study'].update(diabetesSubgroupMatched=True))
reject('subgroup_unconditional', lambda x: x['study'].update(diabetesSubgroupModel='conditional_logistic'))
reject('subgroup_diabetic_never_reference', lambda x: x['study'].update(diabetesSubgroupReference='MGUS_without_diabetes'))
reject('text_sensitivity_not_subgroup_point40', lambda x: x['results'][1]['estimate'].update(OR=.40))
reject('subgroup_not_text_sensitivity_point19', lambda x: x['results'][2]['estimate']['rows'][1].update(adjustedOR=.19))
reject('exact24_boundary_unknown', lambda x: x['results'][2]['estimate'].update(exact24MonthAssignmentKnown=True))
reject('glucose_not_listed_in_TableB_footnote', lambda x: x['results'][2]['estimate'].update(glucoseListedInTableFootnote=True))
reject('literal_BMI_unit_qualification_preserved', lambda x: x['study'].update(primaryAdjustment=['obesity_BMI>30kg/m2','ever_smoking']))
reject('nonsignificance_not_equivalence', lambda x: x['results'][2]['estimate'].update(equivalenceEstablished=True))
reject('no_causal_prevention', lambda x: x['study'].update(causalPreventionEstablished=True))
reject('no_safety_result', lambda x: x['study'].update(safetyOutcomesReported=True))
reject('no_CAL17_pool', lambda x: x['study'].update(CAL17patientDataPooled=True))
reject('reporting_qualifications_retained', lambda x: x.update(sourceQualifications=[]))

result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedObservationalFindings': 3, 'claims': 3, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
