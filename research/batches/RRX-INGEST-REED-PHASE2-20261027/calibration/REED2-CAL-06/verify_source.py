"""Reject observational causality, time-window and risk-set counting errors."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='primary_observational_cohort' and c['inspection']['physicalPagesRead']==list(range(1,11))
 assert not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['separateCompanionContentRead']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];assert not any(s[k] for k in ['assignmentRandomized','drugDosesKnown','exposureStandardized','multivariableConfoundingAdjustment','timeVaryingExposureAnalysis','treatmentResponseOrDiseaseActivityAdjusted','clinicalAnticancerEfficacyEstablished','currentPrescriptionAdopted','preventionOnlyPopulationWithoutPriorVTE'])
 assert s['switchingCommon'] and s['entryDates']==['2012-01','2022-01']
 p=c['populations'];assert p['screened']==293 and p['included']==208 and p['historyVTE']==17 and p['SAVEDAssessed']==172 and p['IMiDAnyDuring2Years']==179
 assert not p['riskSetsEqualWholeCohort'] and not p['uniqueNewIndependentPatientCountAdjudicated']
 assert p['Figure2InitialVTERiskSets']['month3']=={'aspirin':42,'LMWH_VKA':20,'DOAC':54,'none':78}
 assert p['Figure3InitialAnyBleedRiskSets']['month3']=={'aspirin':40,'LMWH_VKA':19,'DOAC':53,'none':75}
 assert p['Figure4InitialMajorBleedRiskSets']['month3']=={'aspirin':40,'LMWH_VKA':20,'DOAC':57,'none':76}
 assert p['Figure1SnapshotCounts']['month3']=={'aspirin':42,'LMWH_VKA':22,'DOAC':57,'none':79}
 assert len(c['results'])==len(c['claims'])==4
 a,b,d,e=[r['estimate'] for r in c['results']]
 assert a['firstVTEPatients']==19 and a['firstBleedingPatients']==35 and a['bleedingCategories']=={'major':14,'CRNM':11,'minor':10}
 assert a['onlyFirstCounted'] and a['VTEComponentsMutuallyExclusive']=={'PEonly':8,'PEandDVT':2,'DVTonly':9}
 assert a['bleedingAt3_6_12Months']==[11,16,25] and a['bodyFirstYearBleedingPercent']==74.3 and not a['bleedingFirstYearCountConflictResolved']
 assert b['baselineFollowupMonths']==24 and b['landmarkRemainingFollowupMonths']==21 and b['landmarkTimeMonths']==3 and b['deathIsCompetingEvent']
 assert b['baseline']['aspirin']=={'cumulativeIncidencePercent':18.73,'CI95':[7.43,33.97]} and b['baseline']['DOAC']['cumulativeIncidencePercent']==4
 assert b['landmark']['aspirin']=={'cumulativeIncidencePercent':12.46,'CI95':[4.48,24.74]} and b['landmark']['DOAC']['cumulativeIncidencePercent']==0
 assert b['GrayPBaselineLandmark']==[.100,.078] and b['noVTEWhileOnDOACorVKA']
 assert b['eventMedicationSentenceLiteral']=={'anyProphylaxis':8,'aspirin':9,'LMWH':2,'VKA':0,'DOAC':0} and not b['contradictorySentenceResolved']
 assert b['causalAdjustedEffect'] is None and not b['statisticalSuperiorityEstablished'] and not b['completeProtectionEstablished']
 assert d['baselineMajor']['aspirin']=={'cumulativeIncidencePercent':3.57,'CI95':[2.48,15.72]} and not d['majorCIRepaired']
 assert d['baselineMajor']['DOAC']['cumulativeIncidencePercent']==0 and d['landmarkMajor']['DOAC']['cumulativeIncidencePercent']==5.92
 assert d['GrayPAnyBaselineLandmark']==[.726,.030] and d['GrayPMajorBaselineLandmark']==[.298,.704]
 assert d['anyBleedEventMedicineUnassignedCountDerived']==1 and not d['eventMedicineCountsSilentlyRepaired']
 assert d['majorBleedEventMedicineAsPrinted']['DOAC']==4 and not d['generalEqualSafetyEstablished'] and not d['noninferiorityEstablished'] and d['causalAdjustedEffect'] is None
 assert e['kind']=='univariate_cause_specific_Cox_not_adjusted' and not e['subdistributionHR'] and not e['multiplicityCorrected']
 assert e['IMPEDEPerPointHR']==1.19 and e['IMPEDEPerPointCI95']==[1.04,1.37] and e['IMPEDEOverallCategoryP']==.12
 assert e['SAVEDN']==172 and e['SAVEDHighVsLowHR']==.97 and e['SAVEDCI95']==[.34,2.75] and e['SAVEDP']==.95 and not e['SAVEDUniversalInvalidityEstablished']
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and len(c['sourceQualifications'])==15
 assert c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for r in c['results']:assert not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for n in ['AUDIT-MANIFEST.json','READINESS.json']:
 for f,h in read(B/n).get('files',read(B/n).get('hashes',{})).items():assert sha(B/f)==h
reed=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(reed/'aspirin-myeloma/pdfs/41069611-vospernik-2025.pdf')==c['source']['sha256'];assert sha(reed/'aspirin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(R/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(z) for z in (B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field']) for e in es}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in es:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['sourceHash']==c['source']['sha256'] and e['status'] in inv['answerStatuses']
checks=[]
def reject(n,path,value):
 x=copy.deepcopy(c);p=x
 for k in path[:-1]:p=p[k]
 p[path[-1]]=value
 try:validate(x)
 except AssertionError:checks.append(n);return
 raise AssertionError(n+' accepted')
for n,p,v in [
 ('cohort_not_RCT',['study','assignmentRandomized'],True),
 ('doses_not_known',['study','drugDosesKnown'],True),
 ('no_multivariable_effect',['study','multivariableConfoundingAdjustment'],True),
 ('no_timevarying_analysis',['study','timeVaryingExposureAnalysis'],True),
 ('priorVTE_not_uniform_primary_only',['study','preventionOnlyPopulationWithoutPriorVTE'],True),
 ('no_new_independent208claim',['newIndependentPatients'],208),
 ('SAVED_not_all208',['populations','SAVEDAssessed'],208),
 ('risksets_not208',['populations','riskSetsEqualWholeCohort'],True),
 ('VTE_landmark_not_snapshotDOAC57',['populations','Figure2InitialVTERiskSets','month3','DOAC'],57),
 ('anybleed_riskset_not_VTE',['populations','Figure3InitialAnyBleedRiskSets','month3','aspirin'],42),
 ('only_first_event_counted',['results',0,'estimate','onlyFirstCounted'],False),
 ('no_firstyear_count_repair',['results',0,'estimate','bleedingAt3_6_12Months'],[11,16,26]),
 ('landmark21_not24months',['results',1,'estimate','landmarkRemainingFollowupMonths'],24),
 ('CIF_death_competing',['results',1,'estimate','deathIsCompetingEvent'],False),
 ('baselineDOAC_not_onmedicationzero',['results',1,'estimate','baseline','DOAC','cumulativeIncidencePercent'],0),
 ('VTEtrend_not_significant',['results',1,'estimate','statisticalSuperiorityEstablished'],True),
 ('zeroDOAC_not_completeprotection',['results',1,'estimate','completeProtectionEstablished'],True),
 ('8any_not_silent11fix',['results',1,'estimate','eventMedicationSentenceLiteral','anyProphylaxis'],11),
 ('event_sentence_not_adjudicated',['results',1,'estimate','contradictorySentenceResolved'],True),
 ('CIF_not_adjusted_causalRR',['results',1,'estimate','causalAdjustedEffect'],.2),
 ('literalASAmajorCI_not_repaired',['results',2,'estimate','baselineMajor','aspirin','CI95'],[.248,15.72]),
 ('landmarkDOACmajor_not_zero',['results',2,'estimate','landmarkMajor','DOAC','cumulativeIncidencePercent'],0),
 ('bleeding_unassigned_not_silentzero',['results',2,'estimate','anyBleedEventMedicineUnassignedCountDerived'],0),
 ('majorbleed_null_not_safetyequality',['results',2,'estimate','generalEqualSafetyEstablished'],True),
 ('no_noninferiority',['results',2,'estimate','noninferiorityEstablished'],True),
 ('cause_specific_not_subdistribution',['results',3,'estimate','subdistributionHR'],True),
 ('unadjusted_nominal_not_corrected',['results',3,'estimate','multiplicityCorrected'],True),
 ('IMPEDE_globalP12_not_pointP01',['results',3,'estimate','IMPEDEOverallCategoryP'],.01),
 ('SAVED_null_not_universalinvalidity',['results',3,'estimate','SAVEDUniversalInvalidityEstablished'],True),
 ('no_fullscience',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourcePDFAndIndexHashes':'PASS','prospectiveAndAuditDependencyHashes':'PASS','typedInputInventory':'PASS_15Q_67fields','sourceGuards':'PASS','rejectedRegressions':checks,'independentSourceAudit':'pending','fullFieldMapAcceptance':False,'scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('PASS',len(checks),'meaningful observational guards/source/index/GP/deps/67fields')
