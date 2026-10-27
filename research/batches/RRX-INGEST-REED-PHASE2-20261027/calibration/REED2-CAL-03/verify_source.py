"""Guard secondhand provenance, shared arms, null uncertainty and prevention scope."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy,os
B=Path(__file__).resolve().parent;ROOT=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='secondary_systematic_review_meta_analysis'
 assert c['inspection']['physicalPagesRead']==list(range(1,169)) and c['inspection']['primaryReportsRead']==0 and not c['inspection']['fullScientificReviewComplete']
 assert not any(c[k] for k in ['scientificAcceptance','humanApproval','released']) and c['newIndependentTrials']==c['newIndependentPatients']==0
 m=c['reviewMethods'];assert m['reviewReportedStudies']==32 and m['reviewReportedParticipants']==15678 and m['reportedSearchCutoff']=='2020-08-03'
 assert not any(m[k] for k in ['WHOAugust2020PortalAvailable','currentExternalSearchPerformed','currentRecommendationAdopted','clinicalTumorEfficacyEstablished'])
 s=c['includedStudies'];assert s[0]['canonicalRelatedPaperId']=='P-D23-MYELOMA' and s[0]['N']==342
 assert s[1]['reportedAnalyzedArms']=={'aspirin':220,'warfarin':220,'LMWH':219} and s[1]['reportedRandomizedArms']=={'aspirin':224,'warfarin':222,'LMWH':221}
 assert s[2]['explicitArmDenominators'] is None and not s[2]['armNInferredFromGenderPercentages']
 assert all(not x['primaryOriginalReadInThisPacket'] for x in s)
 assert len(c['results'])==len(c['claims'])==3
 a,b,d=[r['estimate'] for r in c['results']]
 assert a['N']==781 and a['arms']==['LMWH','aspirin'] and a['studies']==['Larocca2012','Palumbo2011']
 z=a['outcomes'];assert z[0]['eventsAndTotals']=={'LMWH':[8,385],'aspirin':[16,396]} and z[0]['riskRatio']==.51 and z[0]['CI95']==[.22,1.17] and z[0]['PAsPrinted']==.11
 assert z[1]['eventsAndTotals']=={'LMWH':[0,385],'aspirin':[3,396]} and a['majorBleedingEstimableStudies']==1 and a['majorBleedingIncludedStudies']==2
 assert z[2]['riskRatio']==.13 and z[2]['CI95']==[.02,1.03] and z[2]['PAsPrinted']==.05
 assert z[3]['riskRatio']==.81 and z[3]['CI95']==[.32,2.04]
 assert a['superficialThrombosisN']==342 and z[6]['eventsAndTotals']=={'LMWH':[0,166],'aspirin':[4,176]}
 assert a['allCauseMortalityResult'] is None and a['seriousAdverseEventsResult'] is None
 assert not any(a[k] for k in ['firmSuperiorityEstablished','formalEquivalenceEstablished','primaryOriginalsVerified'])
 assert b['N']==440 and b['warfarinDoseMgDay']==1.25 and b['sharedAspirinParticipantsWithO01']==220
 assert b['outcomes'][0]['eventsAndTotals']=={'warfarin':[18,220],'aspirin':[12,220]} and b['outcomes'][0]['riskRatio']==1.50 and b['outcomes'][0]['CI95']==[.74,3.04]
 assert not b['firmSuperiorityEstablished'] and not b['formalEquivalenceEstablished'] and not b['primaryOriginalVerified']
 assert d['reportedTotalN']==23 and d['explicitOutcomeArmDenominators'] is None and d['VTEEvents']=={'rivaroxaban':0,'aspirin':1}
 assert d['riskRatio'] is None and d['CI95'] is None and d['VTEEventComponentAndSymptomaticStatus'] is None
 assert not d['superiorityEstablished'] and not d['generalSafetyEstablished'] and not d['primaryAbstractVerified']
 assert c['sourceQualifications']==read(B/'SOURCE-QUALIFICATIONS.json') and len(c['sourceQualifications'])==13
 assert c['overlapRecords'][0]==read(B/'OVERLAP-RECONCILIATION.json') and c['reviewInputs'][13]['downstreamMapping']==read(B/'DOWNSTREAM-MAPPING.json')
 assert c['reviewInputs'][13]['downstreamMapping']['existingGuideIds']==['G-DRUG-D23','G-CONDITION-C21']
 for r in c['results']:
  assert r['grade'] is None and r['benefitGrade'] is None and not r['acceptedSupport']
  assert all(v['sourceSha256']==c['source']['sha256'] and 1<=v['physicalPage']<=168 for v in r['sourceLocators'])
c=read(B/'SOURCE-CANDIDATE.json');validate(c)
for n in ['AUDIT-MANIFEST.json','READINESS.json','READINESS-v2.json']:
 for f,h in read(B/n).get('files',read(B/n).get('hashes',{})).items():assert sha(B/f)==h
reed=Path(os.environ.get('REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill'))
assert sha(reed/'aspirin-myeloma/pdfs/33337539-rutjes-2020.pdf')==c['source']['sha256'] and sha(reed/'aspirin-myeloma/index.csv')==read(B/'READINESS.json')['indexSha256']
inv=read(ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json');es=[json.loads(x) for x in (B/'review-inputs.jsonl').read_text().splitlines()]
assert len(es)==67 and {(e['questionId'],e['field']) for e in es}=={(q['id'],f) for q in inv['questions'] for f in q['inputFields']}
for e in es:assert set(inv['requiredReviewInputEntryFields'])<=e.keys() and e['status'] in inv['answerStatuses'] and e['sourceHash']==c['source']['sha256']
checks=[]
def reject(name,path,value):
 x=copy.deepcopy(c);p=x
 for k in path[:-1]:p=p[k]
 p[path[-1]]=value
 try:validate(x)
 except AssertionError:checks.append(name);return
 raise AssertionError(name+' accepted')
for n,p,v in [
 ('review_not_primary',['paper','sourceType'],'primary_RCT'),
 ('no_new_trials_from_review',['newIndependentTrials'],3),
 ('no_new_participants_from_review',['newIndependentPatients'],15678),
 ('all_cancer_N_not_aspirin_N',['results',0,'estimate','N'],15678),
 ('LMWH_relative_aspirin_direction',['results',0,'estimate','arms'],['aspirin','LMWH']),
 ('VTE_CI_crosses_no_difference',['results',0,'estimate','outcomes',0,'CI95'],[.22,.83]),
 ('no_firm_LMWH_superiority',['results',0,'estimate','firmSuperiorityEstablished'],True),
 ('major_bleeding_double_zero_not_two_estimating_trials',['results',0,'estimate','majorBleedingEstimableStudies'],2),
 ('zero_events_not_zero_harm_claim',['results',0,'estimate','seriousAdverseEventsResult'],0),
 ('PE_roundedP_not_less_than05',['results',0,'estimate','outcomes',2,'PAsPrinted'],.005),
 ('superficial_endpoint_not_pooled781',['results',0,'estimate','superficialThrombosisN'],781),
 ('shared_aspirin_arm_retained',['results',1,'estimate','sharedAspirinParticipantsWithO01'],0),
 ('fixed_low_dose_warfarin_not_therapeutic_INR',['results',1,'estimate','warfarinDoseMgDay'],5),
 ('PE_equal_events_not_equivalence',['results',1,'estimate','formalEquivalenceEstablished'],True),
 ('pilot_gender_percentages_not_outcome_denominators',['results',2,'estimate','explicitOutcomeArmDenominators'],[5,18]),
 ('pilot_no_RR_invention',['results',2,'estimate','riskRatio'],0),
 ('pilot_VTE_component_unknown',['results',2,'estimate','VTEEventComponentAndSymptomaticStatus'],'symptomatic_PE'),
 ('pilot_no_safety_proof',['results',2,'estimate','generalSafetyEstablished'],True),
 ('source_primary_not_checked',['inspection','primaryReportsRead'],3),
 ('WHO_portal_not_assumed_available',['reviewMethods','WHOAugust2020PortalAvailable'],True),
 ('historical_search_not_current',['reviewMethods','currentExternalSearchPerformed'],True),
 ('supportive_care_not_tumor_efficacy',['reviewMethods','clinicalTumorEfficacyEstablished'],True),
 ('source_GRADE_not_new_site_acceptance',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceGuards':'PASS','rejectedRegressions':checks,'sourcePDFAndIndex':'PASS','allProspectiveAndAuditDependencies':'PASS','typedInventory':'PASS_15Q_67fields','independentAudit':'pending','fullFieldMapIndependentAcceptance':False,'scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('PASS',len(checks),'secondary-review regression guards; exact source/dependencies/67inputs')
