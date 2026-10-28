"""Guard compound-specific CFA effects, gas timing and source caption discrepancies."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='primary_preclinical_xenon_memantine_CFA_radiobiology' and c['inspection']['physicalPagesRead']==list(range(1,11)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['separateCompanionContentRead']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];p=c['populations'];assert s['GBMLines']==['U87','U251'] and s['memantineExposureUM']==25 and s['radiationDoseGy']==[0,2,4,6,8] and s['photonEnergyMV']==6
 assert s['xenonTiming']=='Immediately after irradiation' and s['flaskGasTargetPercent']=={'Xe':50,'N2':25,'O2':20,'CO2':5} and s['suppliedMixturePercent']=={'Xe':75,'O2':20,'CO2':5}
 assert not any(s[k]for k in ['humanOrAnimalTreatment','normalBrainSafetyEstablished','formalSynergyTestReported','receptorMechanismNecessaryProven','clinicalRadiosensitizationBenefitEstablished'])
 assert p['independentExperiments']==3 and p['flaskReplicatesPerCondition']==3 and not p['biologicalNisNine'] and p['clinicalPatients']==p['animalSubjects']==0
 assert len(c['results'])==len(c['claims'])==5 and len(c['sourceQualifications'])==15
 a,b,d,e,f=[x['estimate']for x in c['results']]
 assert a['doseWithXenonPresentMGy']=={'mean':2022,'CI95':[2020.6,2023.4]} and a['doseAirMGy']=={'mean':1993,'CI95':[1990.5,1995.4]}
 assert not a['biologicalXenonAppliedDuringRT'] and not a['directXeConcentrationMeasurement'] and not a['clinicalScheduleAdopted']
 assert b['XeSignificantDoseGyP']=={'4':.029,'6':.010,'8':.037} and b['XeMemSignificantDoseGyP']=={'2':.023,'4':.001,'6':.008,'8':.022}
 assert not b['memantineAloneSignificantlyReducesSF'] and b['exactSFMeansCIsNotDigitized'] and not b['clinicalBenefitEstablished']
 assert d['XeTextSignificantDoseGyP']=={'2':.009,'6':.027,'8':.016} and d['XeFigure3CaptionSaysStartsGy']==4 and not d['XeTextPlotCaptionConflictResolved']
 assert d['memantineAloneSignificantDoseGyP']=={'4':.021,'6':.023,'8':.019} and d['XeMemPBoundsByGy']=={'2':'<.017','4':'<.003','6':'<.006','8':'<.026'} and not d['combo2GyAsteriskShownInPlot'] and not d['formalSynergyEstablished']
 assert e['HeLaXeSignificantDoseGyP']=={'8':.029} and not any(e[k]for k in ['HeLaMemOrComboRTDataClaimed','HeLaIsNormalBrain','shamPEGroupDifferencesSignificantAsReported','noIntrinsicToxicityOrEquivalenceEstablished','normalBrainSelectivitySafetyEstablished'])
 assert f['cellLinesWithGluA1GluN1Signals']==['U87','U251','HeLa'] and not any(f[k]for k in ['quantitativeReceptorExpressionCompared','receptorFunctionNecessityProven','DNADamageRepairMechanismMeasuredHere','wholeMechanismResolved','clinicalRadiosensitizationEstablished'])
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for x in c['results']:assert x['grade']is None and x['benefitGrade']is None and not x['acceptedSupport']
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for n in ['AUDIT-MANIFEST.json','READINESS.json']:
 for f,h in read(B/n).get('files',read(B/n).get('hashes',{})).items():assert sha(B/f)==h
p=read(B/'PLAN.json');root='/Users/kmfp/papers-for-claude/remaprx-fill';assert sha(Path(p['source']['ref'].replace('$REMAPRX_REED_ROOT',root)))==c['source']['sha256'];assert sha(Path(p['indexRef'].replace('$REMAPRX_REED_ROOT',root)))==p['indexSha256']
i=read(R/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(z)for z in(B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field'])for e in es}=={(q['id'],f)for q in i['questions']for f in q['inputFields']}
for e in es:assert set(i['requiredReviewInputEntryFields'])<=e.keys() and e['sourceHash']==c['source']['sha256'] and e['status']in i['answerStatuses']
checks=[]
def reject(n,path,v):
 x=copy.deepcopy(c);p=x
 for k in path[:-1]:p=p[k]
 p[path[-1]]=v
 try:validate(x)
 except AssertionError:checks.append(n);return
 raise AssertionError(n+' accepted')
for n,p,v in [
 ('actual_mem25uM',['study','memantineExposureUM'],250),('radiationGy_notMV',['study','radiationDoseGy'],[0,6]),('Xe_after_not_during',['study','xenonTiming'],'During irradiation'),('flask50_not75',['study','flaskGasTargetPercent','Xe'],75),('chamber75_not50',['study','suppliedMixturePercent','Xe'],50),('three_notnine_runs',['populations','independentExperiments'],9),('triplicates_not_newbiologicalN',['populations','biologicalNisNine'],True),('dose_validation_not_experiment',['results',0,'estimate','biologicalXenonAppliedDuringRT'],True),('Xe_not_directly_traced',['results',0,'estimate','directXeConcentrationMeasurement'],True),('mGy_not_Gy',['results',0,'estimate','doseWithXenonPresentMGy','mean'],2.022),('not_clinicalschedule',['results',0,'estimate','clinicalScheduleAdopted'],True),('U87_memnull',['results',1,'estimate','memantineAloneSignificantlyReducesSF'],True),('U87_Xe_doseP',['results',1,'estimate','XeSignificantDoseGyP','4'],.0029),('U87_combo2P',['results',1,'estimate','XeMemSignificantDoseGyP','2'],.001),('no_SF_digitization',['results',1,'estimate','exactSFMeansCIsNotDigitized'],False),('caption4_not_text2',['results',2,'estimate','XeFigure3CaptionSaysStartsGy'],2),('text2_retained',['results',2,'estimate','XeTextSignificantDoseGyP','2'],.029),('U251_conflict_unresolved',['results',2,'estimate','XeTextPlotCaptionConflictResolved'],True),('U251_memdoseP',['results',2,'estimate','memantineAloneSignificantDoseGyP','4'],.21),('comboP_bound_not_equal',['results',2,'estimate','XeMemPBoundsByGy','2'],'=.017'),('plot_star_omission',['results',2,'estimate','combo2GyAsteriskShownInPlot'],True),('not_formalsynergy',['results',2,'estimate','formalSynergyEstablished'],True),('HeLa_only8',['results',3,'estimate','HeLaXeSignificantDoseGyP'],{'2':.029}),('no_HeLamemdata',['results',3,'estimate','HeLaMemOrComboRTDataClaimed'],True),('HeLa_not_normalbrain',['results',3,'estimate','HeLaIsNormalBrain'],True),('PE_null_not_safety',['results',3,'estimate','noIntrinsicToxicityOrEquivalenceEstablished'],True),('IF_not_quantitative',['results',4,'estimate','quantitativeReceptorExpressionCompared'],True),('IF_not_necessity',['results',4,'estimate','receptorFunctionNecessityProven'],True),('DNArepair_not_measured',['results',4,'estimate','DNADamageRepairMechanismMeasuredHere'],True),('no_clinicalRTbenefit',['results',4,'estimate','clinicalRadiosensitizationEstablished'],True),('not_newRCT',['newIndependentTrials'],1),('not_newpatient',['newIndependentPatients'],3),('no_scienceapproval',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL15 PASS',len(checks),'meaningfulguards/source/index/GP/10deps/67fields')
