"""Reject retrospective causality, event/patient and risk-model conflations."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='primary_observational_retrospective_cohort' and c['inspection']['physicalPagesRead']==list(range(1,11))
 assert not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['separateCompanionContentRead']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];assert s['entryDates']==['2016-01','2022-06'] and s['ASAReportedDoseMg']==81 and not s['ASAActualFrequencyExplicitInMain']
 assert not any(s[k] for k in ['assignmentRandomized','suitableAntithromboticComparator','deathCompetingRiskAnalysis','timeDependentVTEForSurvivalDescribed','clinicalRecommendationAdopted','anticancerBenefitEstablished'])
 p=c['populations'];assert p['screened']==356 and p['included']==250 and p['excluded']==106 and p['under3MonthGroup']=={'earlyDeaths':13,'lostFollowup':22}
 assert p['ASAAsReported']=={'N':248,'percent':98.6} and p['ASAInitialPercentArithmeticDerived']==99.2 and not p['reportedPercentConflictResolved']
 assert p['PRISMBodyN']==167 and p['PRISMTable2SumDerived']==156 and not p['PRISMDenominatorAdjudicated']
 assert p['thalidomideN']==245 and p['lenalidomideN']==3 and p['R_ISSFISHN']==158
 assert len(c['results'])==len(c['claims'])==4
 a,b,d,e=[r['estimate'] for r in c['results']]
 assert a['VTEPatients']==37 and a['VTEFirst6Months']==[20,8.] and a['VTEMonths7to12']==[8,3.2] and a['VTEAfter12Months']==[9,3.6]
 assert a['siteLabelsAsSource']=={'lowerExtremities':31,'PE':3,'superficialVenous':2,'temporalVein':1} and not a['all37ConventionalDVTPE']
 assert not a['fixed19MonthRiskWindow'] and a['causalASAEffect'] is None
 assert b['majorBleedingEvents']==14 and b['majorBleedingPatients']==12 and b['majorBleedingPatientPercent']==4.8
 assert b['CRNMBPatients']==11 and b['CRNMBPatientsWithMajorBleedHistory']==2 and b['CRNMBTherapeuticFXaPatients']==4
 assert not b['allEventsAttributableSolelyASA'] and not b['independentUniqueBleedingCountSummed'] and not b['comparativeSafetyEstablished']
 assert b['fatalHemorrhagePatients']==3 and b['sourceCallsAllFatalHemorrhagesAssociatedASA']
 assert d['PRISMBodyGroups']['N']==167 and d['PRISMBodyGroups']['intermediate']==133 and d['PRISMTableGroups']['intermediate'][0]==122 and not d['PRISMDenominatorReconciled']
 assert d['Figure2AUCPercent']['IMPEDE']=={'AUC':61.5,'CI95':[48.8,74.3]} and d['IMPEDEBodyCILiteral']=='48.8%-0.74%'
 assert d['IMPEDE_ROC_P']==.09 and d['Table2P']['IMPEDE']==.41 and d['Figure1LogrankP']['IMPEDE6Month']==.4154
 assert d['SAVED_ROC_P']==.94 and d['Table2P']['SAVED']==.999 and d['Figure1LogrankP']['SAVED6Month']==.6108
 assert d['Table2P']['PRISM']==.93 and d['Figure1LogrankP']['PRISM12Month']==.8459
 assert not d['universalScoreInvalidityEstablished'] and not d['prospectiveClinicalUtilityEstablished'] and not d['multivariateSupplementRead']
 assert e['medianOSMonths']==62 and e['deaths']==64 and e['Figure3Groups']=={'VTE':{'N':37,'deaths':10},'noVTE':{'N':213,'deaths':54}}
 assert e['Figure3LogrankP']==.088 and not e['noMortalityEffectEstablished'] and not e['undetectedFatalPERuledOut'] and e['adjustedCausalHazardRatio'] is None
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and len(c['sourceQualifications'])==15
 assert c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for r in c['results']:assert not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for n in ['AUDIT-MANIFEST.json','READINESS.json']:
 for f,h in read(B/n).get('files',read(B/n).get('hashes',{})).items():assert sha(B/f)==h
reed=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(reed/'aspirin-myeloma/pdfs/39552772-fernandezvargas-2024.pdf')==c['source']['sha256'];assert sha(reed/'aspirin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
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
 ('retrospective_not_RCT',['study','assignmentRandomized'],True),
 ('no_suitable_prophylaxis_control',['study','suitableAntithromboticComparator'],True),
 ('dose_frequency_not_invented',['study','ASAActualFrequencyExplicitInMain'],True),
 ('early_deaths_not_retainedcohort',['populations','under3MonthGroup','earlyDeaths'],0),
 ('ASA_sourcepercent_not_silent99point2',['populations','ASAAsReported','percent'],99.2),
 ('ASA_discrepancy_not_resolved',['populations','reportedPercentConflictResolved'],True),
 ('PRISM167_not_FISH158',['populations','PRISMBodyN'],158),
 ('PRISMtable_not_silent167',['populations','PRISMTable2SumDerived'],167),
 ('VTE_not_all_DVTPE',['results',0,'estimate','all37ConventionalDVTPE'],True),
 ('median19_not_fixedwindow',['results',0,'estimate','fixed19MonthRiskWindow'],True),
 ('no_causal_ASA_effect',['results',0,'estimate','causalASAEffect'],2.),
 ('major14events_not14patients',['results',1,'estimate','majorBleedingPatients'],14),
 ('major4point8_not_eventpercent',['results',1,'estimate','majorBleedingPatientPercent'],5.6),
 ('CRNM_overlap_not_independent',['results',1,'estimate','CRNMBPatientsWithMajorBleedHistory'],0),
 ('concurrentFXa_not_zero',['results',1,'estimate','CRNMBTherapeuticFXaPatients'],0),
 ('fatal_association_not_causalASA',['results',1,'estimate','allEventsAttributableSolelyASA'],True),
 ('no_comparativesafety',['results',1,'estimate','comparativeSafetyEstablished'],True),
 ('PRISMbody133_not_table122',['results',2,'estimate','PRISMBodyGroups','intermediate'],122),
 ('PRISMconflict_not_resolved',['results',2,'estimate','PRISMDenominatorReconciled'],True),
 ('malformedbodyCI_not_silentlyrepaired',['results',2,'estimate','IMPEDEBodyCILiteral'],'48.8%-74.3%'),
 ('ROCnotKM_P',['results',2,'estimate','IMPEDE_ROC_P'],.4154),
 ('TableIMPEDE_notROC_P',['results',2,'estimate','Table2P','IMPEDE'],.09),
 ('SAVED_KM_notROC_P',['results',2,'estimate','Figure1LogrankP','SAVED6Month'],.94),
 ('no_universalriskmodelinvalidity',['results',2,'estimate','universalScoreInvalidityEstablished'],True),
 ('AUC_not_provenclinicalutility',['results',2,'estimate','prospectiveClinicalUtilityEstablished'],True),
 ('supplement_not_independentlyread',['results',2,'estimate','multivariateSupplementRead'],True),
 ('OS_P088_not_P88',['results',3,'estimate','Figure3LogrankP'],.88),
 ('OS_null_not_noeffect',['results',3,'estimate','noMortalityEffectEstablished'],True),
 ('no_adjusted_causal_survivalHR',['results',3,'estimate','adjustedCausalHazardRatio'],1.),
 ('no_scientificacceptance',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourcePDFAndIndexHashes':'PASS','prospectiveAndAuditDependencyHashes':'PASS','typedInputInventory':'PASS_15Q_67fields','sourceGuards':'PASS','rejectedRegressions':checks,'independentSourceAudit':'pending','fullFieldMapAcceptance':False,'scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('PASS',len(checks),'meaningful retrospective guards/source/index/GP/deps/67fields')
