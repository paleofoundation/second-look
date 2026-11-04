"""Reconcile current integrity status and reassess the affected diagnosis row."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
def read(p):return json.loads((ROOT/p).read_text())
def save(p,x):(ROOT/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
co='P-COVIDOUT-2023';a6='P-ACTIV6-2026';rid='SYN-D01-C01-DIAGNOSIS'
correction='The actual correction (DOI 10.1016/S1473-3099(23)00562-5) and current appendix were checked. Corrected Table S4 and Results agree on 35/564 versus 58/562 diagnoses and estimated cumulative incidence of 6.3% versus 10.4%. A Discussion sentence says 10.6% and the current registry lists 59 control diagnoses; those discrepancies remain explicit. Numeric claims are tied to the corrected report and table.'
content=read('data/content.json');public=read('data/public-content.json');reviews=read('data/private-reviews.json')
for data in [content,public]:
 s=next(s for s in data['sources'] if s['id']==co)
 s.update({'preview':'COVID-OUT reported fewer later clinician diagnoses after metformin began during acute infection. The correction and current appendix have been checked; numerical claims use the corrected table, with remaining source discrepancies disclosed.','correction':correction,'decisiveLimit':'Selected long-term follow-up and a secondary endpoint limit interpretation; Discussion and registry values differ from the corrected numeric source.'})
 if data is content:
  r=reviews[co];s.update({'review':{x['id']:x['paragraph'] for x in r['sections']},'reviewVersion':r['version'],'reviewHash':r['contentSha256'],'locators':r['questionAnswers'][12]['locators'],'access':'full_text_with_corrected_appendix','filename':'P-COVIDOUT-2023 corrected report and appendix'})
  s.pop('reviewSentences',None)
# These exact old sentences also appear inside serialized FAQ paragraphs.
old='COVID-OUT’s favorable source-reported diagnosis result remains provisional while a correction is unresolved, whereas ACTIV-6 did not meet its reported efficacy threshold for the primary symptom outcome.'
new='COVID-OUT’s favorable diagnosis result is tied to its checked, corrected table, with remaining Discussion and registry discrepancies disclosed; ACTIV-6 did not meet its efficacy threshold for the primary symptom outcome.'
def replace(x):
 if isinstance(x,str):return x.replace(old,new)
 if isinstance(x,list):return [replace(v) for v in x]
 if isinstance(x,dict):return {k:replace(v) for k,v in x.items()}
 return x
content=replace(content);public=replace(public)
reader=read('data/reader-evidence.json');pubreader=read('data/public-reader-evidence.json')
row=next(r for r in reader['synthesisRows'] if r['id']==rid);pr=next(r for r in pubreader['synthesisRows'] if r['id']==rid)
finding='COVID-OUT reported a lower hazard of later clinician-diagnosed Long COVID in its corrected report. ACTIV-6’s secondary diagnosis estimate favored metformin, but its absolute interval included no difference and its primary symptom result did not meet the efficacy threshold.'
limits=[{'text':'COVID-OUT selected a long-term follow-up cohort from adults with overweight or obesity and no known prior infection; ACTIV-6 included substantial prior immunity and missing follow-up.','sources':[co,a6]},
 {'text':'The COVID-OUT correction notice and current appendix were checked. Corrected Table S4 is the numeric source; the Discussion percentage and current registry count still differ.','sources':[co]},
 {'text':'These are secondary diagnosis outcomes with different timepoints and populations. ACTIV-6’s diagnosis comparisons were not adjusted for multiplicity, and its primary symptom endpoint was not positive.','sources':[co,a6]}]
coverage={'scope':'Selected-source assessment, not an exhaustive systematic review','complete':False,'pending':['Independent verification and human scientific review','COVID-OUT Discussion/registry discrepancies retained; corrected Table S4 controls numeric claims','ACTIV-6 separately referenced SAP and full historical registry audit not recovered']}
for r in [row,pr]:
 r['finding']['text']=finding;r['limitations']=limits;r['coverage']=coverage
 r['magnitudeText']='COVID-OUT: hazard ratio 0.59 (95% CI 0.39 to 0.89), using the corrected report. ACTIV-6 secondary diagnosis: risk difference -0.7 percentage points (95% credible interval -1.5 to 0.1).'
 # Retain conservative hold for unresolved cross-source discrepancies, not missing correction access.
 r['status']='provisional_correction_hold'
 r['sourceLocators']=[{'sourceId':co,'label':'Corrected appendix Table S4, printed p9/PDF p10; Results and Figure 2'},{'sourceId':a6,'label':'Published report Results and Table 2; secondary clinician diagnosis analysis'}]
for e in row['effects']:
 if e['sourceId']==co:
  e['recordedNotes']='Corrected Table S4 checked: 35/564 versus 58/562 diagnoses; estimated cumulative incidence 6.3% versus 10.4%; absolute difference 4.1 percentage points (95% CI 0.9 to 7.4). Discussion and current registry discrepancies retained; values are not combined.'
  e['sourceAccess']='full_text_with_corrected_appendix'
  e['locators']=reviews[co]['questionAnswers'][5]['locators']
 if e['sourceId']==a6:
  e['recordedNotes']='Published secondary clinician-diagnosis estimate; not adjusted for multiple comparisons. Primary symptom analysis failed its efficacy decision threshold. Raw diagnosis observations and model estimates are distinct.'
row['conflictsOrCorrections'][0].update({'status':correction,'complete':False})
row.pop('contentSha256',None);row['contentSha256']=digest(row)
# Historical index duplicates are status summaries, not archived raw receipts.
revive='The original REVIVE report is retracted and excluded. The actual notice and replacement DOI 10.7326/ANNALS-26-02144 were acquired and assessed; dose modification and futility stopping are retained.'
def status_updates(x):
 if isinstance(x,str):
  if x.startswith('QUARANTINE: NCBI RetractionIn points to PMID 42832813'):return revive
  if x.startswith('Correction indexed as PMID 37666258; exact amended content not yet reconciled.'):return correction
  return x
 if isinstance(x,list):return [status_updates(v) for v in x]
 if isinstance(x,dict):return {k:status_updates(v) for k,v in x.items()}
 return x
reader=status_updates(reader)
assess=read('editorial/evidence-assessments.json');entry=next(x for x in assess['records'] if x['rowId']==rid)
entry.update({'grade':'Low','integrity':'correction_unresolved','assessedAt':'2026-11-04','rationale':'Two randomized trial families inform later diagnosis after acute infection, but selective follow-up, substantial missing data, secondary endpoint status and lack of multiplicity adjustment limit confidence. The actual COVID-OUT correction and corrected table are now checked. Remaining Discussion/registry discrepancies are disclosed rather than silently reconciled, and ACTIV-6’s absolute diagnosis interval includes no difference. The source-access blocker is resolved; a settled preventive benefit is still not established.'})
texts=[
 'Both trials used masked random allocation. COVID-OUT selected participants for long-term follow-up; ACTIV-6 excluded participants after allocation and had substantial missing day-180 outcomes.',
 'Both address prevention after acute infection, not recovery from established Long COVID. Prior immunity, population selection, case definitions and follow-up timepoints differ.',
 'COVID-OUT reported HR 0.59 (95% CI 0.39 to 0.89) and corrected cumulative incidence 6.3% versus 10.4%. ACTIV-6’s secondary absolute difference was -0.7 points (95% credible interval -1.5 to 0.1).',
 'Diagnosis point estimates favor metformin, but differing populations, follow-up and uncertain absolute effects prevent treating these as a replicated common magnitude. ACTIV-6’s primary symptom result was not positive.',
 'Actual COVID-OUT correction and current appendix obtained and checked. Corrected Table S4 controls the estimates; Discussion and registry discrepancies remain. ACTIV-6’s published full report was assessed, while its separately referenced SAP and exhaustive version history remain unavailable.'
]
for d,t in zip(entry['domains'],texts):d['text']=t
entry['basis']=[{'sourceId':co,'locator':'Corrected appendix Table S4, printed p9/PDF p10; correction DOI 10.1016/S1473-3099(23)00562-5; assessment Q05-Q09 and Q13.'},{'sourceId':a6,'locator':'Published full report Results/Table 2; master protocol v12.0 Appendix G printed pp108-109; assessment Q05-Q09 and Q13.'}]
entry['inputSha256']=digest({'row':row,'publicRow':pr,'sources':[next(s for s in content['sources'] if s['id']==sid) for sid in row['sourceIds']],'publicSources':[next(s for s in public['sources'] if s['id']==sid) for sid in row['sourceIds']]})
summary=read('data/outcome-summaries.json');authored=read('editorial/outcome-summary/authored.json');proof=read('editorial/outcome-summary/assessments.json')
s=next(x for x in summary['records'] if rid in x['synthesisIds']);a=next(x for x in authored if x['id']==s['id']);p=next(x for x in proof['records'] if x['id']==s['id'])
rationale='The correction-access task is complete: COVID-OUT’s actual notice and corrected table were checked. Its Discussion and current registry still disagree with that table, and selective follow-up limits inference. ACTIV-6 contributes an uncertain secondary diagnosis effect and a negative primary symptom decision. No settled benefit letter is assigned to this conservatively held synthesis.'
s['grade'].update({'label':'Source discrepancies retained','rationale':rationale});s['effect'].update({'detail':'HR 0.59 in corrected COVID-OUT report; -0.7 percentage points in ACTIV-6','rationale':finding+' Estimates remain separate; no clinical-importance threshold or pooled effect is imposed.'});s['assessedOn']='2026-11-04'
a.update({'ungradedLabel':s['grade']['label'],'rationale':rationale,'effectDetail':s['effect']['detail'],'effectRationale':s['effect']['rationale'],'assessedOn':'2026-11-04'})
fingerprint=digest({'rows':[row],'publicRows':[pr],'priorAssessments':[entry],'sources':[next(v for v in public['sources'] if v['id']==sid) for sid in row['sourceIds']]})
a['assessedInputSha256']=fingerprint;p.update({'assessedOn':'2026-11-04','authoring':'AI-assisted reassessment after inspection of full reports, actual COVID-OUT correction, current appendix and available protocol/registry records. Independent human approval not recorded.','inputsSha256':fingerprint,'publicRecordSha256':digest(s),'sourceLocators':entry['basis']})
for path,x in [('data/content.json',content),('data/public-content.json',public),('data/reader-evidence.json',reader),('data/public-reader-evidence.json',pubreader),('editorial/evidence-assessments.json',assess),('data/outcome-summaries.json',summary),('editorial/outcome-summary/authored.json',authored),('editorial/outcome-summary/assessments.json',proof)]:save(path,x)
print('COVID-OUT integrity metadata and the affected diagnosis synthesis reassessed; remaining source discrepancies explicit.')
