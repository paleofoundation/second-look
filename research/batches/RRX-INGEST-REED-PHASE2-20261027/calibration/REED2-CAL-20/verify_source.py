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
 assert len(c['results'])==len(c['claims'])==4 and len(c['sourceQualifications'])==16
 s=c['study'];p=c['populations'];assert s['models']==['RPMI8226'] and not s['clinicalOrAnimalStudy'] and s['metforminRangeMM']==[0,1.25,2.5,5,10,20,40] and s['melphalanRangeUM']==[0,.08,.4,2,10,50,250] and p['cellLines']==1 and p['clinicalPatients']==p['animals']==0
 a,b,d,e=[x['estimate']for x in c['results']]
 assert a['metforminMM']==10 and a['melphalanUM']==[2,10,50,250] and a['sourceCompuSynCI']=='<1' and not a['exactCIsReported'] and not a['synergyIndependentlyReproduced'] and not a['logUnitSourceConflictResolved']
 assert b['hours']==24 and b['melphalanUM']==10 and b['metforminMM']==10 and b['rotenoneMM']==1 and b['abstractMeansPercent']==[12.7,18.8] and b['abstractSD']==[2.8,1.5] and b['figure2RepresentativeMelQuadrantsPercent']=={'D2':11.5,'D4':14.2} and b['figure2RepresentativePairQuadrantsPercent']=={'D2':15.5,'D4':30.6} and not b['abstractFigureBasisResolved'] and not b['representativeQuadrantsAreAggregateMeans']
 assert d['hours']==24 and not d['directRepairRateMeasured'] and not d['specificDSBRepairNecessityEstablished'] and not d['exactMeansDigitized']
 assert e['abstractContrastUM']==[.42,.08] and e['abstractSD']==[.01,.02] and not e['perCellNormalizationVerified'] and not e['ATPRescueNecessityProven'] and not e['exactFullDoseMeansDigitized']
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
for n,p,v in [('one_line', ['populations', 'cellLines'], 2), ('notclinical', ['study', 'clinicalOrAnimalStudy'], True), ('metmM', ['results', 0, 'estimate', 'metforminMM'], 0.01), ('meluM', ['results', 0, 'estimate', 'melphalanUM'], [2000, 10000, 50000, 250000]), ('CIreported', ['results', 0, 'estimate', 'sourceCompuSynCI'], 'not assessed'), ('CIvaluesunknown', ['results', 0, 'estimate', 'exactCIsReported'], True), ('not_reproduced', ['results', 0, 'estimate', 'synergyIndependentlyReproduced'], True), ('unitsheld', ['results', 0, 'estimate', 'logUnitSourceConflictResolved'], True), ('24h', ['results', 1, 'estimate', 'hours'], 48), ('rotenone1mM', ['results', 1, 'estimate', 'rotenoneMM'], 0.001), ('abstractvalues', ['results', 1, 'estimate', 'abstractMeansPercent'], [25.7, 46.1]), ('abstractSD', ['results', 1, 'estimate', 'abstractSD'], [0, 0]), ('Melquadrants', ['results', 1, 'estimate', 'figure2RepresentativeMelQuadrantsPercent', 'D4'], 30.6), ('pairquadrants', ['results', 1, 'estimate', 'figure2RepresentativePairQuadrantsPercent', 'D4'], 14.2), ('no_harmonization', ['results', 1, 'estimate', 'abstractFigureBasisResolved'], True), ('not_aggregatequadrants', ['results', 1, 'estimate', 'representativeQuadrantsAreAggregateMeans'], True), ('comet_notrepairrate', ['results', 2, 'estimate', 'directRepairRateMeasured'], True), ('noDSBnecessity', ['results', 2, 'estimate', 'specificDSBRepairNecessityEstablished'], True), ('no_graphmeans', ['results', 2, 'estimate', 'exactMeansDigitized'], True), ('ATPpoint42', ['results', 3, 'estimate', 'abstractContrastUM'], [4.2, 0.8]), ('ATPSD', ['results', 3, 'estimate', 'abstractSD'], [0.1, 0.2]), ('no_percellproof', ['results', 3, 'estimate', 'perCellNormalizationVerified'], True), ('no_ATPrescue', ['results', 3, 'estimate', 'ATPRescueNecessityProven'], True), ('no_dosemeans', ['results', 3, 'estimate', 'exactFullDoseMeansDigitized'], True), ('no_newtrial', ['newIndependentTrials'], 1), ('no_newpatients', ['newIndependentPatients'], 1), ('no_science', ['scientificAcceptance'], True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL20 PASS',len(checks),'meaningful guards/source/index/GP/10deps/67fields')
