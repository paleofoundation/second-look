"""Check actual sample, stopping rule, treatment/time origins and safety bounds."""
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
    assert c['paper']['sourceType'] == 'primary_single_arm_phase_II_letter'
    assert c['inspection']['textualPagesRead'] == [1, 2]
    assert not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance', 'humanApproval', 'released'])
    s = c['study']
    assert s['design'] == 'prospective_single_arm_phase_II_Fleming_two_stage'
    assert not s['randomized'] and s['concurrentControlN'] == 0
    assert (s['actualPatientN'], s['plannedMaximumN'], s['plannedInterimN'], s['priorVADResistantN']) == (12, 40, 12, 7)
    assert not s['simvastatinAloneEffectIsolated'] and not s['therapeuticEquivalenceEstablished']
    assert not s['currentPatientPKMeasured']
    dose = s['simvastatin']
    assert (dose['dose'], dose['unit'], dose['route'], dose['cycleDays'], dose['cycleLengthDays'], dose['dailyDividedDoses']) == (15, 'mg/kg/day', 'oral', [1, 7], 28, 2)
    stop = s['stoppingRule']
    assert (stop['CRplusPRRateBelow'], stop['nonhematologicWHOGrade3to4RateAbove'], stop['stopIfResponsesAtInterimLessThan'], stop['interimN']) == (.10, .30, 2, 12)
    assert stop['actualAccrualStopped']
    assert len(c['results']) == len(c['claims']) == 2
    response, safety = c['results']
    e = response['estimate']
    assert (e['treatedN'], e['PR'], e['SD'], e['PD']) == (12, 1, 6, 5)
    assert e['prespecifiedContinueThresholdResponses'] == 2 and e['accrualStopped']
    assert e['SDPriorProgressionN'] == 5 and e['SDTotalN'] == 6
    assert e['SDDurationDaysMedian'] == 103 and e['SDDurationDaysRange'] == [94, 258]
    assert e['PRPatientRelapseDaysFromTreatmentStart'] == 230 and e['PRDurationOfResponseDays'] is None
    assert e['cohortPFS'] is None and e['cohortOS'] is None and e['CI'] is None and e['P'] is None
    e = safety['estimate']
    assert (e['treatedN'], e['WHOGrade3to4NeutropeniaPatients'], e['WHOGrade3to4ThrombocytopeniaPatients'], e['grade3GIToxicityWithDehydrationPatients']) == (12, 8, 2, 1)
    assert e['neutropenicFeverReported'] == 0 and e['rhabdomyolysisReported'] == 0
    assert not e['overlapBetweenToxicityCategoriesKnown'] and e['totalUniqueSevereAEPatients'] is None
    assert not e['soleSimvastatinCausationEstablished'] and not e['zeroFutureRiskEstablished']
    for result in c['results']:
        assert result['comparator'] is None and not result['simvastatinAloneEffect']
        assert result['grade'] is None and result['benefitGrade'] is None and not result['acceptedSupport']
        for loc in result['sourceLocators']:
            assert loc['physicalPage'] == 1 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C12-SAFETY-WORDING', 'C12-SCHEDULE', 'C12-TIME', 'C12-PRIOR-STUDY'}
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
assert sha(reed / 'simvastatin-myeloma/pdfs/18055977-van-2007.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
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

reject('actual12_not_planned40', lambda x: x['study'].update(actualPatientN=40))
reject('seven_not_twelve_prior_VAD_resistant', lambda x: x['study'].update(priorVADResistantN=12))
reject('single_arm_not_randomized', lambda x: x['study'].update(randomized=True))
reject('regimen_not_simvastatin_alone', lambda x: x['study'].update(simvastatinAloneEffectIsolated=True))
reject('threshold_two_not_ten_percent_rounding', lambda x: x['study']['stoppingRule'].update(stopIfResponsesAtInterimLessThan=1))
reject('null_pilot_not_equivalence', lambda x: x['study'].update(therapeuticEquivalenceEstablished=True))
reject('230_days_from_start_not_response_duration', lambda x: x['results'][0]['estimate'].update(PRDurationOfResponseDays=230))
reject('severe_neutropenia_not_erased_by_abstract', lambda x: x['results'][1]['estimate'].update(WHOGrade3to4NeutropeniaPatients=0))
reject('overlapping_toxicities_not_unique_sum', lambda x: x['results'][1]['estimate'].update(totalUniqueSevereAEPatients=11))
reject('no_reported_rhabdomyolysis_not_future_zero_risk', lambda x: x['results'][1]['estimate'].update(zeroFutureRiskEstablished=True))
reject('prior_PK_not_measured_current_patient_PK', lambda x: x['study'].update(currentPatientPKMeasured=True))
result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedClinicalFindings': 2, 'claims': 2, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
