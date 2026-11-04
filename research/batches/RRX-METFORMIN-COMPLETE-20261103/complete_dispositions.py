import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
sources={s['sourceId']:s for s in json.loads((B/'source-access.json').read_text())['sources']}
notes={
'MF-LABEL-2025':('official_context','Historical Time-Cap label revised February 2025. Verified type 2 diabetes indication, kidney precautions, B12 monitoring and GI adverse effects. Current formulation-specific SPLs take precedence for this edition.','Archived official product labeling; not an independent efficacy study.'),
'MF-LABEL-IR-2025':('official_context','Current SPL effectiveTime October 26, 2026. Sections 1,2,4,5,6,7,12 inspected. Type 2 diabetes indication in adults and age 10+; renal contraindication below eGFR30; initiation not recommended 30–45; reassess below45. GI effects, B12 deficiency and serious lactic acidosis precautions retained.','Stable ID contains 2025 but retrieved version is 2026. Label trial rates cannot be compared directly to ER trials. No repurposing approval inferred.'),
'MF-LABEL-ER-2025':('official_context','Current SPL effectiveTime June 25, 2026. Sections 1,2,4,5,6,7,12 inspected. Adult type 2 diabetes indication; swallow whole; formulation-specific dosing and comparable renal/interaction/B12 precautions.','This product’s 23-person crossover reports Cmax 2849 versus 1820 ng/mL for ER2000 once daily versus IR1000 twice daily, despite slower appearance. Do not claim universally lower ER peak concentration or universal IR superiority.'),
'MF-FDA-GENERICS':('official_context','FDA Generic Drug Facts page, content dated November 1, 2021, accessed November 3, 2026. Approved generics must meet sameness and quality requirements relative to their corresponding reference product.','Does not mean immediate- and extended-release products are interchangeable schedules or establish efficacy for a new indication.'),
'COVIDOUT-CORRECTION':('integrity_context','Actual Lancet Infectious Diseases correction DOI10.1016/S1473-3099(23)00562-5 and current appendix acquired. Notice adds COVID-OUT Study Team to author list and records appendix correction September 1, 2023; it does not enumerate every changed cell. Current Table S4 agrees with Results:35/564 versus58/562, KM6.3% versus10.4%, HR.587.','Original Discussion10.6% differs; current registry lists59 placebo diagnoses. Edition binds estimates to current corrected report/table, retains discrepancies and does not claim complete historical cell-by-cell reconciliation.'),
'REVIVE-NOTICE':('integrity_context','Actual retraction/republication notice DOI10.7326/ANNALS-26-03050 acquired. Original omitted dose modification and futility stopping; replacement DOI10.7326/ANNALS-26-02144 acquired and assessed separately.','Original remains excluded. Replacement result for metformin is inconclusive; not an independent second trial.'),
'P-REVIVE-2026':('excluded_retracted','Original DOI10.7326/ANNALS-25-03959, PMID41911553 is retracted and replaced. Exact notice and replacement now acquired; prior “reason/replacement not acquired” state is superseded.','No efficacy claim may cite the original. Replacement sourceId REVIVE-REPLACEMENT; dose-change and futility information retained. Original source history preserved.'),
'ABRILLA-2021':('excluded_full_text_unavailable','PubMed/Europe PMC abstract and identity acquired; bounded publisher/repository search did not recover complete report and appendices.','No fully assessed review or quantitative formulation-superiority claim. Nine-trial abstract cannot substitute for study-level methods, heterogeneity and risk-of-bias assessment. Full-text access is needed before inclusion.'),
'EL-MIR-2000':('excluded_full_text_unavailable','Identity and abstract located. Publisher PDF returned403; alternative open-copy endpoint returned202 with zero bytes.','No full-text assessment or efficacy/mechanistic claim attributed to this unacquired report. Owen2000 is assessed directly; its account of El-Mir is not substituted for the original.')}
out=[]
for sid,(disposition,finding,limit) in notes.items():
 s=sources[sid];out.append({'sourceId':sid,'disposition':disposition,'finding':finding,'limits':limit,'sourceAssets':[{'path':a['path'],'sha256':a['sha256']} for a in s['assets']],'checkedAt':'2026-11-04','humanApproval':'pending','release':'private_candidate'})
(B/'context-and-exclusions.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
rows=[]
for sid,s in sources.items():
 f=B/'assessments'/f'{sid}.json'
 if f.exists():
  r=json.loads(f.read_text());row={'sourceId':sid,'disposition':'assessed_for_bounded_private_guide','assessment':str(f.relative_to(B)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'inputCount':len(r['inputs']),'completion':r['completion'],'unresolvedInputs':r['unresolvedInputs']}
 else:
  n=next(n for n in out if n['sourceId']==sid);row={'sourceId':sid,'disposition':n['disposition'],'record':'context-and-exclusions.json','limits':n['limits']}
 rows.append(row)
payload={'schemaVersion':1,'version':'2026-11-04.1','originalSourceCount':30,'currentSourceCount':len(rows),'fixedSourceQuota':None,'scientificAssessmentCount':sum('assessment' in r for r in rows),'coverage':rows,'release':'private_candidate','independentVerification':'pending','humanApproval':'pending','meaning':'Coverage is a disposition ledger, not a claim that every appendix, question or approval is complete. Missing information remains explicit and constrains manuscript claims.'}
(B/'coverage.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
print(payload['scientificAssessmentCount'],'assessments;',len(rows),'source dispositions')
