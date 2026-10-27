"""Guard compound, dose, phase, replicate and null identities in the original source."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['inspection']['physicalPagesRead']==list(range(1,17)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['rawDataInspected']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 assert len(c['results'])==len(c['claims'])==6 and len(c['sourceQualifications'])==16
 s=c['study'];assert s['MTTModels']==['U266','RPMI8226','LP-1','NCI-H929'] and s['mechanisticModels']==['RPMI8226','U266'] and s['MTTHours']==48 and s['mechanisticHours']==24 and s['metforminMainMM']==20 and s['FTY720MainUM']==20 and s['NACmM']==5 and not s['otherModelsPatientsAnimals']
 a,b,d,e,f,g=[x['estimate']for x in c['results']]
 assert a['sourceU266SDAtFTY20']==22 and a['MetIC50MM_meanSD_pairsByFTY0_5_10_20'][0][-1]==22 and a['FTYIC50UM_meanSD_pairsByMet0_5_10_20'][3][0]==72.4 and a['methodsSoftware']=='CalcuSyn' and a['figureSoftware']=='CompuSyn' and not a['independentCIReproduction'] and not a['clinicalSynergy']
 assert b['caspaseAssay']=='caspase3/7kit' and b['Bax']=='pair increases,singles little effect' and not b['ELISAFractionDeadCalibrationEstablished']
 assert d['ATF4KD']=='attenuates pair viabilityloss/apoptotic signal' and not d['directGRP78KDTested'] and not d['fullSpecificNecessaryPathwayProven']
 assert e['mTOR']=='total protein decrease' and e['myrAkt']=='partial viability/apoptosis rescue' and not e['directmTORKinaseActivityMeasured'] and not e['completeDrugEffectAbolition']
 assert f['NACmM']==5 and f['rescue']=='partial,not all outcomes baseline' and not f['specificROSSpeciesMitoSourceProven'] and not f['geneticRedoxNecessityProven']
 assert g['AMPKActivation']=='not observed, data not shown' and not g['rawNegativeDataInspected'] and not g['AMPKPositiveMechanismAdopted']
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
for n,p,v in [('fourMTTlines', ['study', 'MTTModels'], ['U266', 'RPMI8226']), ('twomechanistic', ['study', 'mechanisticModels'], ['U266', 'RPMI8226', 'LP-1', 'NCI-H929']), ('MTT48', ['study', 'MTTHours'], 24), ('mechanism24', ['study', 'mechanisticHours'], 48), ('Met20mM', ['study', 'metforminMainMM'], 0.02), ('FTY20uM', ['study', 'FTY720MainUM'], 20000), ('NAC5mM', ['study', 'NACmM'], 20), ('noanimals', ['study', 'otherModelsPatientsAnimals'], True), ('literalSD22', ['results', 0, 'estimate', 'sourceU266SDAtFTY20'], 2.2), ('tableSD22', ['results', 0, 'estimate', 'MetIC50MM_meanSD_pairsByFTY0_5_10_20', 0, 7], 2.2), ('FTY72point4', ['results', 0, 'estimate', 'FTYIC50UM_meanSD_pairsByMet0_5_10_20', 3, 0], 7.24), ('methodCalcu', ['results', 0, 'estimate', 'methodsSoftware'], 'CompuSyn'), ('captionCompu', ['results', 0, 'estimate', 'figureSoftware'], 'CalcuSyn'), ('noreproduction', ['results', 0, 'estimate', 'independentCIReproduction'], True), ('noclinicalsynergy', ['results', 0, 'estimate', 'clinicalSynergy'], True), ('kit3and7', ['results', 1, 'estimate', 'caspaseAssay'], 'caspase3only'), ('notdeadfraction', ['results', 1, 'estimate', 'ELISAFractionDeadCalibrationEstablished'], True), ('notGRP78KD', ['results', 2, 'estimate', 'directGRP78KDTested'], True), ('notsoleERpathway', ['results', 2, 'estimate', 'fullSpecificNecessaryPathwayProven'], True), ('totalmTOR', ['results', 3, 'estimate', 'mTOR'], 'phosphorylated mTOR'), ('partialAktrescue', ['results', 3, 'estimate', 'myrAkt'], 'complete rescue'), ('notkinaseactivity', ['results', 3, 'estimate', 'directmTORKinaseActivityMeasured'], True), ('notabolition', ['results', 3, 'estimate', 'completeDrugEffectAbolition'], True), ('NACdose', ['results', 4, 'estimate', 'NACmM'], 0.005), ('partialNAC', ['results', 4, 'estimate', 'rescue'], 'all outcomes baseline'), ('notROSspecies', ['results', 4, 'estimate', 'specificROSSpeciesMitoSourceProven'], True), ('notgeneticROS', ['results', 4, 'estimate', 'geneticRedoxNecessityProven'], True), ('AMPKnegative', ['results', 5, 'estimate', 'AMPKActivation'], 'activated'), ('AMPKrawunseen', ['results', 5, 'estimate', 'rawNegativeDataInspected'], True), ('noAMPKpositive', ['results', 5, 'estimate', 'AMPKPositiveMechanismAdopted'], True), ('notrial', ['newIndependentTrials'], 1), ('nopeople', ['newIndependentPatients'], 4), ('noscience', ['scientificAcceptance'], True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL22 PASS',len(checks),'meaningful guards/source/index/GP/10deps/67fields')
