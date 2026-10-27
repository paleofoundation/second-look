"""Guard diet/radiation contrast, growth endpoint, null interpretation and exposure limits."""
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
    schema=read(B/'SCHEMA.json');assert set(schema['required']) <= c.keys() and c['schemaVersion']==schema['schemaVersion']
    assert c['paper']['sourceType']=='primary_preclinical_diet_radiation_and_culture'
    assert c['paper']['id']=='P-D10-EMT6-DIET-2012' and c['paper']['existingSourceId']=='A-F02-R1176-F01' and c['paper']['doi'] is None
    assert c['inspection']['textualPagesRead']==list(range(1,8)) and not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
    s=c['study'];assert s['mouseStrain']=='BALB/cRw' and s['mouseSex']=='female' and s['mouseAgeMonths']==[2.5,3]
    assert s['initialMicePerArm']==8 and s['arms']==4 and not s['finalCompleteNAllArmsEstablished']
    assert s['allocation']=='mice_randomized_diet_then_cages_randomized_radiation' and not s['clusterAdjustmentReported']
    assert s['dietFenbendazolePPM']==150 and s['dietLeadInDays']==7 and s['dietAdLib']
    assert s['bodyDoseMgPerKgPerDay'] is None and s['ownMeasuredTissueConcentration'] is None
    assert s['localRadiationGy']==10 and s['radiationDayAfterInoculation']==14 and s['euthanasiaTumorMm3']==1000
    for k in ['formalRadiationInteractionTest','clinicalEfficacyEstablished','formalEquivalenceEstablished','universalSafetyEstablished','currentRecommendationAdopted','pooledWithDuan2013orGao2008']:assert not s[k]
    prior=s['priorIdentity'];assert prior==read(B/'PRIOR-RECONCILIATION.json')
    assert not prior['sameBytesAsPriorAsset'] and not prior['priorAcceptanceTransferred'] and prior['canonicalChanges']==0
    assert len(c['results'])==len(c['claims'])==4
    a,b,d,e=[r['estimate'] for r in c['results']]
    assert a['kind']=='time_to_four_times_treatment_volume_days'
    assert a['meansDays']==[12.7,12.1,17.5,20.4] and a['SEMDays']==[.8,.6,1.3,.9]
    assert (a['dietNoRT_P'],a['dietWithinRT_P'])==(.32,.12) and a['radiationVsUnirradiatedP']=='<0.05'
    assert a['treatmentVolumeEndpointNotEuthanasia1000'] and not a['formalInteractionTest'] and not a['equivalenceEstablished'] and a['survivalBenefit'] is None
    assert b['meanLungCounts']==[29.7,29.7,28.6,24.3] and b['SEMLungCounts']==[7.2,4.3,3.9,9.1]
    assert b['allPairwiseDifferencesP']=='>0.05' and b['lungMetastasisObserverBlinded']
    assert not b['metastasisAbsentEverySite'] and not b['equivalenceEstablished']
    assert d['relativeWeightBetweenGroupsP']=='>0.05' and d['irradiatedAnimalsObservedLongerAndLostWeight'] and not d['universalSafetyEstablished']
    assert e['lowMicroM']==[.11,.33] and e['highMicroM']==[1,3]
    assert e['experimentsReported']==2 and e['measurementsPerPoint']==[2,4]
    assert e['cellCountNotApoptosisOrClonogenicSurvival'] and not e['highCultureDoseBenefitTransferredToDiet'] and not e['measuredTissuePK']
    for r in c['results']:
        assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:assert 1 <= loc['physicalPage'] <= 7 and loc['sourceSha256']==c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']}=={'C23-N-UNIT','C23-ENDPOINT','C23-RADIATION','C23-EXPOSURE','C23-DIET','C23-CULTURE','C23-HOST-SAFETY'}
    assert [q['id'] for q in c['reviewInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)]
    assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
    for claim in c['claims']:assert not claim['acceptedSupport'] and set(claim['resultIds']) <= {r['id'] for r in c['results']}

c = read(B / 'SOURCE-CANDIDATE.json')
validate(c)
for f, h in read(B / 'AUDIT-MANIFEST.json')['files'].items():
    assert sha(B / f) == h
for f, h in read(B / 'READINESS.json')['hashes'].items():
    assert sha(B / f) == h
assert c['sourceQualifications'] == read(B / 'SOURCE-QUALIFICATIONS.json')
reed = Path(os.environ.get('REMAPRX_REED_ROOT', '/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed / 'fenbendazole-cancer/pdfs/22776123-duanq-2012.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
assert sha(reed / 'fenbendazole-cancer/index.csv') == read(B / 'READINESS.json')['indexSha256']
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

reject('initial_N_not_complete_final_N', lambda x:x['study'].update(finalCompleteNAllArmsEstablished=True))
reject('cage_radiation_allocation_preserved', lambda x:x['study'].update(allocation='individual_mice_all_randomized'))
reject('150ppm_not_mg_per_kg_bodydose', lambda x:x['study'].update(bodyDoseMgPerKgPerDay=150))
reject('predicted_tissue_not_measured_PK', lambda x:x['study'].update(ownMeasuredTissueConcentration=.1))
reject('table_4x_not_euthanasia1000', lambda x:x['results'][0]['estimate'].update(kind='time_to1000mm3'))
reject('FBZ_P32_not_radiation_P05', lambda x:x['results'][0]['estimate'].update(dietNoRT_P=.04))
reject('FBZ_withinRT_P12_preserved', lambda x:x['results'][0]['estimate'].update(dietWithinRT_P=.01))
reject('no_formal_interaction_test', lambda x:x['results'][0]['estimate'].update(formalInteractionTest=True))
reject('nonsignificance_not_equivalence', lambda x:x['results'][0]['estimate'].update(equivalenceEstablished=True))
reject('SEM_not_CI', lambda x:x['results'][0]['estimate'].update(SEMDays=[1.6,1.2,2.6,1.8]))
reject('lung_metastases_not_absent_all_sites', lambda x:x['results'][1]['estimate'].update(metastasisAbsentEverySite=True))
reject('host_observation_not_universal_safety', lambda x:x['results'][2]['estimate'].update(universalSafetyEstablished=True))
reject('high_culture_not_diet_benefit', lambda x:x['results'][3]['estimate'].update(highCultureDoseBenefitTransferredToDiet=True))
reject('two_experiments_not_four_independent', lambda x:x['results'][3]['estimate'].update(experimentsReported=4))
reject('no_old_source_PASS_transfer', lambda x:x['study']['priorIdentity'].update(priorAcceptanceTransferred=True))
reject('no_Duan2013_Gao_animal_pool', lambda x:x['study'].update(pooledWithDuan2013orGao2008=True))
reject('qualifications_preserved', lambda x:x.update(sourceQualifications=[]))

result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedPreclinicalFindings': 4, 'claims': 4, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
