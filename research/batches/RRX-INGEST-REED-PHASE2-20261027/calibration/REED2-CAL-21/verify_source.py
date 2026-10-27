"""Guard compound, dose, phase, replicate and null identities in the original source."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['inspection']['physicalPagesRead']==list(range(1,12)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['rawDataInspected']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 assert len(c['results'])==len(c['claims'])==5 and len(c['sourceQualifications'])==16
 s=c['study'];assert s['models']==['L363','RPMI8226'] and not s['clinicalOrAnimalStudy'] and s['hypoxiaO2Percent']==1 and s['anoxiaO2PercentEstimatedLessThan']==.01 and s['preincubationHours']==1 and s['mainHIFHours']==24
 a,b,d,e,f=[x['estimate']for x in c['results']]
 assert a['metforminMM']==5 and a['hypoxiaHIFProteinPs']=={'L363':.0413,'RPMI8226':.0489} and a['L363RNA_Ps']['BNIP3trend']==.0987 and a['anoxia']=='no significant attenuation' and a['CoCl2RPMI']=='null' and a['CoCl2L363HIF_P']==.0814 and a['CoCl2L363ANGPTL4_P']==.0049 and not a['allTargetsAllConditionsSuppressed']
 assert b['early1and4hHIF']=='not stabilized' and b['RNA48hMetEffect']==['ANGPTL4 both lines','CAIX RPMI8226'] and b['repeats']==2 and not b['allTargetsPersistent48h']
 assert d['probeUM']==100 and d['hours']==5 and d['metforminMM']==[5,10] and d['repeats']==3 and not d['quantitativeO2Measured'] and not d['respiratoryFluxOrComplexINecessityDemonstrated']
 assert e['hours']==72 and e['MTT_mM']==[1.56,3.125,6.25,12.5,25] and e['count_mM']==[2.5,5,10] and e['drugRelativeGrowthInhibition']=='weaker in hypoxia' and e['doseResponseNormalization']=='each oxygen own untreated control' and e['directCountsPresent'] and not e['cellCycleArrestDirectlyMeasured']
 assert f['metforminMM']==5 and f['hours']==48 and f['independentN']==3 and f['livingEarlyLateFractions']=='no significant differences across conditions' and not f['exactZeroApoptosis'] and not f['universalDoseTimeSafetyConclusion']
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
for n,p,v in [('hypoxia1', ['study', 'hypoxiaO2Percent'], 0.01), ('anoxiaestimated', ['study', 'anoxiaO2PercentEstimatedLessThan'], 1), ('Met5mM', ['results', 0, 'estimate', 'metforminMM'], 0.005), ('L363HIFP', ['results', 0, 'estimate', 'hypoxiaHIFProteinPs', 'L363'], 0.413), ('BNIP3trend', ['results', 0, 'estimate', 'L363RNA_Ps', 'BNIP3trend'], 0.00987), ('anoxianull', ['results', 0, 'estimate', 'anoxia'], 'significant suppression'), ('CoRPMInull', ['results', 0, 'estimate', 'CoCl2RPMI'], 'positive'), ('CoL363trend', ['results', 0, 'estimate', 'CoCl2L363HIF_P'], 0.00814), ('CoANGPTL4exception', ['results', 0, 'estimate', 'CoCl2L363ANGPTL4_P'], 0.49), ('notalltargets', ['results', 0, 'estimate', 'allTargetsAllConditionsSuppressed'], True), ('kinetics2', ['results', 1, 'estimate', 'repeats'], 3), ('not48all', ['results', 1, 'estimate', 'allTargetsPersistent48h'], True), ('earlynostableHIF', ['results', 1, 'estimate', 'early1and4hHIF'], 'stabilized'), ('probe100uM', ['results', 2, 'estimate', 'probeUM'], 5), ('probe5h', ['results', 2, 'estimate', 'hours'], 24), ('notO2quant', ['results', 2, 'estimate', 'quantitativeO2Measured'], True), ('notfluxproof', ['results', 2, 'estimate', 'respiratoryFluxOrComplexINecessityDemonstrated'], True), ('growth72h', ['results', 3, 'estimate', 'hours'], 48), ('weakerhypoxia', ['results', 3, 'estimate', 'drugRelativeGrowthInhibition'], 'stronger in hypoxia'), ('ownbaselines', ['results', 3, 'estimate', 'doseResponseNormalization'], 'shared normoxic baseline'), ('directcounts', ['results', 3, 'estimate', 'directCountsPresent'], False), ('notcellcycle', ['results', 3, 'estimate', 'cellCycleArrestDirectlyMeasured'], True), ('flow48h', ['results', 4, 'estimate', 'hours'], 72), ('flowN3', ['results', 4, 'estimate', 'independentN'], 9), ('flownull', ['results', 4, 'estimate', 'livingEarlyLateFractions'], 'increased apoptosis'), ('notzero', ['results', 4, 'estimate', 'exactZeroApoptosis'], True), ('notsafety', ['results', 4, 'estimate', 'universalDoseTimeSafetyConclusion'], True), ('noRCT', ['newIndependentTrials'], 1), ('nopeople', ['newIndependentPatients'], 1), ('noscience', ['scientificAcceptance'], True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL21 PASS',len(checks),'meaningful guards/source/index/GP/10deps/67fields')
