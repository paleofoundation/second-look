"""Guard compound, dose, phase, replicate and null identities in the original source."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['inspection']['physicalPagesRead']==list(range(1,17)) and c['inspection']['visualInspectedPhysicalPages']==list(range(3,10))
 assert not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['rawAssayDataInspected']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 assert len(c['results'])==len(c['claims'])==5 and len(c['sourceQualifications'])==18
 s=c['study'];assert not s['clinicalStudy'] and s['radiation']['singleGy']==[2,4,6] and s['radiation']['kV']==90 and s['radiation']['GyPerMinute']==1.96
 assert s['memantineMicromolar']=={'migration48h':50,'Figure3CFA':50,'Figure4Foci':100,'Figure4CFA':25}
 a,b,d,e,f=[x['estimate']for x in c['results']]
 assert a['patchN']==22 and a['MTTActualAntagonists']==['MK80110uM','ifenprodil25uM'] and not a['memantineMTTEstimateImported'] and a['cellCycleGluMK801SAS']=='no difference'
 assert b['clonogenicMemantineLD50uM']==26 and b['LD50SEM']==11 and b['LD50N']==3 and not b['clinicalDoseOrInVivoInvasion']
 assert d['fociAt4h']==[29,7] and d['sourceMockIrradiatedComparatorAmbiguous'] and d['CFAmemantineUM']==50 and d['enhancementFactorAt2Gy']==1.4 and d['CFAN']==3 and d['CFAError']=='SD'
 assert e['pCREB30min']['mean']==3.7 and e['pCREB30min']['antibodyAlsoRecognizes']=='pATF1' and e['BDNFFold']['mean']==1.9 and e['BDNFFold']['MK801ResultuM']==10 and e['BDNFFold']['MK801MethoduM']==20
 assert e['gammaH2AXFigure4B']['hours']==4 and e['gammaH2AXFigure4B']['MK801']['significance']=='NS' and e['gammaH2AXFigure4B']['KG501']['P']=='<.05' and e['bodyClaimsBothSignificantAt30min'] and not e['sourceConflictResolved']
 assert f['foci']['phase']=='EdU-negative/non-S' and f['foci']['memantineUM']==100 and f['foci']['KG501UM']==25 and f['foci']['combinedEffect']=='subadditive'
 assert f['CFA']['memantineUM']==25 and f['CFA']['KG501UM']==1 and f['CFA']['LN229N']==3 and f['CFA']['U87N']==2 and f['CFA']['error']=='SD' and f['CFA']['U87CombinationFurtherEffect']=='not significant' and not f['formalSynergyEstablished']
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
 ('notclinical',['study','clinicalStudy'],True),('singleRTdoses',['study','radiation','singleGy'],[2,4,8]),('RTkVnotMV',['study','radiation','kV'],6),('no_memMTTtransfer',['results',0,'estimate','memantineMTTEstimateImported'],True),('cellcyclenull',['results',0,'estimate','cellCycleGluMK801SAS'],'arrest'),('LD50notclinicaldose',['results',1,'estimate','clonogenicMemantineLD50uM'],.5),('LD50SEMnotSD',['results',1,'estimate','LD50SEM'],0),('noinvivoinvasion',['results',1,'estimate','clinicalDoseOrInVivoInvasion'],True),('mockambiguity',['results',2,'estimate','sourceMockIrradiatedComparatorAmbiguous'],False),('figure3mem50',['results',2,'estimate','CFAmemantineUM'],25),('factor1point4',['results',2,'estimate','enhancementFactorAt2Gy'],1.81),('figure3SD',['results',2,'estimate','CFAError'],'SEM'),('pCREBmean',['results',3,'estimate','pCREB30min','mean'],3.9),('pATFcrossreactivity',['results',3,'estimate','pCREB30min','antibodyAlsoRecognizes'],'CREB only'),('BDNFmethod20',['results',3,'estimate','BDNFFold','MK801MethoduM'],10),('BDNFresult10',['results',3,'estimate','BDNFFold','MK801ResultuM'],20),('figure4B4hours',['results',3,'estimate','gammaH2AXFigure4B','hours'],.5),('MK801null',['results',3,'estimate','gammaH2AXFigure4B','MK801','significance'],'significant'),('conflictheld',['results',3,'estimate','sourceConflictResolved'],True),('nonSphase',['results',4,'estimate','foci','phase'],'S/G2'),('focimem100',['results',4,'estimate','foci','memantineUM'],25),('fociKG25',['results',4,'estimate','foci','KG501UM'],1),('subadditive',['results',4,'estimate','foci','combinedEffect'],'synergistic'),('CFAmem25',['results',4,'estimate','CFA','memantineUM'],100),('CFAKG1',['results',4,'estimate','CFA','KG501UM'],25),('LN229n3',['results',4,'estimate','CFA','LN229N'],9),('U87n2',['results',4,'estimate','CFA','U87N'],3),('CFASD',['results',4,'estimate','CFA','error'],'SEM'),('combonull',['results',4,'estimate','CFA','U87CombinationFurtherEffect'],'significant'),('nosynergy',['results',4,'estimate','formalSynergyEstablished'],True),('no_newRCT',['newIndependentTrials'],1),('no_patients',['newIndependentPatients'],22),('no_science',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL17 PASS',len(checks),'meaningful guards/source/index/GP/10deps/67fields')
