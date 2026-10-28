from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,hashlib,copy
B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((B/'SOURCE-CANDIDATE.json').read_text());m=json.loads((B/'AUDIT-MANIFEST.json').read_text());p=json.loads((B/'PLAN.json').read_text());inputs=[json.loads(z)for z in(B/'review-inputs.jsonl').read_text().splitlines()];done=[]
def check(n,v):
 assert v,n
 done.append(n)
def source_guards(c):
 s=c['study'];v=[x['estimate']for x in c['results']];flow=s['flow'];g=[]
 def guard(n,t):
  assert t,n
  g.append(n)
 guard('PMID7833731 and source0b36c930 exact',c['paper']['pmid']=='7833731' and c['source']['sha256']=='0b36c930393525128d07fb5d8b5fe6a0c4f69db4f830a80c0978d0d13a871b6f')
 guard('No invented DOI',c['paper']['doi'] is None)
 guard('2769 randomized not2520',flow['randomized']==2769 and flow['reported']==2520 and flow['lostOrDied3y']==249)
 guard('Referral and runin flow exact',flow['referred']==6147 and flow['initialExcluded']==1675 and flow['runinWithdrawn']==397 and flow['afterRunin']==4075 and flow['persistentHighGlucoseOrSymptoms']==560 and flow['dietResponders']==746)
 guard('Report obese/nonobese1256/1264',flow['reportedObese']==1256 and flow['reportedNonObese']==1264)
 guard('Metformin restricted obese262',s['TableIAllocationsReportedCohort']['metformin']=={'all':262,'nonObese':0,'obese':262} and c['populations']['metforminOnlyObese'])
 guard('TableI diet664/373/291 not corrected to677',s['TableIAllocationsReportedCohort']['diet']=={'all':664,'nonObese':373,'obese':291})
 guard('Allocation proportions stratified, not equal arms',s['stratification']['nonObeseAllocationPercent']=={'diet':30,'chlorpropamide':20,'glibenclamide':20,'insulin':30} and s['stratification']['obeseAllocationPercent']=={'diet':24,'chlorpropamide':16,'glibenclamide':16,'insulin':24,'metformin':20})
 guard('Obesity inclusive/exclusive source mismatch retained','at least120%' in s['stratification']['textObese'] and 'greater than120%' in s['stratification']['TableIFootnote'])
 guard('Metformin850once up to850TID',s['metformin']['startMgPerDay']==850 and s['metformin']['maxMgPerDose']==850 and s['metformin']['maxDosesPerDay']==3)
 guard('Metformin rescue glibenclamide theninsulin','glibenclamide then insulin' in s['metformin']['rescue'])
 guard('Sulphonylurea doses distinct',s['sulphonylureas']['chlorpropamideMaxMgOnceDaily']==500 and s['sulphonylureas']['glibenclamideMaxMgTwiceDaily']==10)
 guard('Insulin assay100percent proinsulin crossreactivity','100%' in s['assays']['insulin'])
 guard('AlloverallFPG pointCI values',v[1]['fastingGlucoseMedian_mmolL']=={'diet':[9.0,8.8,9.3],'chlorpropamide':[7.0,6.8,7.2],'glibenclamide':[7.6,7.3,7.9],'insulin':[7.4,7.2,7.6]})
 guard('AlloverallHbA1c pointCI values',v[1]['HbA1cMean_percent']=={'diet':[7.6,7.4,7.7],'chlorpropamide':[6.8,6.6,6.9],'glibenclamide':[6.9,6.7,7.0],'insulin':[7.0,6.9,7.1]})
 guard('Metformin not mixed into overall comparator rows',not v[1]['metforminIncludedInTheseOverallRows'])
 guard('Obese matchedFPG Met7.7/7.5/8 diet9.6/9/10.2',v[2]['fastingGlucoseMedian_mmolL']['metformin']==[7.7,7.5,8.0] and v[2]['fastingGlucoseMedian_mmolL']['diet']==[9.6,9.0,10.2])
 guard('Obese matchedHbA1c Met7.1/6.9/7.3 diet7.8/7.6/8',v[2]['HbA1cMean_percent']=={'diet':[7.8,7.6,8.0],'metformin':[7.1,6.9,7.3]})
 guard('OtherobeseFPG comparator CIs retained',v[2]['fastingGlucoseMedian_mmolL']['chlorpropamide']==[7.4,7.1,7.8] and v[2]['fastingGlucoseMedian_mmolL']['glibenclamide']==[8.5,7.9,9.1] and v[2]['fastingGlucoseMedian_mmolL']['insulin']==[7.9,7.6,8.2])
 guard('No formal equivalence inferred',not v[2]['formalEquivalenceOrNoninferiority'])
 guard('Weight absolute levels not zerochange',v[3]['obeseBodyWeightMean_kg']=={'metformin':[87.4,85.3,89.5],'diet':[86.2,84.4,88.0]} and 'not significantly different' in v[3]['obeseMetforminVsDietWeight'])
 guard('Insulin geometricmean levels retained',v[3]['obeseInsulinGeometricMean_mUL']=={'metformin':[13.2,12.4,14.1],'diet':[14.8,13.9,15.7]})
 guard('Abstractinsulin -2.5 distinct discussion -16.5percent',v[3]['abstractMetforminInsulinChange_mUL']==-2.5 and v[3]['discussionInsulinRelativeChanges_percent']['metformin']==-16.5 and v[3]['summariesMustRemainDistinct'])
 guard('TableII literal489+188 mismatch not repaired',v[4]['diet_all']==[[489,74],[188,26],None] and v[4]['dietAllPrintedSum677Not664'])
 guard('TableII obese214+90 mismatch retained',v[4]['diet_obese']==[[214,69],[90,31],None] and v[4]['obeseDietPrintedSum304Not291'])
 guard('Met adherence207/25/30 and23288,not30specificAEs',v[4]['metformin_obese']==[[207,79],[25,10],[30,11]] and v[4]['metforminAnyContinuedBody']==[232,88] and v[4]['refusalAndSideEffectsCombined'])
 guard('TableIII met29/85/93/55 printedpercent11/32/36/21',v[5]['obese_metformin']==[[29,11],[85,32],[93,36],[55,21]])
 guard('TableIII source row mismatch not imputed',v[5]['obese_diet']==[[12,4],[49,16],[147,48],[90,32]] and v[5]['nonObese_diet']==[[10,3],[80,21],[184,49],[98,27]] and v[5]['printedRowsNotSilentlyReconciled'])
 guard('TableIII thresholds less6 not <=6 substitution',v[5]['columns']==['lessThan6.0','6.0to7.7','7.8to14.9','notOnRandomizedTreatment'])
 guard('Met annualany16/11/8 with8.2/5.7/4.1',v[6]['metformin_obese'][:4]==[[16,8.2],[11,5.7],[8,4.1],6.3])
 guard('Met major1peryear0.5percent not zero',v[6]['metformin_obese'][4:]==[[1,0.5],[1,0.5],[1,0.5],0.5] and not v[6]['zeroMetforminHypoglycemia'])
 guard('No invented safetydenominator or cumulative unique3yrisk',v[6]['annualExactDenominators'] is None and v[6]['cumulativeThreeYearUniqueRisk'] is None)
 guard('Annualsafety comparator means distinct',v[6]['diet_all'][3]==1.2 and v[6]['chlorpropamide_all'][3]==13.5 and v[6]['glibenclamide_all'][3]==27.8 and v[6]['insulin_all'][3]==33.4)
 guard('Runin changes not randomized Met effect',v[7]['beforeRandomization'] and not v[7]['randomizedMetforminEffect'] and v[7]['meanSDReduction']=={'fastingGlucose_mmolL':[2.9,3.1],'HbA1c_percentPoints':[1.9,2.0],'weight_kg':[3.7,3.5],'insulin_mUL':[1.3,7.6]})
 guard('Runin hypertension1361to1058 not postdrug endpoint',v[7]['hypertensionRecruitment']==[1361,54] and v[7]['hypertensionAfterTwoMonths']==[1058,42])
 guard('Figure3 monotherapy vsallocation no plotdigitization','no numerical digitization' in v[8]['Figure3'] and v[8]['fullRandomized2769ITTNotEstablished'])
 guard('Bonferroni explicitly retained','Bonferroni for multiple comparisons' in v[8]['tests'])
 guard('No clinicaleventriskreduction or directGLUT1test',not s['ownClinicalEventRiskReduction'] and not s['directMolecularMechanismTest'] and not v[3]['GLUT1Measured'] and not v[8]['longTermClinicalBenefitReported'])
 guard('Unrelated nextarticle excluded',v[8]['unrelatedArticleBottomPhysical6Excluded'])
 guard('No newindependenttrialpatientcounts or scientificrelease',c['newIndependentTrials']==c['newIndependentPatients']==0 and not any(c[k]for k in ['scientificAcceptance','humanApproval','released']))
 return g
