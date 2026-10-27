"""Guard nonMM CONTEXT, assay normalization and mechanistic/source limits."""
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
    schema = read(B/'SCHEMA.json')
    assert set(schema['required']) <= c.keys() and c['schemaVersion'] == schema['schemaVersion']
    assert c['paper']['sourceType'] == 'primary_preclinical_nonMM_CONTEXT'
    assert c['inspection']['textualPagesRead'] == list(range(1,11)) and not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
    s=c['study']
    assert s['evidenceTierForMyeloma'] == 'CONTEXT'
    assert s['actualCellLines'] == {'Jeko1':'mantle_cell_lymphoma','H1299':'non_small_cell_lung_cancer'}
    assert s['myelomaCellLinesTested'] == s['humanParticipants'] == s['animalExperimentsCurrentReport'] == 0
    assert (s['metforminMM'],s['metforminTotalHours']) == (10,72)
    assert (s['captionJekoPretreatmentHours'],s['captionJekoBTZHours']) == (48,24)
    assert (s['captionH1299PretreatmentHours'],s['captionH1299BTZHours'],s['bodyBothPretreatmentHours']) == (24,48,48)
    assert s['MTTNormalization'] == 'own_zero_nM_bortezomib_for_each_cell_line_and_metformin_group'
    for k in ['MTTAbsoluteViableCellCount','clinicalDrugInteractionEstablished','clinicalSafetyEstablished','currentRecommendationAdopted','directMyelomaOutcomeSupport','measuredPatientPK','allSupplementaryInputsRead','causalAssemblyFactorRescuePerformed','currentTranscriptExperimentReported']:assert not s[k]
    assert s['pooledIndependentN'] is None
    assert len(c['results']) == len(c['claims']) == 3
    a,b,d = [r['estimate'] for r in c['results']]
    assert a['proliferationIndependentExperimentsPerLine'] == a['flowIndependentExperiments'] == 3
    assert a['MTTReplicateN'] is None and not a['absoluteCellSurvivalEstablished'] and not a['myelomaCellResult']
    assert a['flowBTZnM'] == [20,75] and not a['necrosisDifferenceSignificant']
    assert b['H1299_30S_quantity_P'] == .0744 and not b['allComplexChangesSignificant']
    assert not b['quantityPTransferredToActivity'] and not b['directDrugBindingEstablished'] and b['replicateN'] is None
    assert b['JekoComplexQuantity']['20S'] == 'increased_P<0.01'
    assert d['JekoS5b'] == 'increased_P<0.05' and d['H1299P28'] == 'decreased_P<0.01'
    assert d['JekoRpn6'] == d['H1299Rpn6'] == 'not_changed'
    assert not d['currentTranscriptMeasurement'] and not d['S5bP28IsolatedCausalRescue'] and not d['mTOROnlyMediatorProven']
    for r in c['results']:
        assert r['evidenceTierForMyeloma'] == 'CONTEXT' and r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:assert 1 <= loc['physicalPage'] <= 10 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C20-MODEL','C20-PRETREATMENT','C20-H1299-SURVIVAL','C20-H1299-30S','C20-PROLIFERATION-TIME','C20-N-AND-ASSAY','C20-MECHANISM'}
    assert [q['id'] for q in c['reviewInputs']] == ['Q'+str(i).zfill(2) for i in range(1,16)]
    m=c['reviewInputs'][13]['downstreamMapping'];assert m == read(B/'DOWNSTREAM-MAPPING.json')
    assert m['existingGuideId'] is None and m['contextTier'] == 'CONTEXT' and m['directConditionSupportDisposition'] == 'rejected_model_mismatch_Jeko1_MCL_H1299_NSCLC_not_MM'
    for claim in c['claims']:assert not claim['acceptedSupport'] and set(claim['resultIds']) <= {r['id'] for r in c['results']}

c = read(B / 'SOURCE-CANDIDATE.json')
validate(c)
for f, h in read(B / 'AUDIT-MANIFEST.json')['files'].items():
    assert sha(B / f) == h
for f, h in read(B / 'READINESS.json')['hashes'].items():
    assert sha(B / f) == h
assert c['sourceQualifications'] == read(B / 'SOURCE-QUALIFICATIONS.json')
reed = Path(os.environ.get('REMAPRX_REED_ROOT', '/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed / 'metformin-myeloma/pdfs/35740881-schlesser-2022.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
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

reject('actual_nonMM_models', lambda x: x['study'].update(myelomaCellLinesTested=2))
reject('no_patients', lambda x: x['study'].update(humanParticipants=6))
reject('CONTEXT_not_direct_condition_primary', lambda x: x['study'].update(evidenceTierForMyeloma='PRIMARY'))
reject('H1299_caption_leadin_not_uniform48hours', lambda x: x['study'].update(captionH1299PretreatmentHours=48))
reject('MTT_own_baseline_not_absolute_survival', lambda x: x['study'].update(MTTAbsoluteViableCellCount=True))
reject('MTT_unknown_N_not_assumed3', lambda x: x['results'][0]['estimate'].update(MTTReplicateN=3))
reject('flow20_and75nM_line_specific', lambda x: x['results'][0]['estimate'].update(flowBTZnM=[20,20]))
reject('H1299_30S_P0744_not_significant', lambda x: x['results'][1]['estimate'].update(allComplexChangesSignificant=True))
reject('quantity_P_not_activity_P', lambda x: x['results'][1]['estimate'].update(quantityPTransferredToActivity=True))
reject('Rpn6_null_retained', lambda x: x['results'][2]['estimate'].update(H1299Rpn6='decreased'))
reject('protein_not_current_transcript_result', lambda x: x['study'].update(currentTranscriptExperimentReported=True))
reject('no_assembly_factor_causal_rescue', lambda x: x['study'].update(causalAssemblyFactorRescuePerformed=True))
reject('no_measured_patient_PK', lambda x: x['study'].update(measuredPatientPK=True))
reject('no_clinical_interaction_inference', lambda x: x['study'].update(clinicalDrugInteractionEstablished=True))
reject('no_MM_outcome_support', lambda x: x['study'].update(directMyelomaOutcomeSupport=True))
reject('no_supplement_read_claim', lambda x: x['study'].update(allSupplementaryInputsRead=True))
reject('source_conflicts_retained', lambda x: x.update(sourceQualifications=[]))

result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedPrimaryContextFindings': 3, 'claims': 3, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
