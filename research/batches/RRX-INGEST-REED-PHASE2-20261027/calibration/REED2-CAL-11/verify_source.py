"""Keep a mechanistic correspondence separate from original clinical evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='correspondence_mechanistic_caution_no_original_data' and c['paper']['doi']=='10.1111/j.1365-2141.2006.06050.x'
 assert c['inspection']['physicalPagesRead']==c['inspection']['visualInspectedPhysicalPages']==[1] and not c['inspection']['citedPrimaryStudiesRead'] and not c['inspection']['fullScientificReviewComplete']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];assert s['author']=='R. E. Kast' and s['originalParticipantN']is None and s['originalExperiments']==s['originalClinicalOutcomes']==0
 assert s['sourceDOI']=='10.1111/j.1365-2141.2006.06050.x' and s['unrelatedPageHeaderDOIExcluded']=='10.1111/j.1365-2141.2006.06048.x'
 assert not any(s[k]for k in ['clinicalASAHarmDemonstratedHere','bupropionReversalDemonstratedHere','monitoringRecommendationAdopted'])
 p=c['populations'];assert p['ownCohortN']is None and not p['newUniqueCrossCorpusPatientsAdjudicated'] and p['originalParticipantCountNotZeroOutcome']
 assert len(c['results'])==len(c['claims'])==1 and len(c['sourceQualifications'])==10
 e=c['results'][0]['estimate'];assert e['kind']=='narrative_mechanistic_hypothesis_only' and e['originalQuantitativeResult']is None and e['proposedTNFElevation']
 assert not any(e[k]for k in ['measuredAspirinTNFMMChainHere','clinicalASAHarmDemonstrated','bupropionReversalDemonstrated','monitoringRecommendationAdopted','newIndependentClinicalSupport'])
 assert e['81mgDay']=='CitedHassounregimencontext_notnewexposure'
 assert c['results'][0]['sourceLocators'][0]['printedPage']==216 and c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
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
 ('commentary_not_RCT',['paper','sourceType'],'RCT'),('DOI_not_precedingletter',['paper','doi'],'10.1111/j.1365-2141.2006.06048.x'),('author_not_priorletter',['study','author'],'Zecca'),('no_originalN',['study','originalParticipantN'],81),('no_originalexperiment',['study','originalExperiments'],1),('no_originaloutcome',['study','originalClinicalOutcomes'],1),('ASA_harm_not_proven',['study','clinicalASAHarmDemonstratedHere'],True),('bupropion_reversal_not_proven',['study','bupropionReversalDemonstratedHere'],True),('monitoring_not_adopted',['study','monitoringRecommendationAdopted'],True),('no_owncohort',['populations','ownCohortN'],81),('missingN_not_zeroevents',['populations','originalParticipantCountNotZeroOutcome'],False),('hypothesis_not_quantitative',['results',0,'estimate','kind'],'clinical_effect'),('no_effectestimate',['results',0,'estimate','originalQuantitativeResult'],.81),('chain_not_measured',['results',0,'estimate','measuredAspirinTNFMMChainHere'],True),('no_newclinicalsupport',['results',0,'estimate','newIndependentClinicalSupport'],True),('dose_is_cited',['results',0,'estimate','81mgDay'],'owntrialdose'),('not_newRCT',['newIndependentTrials'],1),('not_newpatients',['newIndependentPatients'],81),('citedoriginals_unread',['inspection','citedPrimaryStudiesRead'],True),('not_fullscience',['inspection','fullScientificReviewComplete'],True),('printed216',['results',0,'sourceLocators',0,'printedPage'],1),('no_scienceapproval',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL11 PASS',len(checks),'meaningfulguards/source/index/GP/10deps/67fields')
