"""Guard compound, dose, phase, replicate and null identities in the original source."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['inspection']['physicalPagesRead']==list(range(1,10)) and not c['inspection']['fullScientificReviewComplete'] and not c['inspection']['rawDataInspected']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 assert len(c['results'])==len(c['claims'])==5 and len(c['sourceQualifications'])==18
 s=c['study'];p=c['populations'];assert s['screened']==1240 and s['analyzed']==1083 and not s['randomizedAntidiabeticTreatment'] and not s['timeVaryingTreatmentModelVerified'] and s['landmarkMonths']==[3,6,9,12]
 assert p['ND']==603 and p['HxD']==136 and p['SID']==344 and p['diabeticTotalDerived']==480 and not p['agentSpecificNsReportedMain'] and p['renalInsufficiencyDiabeticN']==55 and p['metforminUsersAmongRenalInsufficiency']==0
 a,b,d,e,f=[x['estimate']for x in c['results']]
 assert a['ND']=={'n':173,'N':603} and a['HxD']=={'n':29,'N':136} and a['SID']=={'n':70,'N':344} and a['sourceCIAsOrdered']==[.901,.501] and not a['metforminSpecific']
 assert b['adjustedSID']['HR']==1.619 and b['adjustedHxD']['HR']==.943 and b['adjustedHxD']['P']==.718 and b['table2AgeOver65']['HR']==.786 and b['table2AgeOver65']['P']==.073 and b['table2SCT']['HR']==.351
 assert d['metformin']['adjusted']=={'HR':.658,'CI95':[.479,.902],'P':.009} and d['metformin']['unadjustedTextP']==.034 and d['metformin']['unadjustedFigureP']==.036
 assert d['insulin']['adjusted']['HR']==1.810 and d['secretagogues']['P']==.515 and d['TZD']['P']==.145 and d['others']['P']==.909
 assert d['metforminLandmarkOSPs']==[.012,.022,.039,.029] and not d['agentNsAvailableMain'] and not d['causalEffectEstablished']
 assert not e['adjudicatedMMCauseOfDeath'] and e['mainNarrativeAdjustedDM']['HR']==1.346 and not e['supplementModelsRead']
 assert f['unadjustedMetformin']=='not significant' and f['mainNarrativeAdjustedMetformin']=={'HR':.663,'CI95':[.452,.975],'P':.037} and f['mainNarrativeAdjustedInsulin']['HR']==1.562 and f['metforminLandmarkPs']==[.041,.027,.053,.054] and not f['lastTwoSignificant'] and not f['supplementModelsRead'] and not f['causalEffectEstablished']
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
for n,p,v in [('screened_not_final', ['study', 'analyzed'], 1240), ('not_randomized', ['study', 'randomizedAntidiabeticTreatment'], True), ('not_timeupdated_proof', ['study', 'timeVaryingTreatmentModelVerified'], True), ('ND603', ['populations', 'ND'], 480), ('HxD136', ['populations', 'HxD'], 344), ('SID344', ['populations', 'SID'], 136), ('diabetic480', ['populations', 'diabeticTotalDerived'], 1083), ('no_agentN', ['populations', 'agentSpecificNsReportedMain'], True), ('renal55', ['populations', 'renalInsufficiencyDiabeticN'], 0), ('renal_noneMet', ['populations', 'metforminUsersAmongRenalInsufficiency'], 55), ('CR_ND173', ['results', 0, 'estimate', 'ND', 'n'], 29), ('reversedCIretained', ['results', 0, 'estimate', 'sourceCIAsOrdered'], [0.501, 0.901]), ('CR_not_met_specific', ['results', 0, 'estimate', 'metforminSpecific'], True), ('SIDHR', ['results', 1, 'estimate', 'adjustedSID', 'HR'], 0.619), ('HxD_null', ['results', 1, 'estimate', 'adjustedHxD', 'P'], 0.018), ('age_inverse_retained', ['results', 1, 'estimate', 'table2AgeOver65', 'HR'], 1.786), ('ageNS', ['results', 1, 'estimate', 'table2AgeOver65', 'P'], 0.001), ('SCTprotective', ['results', 1, 'estimate', 'table2SCT', 'HR'], 3.51), ('metHR', ['results', 2, 'estimate', 'metformin', 'adjusted', 'HR'], 0.34), ('metCI', ['results', 2, 'estimate', 'metformin', 'adjusted', 'CI95'], [0.479, 1.902]), ('textP', ['results', 2, 'estimate', 'metformin', 'unadjustedTextP'], 0.036), ('figureP', ['results', 2, 'estimate', 'metformin', 'unadjustedFigureP'], 0.034), ('insulinHR', ['results', 2, 'estimate', 'insulin', 'adjusted', 'HR'], 0.81), ('TZDnull', ['results', 2, 'estimate', 'TZD', 'P'], 0.045), ('not_causal', ['results', 2, 'estimate', 'causalEffectEstablished'], True), ('not_cancer_specific_death', ['results', 3, 'estimate', 'adjudicatedMMCauseOfDeath'], True), ('no_supplementread', ['results', 3, 'estimate', 'supplementModelsRead'], True), ('met_unadjustednull', ['results', 4, 'estimate', 'unadjustedMetformin'], 'significant'), ('met_progressionHR', ['results', 4, 'estimate', 'mainNarrativeAdjustedMetformin', 'HR'], 0.658), ('late_landmarknull', ['results', 4, 'estimate', 'lastTwoSignificant'], True), ('late_landmarkPs', ['results', 4, 'estimate', 'metforminLandmarkPs'], [0.041, 0.027, 0.043, 0.044]), ('no_newtrial', ['newIndependentTrials'], 1), ('no_newpatient', ['newIndependentPatients'], 1083), ('no_science', ['scientificAcceptance'], True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL18 PASS',len(checks),'meaningful guards/source/index/GP/10deps/67fields')
