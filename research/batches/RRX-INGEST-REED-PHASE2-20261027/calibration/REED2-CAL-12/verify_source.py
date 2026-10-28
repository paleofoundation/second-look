"""Preserve preclinical exposure, source-panel concern and translation limits."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
B=Path(__file__).resolve().parent;R=B.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(c):
 assert c['schemaVersion']==read(B/'SCHEMA.json')['schemaVersion'] and set(read(B/'SCHEMA.json')['required'])<=c.keys()
 assert c['paper']['sourceType']=='primary_preclinical_cell_and_donor_expression' and c['inspection']['physicalPagesRead']==list(range(1,9))
 assert not any(c['inspection'][k]for k in ['fullScientificReviewComplete','separateCompanionContentRead','rawFlowBlotDataInspected','sourcePanelConcernResolved'])
 assert c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released'])
 s=c['study'];p=c['populations'];assert s['expressionDonors']['MM']==60 and s['expressionDonors']['control']==30 and s['concentrationsMmolL']==[0,.5,2.5,5.0] and s['CCK8TimesHours']==[24,48,72]
 assert not any(s[k]for k in ['aspirinClinicalTreatmentStudy','animalEfficacyExperiment','ATF4CHOPNecessityTestReported','ASABlimp1RescueTestReported','clinicalBenefitEstablished'])
 assert p['aspirinTreatedClinicalPatients']==0 and p['clinicalAspirinEffectN']is None and p['reportedIndependentExperimentsFigures2To4']==3 and not p['newUniqueCrossCorpusClinicalPatientsAdjudicated']
 assert len(c['results'])==len(c['claims'])==5 and len(c['sourceQualifications'])==15
 a,b,d,e,f=[x['estimate']for x in c['results']]
 assert a['MMdonors']==60 and a['controlDonors']==30 and not a['healthyVolunteerControls'] and not a['ASAClinicalEffect'] and a['Blimp1']=='higher' and a['ATF4']==a['CHOP']=='lower'
 assert b['IC50MmolL']=={'U266':[7.631,6.356,3.179],'RPMI8226':[8.583,6.024,2.833]} and b['RPMI72hInhibitionPercentAtNonzeroDoses']==[29.56,48.60,68.35]
 assert b['doseMmolL']==[0,.5,2.5,5.0] and b['timeHours']==[24,48,72] and b['inhibitionNotRemainingViability'] and b['earlyIC50AboveTestedMax'] and not b['humanExposureFeasibilityEstablished'] and not b['RPMIMoreSensitiveAtEveryTimepoint']
 assert d['ASAFlowExposureHours']==72 and d['knockdownApoptosisPercentText']=={'U266_sh1':53.2,'U266_sh2':37.,'RPMI_sh1':46.4,'RPMI_sh2':61.7}
 assert d['representativePanelQuadrantsPercent']==[4.3,26.4,49.3,20.] and d['potentialSharedPanels']==['Fig3B physical4 RPMI8226ASA2.5mM','Fig4B physical5 RPMI8226shRNA#1']
 assert not any(d[k]for k in ['panelOriginAdjudicated','rawFCSInspected','independentPanelReplicationAccepted','misconductConclusion'])
 assert e['knockdownATF4CHOP']=='increase' and e['overexpressionATF4CHOP']=='decrease' and e['overexpressionLine']=='RPMI-8226'
 assert not any(e[k]for k in ['ASABlimp1RescueShown','ATF4CHOPNecessityShown','directBlimp1PromoterBindingShown','fullASAMechanismProven'])
 assert f['lowDoseMmolL']==.5 and f['lowDoseRPMIATF4CHOP']=='decrease' and not any(f[k]for k in ['uniformMonotonicATF4CHOPIncrease','feedbackOrNoncodingRNAExplanationTested','normalCellSelectivityEstablished','clinicalAntitumorBenefitEstablished'])
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
 ('not_clinicalASActrial',['study','aspirinClinicalTreatmentStudy'],True),('no_ownanimalexperiment',['study','animalEfficacyExperiment'],True),('donors_not_ASApatients',['populations','aspirinTreatedClinicalPatients'],90),('Nnotclinicaleffect',['populations','clinicalAspirinEffectN'],60),('diseasecontrols_not_healthy',['results',0,'estimate','healthyVolunteerControls'],True),('expression_not_ASAeffect',['results',0,'estimate','ASAClinicalEffect'],True),('mM_not_micromolar',['study','concentrationsMmolL'],[0,.0005,.0025,.005]),('IC50_textliteral',['results',1,'estimate','IC50MmolL','U266',0],.7631),('inhibition_not_viability',['results',1,'estimate','inhibitionNotRemainingViability'],False),('IC50_above_max',['results',1,'estimate','earlyIC50AboveTestedMax'],False),('not_human_exposure',['results',1,'estimate','humanExposureFeasibilityEstablished'],True),('not_alltimes_RPMImoresensitive',['results',1,'estimate','RPMIMoreSensitiveAtEveryTimepoint'],True),('KDnot_ASAdose',['results',2,'estimate','knockdownApoptosisPercentText','U266_sh1'],61.7),('panel_values_retained',['results',2,'estimate','representativePanelQuadrantsPercent'],[0,0,100,0]),('panel_concern_not_adjudicated',['results',2,'estimate','panelOriginAdjudicated'],True),('no_rawFCS_read',['results',2,'estimate','rawFCSInspected'],True),('no_independentpanel_replication',['results',2,'estimate','independentPanelReplicationAccepted'],True),('no_misconduct_conclusion',['results',2,'estimate','misconductConclusion'],True),('no_ASArescue',['results',3,'estimate','ASABlimp1RescueShown'],True),('no_CHOPnecessity',['results',3,'estimate','ATF4CHOPNecessityShown'],True),('no_directbinding',['results',3,'estimate','directBlimp1PromoterBindingShown'],True),('no_fullmechanism',['results',3,'estimate','fullASAMechanismProven'],True),('lowdose_decrease',['results',4,'estimate','lowDoseRPMIATF4CHOP'],'increase'),('not_monotone',['results',4,'estimate','uniformMonotonicATF4CHOPIncrease'],True),('feedback_not_tested',['results',4,'estimate','feedbackOrNoncodingRNAExplanationTested'],True),('not_normalcellselectivity',['results',4,'estimate','normalCellSelectivityEstablished'],True),('not_clinicalbenefit',['results',4,'estimate','clinicalAntitumorBenefitEstablished'],True),('not_newRCT',['newIndependentTrials'],1),('not_newclinicalN',['newIndependentPatients'],90),('not_scienceacceptance',['scientificAcceptance'],True)]:reject(n,p,v)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'status':'PASS_TECHNICAL_SOURCE_GUARDS_ONLY_UNRESOLVED_PANEL_CONCERN_RETAINED','meaningfulRegressionGuards':checks,'count':len(checks),'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'sourceIndexGPDependencies':'PASS','pinned15Q67Inventory':'PASS','independentAudit':'pending','sourcePanelConcernResolved':False,'scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('CAL12 PASS',len(checks),'meaningfulguards/source/index/GP/10deps/67fields,panelconcernunresolved')
