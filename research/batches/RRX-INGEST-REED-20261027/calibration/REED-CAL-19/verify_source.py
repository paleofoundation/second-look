"""Guard preclinical exposure, mixed endpoints, mechanistic limits and source conflicts."""
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
    assert c['paper']['sourceType'] == 'primary_preclinical_in_vitro_and_in_vivo'
    assert c['inspection']['textualPagesRead'] == list(range(1,11)) and not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
    s = c['study']
    assert s['humanParticipants'] == 0 and not s['randomizedClinicalTrial']
    assert s['animalModel'] == 'nondiabetic_C57BL/KaLwRij_5TGM1_GFP'
    assert s['drinkingWaterConcentrationMgPerMl'] == 2.5 and s['pretreatmentWeeks'] == 4
    assert s['drugStoppedBeforeTumorInoculation'] and not s['concurrentTumorTreatment']
    assert s['actualMgPerKgPerDay'] is None and not s['humanExposureEquivalenceMeasured']
    assert (s['inoculumMethods'],s['inoculumFigure3']) == (1500000,1000000) and not s['inoculumResolved']
    assert (s['sacrificeDaysPostInoculationMethods'],s['figureTimelineWeeksPostInoculationApproximate']) == (25,4)
    assert (s['mouseMyelomaControlN'],s['mousePretreatmentN'],s['mouseNonTumorControlN']) == (17,17,8)
    assert (s['Fig4AControlN'],s['Fig4AMetforminN']) == (5,6)
    for key in ['overlapAcrossFiguresAdjudicated','independentNewTrialsPerFigure','clinicalBenefitEstablished','clinicalHarmEstablished','currentRecommendationAdopted','pooledWithCAL17or18','inVivoOPNMediationProven','allSupplementaryFiguresRead']:
        assert not s[key]
    assert len(c['results']) == len(c['claims']) == 4
    r1,r2,r3,r4 = [r['estimate'] for r in c['results']]
    assert r1['ST2Adhesion'] == 'no_reported_effect' and r1['nonmonotonicAt10MM']
    assert r1['5TGM1AdhesionN'] == 5 and r1['MM1SDyeRepresentativeIndependentExperiments'] == 6 and r1['5TGM1DyeRepresentativeIndependentExperiments'] == 3
    assert r1['figure1FUntreated2T3_vsControl'] == '**P<0.01;notgeneralizednull'
    assert not r1['durableDormancyEstablished'] and r1['exactEffectCI'] is None and r1['SEMnotCI']
    assert r2['expressionNRange'] == [3,7] and r2['siRNAGeneN'] == 3 and r2['adhesionN'] == 4
    assert r2['starNotDirectInteractionP'] and not r2['exclusiveMediatorProven'] and not r2['inVivoMediatorProven']
    assert r3['BM_P_vsMyelomaControl'] == '<0.001' and r3['spleenP_vsMyelomaControl'] == '<0.01'
    assert r3['lesionP_vsMyelomaControl'] == '<0.05'
    assert r3['serumIgG2bP_vsMyelomaControl'] is None and r3['serumIgG2bP_vsNonTumor'] == '<0.001_both_tumor_groups'
    assert r3['clinicalRiskOrSurvivalEffect'] is None and r3['figureSubjectsNotIndependentNewReports']
    assert r4['nontumor4weekBM_OPN'] == 'no_reported_increase' and r4['tumorSerumOPN'] == 'no_reported_increase'
    assert r4['tumorBM_OPN'] == 'increased' and r4['tumorBM_P'] == '<0.05'
    assert not r4['myelomaDerivedOPNOrBurdenContributionExcluded'] and not r4['inVivoCausalMediationProven']
    for r in c['results']:
        assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:assert 1 <= loc['physicalPage'] <= 10 and loc['sourceSha256'] == c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']} == {'C19-INOCULUM','C19-TIMING','C19-PARAPROTEIN','C19-OPN-CELL-SOURCE','C19-MICROCT','C19-MODEL-EXPOSURE','C19-PROLIFERATION'}
    assert [l['physicalPage'] for l in next(q for q in c['sourceQualifications'] if q['id']=='C19-MICROCT')['locators']] == [2,4]
    assert [q['id'] for q in c['reviewInputs']] == ['Q'+str(i).zfill(2) for i in range(1,16)]
    assert c['reviewInputs'][13]['downstreamMapping'] == read(B/'DOWNSTREAM-MAPPING.json')
    for claim in c['claims']:assert not claim['acceptedSupport'] and set(claim['resultIds']) <= {r['id'] for r in c['results']}

c = read(B / 'SOURCE-CANDIDATE.json')
validate(c)
for f, h in read(B / 'AUDIT-MANIFEST.json')['files'].items():
    assert sha(B / f) == h
for f, h in read(B / 'READINESS.json')['hashes'].items():
    assert sha(B / f) == h
assert c['sourceQualifications'] == read(B / 'SOURCE-QUALIFICATIONS.json')
reed = Path(os.environ.get('REMAPRX_REED_ROOT', '/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed / 'metformin-myeloma/pdfs/34890968-gamez-2022.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
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

reject('mouse_not_human_population', lambda x: x['study'].update(humanParticipants=42))
reject('pretreatment_not_concurrent_tumor_therapy', lambda x: x['study'].update(concurrentTumorTreatment=True))
reject('water_concentration_not_mg_per_kg_daily_dose', lambda x: x['study'].update(actualMgPerKgPerDay=2.5))
reject('human_PK_relevance_not_measured', lambda x: x['study'].update(humanExposureEquivalenceMeasured=True))
reject('inoculum_conflict_not_silently_resolved', lambda x: x['study'].update(inoculumResolved=True))
reject('method_day25_not_figure_day28', lambda x: x['study'].update(sacrificeDaysPostInoculationMethods=28))
reject('ST2_not_same_adhesion_effect_as2T3', lambda x: x['results'][0]['estimate'].update(ST2Adhesion='increased'))
reject('proxy_not_proven_durable_dormancy', lambda x: x['results'][0]['estimate'].update(durableDormancyEstablished=True))
reject('OPN_siRNA_not_proven_sole_mediator', lambda x: x['results'][1]['estimate'].update(exclusiveMediatorProven=True))
reject('OPN_cell_perturbation_not_proved_in_vivo_mediation', lambda x: x['study'].update(inVivoOPNMediationProven=True))
reject('IgG2b_stars_not_between_tumor_groups', lambda x: x['results'][2]['estimate'].update(serumIgG2bP_vsMyelomaControl='<0.001'))
reject('compartment_null_serum_OPN_retained', lambda x: x['results'][3]['estimate'].update(tumorSerumOPN='increased'))
reject('tumor_derived_OPN_not_excluded', lambda x: x['results'][3]['estimate'].update(myelomaDerivedOPNOrBurdenContributionExcluded=True))
reject('no_clinical_harm_inference', lambda x: x['study'].update(clinicalHarmEstablished=True))
reject('no_CAL17_18_pool', lambda x: x['study'].update(pooledWithCAL17or18=True))
reject('no_supplement_read_claim', lambda x: x['study'].update(allSupplementaryFiguresRead=True))
reject('no_new_independent_trial_per_figure', lambda x: x['study'].update(independentNewTrialsPerFigure=True))
reject('microCT_second_specification_exact_page4', lambda x: next(q for q in x['sourceQualifications'] if q['id']=='C19-MICROCT')['locators'].pop())
reject('source_conflicts_preserved', lambda x: x.update(sourceQualifications=[]))

result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedPreclinicalFindings': 4, 'claims': 4, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
