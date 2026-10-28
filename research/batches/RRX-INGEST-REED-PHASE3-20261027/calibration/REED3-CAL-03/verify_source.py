from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def at(c,path):
 for k in path:c=c[k]
 return c
EXPECTATIONS=[('MetuMnotmM', ['study', 'MetBlotUM'], [0, 40, 80, 120]), ('Metblot16h', ['study', 'MetBlotHours'], 16), ('notclinical', ['study', 'ownClinicalTreatmentTrial'], False), ('MetIP200', ['study', 'MetSystemic', 'MetmgkgIP'], 200), ('Metq2d', ['study', 'MetSystemic', 'everyDays'], 2), ('Met3wk', ['study', 'MetSystemic', 'treatmentWeeks'], 3), ('RemIP10', ['study', 'MetSystemic', 'remodelinmgkgIP'], 10), ('Pimoral10', ['study', 'MetSystemic', 'pimozidemgkgOral'], 10), ('IV1million', ['study', 'MetSystemic', 'Vk12598CellsIV'], 1000000), ('Metburden5', ['study', 'MetSystemic', 'burdenN'], 5), ('Metseparatesurvival6', ['study', 'MetSystemic', 'separateSurvivalN'], 6), ('MSpooledn1', ['results', 2, 'estimate', 'pooledIPMSNPerCondition'], 1), ('DIOserumNS', ['results', 0, 'estimate', 'DIO2DGvsVehicleP', 'serum'], 0.1172), ('DIOboneNS', ['results', 0, 'estimate', 'DIO2DGvsVehicleP', 'boneFlow'], 0.1923), ('DIOspleenNS', ['results', 0, 'estimate', 'DIO2DGvsVehicleP', 'spleenFlow'], 0.0557), ('ADweightNS', ['results', 0, 'estimate', 'pairedSCAD2DGWeightP'], 0.8401), ('ADKi67NS', ['results', 0, 'estimate', 'pairedSCAD2DGKi67P'], 0.544), ('fieldsnotmice', ['results', 0, 'estimate', 'fieldsAreMice'], False), ('flowN3', ['results', 0, 'estimate', 'flowN'], 3), ('2DGIP500', ['results', 0, 'estimate', 'DIO2DGmgkgIPDaily'], 500), ('metabolomicsnormal5', ['results', 1, 'estimate', 'normalBiologicalN'], 5), ('metabolomicsGD7', ['results', 1, 'estimate', 'GDBiologicalN'], 7), ('differential286', ['results', 1, 'estimate', 'metabolomicsDifferential'], 286), ('betaOHBdosecontexts', ['results', 1, 'estimate', 'Figure2gBetaOHBMM'], [0.5, 1]), ('ADWT2DGnull', ['results', 1, 'estimate', 'ADWT2DGWeightP'], 0.9999), ('rescuepartial', ['results', 1, 'estimate', 'fullViabilityRescue'], False), ('CHX50', ['results', 2, 'estimate', 'CHXugML'], 50), ('CHXtimecourse', ['results', 2, 'estimate', 'hours'], [0, 3, 6, 9]), ('BTZ50nM', ['results', 2, 'estimate', 'BTZnM'], 50), ('17AAG2uM', ['results', 2, 'estimate', '17AAGUM'], 2), ('notdirectMetbinding', ['results', 2, 'estimate', 'directMetBindingProven'], False), ('Metpaneltimeunknown', ['results', 3, 'estimate', 'everyMetPanelExactDoseTimeKnown'], False), ('GDfractionation12h', ['results', 3, 'estimate', 'GDfractionationHours'], 12), ('notallMetnecessity', ['results', 3, 'estimate', 'allMetMechanismsGeneticallyProvenNecessary'], False), ('kinaseATP200', ['results', 3, 'estimate', 'kinase', 'ATPUM'], 200), ('kinase30min', ['results', 3, 'estimate', 'kinase', 'minutes'], 30), ('TRIM21knockdown', ['results', 4, 'estimate', 'knockdown'], 'shRNA#1/#2, not knockout'), ('TRIM21normalnull', ['results', 4, 'estimate', 'normalGlucoseIRF4'], 'no marked change'), ('TRIM21partial', ['results', 4, 'estimate', 'GDRescue'], 'partial'), ('IRF4diagram450', ['results', 4, 'estimate', 'fullLengthDiagram'], 450), ('IRF4methods451', ['results', 4, 'estimate', 'fullLengthMethodsAndBlot'], 451), ('notexclusiveaffinity', ['results', 4, 'estimate', 'exclusiveBindingAffinityEstablished'], False), ('betaOHB2mM', ['results', 5, 'estimate', 'betaOHBMM'], 2), ('K87acP0502', ['results', 5, 'estimate', 'AD2DGK87acP'], 0.0502), ('K87acNS', ['results', 5, 'estimate', 'AD2DGK87acSignificant'], False), ('notfullmutantrescue', ['results', 5, 'estimate', 'allViabilityLossPrevented'], False), ('NAT10screen10uM', ['results', 6, 'estimate', 'screenInhibitorUM'], 10), ('KAT2Bchemicaleffect', ['results', 6, 'estimate', 'NSC694623AlsoReducesIRF4Viability'], True), ('NAT10independent3', ['results', 6, 'estimate', 'NAT10PurifiedAssayIndependentN'], 3), ('MetRemWTcontrast', ['results', 6, 'estimate', 'MetRemvsMetP', 'WT'], 2.47e-11), ('MetRemK87QNS', ['results', 6, 'estimate', 'MetRemvsMetP', 'K87Q'], 0.1343), ('MetRemexactdoseunknown', ['results', 6, 'estimate', 'Figure7lExactMetRemDoseTime'], None), ('notisotopetracing', ['results', 6, 'estimate', 'betaOHBCarbonIsotopeTracing'], False), ('notOXCT1geneticproof', ['results', 6, 'estimate', 'mainObservedOXCT1GeneticRescue'], False), ('IHC26', ['results', 7, 'estimate', 'IHCN'], 26), ('IHCnegativeR', ['results', 7, 'estimate', 'IHCpAMPKIRF4SpearmanR'], -0.6551), ('cellline9notpatients', ['results', 7, 'estimate', 'cellLineN'], 9), ('GEO559', ['results', 7, 'estimate', 'GEO', 'MM'], 559), ('GEOhealthy22', ['results', 7, 'estimate', 'GEO', 'healthy'], 22), ('CoMMpass859', ['results', 7, 'estimate', 'CoMMpass', 'total'], 859), ('survivalfiguretest', ['results', 7, 'estimate', 'NAT10FigureTest'], 'two-sided Gehan-Breslow-Wilcoxon'), ('noadjustedHR', ['results', 7, 'estimate', 'adjustedHR'], None), ('noMetpatients', ['results', 7, 'estimate', 'ownMetTreatedPatients'], 0), ('ZIPRem24point279', ['results', 8, 'estimate', 'MetRemScore'], 24.279), ('ZIPPim22point137', ['results', 8, 'estimate', 'MetPimScore'], 22.137), ('ZIPvsBlissunresolved', ['results', 8, 'estimate', 'modelNamingResolved'], False), ('Metmatrix100to180', ['results', 8, 'estimate', 'MetUM'], [100, 120, 140, 160, 180]), ('Remmatrix1to8', ['results', 8, 'estimate', 'RemUM'], [1, 2, 4, 6, 8]), ('Pimmatrix1to16', ['results', 8, 'estimate', 'PimUM'], [1, 2, 6, 8, 10, 12, 16]), ('matrixdurationunknown', ['results', 8, 'estimate', 'matrixHours'], None), ('Fig8cdnotMet', ['results', 8, 'estimate', 'figure8cdDrug'], '2DG, NOTMet'), ('notformalinvivointeraction', ['results', 8, 'estimate', 'formalInvivoInteractionEstimate'], None), ('notdigitizedHRmedian', ['results', 8, 'estimate', 'reconstructedHRorMedian'], False), ('ADFPimketoneNS', ['results', 9, 'estimate', 'PimVsControlKetonesP'], 0.2741), ('ADFPimketoneP', ['results', 9, 'estimate', 'ADFPimVsADFKetonesP'], 0.0012), ('ADFnotclinicalMet', ['results', 9, 'estimate', 'clinicalFastingOrMetTreatmentInference'], False), ('notrial', ['newIndependentTrials'], 0), ('nopeople', ['newIndependentPatients'], 0), ('noscience', ['scientificAcceptance'], False), ('nohuman', ['humanApproval'], False), ('norelease', ['released'], False)]

