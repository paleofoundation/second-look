"""Guard secondary incidence scope and observational meta-analysis identity."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='secondary_observational_incidence_systematic_review' and c['inspection']['physicalPagesRead']==list(range(1,7))
 assert not any(c['inspection'][k]for k in ['fullScientificReviewComplete','separateCompanionContentRead','primaryStudiesRead'])
 assert not any(c[k]for k in ['scientificAcceptance','humanApproval','released']) and c['newIndependentTrials']==c['newIndependentPatients']==0
 s=c['study'];p=c['populations'];assert s['searchCutoff']=='2016-04-11' and not s['searchLanguageRestricted'] and s['includedArticlesEnglishOnly']
 assert not any(s[k]for k in ['causalPreventionEstablished','postDiagnosisTreatmentBenefitEstablished','allFiveStudiesPooled','originalStudiesFreshlyVerified'])
 assert p['reviewStudies']==5 and p['prospectiveCohortReports']==3 and p['caseControlReports']==2 and p['sourceTotalAdults']==332660 and p['sourceTotalCases']==901
 assert p['caseControlN']==1470 and p['caseControlCases']==296 and not p['all901PureMMVerified'] and not p['newUniqueCrossCorpusPatientsAdjudicated']
 assert p['series'][-1]['cases']==66 and 'plasma-cell' in p['series'][-1]['endpointFootnote']
 assert len(c['results'])==len(c['claims'])==3 and len(c['sourceQualifications'])==15
 a,b,d=[x['estimate']for x in c['results']]
 assert a['kind']=='secondary_observational_pooled_adjusted_HR'
 assert a['reports']==3 and a['estimate']==.90 and a['CI95']==[.58,1.39] and a['P']==.638 and a['randomEffects']
 assert not any(a[k]for k in ['allFivePooled','causalPrevention','equivalenceOrNoEffect'])
 assert a['forest']==[{'name':'Teras2013','HR':1.04,'CI95':[.63,1.73],'weightPercent':34.36},{'name':'Birmann2013','HR':.63,'CI95':[.41,.96],'weightPercent':40.33},{'name':'Walter2011','HR':1.31,'CI95':[.67,2.57],'weightPercent':25.32}]
 assert b['reports']==2 and b['subjects']==1470 and b['cases']==296 and b['ORs']==[{'estimate':.90,'CI95':[.65,1.49]},{'estimate':.90,'CI95':[.40,2.00]}]
 assert not any(b[k]for k in ['authorEstimatePairingVerifiedFromParagraph','pooledWithCohorts','clinicalEquivalenceEstablished'])
 assert d['I2Percent']==51.7 and d['QP']==.126 and d['EggerP']==.25 and d['cohortReports']==3
 assert not any(d[k]for k in ['heterogeneityAbsentEstablished','publicationBiasAbsentEstablished','originalSupplementPlotsRead','primaryQualityGradeIndependentlyAssigned','currentEvidenceComplete'])
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for x in c['results']:assert x['grade'] is None and x['benefitGrade'] is None and not x['acceptedSupport']
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
 ('not_original_trial',['paper','sourceType'],'RCT'),('three_not_five_pooled',['results',0,'estimate','reports'],5),('CI_not_selected_Birmann',['results',0,'estimate','CI95'],[.41,.96]),('pooled_not_significant',['results',0,'estimate','P'],.038),('not_causal_prevention',['study','causalPreventionEstablished'],True),('not_postdiagnosis_efficacy',['study','postDiagnosisTreatmentBenefitEstablished'],True),('all5_not_pooled',['study','allFiveStudiesPooled'],True),('primary_not_verified',['study','originalStudiesFreshlyVerified'],True),('English_only_included',['study','includedArticlesEnglishOnly'],False),('historical_search_not_current',['study','searchCutoff'],'2026-10-27'),('no_absence_effect',['results',0,'estimate','equivalenceOrNoEffect'],True),('cohort_not_CC_OR',['results',0,'estimate','kind'],'OR'),('CC_not_pooled',['results',1,'estimate','pooledWithCohorts'],True),('CC_pairing_not_assigned',['results',1,'estimate','authorEstimatePairingVerifiedFromParagraph'],True),('CCnotall_N',['results',1,'estimate','subjects'],332660),('CC_OR_CI_literal',['results',1,'estimate','ORs',0,'CI95'],[.65,1.24]),('heterogeneity_not_absent',['results',2,'estimate','heterogeneityAbsentEstablished'],True),('publicationbias_not_excluded',['results',2,'estimate','publicationBiasAbsentEstablished'],True),('I2_moderate_retained',['results',2,'estimate','I2Percent'],0),('Qnot_effectP',['results',2,'estimate','QP'],.638),('Egger_not_significant',['results',2,'estimate','EggerP'],.025),('supplement_not_read',['results',2,'estimate','originalSupplementPlotsRead'],True),('NOSnot_new_grade',['results',2,'estimate','primaryQualityGradeIndependentlyAssigned'],True),('not_all_pureMM',['populations','all901PureMMVerified'],True),('Walter_cases_retained',['populations','series',4,'cases'],0),('not_newpatients',['newIndependentPatients'],332660),('not_newRCT',['newIndependentTrials'],5),('not_currentcomplete',['results',2,'estimate','currentEvidenceComplete'],True),('forest_Walter_not_benefit',['results',0,'estimate','forest',2,'HR'],.31),('not_scientificacceptance',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n')
print('CAL10 PASS',len(checks),'meaningful guards, source/index/GP/10deps/67fields')
