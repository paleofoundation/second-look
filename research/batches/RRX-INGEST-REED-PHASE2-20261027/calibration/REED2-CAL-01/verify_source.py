"""Guard consequential denominator, estimand, safety and inference errors."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os
B=Path(__file__).resolve().parent; ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion']
 assert set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['id']=='P-PRAM-ANHED-2026' and c['source']['id']=='B-R0116-F01'
 assert c['inspection']['physicalPagesRead']==list(range(1,25))
 assert c['inspection']['embeddedReportingSummaryReadVisually']==[20,21,22,23,24]
 assert not c['inspection']['separateCompanionContentRead'] and not c['inspection']['fullScientificReviewComplete']
 assert not any(c[k] for k in ['priorAcceptanceTransferred','scientificAcceptance','humanApproval','released'])
 assert c['newIndependentTrialCount']==0
 s=c['study'];assert not s['dedicatedTwoFailureTRDPopulationEstablished'] and not s['monotherapy']
 assert s['familyId']=='FAM-NCT05355337' and not s['multiplicityAdjustmentSecondaryExploratory']
 assert s['intervention']['maximumSaltMg']==4.5 and s['intervention']['reportingSummaryMaximumBaseMg']==3.15
 assert s['intervention']['actualEndpointSaltMeanSDMg']['pramipexole']==[3.53,1.13] and s['intervention']['actualEndpointDoseN']==80
 assert not s['intervention']['conversionCalculated']
 ns=c['cohorts'];assert [ns[k]['total'] for k in ['randomized','modifiedITT','week9Observed','flowCompletedFollowup','imaging','activity']]==[85,82,80,81,48,61]
 assert [ns['randomized'][k] for k in ['pramipexole','placebo']]==[43,42]
 assert [ns['modifiedITT'][k] for k in ['pramipexole','placebo']]==[41,41]
 assert [ns['week9Observed'][k] for k in ['pramipexole','placebo']]==[41,39]
 assert len(c['results'])==len(c['claims'])==6
 a,b,d,e,f,g=[r['estimate'] for r in c['results']]
 assert a['instrument']=='SHAPS continuous 14 to 56, lower better'
 assert a['betweenGroupDifference']==-4.04 and a['betweenGroup95CI']==[-6.89,-1.18]
 assert a['PTable']==.0059 and a['supportiveLongitudinalMainEffectP']==.0022
 assert a['directionalHedgesG']==-.62 and a['bodyMagnitudeHedgesG']==.62
 assert not a['responseRemissionSignificantDifferenceEstablished'] and a['responseRemissionExactCounts'] is None
 assert b['MADRS_S']['P']==.1321 and b['HDRS_6']['P']==.1058
 assert b['DARS']['estimate']==6.13 and b['AES_S']['estimate']==-4.97 and not b['multiplicityAdjusted'] and not b['equivalenceEstablished']
 assert d['RCT']['exposedN']==[43,42] and d['RCT']['seriousAdverseEvents']==0 and d['RCT']['activeMildManicSymptomsPatients']==2
 assert d['RCT']['percentActivePlacebo']['dizzinessLiteral']==[32.59,4.76] and d['RCT']['reconstructedEventCounts'] is None
 assert d['extension']['seriousEvents']==3 and d['extension']['patientsWithSeriousEvents']==2 and not d['generalSafetyEstablished']
 assert d['extension']['lossOfAppetitePatients']==9 and 'increasedAppetitePatients' not in d['extension']
 assert [e[k] for k in ['NActive','NPlacebo']]==[25,23] and e['P']==.030 and e['activeSHAPSCorrelationP']==.060
 assert not e['directD3OccupancyMeasured'] and not e['causalMediationEstablished']
 assert [f[k] for k in ['NActive','NPlacebo']]==[32,29] and not f['LPAWeek9Significant']
 assert not f['consistentSedentaryReductionEstablished'] and not f['consistentMVPAIncreaseEstablished'] and not f['clinicalBenefitEstablished']
 assert g['entered']==54 and g['completed']==37 and g['allParticipantsActive'] and not g['controlledSixMonthEffectEstablished']
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json')
 assert '55 degrees' in next(q['description'] for q in c['sourceQualifications'] if q['id'].endswith('IMAGING'))
 assert c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for r in c['results']:
  assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
  assert all(z['sourceSha256']==c['source']['sha256'] and 1<=z['physicalPage']<=24 for z in r['sourceLocators'])
 for q in c['claims']:assert not q['acceptedSupport'] and set(q['resultIds'])<={r['id'] for r in c['results']}
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for name in ['AUDIT-MANIFEST.json','READINESS.json']:
 for f,h in read(B/name).get('files',read(B/name).get('hashes',{})).items():assert sha(B/f)==h
reed=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed/'pramipexole-anhedonia/pdfs/42286321-ventorp-2026.pdf')==c['source']['sha256']
assert sha(reed/'pramipexole-anhedonia/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json')
entries=[json.loads(z) for z in (B/'review-inputs.jsonl').read_text().splitlines()]
assert len(entries)==67 and {(e['questionId'],e['field']) for e in entries}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in entries:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,path,value):
 x=copy.deepcopy(c);p=x
 for k in path[:-1]:p=p[k]
 p[path[-1]]=value
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' was accepted')
for name,path,value in [
 ('randomized_not_mITT',['cohorts','randomized','total'],82),
 ('mITT_not_full_ITT',['cohorts','modifiedITT','total'],85),
 ('endpoint_not_all_mITT',['cohorts','week9Observed','total'],82),
 ('flow_literal_not_silent_repair',['cohorts','flowCompletedFollowup','total'],80),
 ('not_uniform_dedicated_TRD',['study','dedicatedTwoFailureTRDPopulationEstablished'],True),
 ('not_monotherapy',['study','monotherapy'],True),
 ('actual_not_maximum_dose',['study','intervention','actualEndpointSaltMeanSDMg','pramipexole'],[4.5,0]),
 ('no_inferred_salt_base_conversion',['study','intervention','conversionCalculated'],True),
 ('primary_not_longitudinal_P',['results',0,'estimate','PTable'],.0022),
 ('directional_g_retained',['results',0,'estimate','directionalHedgesG'],.62),
 ('no_significant_remission_inference',['results',0,'estimate','responseRemissionSignificantDifferenceEstablished'],True),
 ('MADRS_week9_not_overall_P',['results',1,'estimate','MADRS_S','P'],.012),
 ('no_multiplicity_correction_invention',['results',1,'estimate','multiplicityAdjusted'],True),
 ('safety_not_mITT_denominators',['results',2,'estimate','RCT','exposedN'],[41,41]),
 ('literal_dizziness_not_repaired',['results',2,'estimate','RCT','percentActivePlacebo','dizzinessLiteral'],[32.56,4.76]),
 ('events_not_patients',['results',2,'estimate','extension','patientsWithSeriousEvents'],3),
 ('attribution_not_event_erasure',['results',2,'estimate','extension','seriousEvents'],0),
 ('loss_of_appetite_not_increased',['results',2,'estimate','extension','lossOfAppetitePatients'],0),
 ('no_causal_brain_mediation',['results',3,'estimate','causalMediationEstablished'],True),
 ('MRI_not_all_patients',['results',3,'estimate','NActive'],41),
 ('SHAPS_BOLD_not_significant',['results',3,'estimate','activeSHAPSCorrelationP'],.006),
 ('LPA_week9_null_retained',['results',4,'estimate','LPAWeek9Significant'],True),
 ('no_controlled_extension',['results',5,'estimate','controlledSixMonthEffectEstablished'],True),
 ('companions_not_read_by_main_read',['inspection','separateCompanionContentRead'],True),
 ('same_report_not_new_trial',['newIndependentTrialCount'],1),
 ('no_scientific_approval_transfer',['scientificAcceptance'],True)]:reject(name,path,value)
out={'at':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourcePDFAndIndexHashes':'PASS','prospectiveAndAuditDependencyHashes':'PASS','typedInputInventory':'PASS_15Q_67fields','sourceGuards':'PASS','rejectedRegressions':checks,'independentSourceAudit':'pending','fullFieldMapAcceptance':False,'scientificAcceptance':False,'humanApproval':False,'released':False}
(B/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'meaningful mutation guards; 67 typed entries and exact source dependencies')
