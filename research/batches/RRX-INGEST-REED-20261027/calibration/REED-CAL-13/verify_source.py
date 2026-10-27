"""Guard variable paired samples, biomarker scope and clinical attribution."""
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
    assert c['paper']['sourceType'] == 'primary_single_arm_phaseII_marker_study'
    assert c['inspection']['textualPagesRead'] == [1, 2, 3, 4, 5, 6]
    assert not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance', 'humanApproval', 'released'])
    s = c['study']
    assert s['design'] == 'phase_II_single_arm_serial_within_patient' and not s['randomized']
    assert s['enrolledN'] == 6
    assert s['fullDoseTwoCycleCompleters'] == [2, 4]
    assert s['halfDoseSecondCycleCompleters'] == [5, 6] and s['earlyPneumoniaDeaths'] == [1, 3]
    d = s['dose']
    assert (d['value'], d['unit'], d['dailyDividedDoses'], d['daysOnPerCycle'], d['restDays'], d['plannedCycles']) == (15, 'mg/kg/day', 2, 7, 21, 2)
    assert s['priorTreatmentCounts'] == [6, 2, 3, 5, 7, 4]
    assert s['currentZoledronicAcidPatients'] == [2, 5] and s['bortezomibDuringProtocolPatient'] == 1
    assert not s['boneMarkerChangeIsFractureOutcome'] and not s['pureSimvastatinMonotherapy']
    assert not s['currentClinicalSafetyRecommendation'] and not s['patientPKMeasured']
    assert len(c['results']) == len(c['claims']) == 3
    marker, disease, safety = c['results']
    e = marker['estimate']
    assert e['unit'] == 'percent_of_own_day1'
    assert e['TRACPFirstCycleDisplayedPatients'] == [1, 2, 3, 4, 5, 6]
    assert e['TRACPSecondCycleDisplayedPatients'] == [2, 4, 5, 6]
    assert e['NTXOsteocalcinDisplayedPatients'] == [2, 4, 5, 6]
    assert e['NTX'] == 'transient pattern, authorsreported significance onlyfirstcycle'
    assert e['numericEffect'] is None and e['CI'] is None and e['exactP'] is None
    assert e['figurePThreshold'] == .05
    assert not e['clinicalFracturesMeasured'] and not e['causalHarmEstablished'] and not e['therapeuticEquivalenceEstablished']
    e = disease['estimate']
    assert e['fourSurvivingCompleters'] == {'noChangeReported': 2, 'progressionSignsReported': 2}
    assert e['sixPatientResponseRate'] is None and not e['currentSimvastatinPRFromLaterTherapy']
    assert e['subsequentBortezomibPRPatientsContextOnly'] == [2, 5]
    assert e['cohortPFS'] is None and e['cohortOS'] is None
    e = safety['estimate']
    assert (e['enrolledN'], e['GIPatients'], e['muscularSymptomsPatients'], e['secondCycleHalfDosePatients'], e['earlyPneumoniaDeaths']) == (6, 6, 5, 2, 2)
    assert e['GIGrade'] == [1, 2] and e['muscularGrade'] == [1, 2]
    assert not e['soleSimvastatinCauseOfDeathsEstablished'] and e['populationFatalityRisk'] is None
    assert e['uniqueTotalAEPatientsFromSummingCategories'] is None
    for result in c['results']:
        assert result['grade'] is None and result['benefitGrade'] is None and not result['acceptedSupport']
        for loc in result['sourceLocators']:
            assert 1 <= loc['physicalPage'] <= 6 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C13-DEATH-TIME', 'C13-IG-TYPE', 'C13-CHOLESTEROL', 'C13-PRIOR-TREATMENT', 'C13-FLOW-AND-MARKERS', 'C13-COINTERVENTIONS'}
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
assert sha(reed / 'simvastatin-myeloma/pdfs/18668701-sondergaard-2009.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
assert sha(reed / 'simvastatin-myeloma/index.csv') == read(B / 'READINESS.json')['indexSha256']
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

reject('six_enrolled_not_six_full_dose_completers', lambda x: x['study'].update(fullDoseTwoCycleCompleters=[1, 2, 3, 4, 5, 6]))
reject('second_cycle_marker_N_excludes_early_deaths', lambda x: x['results'][0]['estimate'].update(TRACPSecondCycleDisplayedPatients=[1, 2, 3, 4, 5, 6]))
reject('NTX_significance_not_both_cycles', lambda x: x['results'][0]['estimate'].update(NTX='significant both cycles'))
reject('markers_not_fractures', lambda x: x['study'].update(boneMarkerChangeIsFractureOutcome=True))
reject('marker_pattern_not_proven_clinical_harm', lambda x: x['results'][0]['estimate'].update(causalHarmEstablished=True))
reject('curves_not_digitized_exact_effect', lambda x: x['results'][0]['estimate'].update(numericEffect=50))
reject('cointerventions_not_pure_monotherapy', lambda x: x['study'].update(pureSimvastatinMonotherapy=True))
reject('later_bortezomib_PR_not_simvastatin_response', lambda x: x['results'][1]['estimate'].update(currentSimvastatinPRFromLaterTherapy=True))
reject('no_zero_of_six_ORR_from_incomplete_flow', lambda x: x['results'][1]['estimate'].update(sixPatientResponseRate=0))
reject('early_deaths_not_established_sole_drug_cause', lambda x: x['results'][2]['estimate'].update(soleSimvastatinCauseOfDeathsEstablished=True))
reject('case_deaths_not_population_fatality_risk', lambda x: x['results'][2]['estimate'].update(populationFatalityRisk=2/6))
reject('source_conflicts_retained', lambda x: x.update(sourceQualifications=x['sourceQualifications'][1:]))
result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedClinicalMarkerFindings': 3, 'claims': 3, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
