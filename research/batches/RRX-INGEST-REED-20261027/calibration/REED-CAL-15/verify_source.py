"""Guard OPTIMUM primary hierarchy, analysis populations and safety limits."""
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
    assert c['paper']['sourceType'] == 'primary_randomized_openlabel_fourarm_phaseIII'
    assert c['inspection']['textualPagesRead'] == list(range(1, 9))
    assert not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance', 'humanApproval', 'released'])
    s = c['study']
    assert (s['randomizedITTn'], s['perProtocolN'], s['safetyN']) == (499, 465, 497)
    assert s['ITTArmNs'] == [126, 121, 122, 130] and s['safetyTableArmNs'] == [124, 122, 123, 128]
    assert s['primaryHierarchyFirstDoseMg'] == 400 and not s['primaryHierarchyPassed']
    assert not s['superiorityEstablishedITT'] and not s['equivalenceEstablished']
    assert s['subgroupFindingsExploratory'] and not s['subsequentTherapyCensoredBeforeProgression']
    assert not s['clinicalDoseRecommendationAdopted'] and not s['prophylaxisEffectRandomized']
    assert s['independentTrialCount'] == 1 and s['completedPlanned12Cycles'] == 121
    assert all(not a['safetyArmAssignmentReconciled'] for a in c['arms'])
    assert c['arms'][3]['reportedMedianAverageDoseMgPerScheduledDay'] == 256
    assert len(c['results']) == len(c['claims']) == 5
    ttp, pfs, response, os_result, ae = c['results']
    e = ttp['estimate']
    assert e['ITTmedianMonths'] == [6.1, 7.0, 7.6, 9.1]
    assert e['ITT_HRversusDEX'] == [None, .88, .86, .73]
    assert e['ITT_CI95versusDEX'] == [None, [.63, 1.21], [.63, 1.19], [.53, 1.00]]
    assert e['ITT_PversusDEX'] == [None, .421, .363, .055]
    assert not e['ITTPrimarySuperiorityEstablished'] and e['orderedTestingStoppedAfter400']
    assert e['PP400vsDEX_P'] == .049 and e['PPnotPrimaryITT'] and e['PPsampleN'] == 465
    e = pfs['estimate']
    assert e['ITTmedianMonths'] == [6.0, 6.7, 7.3, 8.1]
    assert (e['ITT400vsDEX_HR'], e['ITT400vsDEX_CI95'], e['ITT400vsDEX_P']) == (.74, [.55, 1.00], .051)
    assert not e['ITT400SignificantAt05'] and not e['equivalenceEstablished']
    assert (e['PP400vsDEX_HR'], e['PP400vsDEX_P'], e['PP400CI95']) == (.72, .039, None)
    e = response['estimate']
    assert e['ITTdenominators'] == [126, 121, 122, 130] and e['ORR_CRplusPR_percent'] == [25, 21, 18, 21]
    assert e['exactResponseCounts'] is None and e['responseConfirmationWeeks'] == 8
    assert e['DORmedianMonths'] == [6.5, 12.7, 13.1, 11.6]
    assert e['DOR_CI95versusDEX'][1] == [.18, 1.02] and e['DOR_PversusDEX'][1] == .046
    assert e['confirmedResponseThenProgressionOrDeathCountsAsReported'] == [27, 13, 11, 17]
    assert not e['DORunconditionalAllRandomizedBenefitEstablished'] and not e['DORcensoringReconciledIndependently']
    e = os_result['estimate']
    assert e['medianMonths'] == [None, 30.0, 25.6, None]
    assert e['medianStatus'] == ['not_reached', 'reported', 'reported', 'not_reached']
    assert e['PversusDEX'] == [None, .521, .904, .457] and e['reportedCensoringPercentRange'] == [65, 75]
    assert not e['survivalBenefitEstablished'] and not e['survivalEquivalenceEstablished'] and not e['notReachedIsInfinity']
    e = ae['estimate']
    assert e['tableSafetyNLabels'] == [124, 122, 123, 128] and not e['NLabelAssignmentReconciled']
    assert e['grade3to4AEpercent'] == [38, 32, 38, 60] and e['pooledTHAL_grade3to4AEpercent'] == 44
    assert e['AEdiscontinuationPercent'] == [17, 12, 15, 18] and e['AEdiscontinuationCountCONSORT'] == 50
    assert not e['flowAndSafetyWithdrawalReconciled']
    assert e['Table5THALclinicalNeuropathyPercent'] == [34, 36, 41] and e['bodyTHALclinicalNeuropathyPercent'] == [34, 35, 41]
    assert e['Table5THALsensoryNeuropathyGrade2plusPercent'] == [12, 20, 22]
    assert not e['equalVTEPercentProvesSafetyEquivalence'] and not e['prophylaxisEffectEstablished']
    for r in c['results']:
        assert r['armOrder'] == ['DEX', 'THAL100', 'THAL200', 'THAL400']
        assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:
            assert 1 <= loc['physicalPage'] <= 8 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C15-SAFETY-NS', 'C15-HIERARCHY', 'C15-DOR', 'C15-NEUROPATHY', 'C15-DOSE-STAT', 'C15-FLOW', 'C15-SUBSEQUENT-THERAPY'}
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
assert sha(reed / 'thalidomide-myeloma/pdfs/22133776-kropff-2012.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
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

reject('ITT499_not_PP465', lambda x: x['study'].update(randomizedITTn=465))
reject('primary_P055_not_superiority', lambda x: x['study'].update(superiorityEstablishedITT=True))
reject('failed_first_test_not_passed_lower_dose_hierarchy', lambda x: x['study'].update(primaryHierarchyPassed=True))
reject('PP049_not_primary_ITT_result', lambda x: x['results'][0]['estimate'].update(PPnotPrimaryITT=False))
reject('nonsuperiority_not_equivalence', lambda x: x['study'].update(equivalenceEstablished=True))
reject('exploratory_subgroups_not_confirmatory', lambda x: x['study'].update(subgroupFindingsExploratory=False))
reject('PFS051_not_significant_at05', lambda x: x['results'][1]['estimate'].update(ITT400SignificantAt05=True))
reject('DOR_selected_censoring_not_unconditional_benefit', lambda x: x['results'][2]['estimate'].update(DORunconditionalAllRandomizedBenefitEstablished=True))
reject('not_reached_OS_not_infinity', lambda x: x['results'][3]['estimate'].update(notReachedIsInfinity=True))
reject('safety_labels_not_silently_reassigned', lambda x: x['results'][4]['estimate'].update(NLabelAssignmentReconciled=True))
reject('assigned400_not_actual400', lambda x: x['arms'][3].update(reportedMedianAverageDoseMgPerScheduledDay=400))
reject('body_table_neuropathy_difference_preserved', lambda x: x['results'][4]['estimate'].update(Table5THALclinicalNeuropathyPercent=[34, 35, 41]))
reject('subsequent_therapy_rule_not_borrowed_CAL14', lambda x: x['study'].update(subsequentTherapyCensoredBeforeProgression=True))
reject('equal_VTE_percentage_not_safety_equivalence', lambda x: x['results'][4]['estimate'].update(equalVTEPercentProvesSafetyEquivalence=True))
reject('source_400mg_recommendation_not_adopted', lambda x: x['study'].update(clinicalDoseRecommendationAdopted=True))
result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedRandomizedFindings': 5, 'claims': 5, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