def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['inspection']['physicalPagesRead']==list(range(1,57)) and c['inspection']['visualInspectedPhysicalPages']==list(range(49,57)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['rawDataInspected'] and not c['inspection']['separateCompanionContentRead']
 assert len(c['results'])==len(c['claims'])==10 and len(c['sourceQualifications'])==30
 for name,path,value in EXPECTATIONS:assert at(c,path)==value,name
 bindings=[{'resultId':r['id'],'estimate':r['estimate'],'sourceLocators':r['sourceLocators']}for r in c['results']]
 union={json.dumps(z,sort_keys=True):z for r in c['results']for z in r['sourceLocators']};locs=sorted(union.values(),key=lambda z:(z['physicalPage'],json.dumps(z,sort_keys=True)))
 assert c['reviewInputs'][5]['sourceLocators']==locs and json.loads(c['reviewInputs'][5]['answer'])==bindings
 assert c['reviewInputs'][8]['status']=='partial'
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for x in c['results']:assert x['grade']is None and x['benefitGrade']is None and not x['acceptedSupport']
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for n in ['AUDIT-MANIFEST.json','READINESS.json']:
 for f,h in read(B/n).get('files',read(B/n).get('hashes',{})).items():assert sha(B/f)==h
p=read(B/'PLAN.json');root='/Users/kmfp/papers-for-claude/remaprx-fill';assert sha(Path(p['source']['ref'].replace('$REMAPRX_REED_ROOT',root)))==c['source']['sha256'];assert sha(Path(p['indexRef'].replace('$REMAPRX_REED_ROOT',root)))==p['indexSha256']
assert p['phase3ReadinessSha256']==sha(B.parents[1]/'READINESS.json')
i=read(R/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(z)for z in(B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field'])for e in es}=={(q['id'],f)for q in i['questions']for f in q['inputFields']}
for e in es:assert set(i['requiredReviewInputEntryFields'])<=e.keys() and e['sourceHash']==c['source']['sha256'] and e['status']in i['answerStatuses'] and 1<=e['nativeLocator']['physicalPage']<=56
def validate_typed(entries,c):
 arm=next(e for e in entries if e['questionId']=='Q06'and e['field']=='arm_results')
 assert arm['value_or_null']==[{'resultId':r['id'],'estimate':r['estimate'],'sourceLocators':r['sourceLocators']}for r in c['results']]
 mult=next(e for e in entries if e['questionId']=='Q09'and e['field']=='multiplicity')
 assert mult['status']=='partial'and 'global multiplicity' in mult['reason']
validate_typed(es,c)
checks=[]
def reject(n,path,v):
 x=copy.deepcopy(c);p=x
 for k in path[:-1]:p=p[k]
 p[path[-1]]=v
 try:validate(x)
 except AssertionError:checks.append(n);return
 raise AssertionError(n+' accepted')
for name,path,value in EXPECTATIONS:
 wrong=not value if isinstance(value,bool) else 123456 if value is None else value*10+1 if isinstance(value,(int,float)) else list(reversed(value))+['invalid'] if isinstance(value,list) else 'incorrect_transferred_or_unqualified_value'
 reject(name,path,wrong)
reject('Q06all10groupLocatorUnion',['reviewInputs',5,'sourceLocators'],c['reviewInputs'][5]['sourceLocators'][-4:])
reject('Q06directResultBindings',['reviewInputs',5,'answer'],json.dumps([r['estimate']for r in c['results']]))
reject('Q09questionUnfinished',['reviewInputs',8,'status'],'source_answer_candidate')
armidx=next(i for i,e in enumerate(es)if e['questionId']=='Q06'and e['field']=='arm_results');multidx=next(i for i,e in enumerate(es)if e['questionId']=='Q09'and e['field']=='multiplicity')
for name,kind in [('TypedQ06plainEstimates','plain'),('TypedQ06missingGroup','group'),('TypedQ06missingLocator','locator'),('TypedQ09unverifiedGlobalControl','mult')]:
 x=copy.deepcopy(es)
 if kind=='plain':x[armidx]['value_or_null']=[r['estimate']for r in c['results']]
 elif kind=='group':x[armidx]['value_or_null']=x[armidx]['value_or_null'][1:]
 elif kind=='locator':x[armidx]['value_or_null'][0]['sourceLocators']=x[armidx]['value_or_null'][0]['sourceLocators'][1:]
 else:x[multidx]['status']='answered'
 try:validate_typed(x,c)
 except AssertionError:checks.append(name)
 else:raise AssertionError(name+' accepted')
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('REED3-CAL03 PASS',len(checks),'source-specific negative guards/source/index/GP/10deps/67fields')
