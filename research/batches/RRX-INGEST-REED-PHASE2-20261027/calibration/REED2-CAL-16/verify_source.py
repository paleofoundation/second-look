"""Guard MTT exposure, pair-versus-triple design and untreated donor identities."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='primary_preclinical_MTT_and_descriptive_GBM_tissue' and c['inspection']['physicalPagesRead']==list(range(1,6)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['rawBlotMTTDataInspected']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];p=c['populations'];assert s['cellLines']==['T98G','U87-MG'] and s['exposureHours']==48 and not s['tripleMetforminDCAMemantineCombinationTested']
 assert not any(s[k]for k in ['clinicalDrugEfficacyStudy','directMetabolicFluxMechanismAssayReported','formalCombinationSynergyReported','clinicalDoseFeasibilityEstablished'])
 assert p['seededCellsPerWell']==3000 and p['donorsCollected']==17 and p['GBMPositiveAnalyzed']==15 and p['nonGBMExcluded']==2 and p['clinicalDrugTreatmentN']==0 and not p['biologicalReplicateHierarchyVerified']
 assert len(c['results'])==len(c['claims'])==3 and len(c['sourceQualifications'])==15
 a,b,d=[x['estimate']for x in c['results']]
 assert a['unit']=='millimolar' and a['timeHours']==48 and a['metformin']=={'T98G':45,'U87MG':25} and a['DCA']=={'T98G':45,'U87MG':45}
 assert a['combination']=={'DCA':20,'metformin':20,'cellLines':['T98G','U87-MG']} and a['memantine']=={'T98G':.5,'U87MG':.5}
 assert not any(a[k]for k in ['relativeClaimMatchesListedConcentrations','IC50CIReported','tripleCombinationTested','formalSynergyEstablished','clinicalDoseFeasibilityEstablished']) and a['sourceAbstractRelativeConcentrationClaim']=='nearly10timeslowerthanmetformin'
 assert b['T98GCasp3MetforminAndCombination']=='decrease' and b['T98GBcl2DCACombinationMemantine']=='increase' and b['T98GBaxAllArms']=='decrease' and b['U87MGCasp3AllArms']=='increase'
 assert not any(b[k]for k in ['uniformProapoptoticDirection','cleavedCaspaseActivationEstablished','quantifiedGroupDensitometryReported','metabolicFluxNMDANecessityProven'])
 assert d['collected']==17 and d['GBMPositiveAnalyzed']==15 and d['GBMNegativeExcluded']==2 and not any(d[k]for k in ['drugAdministeredForThisComparison','treatedClinicalResponseOrSurvivalMeasured','healthyControlComparisonPresent','validatedPrognosticPredictiveBiomarker'])
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
 ('two_celllines_not_clinicalN',['study','clinicalDrugEfficacyStudy'],True),('48h_not72',['study','exposureHours'],72),('not_triplecombination',['study','tripleMetforminDCAMemantineCombinationTested'],True),('mM_not_uM',['results',0,'estimate','unit'],'micromolar'),('T98Gmet45',['results',0,'estimate','metformin','T98G'],25),('U87met25',['results',0,'estimate','metformin','U87MG'],45),('DCA45',['results',0,'estimate','DCA','U87MG'],20),('pair20each_not10',['results',0,'estimate','combination','DCA'],10),('mem_point5',['results',0,'estimate','memantine','U87MG'],5),('abstractratio_unresolved',['results',0,'estimate','relativeClaimMatchesListedConcentrations'],True),('no_IC50CI',['results',0,'estimate','IC50CIReported'],True),('no_formalsynergy',['results',0,'estimate','formalSynergyEstablished'],True),('no_clinicaldosefeasibility',['results',0,'estimate','clinicalDoseFeasibilityEstablished'],True),('T98Gcasp3down',['results',1,'estimate','T98GCasp3MetforminAndCombination'],'increase'),('T98GBcl2up',['results',1,'estimate','T98GBcl2DCACombinationMemantine'],'decrease'),('T98GBaxdown',['results',1,'estimate','T98GBaxAllArms'],'increase'),('U87casp3up',['results',1,'estimate','U87MGCasp3AllArms'],'decrease'),('not_uniformapoptosis',['results',1,'estimate','uniformProapoptoticDirection'],True),('not_cleavedactivation',['results',1,'estimate','cleavedCaspaseActivationEstablished'],True),('no_densitometry',['results',1,'estimate','quantifiedGroupDensitometryReported'],True),('no_metabolicNMDAnecessity',['results',1,'estimate','metabolicFluxNMDANecessityProven'],True),('17collected_not15',['results',2,'estimate','collected'],15),('15GBMpositive_not17',['results',2,'estimate','GBMPositiveAnalyzed'],17),('2nonGBMexcluded',['results',2,'estimate','GBMNegativeExcluded'],0),('tissues_not_drugtreated',['results',2,'estimate','drugAdministeredForThisComparison'],True),('no_tissuesurvivaldata',['results',2,'estimate','treatedClinicalResponseOrSurvivalMeasured'],True),('no_validatedbiomarker',['results',2,'estimate','validatedPrognosticPredictiveBiomarker'],True),('not_newRCT',['newIndependentTrials'],1),('not_newpatients',['newIndependentPatients'],15),('no_scienceapproval',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL16 PASS',len(checks),'meaningfulguards/source/index/GP/10deps/67fields')
