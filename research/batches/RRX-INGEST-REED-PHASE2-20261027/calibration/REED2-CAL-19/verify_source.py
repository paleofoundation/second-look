"""Guard compound, dose, phase, replicate and null identities in the original source."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['inspection']['physicalPagesRead']==list(range(1,20)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['rawDataInspected']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 assert len(c['results'])==len(c['claims'])==6 and len(c['sourceQualifications'])==20
 s=c['study'];p=c['populations'];assert s['cellLines']==['H929','MM.1S'] and s['mainCultureMM']==[10,20] and s['drugTimeHours']==48 and s['cultureMetforminMM']==[0,2.5,5,10,20,40]
 assert p['technicalWellsPerCCK8Group']==5 and p['cellFigureN']==3 and not p['cellBiologicalReplicateHierarchyVerified'] and p['clinicalDrugTreatedPatients']==0
 a,b,d,e,f,g=[x['estimate']for x in c['results']]
 assert a['metforminMainMM']==[10,20] and a['hours']==48 and not a['exactAggregateMeansDigitized'] and not a['clinicalDoseEstablished']
 assert b['METTL3']=='decrease' and b['WTAP']=='increase' and b['FTOFigureBothLines']=='decrease' and b['ALKBH5']=='increaseMM1S_notH929' and b['OE']=='partial rescue' and b['KDOnMetProliferationApoptosis']=='no significant additional effect' and not b['completeNecessarySolePathwayProven']
 assert d['MMBloodSamplesAsReported']==92 and d['normalBloodSamplesAsReported']==23 and d['heatmapSubsetPerGroup']==8 and d['reportedDEGs']==21601 and d['GOupregulatedSubset']==300 and d['hubGenes']==22 and d['downregulatedTranscripts']==8 and d['proteinBandsShown']==9 and not d['sourceCountsReconciled'] and not d['clinicalDrugResponseMeasured']
 assert e['targets']==['THRAP3','RBM25','USP4'] and e['METTL3OE']=='partial expression/stability restoration' and not any(e[k]for k in ['directMETTL3BindingSiteValidated','catalyticMutantRescue','DNMT3ABMechanismDemonstrated'])
 assert f['onMetBackground']=='no significant extra transcript/proliferation/apoptosis changes' and not f['tripleSimultaneousKDTestClaimed'] and not f['formalSynergy']
 assert g['micePerGroupMethods']==5 and g['figureN']==3 and g['methodsMetformin']=='oral drinkingwater2mg/mL' and g['resultsMetformin']=='250mg/kg/injection wording' and not any(g[k]for k in ['routeDoseResolved','allocatedAnalyzedReconciled','animalSurvivalMeasured','humanClinicalEfficacy','inVivoKDSensitivityTest']) and g['endDay']==35
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
for n,p,v in [('mMnotuM', ['study', 'mainCultureMM'], [0.01, 0.02]), ('48h', ['study', 'drugTimeHours'], 24), ('dose40shown', ['study', 'cultureMetforminMM'], [0, 2.5, 5, 10, 20]), ('technicalwells', ['populations', 'technicalWellsPerCCK8Group'], 15), ('not15biological', ['populations', 'cellBiologicalReplicateHierarchyVerified'], True), ('notclinical', ['populations', 'clinicalDrugTreatedPatients'], 115), ('no_digitization', ['results', 0, 'estimate', 'exactAggregateMeansDigitized'], True), ('no_dosefeasibility', ['results', 0, 'estimate', 'clinicalDoseEstablished'], True), ('WTAPup', ['results', 1, 'estimate', 'WTAP'], 'decrease'), ('FTOdown', ['results', 1, 'estimate', 'FTOFigureBothLines'], 'unchanged'), ('ALKBH5line_specific', ['results', 1, 'estimate', 'ALKBH5'], 'increaseboth'), ('partialrescue', ['results', 1, 'estimate', 'OE'], 'complete rescue'), ('KDtreatednull', ['results', 1, 'estimate', 'KDOnMetProliferationApoptosis'], 'significant extra effect'), ('not_solepath', ['results', 1, 'estimate', 'completeNecessarySolePathwayProven'], True), ('GEO92', ['results', 2, 'estimate', 'MMBloodSamplesAsReported'], 115), ('normal23', ['results', 2, 'estimate', 'normalBloodSamplesAsReported'], 8), ('subset8', ['results', 2, 'estimate', 'heatmapSubsetPerGroup'], 92), ('genes8vs9', ['results', 2, 'estimate', 'proteinBandsShown'], 8), ('no_countrepair', ['results', 2, 'estimate', 'sourceCountsReconciled'], True), ('not_treatedomics', ['results', 2, 'estimate', 'clinicalDrugResponseMeasured'], True), ('no_directbinding', ['results', 3, 'estimate', 'directMETTL3BindingSiteValidated'], True), ('no_mutantrescue', ['results', 3, 'estimate', 'catalyticMutantRescue'], True), ('DNMTspeculation', ['results', 3, 'estimate', 'DNMT3ABMechanismDemonstrated'], True), ('individualnottriple', ['results', 4, 'estimate', 'tripleSimultaneousKDTestClaimed'], True), ('no_synergy', ['results', 4, 'estimate', 'formalSynergy'], True), ('mice5methods', ['results', 5, 'estimate', 'micePerGroupMethods'], 3), ('FigN3', ['results', 5, 'estimate', 'figureN'], 5), ('routeheld', ['results', 5, 'estimate', 'routeDoseResolved'], True), ('Nheld', ['results', 5, 'estimate', 'allocatedAnalyzedReconciled'], True), ('nosurvival', ['results', 5, 'estimate', 'animalSurvivalMeasured'], True), ('no_invivoKD', ['results', 5, 'estimate', 'inVivoKDSensitivityTest'], True), ('nohumanbenefit', ['results', 5, 'estimate', 'humanClinicalEfficacy'], True), ('no_newtrial', ['newIndependentTrials'], 1), ('no_newpeople', ['newIndependentPatients'], 92), ('no_science', ['scientificAcceptance'], True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL19 PASS',len(checks),'meaningful guards/source/index/GP/10deps/67fields')
