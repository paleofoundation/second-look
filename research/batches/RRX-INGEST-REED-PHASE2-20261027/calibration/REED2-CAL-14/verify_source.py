"""Guard PU probabilities, drug-US model identity and unresolved source contrasts."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='primary_computational_PU_and_preclinical_U87MG_spheroid' and c['inspection']['physicalPagesRead']==list(range(1,20))
 assert not any(c['inspection'][k]for k in ['fullScientificReviewComplete','separateCompanionContentRead','rawCodeDataInspected','sourceTextPlotConflictResolved'])
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];p=c['populations'];assert s['spheroidCellsPerWell']==10000 and s['humanParticipants']==s['animalSubjects']==0
 assert s['drugCompounds']==['carboplatin','memantine hydrochloride','temozolomide'] and s['US']=={'frequencyMHz':1,'intensityWcm2':1,'dutyPercent':20,'pulseDurationMilliseconds':200,'stimulationMinutes':5}
 assert s['figure5SixthArm']=='US+drugIC25' and s['exactIC25ConcentrationsInMain']is None and not s['clinicalEfficacyEstablished'] and not s['synergyFormallyEstablished']
 assert p['Figure5N']==4 and p['sourceSpheroidDiameterMeanSD']==[306.7,6.2] and p['diameterUnitAsPrinted']=='microMolar(uM)' and not p['uniqueBiologicalCultureNVerified']
 assert len(c['results'])==len(c['claims'])==5 and len(c['sourceQualifications'])==16
 a,b,d,e,f=[x['estimate']for x in c['results']]
 assert a['molecules']==364 and a['positiveLabels']==175 and a['descriptors']==204 and a['classPrior']==.5454 and a['trainValidationTestPercent']==[70,15,15]
 assert a['DNN']=={'trainingLoss':.13844,'validationLoss':.27432,'recall':.95382} and a['GNN']=={'trainingLoss':.27766,'validationLoss':.72342,'recall':.8231}
 assert a['candidateConfidencePercent']=={'carboplatin':99.45,'memantineHydrochloride':98.35} and not any(a[k]for k in ['trueNegativesVerified','SCARAssumptionIndependentlyValidated','externalCalibrationLeakageAuditPerformed','probabilityOfClinicalBenefit'])
 assert b['timeHours']==72 and b['unit']=='micromolar' and b['IC50']=={'memantineHydrochloride':131,'carboplatin':252.3,'TMZ':804.5} and b['exactIC25Concentrations']is None
 assert not any(b[k]for k in ['IC25AssumedHalfIC50','measuredClinicalPotencyOrBrainPK','IC50CIReported'])
 assert d['timeHours']==24 and d['memantineDrugOnly']=={'mean':69.5,'SD':9.9} and d['memantinePlusUS']=={'mean':36.7,'SD':13.7}
 assert d['carboplatinPlusUS']=={'mean':66.6,'SD':14.6} and d['TMZPlusUS']=={'mean':51.,'SD':7.1} and d['Figure5N']==4 and d['readoutIsViabilityNotPercentKilled'] and d['USAloneCytotoxicityPresent']
 assert not any(d[k]for k in ['allUSAloneContrastsFormallyQuantified','formalSynergyEstablished','patientBenefitEstablished'])
 assert e['timeHours']==72 and e['carboplatinDrugOnly']=={'mean':44.9,'SD':1.6} and e['carboplatinPlusUS']=={'mean':23.2,'SD':6.2}
 assert e['textClaimsMemantinePlateau'] and e['textClaimsCarboplatinMostCytotoxic72h'] and e['plotMem72LowerThan24Visible'] and e['plotMem72BelowCarb72Visible'] and e['exactMem72MeansNotDigitized']
 assert not e['textPlotDiscrepancyResolved'] and not e['crossTimeEquivalenceEstablished']
 assert f['predictedMemBBBProbability']==.988 and not any(f[k]for k in ['companionFiguresRead','JC1Is3DSpheroidAssay','NMDAPiezoCalciumNecessityTestVerified','directOxygenHypoxiaAssayInMain','humanBBBExposureSafetyEstablished','clinicalSonosensitizerEfficacyEstablished'])
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
 ('cells_not_patients',['study','humanParticipants'],10000),('n4_not_cellsperwell',['populations','Figure5N'],10000),('actual_memantinecompound',['study','drugCompounds',1],'clomipramine'),('US_duty_not100',['study','US','dutyPercent'],100),('US_minutesnotseconds',['study','US','stimulationMinutes'],300),('sixth_arm_not_repeatedIC50',['study','figure5SixthArm'],'US+drugIC50'),('IC25_not_invented',['study','exactIC25ConcentrationsInMain'],65.5),('PU_unlabelednotnegative',['results',0,'estimate','trueNegativesVerified'],True),('SCAR_not_validated',['results',0,'estimate','SCARAssumptionIndependentlyValidated'],True),('confidence_not_patientbenefit',['results',0,'estimate','probabilityOfClinicalBenefit'],True),('prior_not_labelprevalence',['results',0,'estimate','classPrior'],.48),('recall_not_GNN',['results',0,'estimate','DNN','recall'],.8231),('no_external_calibration',['results',0,'estimate','externalCalibrationLeakageAuditPerformed'],True),('IC50_not_millimolar',['results',1,'estimate','unit'],'millimolar'),('memIC50_notTMZ',['results',1,'estimate','IC50','memantineHydrochloride'],804.5),('IC25_not_half',['results',1,'estimate','IC25AssumedHalfIC50'],True),('IC50_not_humanPK',['results',1,'estimate','measuredClinicalPotencyOrBrainPK'],True),('SD_not_CI',['results',2,'estimate','memantinePlusUS','SD'],.137),('viability_not_percentkilled',['results',2,'estimate','readoutIsViabilityNotPercentKilled'],False),('USalone_cytotoxic',['results',2,'estimate','USAloneCytotoxicityPresent'],False),('not_all_UScontrasts',['results',2,'estimate','allUSAloneContrastsFormallyQuantified'],True),('no_formalsynergy',['results',2,'estimate','formalSynergyEstablished'],True),('72h_carbnotmem',['results',3,'estimate','carboplatinPlusUS','mean'],36.7),('sourceconflict_unresolved',['results',3,'estimate','textPlotDiscrepancyResolved'],True),('mem72_not_digitized',['results',3,'estimate','exactMem72MeansNotDigitized'],False),('no_timeequivalence',['results',3,'estimate','crossTimeEquivalenceEstablished'],True),('companions_unread',['results',4,'estimate','companionFiguresRead'],True),('JC1_2Dnot3D',['results',4,'estimate','JC1Is3DSpheroidAssay'],True),('hypoxia_not_directassay',['results',4,'estimate','directOxygenHypoxiaAssayInMain'],True),('predictedBBB_not_safety',['results',4,'estimate','humanBBBExposureSafetyEstablished'],True),('no_NMDAPiezotest',['results',4,'estimate','NMDAPiezoCalciumNecessityTestVerified'],True),('diameterunit_not_repaired',['populations','diameterUnitAsPrinted'],'micrometer'),('not_newRCT',['newIndependentTrials'],1),('not_newpatients',['newIndependentPatients'],4),('not_scienceapproval',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY_SOURCE_CONFLICT_RETAINED','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL14 PASS',len(checks),'meaningfulguards/source/index/GP/10deps/67fields')
