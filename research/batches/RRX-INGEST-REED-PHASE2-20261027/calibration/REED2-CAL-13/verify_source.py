"""Guard canonical identity, gene counts and computational-not-clinical inference."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['id']=='CP002-R01' and c['paper']['sourceType']=='original_in_silico_transcriptomic_drug_nomination'
 assert c['inspection']['physicalPagesRead']==list(range(1,10)) and not any(c['inspection'][k]for k in ['fullScientificReviewComplete','separateCompanionContentRead','rawDatasetCodeInspected'])
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];p=c['populations'];assert s['dataset']=='GSE100833 as reported' and s['sourcePatientClaimN']==327 and s['originalClinicalTreatmentN']==0 and s['candidateDoseAdministered']is None
 assert s['clustersAre']=='Gene coexpression clusters, not established patient subtypes' and s['queryThresholdAsWritten']=='Z<0.001'
 assert not any(s[k]for k in ['uniquePatientCountVerified','clinicalRemissionOrSafetyMeasured','rawGEOOrCMapReanalysisPerformed','signatureReversalEstablishedHere','clinicalRecommendationAdopted'])
 assert p['Table1DEGs']==260 and p['Table1Up']==193 and p['Table1Down']==67 and p['queryUp']==193 and p['queryDown']==65 and p['figureTotalGenes']==247
 assert p['tableClusterGenes']==[158,25,35,42] and p['figureClusterGenes']==[150,26,33,38] and not p['sourceCountDiscrepanciesResolved'] and not p['rawPatientSamplePairingVerified']
 assert len(c['results'])==len(c['claims'])==4 and len(c['sourceQualifications'])==15
 a,b,d,e=[x['estimate']for x in c['results']]
 assert a['tableDEGsUpDown']==[260,193,67] and a['queryUpDown']==[193,65] and a['figureTotalUpDown']==[247,183,64]
 assert not a['countDiscrepanciesResolved'] and not a['clustersArePatientSubtypes'] and a['cluster2PPI']=={'actual':0,'expected':0,'ratio':None,'P':1.0}
 assert b['geneCluster']==2 and b['instance']=='clomipramine-6825' and b['clusterScore']==8.4 and b['downGeneScore']==5.7 and b['allGeneScore']==2.9 and b['tiedCandidateCount']==11
 assert not any(b[k]for k in ['uniqueBestDrug','rowPositionIsEfficacyRank','negativeSignatureReversalVerified','clinicalResponseRemissionSafetyMeasured']) and b['candidateClinicalDose']is None
 assert d['CP69033401']=={'instance':'3823','score':18.8,'sourceInformationAvailable':False} and [x['score']for x in d['tiedSecondProfiles']]==[12.3,12.3,12.3]
 assert d['vorinostatHistoricalNCT']=='NCT03167437' and not any(d[k]for k in ['clomipramineCluster1','FDAForCDClaimIndependentlyVerified','currentTrialStatusVerified','ownExperimentalDrugValidation','mechanismNecessityEstablished'])
 assert not e['cluster3SignificantDrugProfileEnrichments'] and e['cluster3PathwayPPIEnrichmentPresent'] and e['cluster4Highest']['score']==6.0 and e['cluster4OtherScore']==5.9
 assert not e['nullMeansClinicalNoEffect'] and not e['headToHeadDrugEfficacyTested']
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
 ('reusecanonical',['paper','id'],'NEW_REPORT'),('not_treatmenttrial',['study','originalClinicalTreatmentN'],327),('Nnot_uniquelyverified',['study','uniquePatientCountVerified'],True),('no_clinicaldose',['study','candidateDoseAdministered'],25),('geneclusters_notpatients',['results',0,'estimate','clustersArePatientSubtypes'],True),('countconflict_unresolved',['results',0,'estimate','countDiscrepanciesResolved'],True),('Table_not_querygenes',['results',0,'estimate','tableDEGsUpDown'],[258,193,65]),('query_not_tablegenes',['results',0,'estimate','queryUpDown'],[193,67]),('figure_not_tablegenes',['results',0,'estimate','figureTotalUpDown'],[260,193,67]),('cluster2_PPI_null',['results',0,'estimate','cluster2PPI','P'],.001),('cluster2_not1',['results',1,'estimate','geneCluster'],1),('score8point4_notpercent',['results',1,'estimate','clusterScore'],.084),('downscore_notcluster',['results',1,'estimate','downGeneScore'],8.4),('allscore_retained',['results',1,'estimate','allGeneScore'],8.4),('eleven_tied',['results',1,'estimate','tiedCandidateCount'],1),('not_uniquebest',['results',1,'estimate','uniqueBestDrug'],True),('rownot_efficacyrank',['results',1,'estimate','rowPositionIsEfficacyRank'],True),('reversal_not_verified',['results',1,'estimate','negativeSignatureReversalVerified'],True),('no_clinicaloutcomes',['results',1,'estimate','clinicalResponseRemissionSafetyMeasured'],True),('unknownCPinfo',['results',2,'estimate','CP69033401','sourceInformationAvailable'],True),('clomipramine_notcluster1',['results',2,'estimate','clomipramineCluster1'],True),('FDAclaim_not_checked',['results',2,'estimate','FDAForCDClaimIndependentlyVerified'],True),('trialstatus_notcurrent',['results',2,'estimate','currentTrialStatusVerified'],True),('no_own_drugvalidation',['results',2,'estimate','ownExperimentalDrugValidation'],True),('cluster3_drugnull',['results',3,'estimate','cluster3SignificantDrugProfileEnrichments'],True),('null_notclinicalnoeffect',['results',3,'estimate','nullMeansClinicalNoEffect'],True),('no_headtohead',['results',3,'estimate','headToHeadDrugEfficacyTested'],True),('not_newRCT',['newIndependentTrials'],1),('not_newpatients',['newIndependentPatients'],327),('not_scienceapproval',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL13 PASS',len(checks),'meaningfulguards/source/index/GP/10deps/67fields')
