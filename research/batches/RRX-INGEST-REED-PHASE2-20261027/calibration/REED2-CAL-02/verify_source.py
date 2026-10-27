"""Guard economic units, scenario uncertainty, missingness and independence."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['id']=='B-R0112' and c['source']['id']=='B-R0112-F01' and c['paper']['sourceType']=='within_trial_economic_evaluation'
 assert c['inspection']['physicalPagesRead']==list(range(1,14)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['separateCompanionContentRead']
 assert not any(c[k] for k in ['priorAcceptanceTransferred','scientificAcceptance','humanApproval','released']) and c['newIndependentTrials']==c['newIndependentPatients']==0
 s=c['study'];assert s['parentTrialIdentity']=='STUDY-P-D05-PAXD-2025' and s['parentTrialReportId']=='P-D05-PAXD-2025' and s['newIndependentTrialCount']==0
 assert s['horizonsWeeks']==[12,48] and s['perspectives']==['NHS_plus_PSS','societal'] and s['baseCurrency']=='GBP' and s['basePriceYear']=='2022/2023'
 assert not any(s[k] for k in ['currentPricesVerified','WTPThresholdsForCapabilityEstablished','clinicalRecommendationAdopted','currentAccessReimbursementEstablished','monotherapy'])
 p=c['populations'];assert p['sourceReportedRandomized']['total']==150 and p['mainEconomic']['total']==124 and [p['mainEconomic'][k] for k in ['active','placebo']]==[61,63] and p['complete48WeekSensitivity']['total']==56
 assert not p['countsReconciledWithParentOriginal'] and p['parentExistingMetadata']['randomized']==151
 assert len(c['results'])==len(c['claims'])==4
 a,b,d,e=[r['estimate'] for r in c['results']];ss=a['scenarios']
 assert [(x['perspective'],x['weeks']) for x in ss]==[('NHS_plus_PSS',12),('NHS_plus_PSS',48),('societal',12),('societal',48)]
 assert [x['incrementalQALY'] for x in ss]==[.012,.090,.012,.090] and [x['ICER_GBPPerQALY'] for x in ss]==[5069,9007,4218,-2831]
 assert [x['costEffectiveProbabilityPercentAt20000and30000GBP'] for x in ss]==[[93,96],[93,98],[69,79],[98,99]]
 assert ss[3]['incrementalCost95CI']==[-1621,1111] and ss[2]['incrementalCost95CI']==[-693,794]
 assert a['table3MorePreciseCostContrasts']['societal12']==[50.22,[-703.09,803.53]]
 assert not any(a[k] for k in ['societalCostSavingStatisticallyEstablished','probabilityIsIndividualBenefitChance','economicFindingIsNewEfficacyTrial'])
 assert all(not x['unroundedRatioRecalculated'] for x in ss)
 assert b['adjustedBetweenArmChange']==[.097,.067] and b['units']=='EQ-5D utility index point change, not QALY'
 assert not d['allNHSOutcomesAbove90PercentAt20000'] and not d['clinicalRemissionEstablishedByCapability']
 assert d['scenarios'][1]['NHS_plus_PSS']['probabilityPercentAtBorrowed20000and30000Threshold']==[79,92]
 assert d['scenarios'][3]['NHS_plus_PSS']['probabilityPercentAtBorrowed20000and30000Threshold']==[44,75]
 assert d['scenarios'][3]['NHS_plus_PSS']['ICER_GBPPerUnit']==21320 and not any(x['validatedCapabilityWTPThreshold'] for x in d['scenarios'])
 z=e['completeCase48'];assert z['N']==56 and z['incrementalQALY']==.038 and z['incrementalQALY95CI']==[-.050,.126] and z['NHSProbabilityPercentAt20000']==54
 assert z['ICER_GBPPerQALY']==20840 and z['ICER95CI']==[-166588,207354] and not z['fullAppendixChecked']
 assert e['historicalUpdatedCostScenario']['priceYear']=='2024/2025' and not e['historicalUpdatedCostScenario']['currentPricesVerified']
 assert e['reportedNetBenefits']['specificLambdaAssigned'] is None and not e['reportedNetBenefits']['allConfidenceIntervalsExcludeZero']
 assert not e['MARAssumptionVerified'] and not e['robustAcrossAllMissingnessScenariosEstablished']
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and len(c['sourceQualifications'])==13
 assert c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for r in c['results']:
  assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
  assert all(z['sourceSha256']==c['source']['sha256'] and 1<=z['physicalPage']<=13 for z in r['sourceLocators'])
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for name in ['AUDIT-MANIFEST.json','READINESS.json']:
 for f,h in read(B/name).get('files',read(B/name).get('hashes',{})).items():assert sha(B/f)==h
reed=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed/'pramipexole-treatment-resistant-depression/pdfs/41333541-aszewska-2026.pdf')==c['source']['sha256']
assert sha(reed/'pramipexole-treatment-resistant-depression/index.csv')==read(B/'READINESS.json')['indexSha256']
assert not read(B/'PRIOR-RECONCILIATION.json')['sameBytesAsPriorMain'] and not read(B/'PRIOR-RECONCILIATION.json')['priorAcceptanceTransferred']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');entries=[json.loads(z) for z in (B/'review-inputs.jsonl').read_text().splitlines()]
assert len(entries)==67 and {(e['questionId'],e['field']) for e in entries}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in entries:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,path,value):
 x=copy.deepcopy(c);p=x
 for k in path[:-1]:p=p[k]
 p[path[-1]]=value
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' accepted')
for n,p,v in [
 ('same_parent_not_new_trial',['newIndependentTrials'],1),
 ('same_population_not_new_patients',['newIndependentPatients'],124),
 ('main_sample_not_full_randomized',['populations','mainEconomic','total'],150),
 ('literal150_not_silent151_repair',['populations','sourceReportedRandomized','total'],151),
 ('parent_flow_not_independently_verified',['populations','countsReconciledWithParentOriginal'],True),
 ('price_year_not_current',['study','basePriceYear'],'2026'),
 ('no_validated_capability_WTP',['study','WTPThresholdsForCapabilityEstablished'],True),
 ('utility_not_QALY',['results',1,'estimate','adjustedBetweenArmChange'],[.012,.090]),
 ('ICER_not_recalculated_from_rounded',['results',0,'estimate','scenarios',0,'unroundedRatioRecalculated'],True),
 ('perspective12_probability_not_NHS',['results',0,'estimate','scenarios',2,'costEffectiveProbabilityPercentAt20000and30000GBP'],[93,96]),
 ('cost_saving_CI_not_zero_exclusion',['results',0,'estimate','societalCostSavingStatisticallyEstablished'],True),
 ('CE_probability_not_individual_benefit',['results',0,'estimate','probabilityIsIndividualBenefitChance'],True),
 ('table3_CI_not_silent_table4_replacement',['results',0,'estimate','table3MorePreciseCostContrasts','societal12'],[50.22,[-693,794]]),
 ('secondary_not_uniform90percent',['results',2,'estimate','allNHSOutcomesAbove90PercentAt20000'],True),
 ('CWLY44_not93',['results',2,'estimate','scenarios',3,'NHS_plus_PSS','probabilityPercentAtBorrowed20000and30000Threshold'],[93,98]),
 ('complete_case_not_main124',['results',3,'estimate','completeCase48','N'],124),
 ('complete_case54_not93',['results',3,'estimate','completeCase48','NHSProbabilityPercentAt20000'],93),
 ('complete_case_null_CI_retained',['results',3,'estimate','completeCase48','incrementalQALY95CI'],[.003,.021]),
 ('MAR_not_verified',['results',3,'estimate','MARAssumptionVerified'],True),
 ('net_benefit_CIs_cross_zero',['results',3,'estimate','reportedNetBenefits','allConfidenceIntervalsExcludeZero'],True),
 ('NMB_lambda_not_invented',['results',3,'estimate','reportedNetBenefits','specificLambdaAssigned'],20000),
 ('historical_sensitivity_not_currentprice',['results',3,'estimate','historicalUpdatedCostScenario','currentPricesVerified'],True),
 ('no_companion_read_inference',['inspection','separateCompanionContentRead'],True),
 ('no_prior_scientific_PASS_transfer',['scientificAcceptance'],True),
 ('no_current_reimbursement_inference',['study','currentAccessReimbursementEstablished'],True)]:reject(n,p,v)
out={'at':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourcePDFAndIndexHashes':'PASS','prospectiveAndAuditDependencyHashes':'PASS','typedInputInventory':'PASS_15Q_67fields','sourceGuards':'PASS','rejectedRegressions':checks,'independentSourceAudit':'pending','fullFieldMapAcceptance':False,'scientificAcceptance':False,'humanApproval':False,'released':False}
(B/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'meaningful economic regression guards;67 fields/source/hash bindings')
