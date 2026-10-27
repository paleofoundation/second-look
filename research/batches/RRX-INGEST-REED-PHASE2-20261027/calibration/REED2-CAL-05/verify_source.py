"""Reject causal, rate-unit, nested-denominator and sparse-harm inference errors."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,hashlib,os
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='secondary_systematic_review_meta_analysis' and c['inspection']['physicalPagesRead']==list(range(1,12))
 assert c['inspection']['primaryReportsRead']==0 and not c['inspection']['supportingInformationRead'] and not c['inspection']['fullScientificReviewComplete']
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
 m=c['reviewMethods'];assert m['eligibleArticles']==71 and m['thalidomideArticles']==61 and m['lenalidomideArticles']==10
 assert m['totalUniqueParticipantsReported'] is None and not m['prophylaxisAssignmentRandomized'] and m['studyRCTsRandomizedMyelomaRegimensNotProphylaxis']
 assert not m['currentExternalSearchPerformed'] and not m['noProphylaxisIsRandomizedControl'] and not m['pooledPatientTimeReported']
 assert c['includedStudies'][-1]['disposition']=='excluded_from_meta_analysis'
 assert c['includedStudies'][2]['reportedGroups']['ASA81mgFromStart']=={'N':58,'VTE':4} and c['includedStudies'][2]['reportedGroups']['ASA81mgDuringProtocol']=={'N':26,'VTE':11}
 assert not c['includedStudies'][2]['randomizedASAComparison'] and not c['includedStudies'][-2]['ASAOnlyNsIdentified']
 assert len(c['results'])==len(c['claims'])==3
 a,b,d=[r['estimate'] for r in c['results']]
 assert a['kind']=='observational_pooled_incidence_not_causal_contrast' and a['pooledASACausalEffect'] is None and not a['optimalAgentEstablished']
 assert a['rates'][2]['rate']==2.3 and a['rates'][2]['CI95']==[.9,7.9] and a['rates'][2]['patientsAsTable']==80
 assert all(r['units']=='per100patientcycles' and r['pooledPatientTime'] is None for r in a['rates'])
 assert a['thalidomideWithoutDexNone']['tableCI95']==[.4,2.7] and a['thalidomideWithoutDexNone']['bodyCI95']==[.4,7.2] and not a['thalidomideWithoutDexNone']['discrepancyResolved']
 assert [(r['rate'],r['patientsAsTable']) for r in b['rates']]==[(.8,278),(.7,349),(.9,172)]
 assert b['rates'][0]['I2PercentAsBody']==95 and b['rates'][2]['I2PercentAsBody']==55 and b['ASAContainedInAnyProphylaxis']
 assert not b['aspirinHarmsOrInefficacyEstablished'] and b['causalASARiskRatio'] is None
 assert [(r['rate'],r['patientsAsTable']) for r in d['lenalidomideRates']]==[(.7,361),(.6,131)]
 assert all(r['units']=='per100patientmonths' for r in d['lenalidomideRates']) and d['bodyAbstractPreviouslyTreatedLenalidomideUnits']=='per100patientcycles' and not d['unitConflictResolved']
 assert d['ASALabelContainsMixedKnopProphylaxis'] and not d['ASAOnlyPooledEventsAndNIdentifiable']
 assert d['Table6LastRow3point5AssignedTo']=='warfarinFixed1to1.25mg' and d['previousThalidomideDexASAPooledRate'] is None
 assert d['majorBleedingRate'] is None and d['majorBleedingStatus']=='not_reported_inadequately_ascertained_not_zero' and not d['generalSafetyEstablished']
 assert d['causalASARiskRatio'] is None and all(not e['formalStrategyComparisonPerformed'] for e in [a,b,d])
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and len(c['sourceQualifications'])==15
 assert c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for r in c['results']:assert not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for name in ['AUDIT-MANIFEST.json','READINESS.json']:
 for n,h in read(B/name).get('files',read(B/name).get('hashes',{})).items():assert sha(B/n)==h
reed=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'));assert sha(reed/'aspirin-myeloma/pdfs/21255254-carrier-2011.pdf')==c['source']['sha256'];assert sha(reed/'aspirin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(R/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(z) for z in (B/'review-inputs.jsonl').read_text().splitlines()];assert len(es)==67 and {(e['questionId'],e['field']) for e in es}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in es:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['sourceHash']==c['source']['sha256'] and e['status'] in inv['answerStatuses']
checks=[]
def reject(name,path,value):
 x=copy.deepcopy(c);p=x
 for k in path[:-1]:p=p[k]
 p[path[-1]]=value
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' accepted')
for name,path,value in [
 ('review_not_new_primary',['inspection','primaryReportsRead'],71),
 ('regimenRCT_not_prophylaxisRCT',['reviewMethods','prophylaxisAssignmentRandomized'],True),
 ('observational_none_not_randomizedcontrol',['reviewMethods','noProphylaxisIsRandomizedControl'],True),
 ('no_unique_N_sum',['reviewMethods','totalUniqueParticipantsReported'],5000),
 ('no_new_independent_people',['newIndependentPatients'],80),
 ('no_external_supporting_read',['inspection','supportingInformationRead'],True),
 ('no_current_search',['reviewMethods','currentExternalSearchPerformed'],True),
 ('ASACI_not_symmetrized',['results',0,'estimate','rates',2,'CI95'],[.9,3.7]),
 ('rate_not_percentage',['results',0,'estimate','rates',2,'units'],'percent'),
 ('CI_tablebody_not_silent_repair',['results',0,'estimate','thalidomideWithoutDexNone','bodyCI95'],[.4,2.7]),
 ('CI_discrepancy_not_resolved',['results',0,'estimate','thalidomideWithoutDexNone','discrepancyResolved'],True),
 ('no_optimal_agent_conclusion',['results',0,'estimate','optimalAgentEstablished'],True),
 ('no_causal_ASA_RD',['results',0,'estimate','pooledASACausalEffect'],1.8),
 ('any_prophylaxis_not_disjoint_ASA',['results',1,'estimate','ASAContainedInAnyProphylaxis'],False),
 ('newLen_none_not_ASA_N',['results',1,'estimate','rates',0,'patientsAsTable'],172),
 ('high_heterogeneity_retained',['results',1,'estimate','rates',0,'I2PercentAsBody'],0),
 ('no_ASA_harm_from_crossstudy_point',['results',1,'estimate','aspirinHarmsOrInefficacyEstablished'],True),
 ('priorLen_months_not_cycles',['results',2,'estimate','lenalidomideRates',0,'units'],'per100patientcycles'),
 ('unit_conflict_not_silently_adjudicated',['results',2,'estimate','unitConflictResolved'],True),
 ('mixedKnop_not_pure_ASA',['results',2,'estimate','ASALabelContainsMixedKnopProphylaxis'],False),
 ('ASAonly_N_not_inferred',['results',2,'estimate','ASAOnlyPooledEventsAndNIdentifiable'],True),
 ('Table6_3point5_not_ASA',['results',2,'estimate','Table6LastRow3point5AssignedTo'],'ASA'),
 ('blank_ASA_cell_not_zero',['results',2,'estimate','previousThalidomideDexASAPooledRate'],0),
 ('missing_bleeding_not_zero',['results',2,'estimate','majorBleedingRate'],0),
 ('no_general_safety',['results',2,'estimate','generalSafetyEstablished'],True),
 ('Baz_timing_not_randomized',['includedStudies',2,'randomizedASAComparison'],True),
 ('GIMEMA_preliminary_not_included',['includedStudies',-1,'disposition'],'included'),
 ('no_science_approval',['scientificAcceptance'],True)]:reject(name,path,value)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourcePDFAndIndexHashes':'PASS','prospectiveAndAuditDependencyHashes':'PASS','typedInputInventory':'PASS_15Q_67fields','sourceGuards':'PASS','rejectedRegressions':checks,'independentSourceAudit':'pending','fullFieldMapAcceptance':False,'scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('PASS',len(checks),'meaningful regressions and source/index/deps/67fields')
