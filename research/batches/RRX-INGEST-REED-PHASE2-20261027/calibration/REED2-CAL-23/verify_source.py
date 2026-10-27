"""Guard compound, dose, phase, replicate and null identities in the original source."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['inspection']['physicalPagesRead']==list(range(1,9)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['rawDataInspected']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 assert len(c['results'])==len(c['claims'])==5 and len(c['sourceQualifications'])==19
 s=c['study'];p=c['populations'];assert s['mainMetforminUM']==500 and s['mainBortezomibNM']==5 and s['assayTimes']['XTT']==72 and s['assayTimes']['confocal']==16 and not p['donorExVivoNReportedMain'] and p['technicalTriplicatesNotThreePatients']
 a,b,d,e,f=[x['estimate']for x in c['results']]
 assert a['earlyBtzBrdU8h']=='increase' and not a['SPExclusiveStemCellIdentityProven']
 assert b['MetAlone500uMApoptosis']=='not promoted' and b['MetAloneColony']=='not significantly reduced,main narrative ofS4' and not b['formalCIInteractionEstablished'] and not b['donorNMainReported']
 assert d['MetAloneGRP78Western']=='slight increase' and d['MetAloneStaticAutophagosomeFoldApprox']==4 and d['BtzStaticAutophagosomeFoldApprox']==9 and d['BafilomycinNM']==100 and d['BafilomycinFinalHours']==4 and d['sourceFluxStatement']=='Btz,Met,pair increased autophagic flux' and not d['allFluxUniformlyInhibited'] and not d['directMetGRP78BindingOrRescueProven']
 assert e['BtzNonresponders']==86 and e['BtzResponders']==83 and not e['clinicalMetforminTreatment'] and not e['primaryCohortOriginalIndependentlyRead'] and not e['supplementExpressionPanelsRead']
 assert f['micePerGroup']==10 and f['groups']==4 and f['BtzMGkgIV']==.5 and f['MetWaterUgML']==600 and f['BtzDays']==[1,2,3,4] and f['medianEndpointDays']=={'vehicle':17,'Met':18,'Btz':22,'pair':27} and f['endpoint']=='humane tumor/functional thresholds' and not f['clinicalSurvivalBenefit'] and not f['comprehensiveToxicityVerified']
 assert f['medianEndpointDaysBasis']=='attributed body text only, not curve-verified' and f['bodyMedianCurveAgreementUnresolved']
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
for n,p,v in [('Met500uM', ['study', 'mainMetforminUM'], 500000), ('Btz5nM', ['study', 'mainBortezomibNM'], 5000), ('XTT72h', ['study', 'assayTimes', 'XTT'], 24), ('confocal16h', ['study', 'assayTimes', 'confocal'], 72), ('donorNunknown', ['populations', 'donorExVivoNReportedMain'], True), ('tripnotpatients', ['populations', 'technicalTriplicatesNotThreePatients'], False), ('earlyBrdUincrease', ['results', 0, 'estimate', 'earlyBtzBrdU8h'], 'decrease'), ('SPnotexclusivestem', ['results', 0, 'estimate', 'SPExclusiveStemCellIdentityProven'], True), ('Metalonenull', ['results', 1, 'estimate', 'MetAlone500uMApoptosis'], 'promoted'), ('colonyNS', ['results', 1, 'estimate', 'MetAloneColony'], 'significant reduction'), ('noformalCI', ['results', 1, 'estimate', 'formalCIInteractionEstablished'], True), ('MetGRPslightup', ['results', 2, 'estimate', 'MetAloneGRP78Western'], 'decrease'), ('Metstatic4', ['results', 2, 'estimate', 'MetAloneStaticAutophagosomeFoldApprox'], 0), ('Baf100nM', ['results', 2, 'estimate', 'BafilomycinNM'], 100000), ('Baf4h', ['results', 2, 'estimate', 'BafilomycinFinalHours'], 24), ('fluxbodyretained', ['results', 2, 'estimate', 'sourceFluxStatement'], 'all decreased flux'), ('notuniformblockade', ['results', 2, 'estimate', 'allFluxUniformlyInhibited'], True), ('notMetdirectbinding', ['results', 2, 'estimate', 'directMetGRP78BindingOrRescueProven'], True), ('GEP86', ['results', 3, 'estimate', 'BtzNonresponders'], 83), ('GEP83', ['results', 3, 'estimate', 'BtzResponders'], 86), ('notMetclinical', ['results', 3, 'estimate', 'clinicalMetforminTreatment'], True), ('noGEPprimaryread', ['results', 3, 'estimate', 'primaryCohortOriginalIndependentlyRead'], True), ('mice10', ['results', 4, 'estimate', 'micePerGroup'], 3), ('Btzpoint5', ['results', 4, 'estimate', 'BtzMGkgIV'], 5), ('water600', ['results', 4, 'estimate', 'MetWaterUgML'], 600000), ('pair27days', ['results', 4, 'estimate', 'medianEndpointDays', 'pair'], 22), ('humaneendpoint', ['results', 4, 'estimate', 'endpoint'], 'natural mortality only'), ('noclinicalsurvival', ['results', 4, 'estimate', 'clinicalSurvivalBenefit'], True), ('nottoxicityproof', ['results', 4, 'estimate', 'comprehensiveToxicityVerified'], True), ('notrial', ['newIndependentTrials'], 1), ('nopeople', ['newIndependentPatients'], 169), ('KMconflict', ['results',4,'estimate','bodyMedianCurveAgreementUnresolved'], False), ('noscience', ['scientificAcceptance'], True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL23 PASS',len(checks),'meaningful guards/source/index/GP/10deps/67fields')
