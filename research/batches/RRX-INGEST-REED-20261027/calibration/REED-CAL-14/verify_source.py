"""Guard randomized versus safety populations, endpoint and harm distinctions."""
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
    assert c['paper']['sourceType'] == 'primary_randomized_doubleblind_phaseIII'
    assert c['inspection']['textualPagesRead'] == list(range(1, 17))
    assert not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance', 'humanApproval', 'released'])
    s = c['study']
    assert (s['randomizedN'], s['randomizedPerArm'], s['treatedSafetyN'], s['pretreatmentDiscontinuedN']) == (470, 235, [234, 232], 4)
    assert s['primaryEndpoint'] == 'TTP' and s['ITTAsReported'] and s['nonprotocolTherapyCensoring']
    assert s['DMCInterimUnblinding'] and s['finalResponseCommitteeBlinded']
    assert not s['thromboprophylaxisMandated'] and not s['aspirinEffectRandomized']
    assert s['aspirinUseRecordedPercent'] == [34, 29]
    assert not s['overallSurvivalBenefitEstablished'] and not s['clinicalRecommendationAdopted']
    assert s['independentTrialCount'] == 1 and not s['registryCurrentlyVerified']
    assert [a['randomizedN'] for a in c['arms']] == [235, 235]
    assert [a['treatedSafetyN'] for a in c['arms']] == [234, 232]
    assert len(c['results']) == len(c['claims']) == 5
    response, ttp, pfs, ae, vte = c['results']
    e = response['estimate']
    assert e['denominators'] == [235, 235] and e['ORR_CRplusPR_percent'] == [63, 46]
    assert e['CR_percent'] == [7.7, 2.6] and e['CRplusVGPR_IMWG_percent'] == [43.8, 15.8]
    assert e['ORR_exactCounts'] is None and not e['sixMonthOrFourCycleRateAssumed']
    assert e['P'] == {'ORR': '<0.001', 'CR': '0.02', 'CRplusVGPR': '<0.001', 'PR': None}
    e = ttp['estimate']
    assert e['HR'] == .43 and e['CI95'] == [.32, .58] and e['medianMonths'] == [22.6, 6.5]
    assert e['endpointDefinition'] == 'randomassignmenttodiseaseprogression'
    assert not e['deathIncludedInEndpointDefinition'] and not e['medianDifferenceIsOSGain']
    e = pfs['estimate']
    assert e['HR'] == .50 and e['CI95'] == [.38, .64] and e['medianMonths'] == [14.9, 6.5]
    assert e['endpointDefinition'] == 'randomassignmenttoprogressionordeathanycause'
    assert e['deathIncludedInEndpointDefinition'] and not e['medianDifferenceIsOSGain']
    for r in [ttp, pfs]:
        assert r['estimate']['kind'] == 'hazard_ratio' and r['estimate']['P'] == '<0.001'
        assert r['estimate']['nonprotocolTherapyCensored']
    e = ae['estimate']
    assert e['denominators'] == [234, 232] and e['grade3orHigherPercent'] == [79.5, 64.2]
    assert e['grade4Percent'] == [30.3, 22.8] and e['grade4P'] is None
    assert e['exactCountsFromRoundedPercentages'] is None and e['categoriesCanOverlap']
    e = vte['estimate']
    assert e['safetyDenominators'] == [234, 232] and e['allGradeDVTReportedPercent'] == [18.8, 5.6]
    assert e['grade3to4DVTcounts'] == [27, 4] and e['grade3to4PEcounts'] == [16, 4]
    assert e['first4CycleDVTpercent'] == [15.0, 3.9] and e['fatalDVT_PEFirst4CycleCounts'] == [4, 0]
    assert e['DVT_PE_uniqueCombinedPatients'] is None and not e['aspirinProphylaxisEffectEstablished']
    assert not c['overallSurvivalContext']['benefitEstablished']
    assert not c['overallSurvivalContext']['equivalentMortalityEstablished']
    assert c['overallSurvivalContext']['medianOS'] is None
    for result in c['results']:
        assert result['grade'] is None and result['benefitGrade'] is None and not result['acceptedSupport']
        assert result['armOrder'] == ['REED-CAL-14-A', 'REED-CAL-14-B']
        for loc in result['sourceLocators']:
            assert 1 <= loc['physicalPage'] <= 16 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C14-FLOW', 'C14-CENSORING', 'C14-OS', 'C14-DVT-HISTORY', 'C14-NEUROPATHY', 'C14-SUPPLEMENT'}
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
assert sha(reed / 'thalidomide-myeloma/pdfs/18362366-rajkumar-2008.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
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

reject('response_ITT_N_not_safety_N', lambda x: x['results'][0]['estimate'].update(denominators=[234, 232]))
reject('rounded_percent_not_invented_response_counts', lambda x: x['results'][0]['estimate'].update(ORR_exactCounts=[148, 108]))
reject('no_borrowed_ECOG_four_month_window', lambda x: x['results'][0]['estimate'].update(sixMonthOrFourCycleRateAssumed=True))
reject('TTP_not_PFS_death_endpoint', lambda x: x['results'][1]['estimate'].update(deathIncludedInEndpointDefinition=True))
reject('PFS_includes_death', lambda x: x['results'][2]['estimate'].update(deathIncludedInEndpointDefinition=False))
reject('progression_median_difference_not_OS_gain', lambda x: x['results'][1]['estimate'].update(medianDifferenceIsOSGain=True))
reject('nonprotocol_censoring_not_erased_by_ITT_label', lambda x: x['study'].update(nonprotocolTherapyCensoring=False))
reject('safety_N_not_randomized_N', lambda x: x['results'][3]['estimate'].update(denominators=[235, 235]))
reject('grade3_4_DVT_not_all_grade_count', lambda x: x['results'][4]['estimate'].update(grade3to4DVTcounts=[44, 13]))
reject('DVT_PE_not_summed_as_unique_patients', lambda x: x['results'][4]['estimate'].update(DVT_PE_uniqueCombinedPatients=[43, 8]))
reject('aspirin_observation_not_randomized_prophylaxis_effect', lambda x: x['results'][4]['estimate'].update(aspirinProphylaxisEffectEstablished=True))
reject('immature_unpowered_OS_not_benefit', lambda x: x['study'].update(overallSurvivalBenefitEstablished=True))
reject('source_flow_qualifications_not_silently_repaired', lambda x: x.update(sourceQualifications=x['sourceQualifications'][1:]))
result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedRandomizedFindings': 5, 'claims': 5, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
