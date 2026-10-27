"""Guard compound, dose, phase, replicate and null identities in the original source."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['inspection']['physicalPagesRead']==list(range(1,14)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['rawDataInspected']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 assert len(c['results'])==len(c['claims'])==6 and len(c['sourceQualifications'])==20
 s=c['study'];p=c['populations'];assert s['confocal']=={'MetMM':1,'BtzNM':10,'hours':18} and s['Fig2FWestern']=={'MetMM':[2,4],'BtzNM':3,'hours':18} and not s['ownAnimalStudy']
 assert not p['donorExVivoNReportedMain'] and p['independentExperimentMinimumMethods']==2 and p['technicalTriplicatesNotThreePatients'] and not p['clinicalMetforminTreatment']
 a,b,d,e,f,g=[x['estimate']for x in c['results']]
 assert a['largestMMvsMGUSHSP']=='HSPA5' and a['largestResistantVsNaiveHSP']=='HSPA8' and a['resistanceMonths']==6 and not a['clinicalMetforminTreatment']
 assert b['confocalMetMM']==1 and b['confocalBtzNM']==10 and b['hours']==18 and b['controlAggresomeFolds']=={'Btz':11,'Met':8,'pair':41} and b['autophagosomeFoldsApprox']=={'Btz':12,'Met':4} and not b['MetAndPairGRP78BelowUntreatedEstablished'] and not b['HSPA5KDPreventsAggresomes'] and not b['dynamicFluxOrDeliveryRateMeasured']
 assert d['methodsMutant']=='P495L' and d['plotLabel']=='GRP78-KDEL' and not d['verifiedKDELDeletion'] and not d['comparatorIdentityConsistent'] and not d['bodyNoMutantAssociationAllFourAccepted'] and d['visualConflict']=='HDAC6 and KDEL receptor bands retained in mutant lanes' and d['highBtzCurves']=='converge at5/10/20nM' and not d['directMetBindingOrWTMetRescueProven']
 assert e['BtzNM']==2 and e['hours']==72 and e['MetMM']==[0,.5,1,2,4,8] and e['phenforminUM']==[0,20,40,100,200,500] and not e['formalCIInteractionEstablished'] and not e['clinicalEfficacy']
 assert f['model']=='MEFs' and not f['MMAMPKKnockoutTested'] and f['drugEffectsPersistInDKO'] and not f['allAMPKContributionExcluded'] and f['apoptosisPanelModel']=='MEFs'
 assert g['model']=='U266' and g['cleaved']==['caspase3','caspase8','caspase10','PARP'] and not g['MetSpecificApoptosisTest'] and not g['Fig6BExplicitAxisUnits']
 assert not c['overlapRecords'][0]['independentSampleReplicationEstablished']
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
for n,p,v in [('Met1mM', ['study', 'confocal', 'MetMM'], 1000), ('Btz10nM', ['study', 'confocal', 'BtzNM'], 10000), ('confocal18h', ['study', 'confocal', 'hours'], 72), ('Western3nM', ['study', 'Fig2FWestern', 'BtzNM'], 10), ('noanimals', ['study', 'ownAnimalStudy'], True), ('donorNunknown', ['populations', 'donorExVivoNReportedMain'], True), ('methodsmin2', ['populations', 'independentExperimentMinimumMethods'], 3), ('HSPA8top', ['results', 0, 'estimate', 'largestResistantVsNaiveHSP'], 'HSPA5'), ('6months', ['results', 0, 'estimate', 'resistanceMonths'], 180), ('aggresome41', ['results', 1, 'estimate', 'controlAggresomeFolds', 'pair'], 4.1), ('Metstatic4', ['results', 1, 'estimate', 'autophagosomeFoldsApprox', 'Met'], 0), ('notbelowbaseline', ['results', 1, 'estimate', 'MetAndPairGRP78BelowUntreatedEstablished'], True), ('aggresomesremain', ['results', 1, 'estimate', 'HSPA5KDPreventsAggresomes'], True), ('staticnotflux', ['results', 1, 'estimate', 'dynamicFluxOrDeliveryRateMeasured'], True), ('P495L', ['results', 2, 'estimate', 'methodsMutant'], 'KDEL deletion'), ('noKDELdeletion', ['results', 2, 'estimate', 'verifiedKDELDeletion'], True), ('WTvectorconflict', ['results', 2, 'estimate', 'comparatorIdentityConsistent'], True), ('coIPconflict', ['results', 2, 'estimate', 'bodyNoMutantAssociationAllFourAccepted'], True), ('visualbands', ['results', 2, 'estimate', 'visualConflict'], 'no mutant bands'), ('highdoseconverge', ['results', 2, 'estimate', 'highBtzCurves'], 'uniform separation'), ('nodirectbinding', ['results', 2, 'estimate', 'directMetBindingOrWTMetRescueProven'], True), ('XTT2nM', ['results', 3, 'estimate', 'BtzNM'], 10), ('XTT72h', ['results', 3, 'estimate', 'hours'], 18), ('noformalCI', ['results', 3, 'estimate', 'formalCIInteractionEstablished'], True), ('noclinicalefficacy', ['results', 3, 'estimate', 'clinicalEfficacy'], True), ('MEFnotMM', ['results', 4, 'estimate', 'model'], 'MM'), ('noMMAMPKKO', ['results', 4, 'estimate', 'MMAMPKKnockoutTested'], True), ('notallAMPKexcluded', ['results', 4, 'estimate', 'allAMPKContributionExcluded'], True), ('caspase10', ['results', 5, 'estimate', 'cleaved'], ['caspase3', 'caspase8', 'PARP']), ('notMetapoptosis', ['results', 5, 'estimate', 'MetSpecificApoptosisTest'], True), ('unitgap', ['results', 5, 'estimate', 'Fig6BExplicitAxisUnits'], True), ('overlapnotreplication', ['overlapRecords', 0, 'independentSampleReplicationEstablished'], True), ('notrial', ['newIndependentTrials'], 1), ('nopeople', ['newIndependentPatients'], 33), ('noscience', ['scientificAcceptance'], True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL24 PASS',len(checks),'meaningful guards/source/index/GP/10deps/67fields')
