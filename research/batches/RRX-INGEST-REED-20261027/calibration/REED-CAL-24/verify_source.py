"""Guard reused diet data, SD/SEM, route and clonogenic normalization."""
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
    assert c['paper']['sourceType']=='primary_preclinical_clonogenic_and_injection_with_reused_diet_context'
    assert c['paper']['id']=='P-D10-EMT6-2013' and c['paper']['existingSourceId']=='A-F02-R1158-F01' and c['paper']['doi'] is None
    assert c['inspection']['textualPagesRead']==list(range(1,15)) and not c['inspection']['fullScientificReviewComplete']
    assert not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
    s=c['study'];assert s['humanParticipants']==0 and s['newMouseRoute']=='intraperitoneal'
    assert s['injectionMgPerKgPerDay']==50 and s['injectionDays']==3 and s['dosingTimesRelativeRT']==['minus1day','minus2hours','plus1day']
    assert s['growthEndpoint']=='time_to_four_times_volume_at_stratification' and s['euthanasiaMm3']==1000
    assert s['mainMouseNPerGroupRange']==[7,8] and s['mainTotalExactN'] is None and s['secondInjectionExperimentN'] is None
    assert s['dietExperimentIsReusedCAL23'] and s['newIndependentDietAnimalsAdded']==0
    for k in ['directPatientExposureMeasured','validatedMaximumToleratedDose','formalEquivalenceEstablished','clinicalBenefitOrHarmEstablished','currentRecommendationAdopted','tubulinBindingOrMetabolicMediatorMeasured']:assert not s[k]
    prior=s['priorIdentity'];assert prior==read(B/'PRIOR-RECONCILIATION.json')
    assert not prior['sameBytesAsPriorAsset'] and not prior['priorAcceptanceTransferred'] and prior['canonicalChanges']==0
    o=s['overlap'];assert o==read(B/'OVERLAP-RECONCILIATION.json')==c['overlapRecords'][0]
    assert o['sameDietExperimentExplicitlyReported'] and o['independentNewAnimalCohortCount']==0
    assert o['currentMeansDays']==o['priorMeansDays']==[12.7,12.1,17.5,20.4]
    assert o['currentSDDays']==[.1,1.2,3.7,2.4] and o['priorSEMDays']==[.8,.6,1.3,.9] and not o['precisionDifferenceResolved']
    assert len(c['results'])==len(c['claims'])==5
    a,b,d,e,f=[r['estimate'] for r in c['results']]
    assert a['aerobic2h']=='no_reported_toxicity_or_cellnumber_change' and a['independentExperiments']==3
    assert not a['SFandYCSFEquivalent'] and not a['apoptosisDirectlyMeasured']
    assert b['fenbendazoleMicroM']==10 and not b['radiationResponseAltered'] and not b['radiationSynergyEstablished'] and not b['formalEquivalenceEstablished']
    assert d['kind']=='time_to_fourfold_volume_mean_SD_days'
    assert d['firstMeans']==[10.4,12.4,18.3,17.5] and d['firstSD']==[3.0,2.6,5.1,7.5]
    assert d['secondMeans']==[11.4,11.5] and d['secondSD']==[3.0,1.0] and d['secondN'] is None
    assert d['secondRadiationArmsLiteral']=='ND' and d['secondRadiationArmsNumeric'] is None
    assert not d['dietDataCountedAsThirdIndependentExperiment'] and not d['FBZSignificantGrowthBenefitReported'] and d['radiationSignificantDelayReported']
    assert d['survivalBenefit'] is None and not d['formalEquivalenceEstablished']
    assert e['lungMetastasesNoRT_P']==.54 and e['lungMetastasesWithRT_P']==.44 and e['rawMetastasisCounts'] is None
    assert not e['formalClinicalSafetyOrEquivalence']
    assert f['fenbendazoleMicroM']==10 and f['fenbendazoleHours']==[2,24] and f['docetaxelHours']==2
    assert f['FBZ24hAloneSF']==.18 and f['FBZ24hAloneSEM']==.02 and f['classification']=='additive'
    assert f['normalization']=='untreated_for_docetaxelalone;matched_FBZalone_for_combinations'
    assert not f['significantSynergismOrAntagonismReported'] and not f['combinationAbsoluteSurvivalUnchanged']
    for r in c['results']:
        assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
        for loc in r['sourceLocators']:assert 1 <= loc['physicalPage'] <= 14 and loc['sourceSha256']==c['source']['sha256']
    assert {q['id'] for q in c['sourceQualifications']}=={'C24-REUSED-DIET','C24-ERROR-MEASURE','C24-DOSE-TIMING','C24-BASELINE','C24-N-UNIT','C24-CITATIONS','C24-TRANSLATION'}
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
assert sha(reed / 'fenbendazole-cancer/pdfs/23393324-duanq-2013.pdf') == c['source']['sha256'] == read(B / 'READINESS.json')['sourceSha256']
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