check('Fresh original PDF hash',sha(Path(p['source']['ref'].replace('$REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill')))==H if (H:=m['sourceSha256']) else False)
check('Fresh exact suppliedindex hash',sha(Path(p['indexRef'].replace('$REMAPRX_REED_ROOT','/Users/kmfp/papers-for-claude/remaprx-fill')))==p['indexSha256'])
check('Ten dependency hashes exact',len(m['files'])==10 and all(sha(B/n)==h for n,h in m['files'].items()))
check('Exact candidate hash',sha(B/'SOURCE-CANDIDATE.json')==m['candidateSha256'])
gp=json.loads((B/'READINESS.json').read_text());check('Prospective source GP hashes exact',all(sha(B/n)==h for n,h in gp['files'].items()) and gp['ownSourceContentRead'] is False)
check('Allsixtext andvisualpages',c['inspection']['physicalPagesRead']==c['inspection']['visualInspectedPhysicalPages']==[1,2,3,4,5,6])
check('Nine result/claim groups25qualifications',len(c['results'])==len(c['claims'])==9 and len(c['sourceQualifications'])==25)
check('Exactly15Q67uniqueinputfields',len(c['reviewInputs'])==15 and len(inputs)==67 and len({(x['questionId'],x['field'])for x in inputs})==67)
check('All resultclaims bound without scientificgrade',all(cl['resultIds']==[re['id']] and re['grade'] is None and re['benefitGrade'] is None and not re['acceptedSupport'] for cl,re in zip(c['claims'],c['results'])))
bind=[{'resultId':x['id'],'estimate':x['estimate'],'sourceLocators':x['sourceLocators']}for x in c['results']]
check('Q06 narrative all9 directbindings',json.loads(c['reviewInputs'][5]['answer'])==bind)
check('Q06 typed all9 directbindings',next(x for x in inputs if(x['questionId'],x['field'])==('Q06','arm_results'))['value_or_null']==bind)
check('Q06 full source locatorunion',{json.dumps(x,sort_keys=True)for x in c['reviewInputs'][5]['sourceLocators']}=={json.dumps(x,sort_keys=True)for r in c['results']for x in r['sourceLocators']})
check('Physical/printed83to88locators',all(x['printedPage']==str(82+x['physicalPage']) and 1<=x['physicalPage']<=6 for r in c['results']for x in r['sourceLocators']))
check('Conflicts not_reported not no-conflicts',next(x for x in inputs if(x['questionId'],x['field'])==('Q12','conflicts'))['status']=='not_reported')
check('Registration/currentintegrity unchecked',all(next(x for x in inputs if(x['questionId'],x['field'])==('Q13',f))['status']=='not_checked'for f in ['registration','corrections_retractions','supplements']))
check('Multiplicity honestly partial',next(x for x in inputs if(x['questionId'],x['field'])==('Q09','multiplicity'))['status']=='partial')
check('Only actual existing originaluseguide mappings',c['reviewInputs'][13]['downstreamMapping']['existingGuideIds']==['G-METFORMIN','G-CONDITION-C31'] and c['reviewInputs'][13]['downstreamMapping']['canonicalChanges']==0)
done.extend(source_guards(c))
mutations=[('reportedN substituted asrandomized',lambda x:x['study']['flow'].__setitem__('randomized',2520)),('metformin mixednonobese',lambda x:x['study']['TableIAllocationsReportedCohort']['metformin'].__setitem__('nonObese',262)),('matchedobesedietreplacedoverall',lambda x:x['results'][2]['estimate']['fastingGlucoseMedian_mmolL'].__setitem__('diet',[9.0,8.8,9.3])),('literalTableII silentlyrepaired',lambda x:x['results'][4]['estimate'].__setitem__('diet_all',[[489,74],[175,26],None])),('zeroMetforminmajorharms',lambda x:x['results'][6]['estimate']['metformin_obese'].__setitem__(4,0)),('inventedsafetydenominator',lambda x:x['results'][6]['estimate'].__setitem__('annualExactDenominators',262)),('inferredcardiovascularbenefit',lambda x:x['study'].__setitem__('ownClinicalEventRiskReduction',True)),('includedunrelatedarticle',lambda x:x['results'][8]['estimate'].__setitem__('unrelatedArticleBottomPhysical6Excluded',False))];rejected=[]
for name,mutate in mutations:
 x=copy.deepcopy(c);mutate(x)
 try:source_guards(x)
 except AssertionError:rejected.append(name)
 else:raise AssertionError('Mutation not rejected: '+name)
counts=dict(Counter(x['status']for x in inputs));unfinished=sum(x['status']in ['partial','not_checked','not_extracted','not_accessible']for x in inputs)
(B/'VALIDATION.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'result':'PASS_PRIVATE_SOURCE_FIDELITY_GUARDS_NOT_SCIENTIFIC_ACCEPTANCE','count':len(done),'checks':done,'negativeMutationsRejected':rejected,'typedStatusCounts':counts,'canonicalUnfinished':unfinished,'candidateSha256':sha(B/'SOURCE-CANDIDATE.json'),'manifestSha256':sha(B/'AUDIT-MANIFEST.json'),'scientificAcceptance':False,'humanApproval':False,'released':False},indent=2)+'\n');print('PASS',len(done),'guards;',len(rejected),'negative mutations rejected;',counts,'unfinished',unfinished,'independent exact source audit pending')
