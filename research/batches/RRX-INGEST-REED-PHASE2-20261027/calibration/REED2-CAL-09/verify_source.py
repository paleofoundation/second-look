"""Reject altered ASCT safety denominators, source conflicts and causal inference."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='original_retrospective_ASCT_safety_cohort'
 assert c['inspection']['physicalPagesRead']==list(range(1,13)) and c['inspection']['visualInspectedPhysicalPages']==[4,5,6,7,8,10,11]
 assert not any(c['inspection'][k]for k in ['fullScientificReviewComplete','separateCompanionContentRead','rawEMRInspected'])
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];p=c['populations'];assert not any(s[k]for k in ['randomizedASA','ASAPlateletInhibitionMeasured','causalSafetyEstablished','authorsRecommendationsAdopted'])
 assert p['mainN']==1113 and p['ASA']==57 and p['control']==1056 and p['excludedEarlyASAPause']==13
 assert p['ASAIndications']=={'primary':5,'secondary':52} and not p['ASAControlsBalanced'] and not p['newUniqueCrossCorpusPatientsAdjudicated']
 assert len(c['results'])==len(c['claims'])==4 and len(c['sourceQualifications'])==15
 a,b,d,e=[r['estimate']for r in c['results']]
 assert a['ASA']==[3,57] and a['control']==[20,1056] and a['comparisonP']==.082 and a['univariateASAOR']=={'estimate':2.78,'CI95':[.83,9.98],'P':.096}
 assert a['multivariableASAExactEstimateInMain'] is None and a['totalBleedingPatients']==23 and a['BSMSClinicallySignificant']==16 and not a['severeMajorAll23']
 assert a['mainASARetinalN']==2 and a['excludedEarlyPauseRetinalN']==1 and a['onsetMedianRangeDays']==[6,[-2,40]] and not a['causalSafetyOrEquivalence']
 assert b['GIHistoryText']=={'estimate':24.230,'CI95':[5.653,103.861],'P':'<.001'} and b['GIHistoryFigure2E']=={'estimate':24.23,'CI95':[5.563,103.861],'P':'<.001'}
 assert b['durationPLCLe50']=={'estimate':1.166,'CI95':[1.066,1.277],'P':'<.001'} and b['diarrhea']=={'estimate':4.038,'CI95':[1.693,9.632],'P':.002}
 assert b['selectionTextFigure']==['backward','forward'] and not b['GICIDiscrepancyResolved'] and not b['FirthOriginalSupplementRead']
 assert d['plateletPText']=='<.001' and d['plateletPTable2']==.007 and not d['PDiscrepancyResolved'] and not d['ASAIndependentlyIncreasesPLTXEstablished']
 assert d['plateletUnitsASA']=={'mean':1.32,'SD':1.42} and d['plateletUnitsControl']=={'mean':.78,'SD':.96} and d['PRBCP']==.354
 assert d['PTTDurationBetaPText']==[.103,'>.001'] and d['bleedingSumScoreORText']['CI95']==[.731,19.52] and d['durationPredictionR2']==.113
 assert e['mostStoppedPlateletRange20To50N']==41 and e['continuedThroughoutThrombocytopenia']==1 and e['MACEInHospitalN']==3 and e['MACEAmongASAUsers']==e['MACEAmongASAIndicationPatients']==0
 assert e['doseMg']==[75,100] and not any(e[k]for k in ['postDischargeMACEAdequatelyCaptured','plateletInhibitionDirectlyMeasured','safeBelow20Established','currentRecommendationAdopted','cancerControlBenefitEstablished'])
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for r in c['results']:assert not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for n in ['AUDIT-MANIFEST.json','READINESS.json']:
 for f,h in read(B/n).get('files',read(B/n).get('hashes',{})).items():assert sha(B/f)==h
plan=read(B/'PLAN.json');root='/Users/kmfp/papers-for-claude/remaprx-fill';assert sha(Path(plan['source']['ref'].replace('$REMAPRX_REED_ROOT',root)))==c['source']['sha256'];assert sha(Path(plan['indexRef'].replace('$REMAPRX_REED_ROOT',root)))==plan['indexSha256']
inv=read(R/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(z)for z in(B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field'])for e in es}=={(q['id'],f)for q in inv['questions']for f in q['inputFields']}
for e in es:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['sourceHash']==c['source']['sha256'] and e['status']in inv['answerStatuses']
checks=[]
def reject(n,path,v):
 x=copy.deepcopy(c);p=x
 for k in path[:-1]:p=p[k]
 p[path[-1]]=v
 try:validate(x)
 except AssertionError:checks.append(n);return
 raise AssertionError(n+' accepted')
for n,p,v in [
 ('not_randomized',['study','randomizedASA'],True),('inhibition_assumed',['study','ASAPlateletInhibitionMeasured'],True),('not_causally_safe',['study','causalSafetyEstablished'],True),('algorithm_not_adopted',['study','authorsRecommendationsAdopted'],True),('mainN_not_excluded_sum',['populations','mainN'],1126),('ASA_not_controls',['populations','ASA'],1056),('not_balanced',['populations','ASAControlsBalanced'],True),('secondary_not_primary',['populations','ASAIndications','primary'],52),('three_not_all_retinal',['results',0,'estimate','mainASARetinalN'],3),('excluded_retinal_not_main',['results',0,'estimate','excludedEarlyPauseRetinalN'],0),('univariate_not_adjusted',['results',0,'estimate','multivariableASAExactEstimateInMain'],2.78),('P082_not_significant',['results',0,'estimate','comparisonP'],.0082),('CI_crosses_one',['results',0,'estimate','univariateASAOR','CI95'],[1.83,9.98]),('not_all_major',['results',0,'estimate','severeMajorAll23'],True),('GI_text_not_figure',['results',1,'estimate','GIHistoryText','CI95'],[5.563,103.861]),('GI_figure_not_text',['results',1,'estimate','GIHistoryFigure2E','CI95'],[5.653,103.861]),('GI_conflict_unresolved',['results',1,'estimate','GICIDiscrepancyResolved'],True),('Firth_not_checked',['results',1,'estimate','FirthOriginalSupplementRead'],True),('transfusion_P_table_not_text',['results',2,'estimate','plateletPTable2'],.001),('transfusion_P_unresolved',['results',2,'estimate','PDiscrepancyResolved'],True),('PTT_typography_not_repaired',['results',2,'estimate','PTTDurationBetaPText'],[.103,'<.001']),('sumscore_CI_not_repaired',['results',2,'estimate','bleedingSumScoreORText','CI95'],[.731,1.952]),('not_all_continuous',['results',3,'estimate','continuedThroughoutThrombocytopenia'],57),('MACE_not_absent_all',['results',3,'estimate','MACEInHospitalN'],0),('postdischarge_not_captured',['results',3,'estimate','postDischargeMACEAdequatelyCaptured'],True),('below20_not_provensafe',['results',3,'estimate','safeBelow20Established'],True),('not_antitumor',['results',3,'estimate','cancerControlBenefitEstablished'],True),('not_newRCT',['newIndependentTrials'],1),('not_new_people',['newIndependentPatients'],1113),('not_scientific_acceptance',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n')
print('CAL09 PASS',len(checks),'meaningful guards, source/index/GP/10deps/67fields')