reject('IP_not_oral_route', lambda x:x['study'].update(newMouseRoute='oral'))
reject('50mg_perkg_perday_not_total_three_days', lambda x:x['study'].update(injectionMgPerKgPerDay=50/3))
reject('main_N_range_not_exact32', lambda x:x['study'].update(mainTotalExactN=32))
reject('second_experiment_N_unknown', lambda x:x['study'].update(secondInjectionExperimentN=16))
reject('diet_reuse_not_independent_new_animals', lambda x:x['study'].update(newIndependentDietAnimalsAdded=32))
reject('diet_crossreport_SD_not_silently_repaired', lambda x:x['study']['overlap']['currentSDDays'].__setitem__(0,.8))
reject('precision_conflict_not_resolved', lambda x:x['study']['overlap'].update(precisionDifferenceResolved=True))
reject('SF_not_yield_corrected_SF', lambda x:x['results'][0]['estimate'].update(SFandYCSFEquivalent=True))
reject('clonogenicity_not_direct_apoptosis', lambda x:x['results'][0]['estimate'].update(apoptosisDirectlyMeasured=True))
reject('no_radiation_sensitization', lambda x:x['results'][1]['estimate'].update(radiationSynergyEstablished=True))
reject('table_SD_not_SEM', lambda x:x['results'][2]['estimate'].update(kind='time_to_fourfold_volume_mean_SEM_days'))
reject('ND_not_zero', lambda x:x['results'][2]['estimate'].update(secondRadiationArmsNumeric=[0,0]))
reject('reused_diet_not_third_new_experiment', lambda x:x['results'][2]['estimate'].update(dietDataCountedAsThirdIndependentExperiment=True))
reject('RT_delay_not_FBZ_benefit', lambda x:x['results'][2]['estimate'].update(FBZSignificantGrowthBenefitReported=True))
reject('docetaxel_additive_not_synergistic', lambda x:x['results'][4]['estimate'].update(classification='synergistic'))
reject('normalized_curves_not_absolute_survival_unchanged', lambda x:x['results'][4]['estimate'].update(combinationAbsoluteSurvivalUnchanged=True))
reject('max_solubility_not_validated_MTD', lambda x:x['study'].update(validatedMaximumToleratedDose=True))
reject('no_old_PASS_transfer', lambda x:x['study']['priorIdentity'].update(priorAcceptanceTransferred=True))
reject('source_qualifications_retained', lambda x:x.update(sourceQualifications=[]))

result = {'status': 'PASS', 'candidateSha256': sha(B / 'SOURCE-CANDIDATE.json'), 'sourceSha256': c['source']['sha256'], 'boundedPreclinicalFindings': 5, 'claims': 5, 'questions': 15, 'typedFields': 67, 'regressions': checks, 'independentAudit': 'pending', 'fullScientificReviewComplete': False, 'scientificAcceptance': False}
(B / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
