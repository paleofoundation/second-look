"""Reject comparator, study-overlap, sparse-event and source-conflict errors."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,hashlib,os
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='secondary_systematic_review_meta_analysis'
 assert c['inspection']['physicalPagesRead']==list(range(1,55)) and not c['inspection']['fullScientificReviewComplete'] and c['inspection']['primaryReportsRead']==0
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k] for k in ['scientificAcceptance','humanApproval','released'])
 m=c['reviewMethods'];assert m['reviewReportedRCTs']==4 and m['reviewReportedArticles']==11 and m['reviewReportedParticipants']==1042
 assert m['mainSearchCutoff']=='2021-06-14' and not m['currentExternalSearchPerformed'] and not m['publishedReviewProtocol'] and not m['clinicalTumorEfficacyEstablished']
 assert not m['currentRecommendationAdopted'] and m['primaryOutcome']=='all-cause mortality'
 ss=c['includedStudies'];assert ss[0]['existingCanonicalPaperId']=='P-D23-MYELOMA' and ss[1]['reportedReceivedAtLeastOneDose']==659
 assert ss[1]['reported6MonthAnalyzedArms']['LMWH']==219 and ss[1]['reported2YearAnalysisArms']['LMWH']==220
 assert ss[2]['standardRiskRandomizedComparison']=={'aspirin':4,'apixaban':4} and ss[2]['additionalHighRiskApixaban']==2 and not ss[2]['percentagesReconciled']
 assert ss[3]['explicitArmNs']=={'aspirin':18,'rivaroxaban':5} and ss[3]['primaryOriginalState']=='not_checked'
 assert len(c['results'])==len(c['claims'])==3
 a,b,d=[r['estimate'] for r in c['results']]
 assert a['direction']==['aspirin','VKA'] and a['doseWarfarinMgDayFixed']==1.25
 assert a['sixMonths'][1]['eventsAndTotals']=={'aspirin':[8,220],'VKA':[14,220]} and a['sixMonths'][1]['riskRatio']==.57 and a['sixMonths'][1]['CI95']==[.24,1.33]
 assert a['twoYears'][1]['eventsAndTotals']=={'aspirin':[12,220],'VKA':[17,220]} and a['twoYears'][1]['riskRatio']==.71
 assert a['majorMinorBleeding2YearStatus']=='not_reported' and a['sameStudyAcrossWindows']
 assert b['direction']==['aspirin','LMWH'] and b['sixMonths'][1]['riskRatio']==1.23 and b['sixMonths'][1]['CI95']==[.49,3.08]
 assert b['sixMonths'][2]['riskRatio']==7.71 and b['sixMonths'][2]['CI95']==[.97,61.44] and b['sixMonths'][2]['PAsPrinted']==.05
 assert b['sixMonths'][3]['estimatingStudies']==1 and b['sixMonths'][3]['includedStudies']==2 and b['sixMonths'][3]['eventsAndTotals']=={'aspirin':[3,396],'LMWH':[0,385]}
 assert b['sixMonths'][0]['estimatingStudies']==1 and b['sixMonths'][4]['PAsPrinted']==.63
 assert b['twoYearPalumboLMWHDenominator']==220 and not b['crossWindowDenominatorReconciled']
 assert b['majorMinorBleeding2YearStatus']=='not_reported' and b['reportedCertainty']=='very_low'
 assert d['mainAnalyzedN']==8 and d['main'][0]['eventsAndTotals']=={'aspirin':[2,4],'apixaban':[0,4]}
 assert d['main'][0]['riskRatio']==5 and d['main'][0]['CI95']==[.31,79.94] and not d['mainSummaryLabelsReconciled']
 assert d['sensitivityN']==31 and d['sensitivity'][0]['riskRatio']==.95 and d['sensitivity'][0]['eventsAndTotals']=={'aspirin':[1,22],'DOAC':[0,9]}
 assert d['sensitivity'][1]['riskRatio'] is None and d['sensitivity'][1]['estimatingStudies']==0
 assert d['sensitivity'][2]['componentStudyEvents']['CamposCabrera2018']=={'aspirin':[1,18],'rivaroxaban':[0,5]}
 assert not d['sensitivity'][2]['rawRateRRRecomputed'] and not d['CamposBleedingDiscrepancyWithRutjesResolved'] and not d['primaryAbstractChecked']
 assert not any(e[k] for e in [a,b,d] for k in ['formalEquivalenceEstablished','firmSuperiorityEstablished'])
 assert not d['generalSafetyEstablished'] and d['sixMonthMortalityStatus']=='not_reported'
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and len(c['sourceQualifications'])==15
 assert c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 for r in c['results']:
  assert not r['acceptedSupport'] and r['grade'] is None and r['benefitGrade'] is None
  assert all(z['sourceSha256']==c['source']['sha256'] and 1<=z['physicalPage']<=54 for z in r['sourceLocators'])
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for n in ['AUDIT-MANIFEST.json','READINESS.json']:
 for f,h in read(B/n).get('files',read(B/n).get('hashes',{})).items():assert sha(B/f)==h
reed=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed/'aspirin-myeloma/pdfs/34582035-kahale-2021.pdf')==c['source']['sha256'];assert sha(reed/'aspirin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(R/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');entries=[json.loads(z) for z in (B/'review-inputs.jsonl').read_text().splitlines()]
assert len(entries)==67 and {(e['questionId'],e['field']) for e in entries}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in entries:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,path,value):
 x=copy.deepcopy(c);p=x
 for k in path[:-1]:p=p[k]
 p[path[-1]]=value
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' accepted')
for name,path,value in [
 ('secondary_not_original',['paper','sourceType'],'randomized_trial'),
 ('review_N_not_new_people',['newIndependentPatients'],1042),
 ('overlapping_trials_not_replication',['newIndependentTrials'],4),
 ('no_primary_original_read_inference',['inspection','primaryReportsRead'],4),
 ('historical_search_not_current',['reviewMethods','currentExternalSearchPerformed'],True),
 ('no_published_protocol_invention',['reviewMethods','publishedReviewProtocol'],True),
 ('Palumbo6month219not220',['includedStudies',1,'reported6MonthAnalyzedArms','LMWH'],220),
 ('Palumbo2year220not219',['includedStudies',1,'reported2YearAnalysisArms','LMWH'],219),
 ('TiMM_not_all10',['results',2,'estimate','mainAnalyzedN'],10),
 ('TiMM_highrisk_not_randomizedASAcontrast',['includedStudies',2,'standardRiskRandomizedComparison','apixaban'],6),
 ('ASA_VKA_not_inverse_direction',['results',0,'estimate','direction'],['VKA','aspirin']),
 ('ASA_LMWH_not_Rutjes_VTE',['results',1,'estimate','sixMonths',1,'riskRatio'],.51),
 ('PE_CI_includes_null',['results',1,'estimate','sixMonths',2,'CI95'],[1.01,61.44]),
 ('no_PE_P_below05_repair',['results',1,'estimate','sixMonths',2,'PAsPrinted'],.049),
 ('doublezero_not_two_estimating_trials',['results',1,'estimate','sixMonths',3,'estimatingStudies'],2),
 ('two_year_bleeding_not_zero',['results',0,'estimate','majorMinorBleeding2YearStatus'],'zero'),
 ('sourceGRADE_not_Rutjesmoderate',['results',1,'estimate','reportedCertainty'],'moderate'),
 ('LMWH_flow_discrepancy_not_silently_resolved',['results',1,'estimate','crossWindowDenominatorReconciled'],True),
 ('DOAC_correctedRR_not_rawrate',['results',2,'estimate','sensitivity',0,'riskRatio'],5),
 ('doublezero_PE_not_RR1',['results',2,'estimate','sensitivity',1,'riskRatio'],1),
 ('Campos_majorbleed_not_priorreview_zero',['results',2,'estimate','sensitivity',2,'componentStudyEvents','CamposCabrera2018','aspirin'],[0,18]),
 ('Campos_conflict_not_adjudicated',['results',2,'estimate','CamposBleedingDiscrepancyWithRutjesResolved'],True),
 ('Campos_original_not_checked',['results',2,'estimate','primaryAbstractChecked'],True),
 ('no_equivalence_from_sparse_null',['results',0,'estimate','formalEquivalenceEstablished'],True),
 ('no_general_safety_from_zeroevents',['results',2,'estimate','generalSafetyEstablished'],True),
 ('no_tumor_efficacy',['reviewMethods','clinicalTumorEfficacyEstablished'],True),
 ('no_current_prescribing',['reviewMethods','currentRecommendationAdopted'],True),
 ('no_scientific_approval',['scientificAcceptance'],True)]:reject(name,path,value)
out={'at':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourcePDFAndIndexHashes':'PASS','prospectiveAndAuditDependencyHashes':'PASS','typedInputInventory':'PASS_15Q_67fields','sourceGuards':'PASS','rejectedRegressions':checks,'independentSourceAudit':'pending','fullFieldMapAcceptance':False,'scientificAcceptance':False,'humanApproval':False,'released':False};(B/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'meaningful source regression guards and67typed/source/hash checks')
