"""Check cohort denominators, comparison direction and limits on inference."""
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
    assert set(schema['required']) <= c.keys()
    assert c['schemaVersion'] == schema['schemaVersion']
    assert c['paper']['sourceType'] == 'primary_retrospective_cohort'
    assert c['inspection']['textualPagesRead'] == list(range(1, 9))
    assert not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance', 'humanApproval', 'released'])
    s = c['study']
    assert s['design'] == 'singlecenter_retrospective_cohort' and not s['randomized']
    assert s['patientN'] == 305 and s['clinicalPurpose'] == 'thromboprophylaxis_supportive_care'
    window = 'Firstdayofinductiontherapy through90daysaftercompletionofinduction'
    assert s['observationWindow'] == window
    assert s['policyYearConflict'] == [2017, 2018]
    assert s['adjustedORShown'] is None
    assert not s['causalProphylaxisEffectEstablished'] and not s['clinicalGuidanceAdopted']
    assert [g['n'] for g in c['cohorts']] == [124, 99, 82]
    assert all(g['frequency'] is None and g['doseFrequencyStatus'] == 'not_reported'
               and g['prescribedUseNotVerifiedAdherence'] for g in c['cohorts'])
    assert c['cohorts'][0]['reportedDoseMgCounts'] == {'81': 122, '325': 2}
    assert len(c['results']) == len(c['claims']) == 3
    for r in c['results']:
        assert not r['causalAttributionToProphylaxisAlone'] and not r['acceptedSupport']
        assert r['grade'] is None and r['benefitGrade'] is None
        assert r['estimate']['timeWindow'] == window
        for loc in r['sourceLocators']:
            assert 1 <= loc['physicalPage'] <= 8 and loc['sourceSha256'] == c['source']['sha256']
    r1, r2, r3 = c['results']
    assert [(g['events'], g['total'], g['reportedPercent']) for g in r1['cohortCounts']] == [(6, 124, 4.8), (16, 99, 16.1), (4, 82, 4.8)]
    assert r1['estimate']['globalThreeGroupP'] == .0067 and r1['estimate']['individualCohortP'] is None
    e = r2['estimate']
    assert e['kind'] == 'odds_ratio' and e['value'] == 3.76
    assert e['analysis'] == 'univariate' and e['adjustedEstimateShown'] is None
    assert e['reference'] == 'KRD+XA' and e['exposed'] == 'KRD+ASA' and not e['causalDrugEffect']
    u = r2['uncertainty']
    assert (u['CILevel'], u['lower'], u['upper'], u['pairwisePReportedInText'], u['globalTableRegimenP']) == (.95, 1.2, 11.73, .02, .0067)
    assert [g['minorReportedPatients'] for g in r3['cohortCounts']] == [1, 5, 1]
    e = r3['estimate']
    assert e['totalMinorEpisodesReported'] == 7 and e['majorEpisodesObserved'] == 0
    assert e['globalMinorBleedingP'] == .1 and not e['equivalentSafetyEstablished']
    assert not e['uniqueEpisodePatientMappingVerified']
    assert {q['id'] for q in c['sourceQualifications']} == {'C10-POLICY-YEAR', 'C10-ADJUSTMENT', 'C10-BLEEDING', 'C10-DOSE-FREQUENCY', 'C10-NULL-OR-DIRECTION'}
    assert [q['id'] for q in c['reviewInputs']] == ['Q' + str(i).zfill(2) for i in range(1, 16)]
    assert c['reviewInputs'][13]['downstreamMapping'] == read(B / 'DOWNSTREAM-MAPPING.json')
    for claim in c['claims']:
        assert not claim['acceptedSupport'] and set(claim['resultIds']) <= {r['id'] for r in c['results']}
    return True

c = read(B / 'SOURCE-CANDIDATE.json')
validate(c)
for f, h in read(B / 'AUDIT-MANIFEST.json')['files'].items():
    assert sha(B / f) == h
for f, h in read(B / 'READINESS.json')['hashes'].items():
    assert sha(B / f) == h
assert c['sourceQualifications'] == read(B / 'SOURCE-QUALIFICATIONS.json')
v1 = read(B / 'SOURCE-CANDIDATE-v1.json')
assert v1['results'] == c['results'] and v1['claims'] == c['claims']
reed = Path(os.environ.get('REMAPRX_REED_ROOT', '/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed / 'aspirin-myeloma/pdfs/34396516-piedra-2022.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
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

reject('retrospective_not_randomized', lambda x: x['study'].update(randomized=True))
reject('group_denominators_preserved', lambda x: x['cohorts'][2].update(n=99))
reject('OR_not_RR', lambda x: x['results'][1]['estimate'].update(kind='risk_ratio'))
reject('univariate_not_adjusted', lambda x: x['results'][1]['estimate'].update(analysis='adjusted'))
reject('comparison_reference_not_reversed', lambda x: x['results'][1]['estimate'].update(reference='KRD+ASA'))
reject('global_P_not_pairwise', lambda x: x['results'][0]['estimate'].update(individualCohortP=.0067))
reject('window_extends_after_induction_completion', lambda x: x['study'].update(observationWindow='90daysfromstart'))
reject('nonsignificant_bleeding_not_safety_equivalence', lambda x: x['results'][2]['estimate'].update(equivalentSafetyEstablished=True))
reject('dose_frequency_not_inferred_daily', lambda x: x['cohorts'][0].update(frequency='daily'))
reject('supportive_care_not_anticancer_efficacy', lambda x: x['study'].update(clinicalPurpose='anticancer_efficacy'))
reject('source_reference_direction_conflict_retained', lambda x: x.update(sourceQualifications=x['sourceQualifications'][:-1]))
reject('association_not_causal_prophylaxis_effect', lambda x: x['study'].update(causalProphylaxisEffectEstablished=True))
result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedCohortFindings': 3, 'claims': 3, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'v1v2ResultsClaimsUnchanged': True, 'sourceQualificationsResolved': False, 'independentAudit': 'see_exact_acceptance_update', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
