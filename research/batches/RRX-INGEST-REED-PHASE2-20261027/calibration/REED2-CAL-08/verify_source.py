"""Reject pooled-trial, observational-effect and conflicting-source substitutions."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='original_posthoc_IPD_observational_analysis_of_RCTs' and c['inspection']['physicalPagesRead']==list(range(1,15))
 assert not any(c['inspection'][k] for k in ['fullScientificReviewComplete','separateCompanionContentRead','rawIPDInspected','originalParentReportsRead'])
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];assert not any(s[k] for k in ['antithromboticAssignmentRandomized','allPatientsIMiDTreated','adverseEventLandmarkNsReported','causalityEstablished','currentClinicalRecommendationAdopted'])
 assert [p['registryId'] for p in s['parentTrials']]==['NCT02252172','NCT02076009','NCT02136134'] and [p['N'] for p in s['parentTrials']]==[737,569,498]
 p=c['populations'];assert p['pooledN']==1804 and p['landmarkOSN']==1568 and p['landmarkPFSN']==1348 and p['landmarkAdverseEventN'] is None
 assert p['baselineAnticoagulantN']==248 and p['within6MonthAnticoagulantN']==558 and p['baselineAntiplateletN']==457 and p['within6MonthAntiplateletN']==623
 assert not p['classOverlapDeduplicated'] and not p['newUniqueCrossCorpusParticipantsAdjudicated']
 assert len(c['results'])==len(c['claims'])==4
 a,b,d,e=[r['estimate'] for r in c['results']]
 assert a['pooledEventPatients']=={'VTE':178,'bleeding':250,'IHD':65,'stroke':31,'grade3plusAE':1469}
 assert a['salicylicAcidDerivativeNs']=={'baseline':428,'within6Months':604} and not any(a[k] for k in ['allAntiplateletsConfirmedASA','combinedClassNsDeduplicated','allBleedingIsMajor','sourcePercentLabelsRepaired'])
 assert a['anticoagIndications']['within6Months']['eventTreatment']==146 and a['antiplateletIndications']['baseline']['medicalHistory']==139
 assert a['rawBaselineAnticoagVTE']['P']==.038 and a['rawBaselineAnticoagVTE']['bodySaysNoSignificantDifference']
 assert b['kind']=='observational_adjusted_OR' and b['landmarkVTEAbstractBody']=={'estimate':.45,'CI95':[.26,.77],'P':.004}
 assert b['landmark6MonthsTable5']['VTE']=={'estimate':.39,'CI95':[.22,.69],'P':.001}
 assert b['baseline']['VTE']=={'estimate':1.13,'CI95':[.74,1.72],'P':.580}
 assert not any(b[k] for k in ['landmarkVTEDiscrepancyResolved','effectIsRiskRatio','causalPreventiveBenefitEstablished','specificDOACEfficacyEstablished'])
 assert d['baseline']['IHD']=={'estimate':1.86,'CI95':[1.09,3.14],'P':.022}
 assert d['abstractSaysNoAssociations'] and not d['allBaselineAssociationsNull'] and not any(d[k] for k in ['causalASAIHDHarmEstablished','equalBleedingSafetyEstablished','specificASAEffectEstablished'])
 assert d['landmark6MonthsTable5']['VTE']=={'estimate':1.12,'CI95':[.68,1.84],'P':.656}
 assert e['anticoag']['OSbaseline']=={'estimate':1.27,'CI95':[1.,1.61],'P':.051} and e['landmarkN']=={'OS':1568,'PFS':1348}
 assert e['antiplatelet']['OSlandmark']=={'estimate':.85,'CI95':[.66,1.10],'P':.218}
 assert not any(e[k] for k in ['baselineAnticoagOSStatisticallySignificant','equivalenceOrNoEffectEstablished','aspirinAnticancerBenefitEstablished'])
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and len(c['sourceQualifications'])==15
 assert c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for r in c['results']:assert not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for n in ['AUDIT-MANIFEST.json','READINESS.json']:
 for f,h in read(B/n).get('files',read(B/n).get('hashes',{})).items():assert sha(B/f)==h
reed=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(reed/'aspirin-myeloma/pdfs/39229471-almansour-2024.pdf')==c['source']['sha256'];assert sha(reed/'aspirin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(R/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(z) for z in(B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field']) for e in es}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
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
 ('regimenRCT_not_antithromboticRCT',['study','antithromboticAssignmentRandomized'],True),
 ('CASTOR_not_IMiD',['study','allPatientsIMiDTreated'],True),
 ('three_report_not_newtrials',['newIndependentTrials'],3),
 ('pooled1804_not_new_people',['newIndependentPatients'],1804),
 ('rawIPD_not_inspected',['inspection','rawIPDInspected'],True),
 ('AE_landmarkNs_not_invented',['populations','landmarkAdverseEventN'],1568),
 ('OS_landmark_not1804',['populations','landmarkOSN'],1804),
 ('PFS_landmark_not_OSN',['populations','landmarkPFSN'],1568),
 ('class_sum_not_uniqueusers',['populations','classOverlapDeduplicated'],True),
 ('antiplatelet_not_all_ASA',['results',0,'estimate','allAntiplateletsConfirmedASA'],True),
 ('bleeding_not_all_major',['results',0,'estimate','allBleedingIsMajor'],True),
 ('active_event_treatment_not_prophylaxis',['results',0,'estimate','anticoagIndications','within6Months','eventTreatment'],0),
 ('raw_P038_not_adjusted580',['results',0,'estimate','rawBaselineAnticoagVTE','P'],.580),
 ('Table_OR39_not_text45',['results',1,'estimate','landmark6MonthsTable5','VTE','estimate'],.45),
 ('text_OR45_not_table39',['results',1,'estimate','landmarkVTEAbstractBody','estimate'],.39),
 ('Table_CI_not_textCI',['results',1,'estimate','landmark6MonthsTable5','VTE','CI95'],[.26,.77]),
 ('unresolved_OR_not_reconciled',['results',1,'estimate','landmarkVTEDiscrepancyResolved'],True),
 ('odds_not_risk_ratio',['results',1,'estimate','effectIsRiskRatio'],True),
 ('adjustment_not_causality',['results',1,'estimate','causalPreventiveBenefitEstablished'],True),
 ('class_not_specific_DOACefficacy',['results',1,'estimate','specificDOACEfficacyEstablished'],True),
 ('AP_baselineIHD_positive_retained',['results',2,'estimate','allBaselineAssociationsNull'],True),
 ('AP_IHD_positive_not_nullreplacement',['results',2,'estimate','baseline','IHD','estimate'],1.),
 ('IHD_association_not_ASAcausalharm',['results',2,'estimate','causalASAIHDHarmEstablished'],True),
 ('adjusted_bleed_null_not_equalsafety',['results',2,'estimate','equalBleedingSafetyEstablished'],True),
 ('baselineAP_not_landmarkAP_VTE',['results',2,'estimate','landmark6MonthsTable5','VTE','estimate'],1.05),
 ('OS_P051_not_significant',['results',3,'estimate','baselineAnticoagOSStatisticallySignificant'],True),
 ('rounded_CI_not_P05_repair',['results',3,'estimate','anticoag','OSbaseline','P'],.049),
 ('null_survival_not_equivalence',['results',3,'estimate','equivalenceOrNoEffectEstablished'],True),
 ('no_ASA_anticancerbenefit',['results',3,'estimate','aspirinAnticancerBenefitEstablished'],True),
 ('no_scientificapproval',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourcePDFAndIndexHashes':'PASS','prospectiveAndAuditDependencyHashes':'PASS','typedInputInventory':'PASS_15Q_67fields','sourceGuards':'PASS','rejectedRegressions':checks,'independentSourceAudit':'pending','fullFieldMapAcceptance':False,'scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('PASS',len(checks),'meaningful pooled-report guards/source/index/GP/deps/67fields')
