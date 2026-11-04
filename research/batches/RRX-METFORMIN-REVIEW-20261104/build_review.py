"""Serialize the model's source-based review judgments and exact private-asset bindings.

The prose judgments below are authored review decisions, not rules inferred by code.
The validator separately checks identities, preservation, closure and asset parity.
"""
import datetime, hashlib, json
from pathlib import Path

B = Path(__file__).resolve().parent
PREVIOUS = B.parent / 'RRX-METFORMIN-COMPLETE-20261103'
PRIVATE = B.parents[3] / 'private-guides/metformin-reviewed-20261104'
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name, data): (B/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

plan = read(B/'plan.json')
old = read(plan['inputs'][0]['path'])['manuscript']
new = read(PRIVATE/'manuscript-source.json')['manuscript']
manifest = read(PRIVATE/'output/build-manifest.json')

locators = {
 'MF-LABEL-2025':'Archived Time-Cap label; provenance only, not the current safety authority',
 'MF-LABEL-IR-2025':'Current SPL effectiveTime 20261026; sections 1, 2.3, 2.4, 4, 5.1-5.3, 7/Table 3, 8.1-8.7 and 12.1',
 'MF-LABEL-ER-2025':'Current SPL effectiveTime 20260625; sections 1, 2, 4, 5, 7, 8 and 12.1',
 'MF-FDA-GENERICS':'Generic Drug Facts: reference-product sameness, bioequivalence and labeling requirements',
 'OWEN-2000':'Full report pp607-614; abstract, experimental methods and complex-I/time/concentration results; rat/cell experiments',
 'MF-PD-MECHANISM-2016':'Methods and results for MPTP/probenecid mouse model; autophagy and mitochondrial ROS experiments',
 'MF-MYELOMA-MODELS-2018':'Methods: cell culture, viability and xenograft experiment; six mice per cohort; concentration-response and AMPK/mTOR results',
 'COND-C15-MA32-METABOLIC':'Methods: paired on-treatment samples and assays; Results/metabolic-factor tables; median six-month weight changes',
 'COND-C15-MA32-2022':'Primary ER/PgR-positive outcome, Table 2/Figure 2A; adverse-event text/table; exploratory subgroup methods',
 'COND-C02-COVIDOUT-2022':'Methods: population, primary composite and statistical analysis; primary and secondary outcome results',
 'P-COVIDOUT-2023':'Long-term report and corrected appendix Table S4, printed p9/PDF p10; flow diagram; Discussion/current registry discordance',
 'COVIDOUT-CORRECTION':'Formal correction DOI 10.1016/S1473-3099(23)00562-5: COVID-OUT Study Team and appendix corrected September 1, 2023',
 'P-ACTIV6-2026':'Outcome Measures; Statistical Analysis; Table 3 primary day-180 PASC endpoint and separate clinician-diagnosis endpoint; missingness discussion',
 'MF-COVID-VIRAL-2024':'Methods: optional self-collected nasal samples, administrative censoring and analysis; Results: viral load -0.56 log10 copies/mL',
 'P-KOREA-2026':'Trial methods, eight-week recovery result and Table 2: 84/132 versus 90/132; 14-day treatment',
 'REVIVE-REPLACEMENT':'Replacement DOI ANNALS-26-02144; Interventions, Outcomes, Safety Monitoring, Tables 2 and 5, DSMC dose change/futility stop; available protocol',
 'REVIVE-NOTICE':'Formal retraction/republication notice ANNALS-26-03050; omitted dose amendment and futility stop, replacement analysis and inconclusive metformin result',
 'CP016':'Methods/randomization and flow; Results/Table 2 UPDRS between-group comparison; biomarkers and withdrawals',
 'MF-SCHIZOPHRENIA-PARENT-2023':'Methods: evaluator-masked open-label allocation; Results and Table S2 discussion, MCCB composite estimate; Figure 1, 59/72 completion; registry',
 'CP017':'Methods: 58-person metabolite subset of parent trial; metabolite and functional-connectivity results; same registration/family',
 'MF-NRG-LU001-2021':'Eligible population and primary PFS results; treatment delivery/adherence; 1-year PFS and OS; toxicity',
 'MF-ALMERA-2021':'Methods: failure endpoint includes treatment withdrawal; primary outcome and PFS results; grade 3+ events and limitations',
 'MF-STAMPEDE-2025':'Primary OS results; subgroup interaction; metabolic effects at 104 weeks; adverse-event windows and diarrhea counts',
 'COND-C17-MET-2015':'Abstract and survival results/Figure 2; six-month survival; dose modifications and exploratory concentration analysis',
 'MF-ADENOMA-2016':'Flow and one-year colonoscopy results; total polyps and adenomas; abstract/table denominator inconsistency; limitations',
 'MF-COLON-MECHANISM-2010':'Scanned report visually reread, archive PDF pages 5-10 = printed pp1077-1082; abstract, Statistical analysis, Results, Tables 1-2/Figure 2',
 'MF-MASTERS-2019':'Main report DXA/CT/muscle-fiber/strength results; registered type-II fiber outcome; corrigendum to Table 2 relative strength',
 'MF-METPREVENT-2025':'Methods: frail/prefrail population, immediate-release regimen; primary walk-speed estimate, discontinuation and hospital admission results',
 'CP018':'2023 narrative review scope, sarcopenia mechanisms and clinical evidence; predates MET-PREVENT outcome report',
 'INZUCCHI-2014':'2014 systematic review abstract/conclusions and renal evidence; historical policy is subordinate to current labels',
}

# One substantive judgment per original manuscript block, in chapter order.
judgments = {
 'orientation': [
  'Approved type 2 diabetes use is distinguished from investigational repurposing; current IR/ER label populations govern.',
  'Top-line synthesis preserves the major null cancer results and separates acute prevention from treatment of established Long COVID.',
  'Scope expressly describes a selected evidence set, not a systematic review or complete account of all metformin indications.',
  'Question/outcome table keeps human neurological pilots, cancer endpoints, prevention/treatment and physical function separate; no pooled benefit claim.',
  'Shared safety limitation identifies GI effects, B12, kidney function and serious lactic-acidosis risk; it remains visible in all variants.',
 ],
 'mechanisms': [
  'Label-supported effects on hepatic glucose output, intestinal absorption and insulin sensitivity are distinguished from proposed repurposing pathways.',
  'Owen full report supports time/concentration-dependent complex-I findings in rat/cell preparations; micromolar cell exposure and millimolar particle exposure are not a human efficacy estimate.',
  'Parkinson mouse and myeloma cell/xenograft mechanisms are explicitly preclinical; no disease-modification or human cancer response inference.',
  'The mechanism/marker/outcome ladder correctly separates molecular changes, metabolic/viral surrogates and patient-important outcomes.',
  'MA.32 metabolic improvement does not override the null primary invasive disease-free survival result; related reports are one trial family.',
 ],
 'infection': [
  'Acute treatment, later diagnosis prevention and established-symptom treatment are separate questions with different study populations.',
  'COVID-OUT acute primary OR 0.84 (0.66-1.09) is accurate; secondary estimates are not promoted to primary success or multiplicity-adjusted confirmation.',
  'Corrected appendix Table S4 verifies 35/564 versus 58/562, KM 6.3% versus 10.4%, 4.1 percentage points (0.9-7.4) and HR approximately 0.59; raw fractions and KM estimates remain separate.',
  'Actual correction addresses authorship and appendix; guide does not invent a cell-by-cell change history. Discussion 10.6% and registry control-count discrepancy remain disclosed.',
  'Corrected to identify self-reported day-180 symptoms or death as the primary endpoint, with no deaths; 2,983 mITT, model rates, -0.8 (-2.2 to 0.6) points and 83% versus 97.5% threshold are supported by Table 3/methods.',
  'Explains differences in prior immunity, ascertainment, baseline risk and missing follow-up; avoids claiming the two prevention trials measured identical events.',
  'Viral-load estimate -0.56 log10 copies/mL (-1.05 to -0.06) matches report; optional swabs, RNA versus viable virus and COVID-OUT family overlap are explicit.',
  'Korean established-PASC trial: 396 randomized, 132 per arm, 84 versus 90 recovery events, -4.55 points (-15.98 to 6.88); treatment lasts 14 days and outcome is eight weeks.',
  'Notice/replacement justify exclusion of original REVIVE efficacy analysis. Sequential 750/500 mg ER cohorts, safety dose amendment and futility stop are not a randomized dose comparison.',
  'Added FSS mean-of-nine 1-7 scale, direction and exact day-60 CrIs: -0.02 (-0.48 to 0.44), -0.04 (-0.63 to 0.54). AE counts 49/111 versus 49/138 verified. Protocol timing uncertainty retained.',
  'Questions focus on prevention versus treatment, applicability, outcomes and uncertainty; no self-prescribing course is recommended.',
 ],
 'neurology': [
  'Parkinson pilot randomized 60 and retained 52 after eight withdrawals; within-arm improvement is not evidence of a positive between-arm UPDRS effect.',
  'Biomarker movement is not established disease modification; attrition and preclinical-to-clinical translation limitations remain explicit.',
  'Schizophrenia parent trial is open-label with masked evaluators, 72 randomized and 59 completers; MCCB composite 3.43 (1.83-5.02) is a scale estimate, with population and timing limits.',
  '58-person metabolite companion and smaller imaging analyses share the parent study family; correlations and within-arm changes do not establish a causal metabolic mediator.',
  'Future-evidence discussion calls for replication and functional outcomes; it does not claim efficacy in an unstudied neurological population.',
 ],
 'breast': [
  'MA.32 3,649 randomized; primary hormone-receptor-positive group 234/1268 versus 231/1265, HR 1.01 (0.84-1.21); clinical null result accurately dominates synthesis.',
  'Selected paired metabolic subset has median six-month weight changes -1.4 kg versus +0.5 kg; not a survival endpoint or independent trial; molecular subgroup work is exploratory.',
  'Grade 3 nonhematologic toxicity direction is accurately unfavorable. Published count/percentage and diarrhea-order inconsistencies preclude inventing a precise incremental harm rate.',
 ],
 'lung': [
  'NRG-LU001 eligible analysis n=167, PFS 51.3% versus 60.4%, HR 1.15 (0.77-1.73); no OS benefit and incomplete metformin delivery are reported.',
  'ALMERA primary endpoint includes treatment discontinuation, so its 18/26 versus 12/28 failures are not relabeled as ordinary disease progression alone.',
  'ALMERA PFS HR 2.42 (1.14-5.10) and severe-event counts 14/26 versus 7/28 match source; small early-closed trial and imbalance limit certainty without erasing harm signal.',
  'Different chemoradiation settings are preserved; these studies do not instruct patients to discontinue metformin prescribed for diabetes.',
 ],
 'prostate': [
  'STAMPEDE 1,874 men, most treated with ADT/docetaxel and few with newer ARPIs; 453 versus 473 deaths, HR 0.91 (0.80-1.03) is not an overall survival benefit.',
  'High-volume subgroup signal is not presented as confirmed OS effect modification; interaction evidence governs, not contrasting subgroup P values.',
  '104-week weight gains 2.00 versus 4.40 kg and adjusted difference -2.48 (-3.55 to -1.41) are distinguished from unadjusted subtraction and from cardiovascular/survival outcomes; subset n=583.',
  'Diarrhea 600/921 versus 350/938 and grade 3 counts 46 versus 29 match report; different ascertainment windows prevent a simplistic cross-trial safety comparison.',
 ],
 'pancreas': [
  '121-patient gemcitabine/erlotinib setting retained; six-month survival 56.7% versus 63.9%, medians 6.8 versus 7.6 months and unadjusted HR rounded to 1.06 (0.72-1.55) are accurate.',
  'Dose reductions and exploratory drug-level associations are described without claiming that higher prescribed dosing would improve survival.',
 ],
 'colorectal': [
  '151 randomized but 133 colonoscopies (71/62); polyps 27/71 versus 35/62, adenomas 22/71 versus 32/62, RR 0.60 (0.39-0.92) reproduced with actual denominators.',
  'Short-term adenoma/polyp endpoints are not cancer mortality; attrition, regional population, multiplicity and printed adenoma percentage discrepancy retained.',
  'Scanned Hosono pp1077-1082 verify 26 randomized and 23 evaluable, all three missing from metformin; primary comparisons are within-arm over one month, not proof from differing P values.',
  'No lifetime cancer-prevention, universally effective dose, long-term safety or replacement-for-surveillance claim is made.',
 ],
 'myeloma': [
  'Human-derived cell lines are not treated patients; xenografts have six mice per group. Concentrations and AMPK/mTOR experiments support laboratory mechanisms only.',
  'No human response, survival or combination-safety benefit is inferred from the cell/mouse evidence.',
 ],
 'physical': [
  'MASTERS DXA/CT muscle gains and registered type-II fiber result are kept separate; corrected relative-strength result is not described as statistically positive.',
  'MET-PREVENT frail older population and four-month endpoint retained; adjusted walk-speed difference 0.001 m/s (-0.06 to 0.06) excludes the trial 0.1 m/s target.',
  'Discontinuation 13/34 versus 5/36 and admissions 12/35 versus 3/36 are presented with distinct denominators; immediate-release regimen without titration limits generalization.',
  'CP018 is a 2023 narrative review, not an additional trial and not a demonstration of human lifespan extension; subsequent negative trial evidence remains prominent.',
 ],
 'interpretation': [
  'Applicability table asks about population, timing, formulation, outcome and analysis; it does not generate individualized benefit probabilities.',
  'Refined hazard ratio as a time-specific rate among people not yet diagnosed; maintained 10.4-6.3=4.1 point absolute difference without equating KM risks, hazards and raw fractions.',
  'Confidence and credible intervals remain distinct; intervals including the null are not proof of equivalence or exact absence of effect.',
  'Subgroup interaction principle is accurate and stops isolated favorable subgroup findings from overriding overall estimates.',
  'COVID-OUT, MA.32 and schizophrenia companion reports are explicitly linked as shared trial families, avoiding double-counted independent replication.',
 ],
 'safety': [
  'GI effects, B12 reduction and insulin/secretagogue-associated hypoglycemia match current label warnings.',
  'Added omitted formal contraindications: metformin hypersensitivity and acute/chronic metabolic acidosis including DKA. Retained renal thresholds and made the minimum annual renal-check interval explicit.',
  'Strengthened hepatic avoidance and mitochondrial-disease not-recommended wording to match current labels; fatal lactic-acidosis risk and urgent assessment language retained.',
  'Procedure interruption is conditional on contrast route, renal function and other factors; no universal stop/restart instruction is supplied.',
  'Annual hematologic monitoring and B12 every two to three years match labels; symptoms/risk may need individualized assessment.',
  'ER whole-tablet administration is product-specific; label AE tables are not a head-to-head tolerability trial or proof of antiviral/anticancer superiority.',
  'Generic approval is relative to a corresponding reference product; different release formulations are not declared interchangeable. Old label is provenance only.',
  'Medication/renal/procedure/B12 questions retained and expanded for omitted contraindications, pregnancy planning and breastfeeding; new interaction and special-population paragraphs precede the questions.',
 ],
 'discussion': [
  'Personal worksheet is a reader-held preparation tool, not a request to transmit medical details to the service.',
  'Discussion prompts preserve indication, target outcome and applicability; no diagnosis, prescription or universal regimen is offered.',
  'Medication, kidney function, adverse effects and monitoring prompts support professional discussion rather than automated eligibility decisions.',
  'Condition-specific questions reflect distinct study populations and outcome limitations without promising a benefit.',
  'Glossary definitions of primary outcome, surrogate, intention-to-treat, attrition, trial family and off-label use are consistent with their use in the guide.',
 ],
 'sources-scope': [
  '33 dispositions versus 30 cited references and 24 study assessments are different inventories, not a reference ceiling or a claim of 33 independent trials.',
  'Abrilla and El-Mir are excluded for missing full text, and the retracted REVIVE original is excluded for integrity; no excluded source supports a claim.',
  'Source/supplement/protocol access limits remain visible; completed assessment of available material does not imply complete access.',
  'Updated provenance records completed model review while preserving genuine pending independent clinical, human editorial and legal/commercial decisions.',
 ],
}

corrected = {('infection',5),('infection',10),('interpretation',2),('safety',2),('safety',3),('safety',8),('sources-scope',4)}
audits = []
for chapter in old['chapters']:
    assert len(chapter['blocks']) == len(judgments[chapter['id']]), chapter['id']
    for i,block in enumerate(chapter['blocks'],1):
        audits.append({
            'chapterId':chapter['id'], 'block':i, 'sourceIds':block['sourceIds'],
            'decision':'corrected' if (chapter['id'],i) in corrected else ('verified' if block['sourceIds'] else 'editorial_only'),
            'rationale':judgments[chapter['id']][i-1],
            'sourceLocators':[{'sourceId':sid,'locator':locators[sid]} for sid in block['sourceIds']],
            'outputBlock':10 if chapter['id']=='safety' and i==8 else i,
        })

finding_specs = [
 ('R01','high','Formal contraindications omitted','safety:2','Added hypersensitivity and acute/chronic metabolic acidosis, including DKA, alongside the existing severe-renal-impairment contraindication.',['MF-LABEL-IR-2025','MF-LABEL-ER-2025']),
 ('R02','moderate','Risk-management wording incomplete','safety:2-3','Made annual renal assessment, hepatic avoidance, mitochondrial-disease recommendation and potentially fatal lactic acidosis explicit.',['MF-LABEL-IR-2025','MF-LABEL-ER-2025']),
 ('R03','moderate','Interaction discussion too generic','safety:new8','Added source-supported drug classes/examples and alcohol, while preserving individualized review rather than blanket discontinuation.',['MF-LABEL-IR-2025','MF-LABEL-ER-2025']),
 ('R04','moderate','Special-population applicability missing','safety:new9-10','Added pregnancy/lactation evidence limits, potential ovulation, product-specific pediatric limits and related discussion questions.',['MF-LABEL-IR-2025','MF-LABEL-ER-2025']),
 ('R05','moderate','ACTIV-6 primary outcome undefined','infection:5','Defined self-reported symptoms or death at day 180, separated clinician diagnosis, and gave posterior probability and prespecified success threshold.',['P-ACTIV6-2026']),
 ('R06','moderate','REVIVE fatigue units and intervals unclear','infection:10','Defined FSS scale and direction, and included exact dose-specific credible intervals.',['REVIVE-REPLACEMENT','REVIVE-NOTICE']),
 ('R07','low','Hazard ratio explanation imprecise','interpretation:2','Specified time-specific new-diagnosis rate among not-yet-diagnosed participants; kept hazards distinct from cumulative risk.',['P-COVIDOUT-2023','COVIDOUT-CORRECTION']),
 ('R08','low','Edition timestamp was in the future','metadata:updatedAt','Replaced candidate-1 hardcoded 12:00Z timestamp with actual UTC generation time in a new edition; historical candidate preserved.',[]),
]
findings=[dict(id=i,severity=s,title=t,location=l,resolution=r,sourceIds=ids,status='resolved_in_candidate_2') for i,s,t,l,r,ids in finding_specs]
review = {
 'schemaVersion':1, 'productId':new['productId'],
 'reviewer':'Codex (OpenAI), model review; not independent human approval',
 'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
 'inputEditionId':old['editionId'], 'outputEditionId':new['editionId'],
 'method':'Read all original manuscript blocks; reconcile each against the prior completed Q01-Q15 assessments and targeted primary-source re-reading of outcomes, methods, safety and integrity records. Re-read scanned Hosono report pages visually. No fresh exhaustive systematic search or independent replication of patient-level analyses is claimed.',
 'inputHashes':plan['inputs'], 'blockAudits':audits, 'findings':findings,
 'newBlockAudits':[
  {'chapterId':'safety','block':8,'sourceIds':['MF-LABEL-IR-2025','MF-LABEL-ER-2025'],'decision':'verified','rationale':'Examples and mechanisms match current label section 7/Table 3. Not exhaustive; distinguishes increased monitoring/risk assessment from contraindication.','sourceLocators':['IR section 7/Table 3; ER section 7']},
  {'chapterId':'safety','block':9,'sourceIds':['MF-LABEL-IR-2025','MF-LABEL-ER-2025'],'decision':'verified','rationale':'Current sections 8.1-8.4 support pregnancy uncertainty, milk presence, ovulation and product-specific pediatric limits; pregnancy is not labeled a blanket contraindication.','sourceLocators':['IR/ER sections 1, 8.1, 8.2, 8.3, 8.4']},
 ],
 'sourceChecks':[{'sourceId':sid,'locator':locators[sid],'result':'claim_support_with_recorded_limits'} for sid in plan['sourceIds']],
 'webChecks':[
  {'url':'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=30658e19-8e6e-49aa-a007-e414224797c5','date':'2026-11-04','result':'Current official page reachable; safety claims checked against hashed current SPL text.'},
  {'url':'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=96c8a89d-99db-24b1-e053-2a95a90ac2b8','date':'2026-11-04','result':'Current official page reachable; safety claims checked against hashed current SPL text.'},
  {'url':'https://doi.org/10.7326/ANNALS-26-03050','date':'2026-11-04','result':'Web tool could not open DOI; substantive check uses previously acquired hashed publisher full-text notice, not a failed request.'},
  {'url':'https://doi.org/10.7326/ANNALS-26-02144','date':'2026-11-04','result':'Web tool could not open DOI; substantive check uses previously acquired hashed publisher replacement full text and tables.'},
 ],
 'checks':{
  'sourceCountCeiling':None, 'originalBlocksReviewed':len(audits), 'outputBlocks':sum(len(c['blocks']) for c in new['chapters']),
  'references':len(new['references']), 'findingsResolved':len(findings), 'newStudyAssessmentRequired':False,
  'covidOutCorrection':'Verified corrected Table S4; discrepancies retained and attributed.',
  'reviveQuarantine':'Retracted original remains excluded; replacement reviewed as same trial family, metformin results inconclusive.',
  'clinicalContent':'Model review completed with safety/applicability corrections; no clinician credential or independent medical approval claimed.',
  'editorial':'All original blocks reviewed; numerical units/endpoint definitions and status updated; no mechanistic-to-clinical or within-arm-to-between-arm promotion.',
  'legalCommercialContent':'Editorial risk screen only: original synthesis, links rather than reproduced papers, educational scope, no individualized prescribing or promised outcomes; not legal approval or merchant-terms acceptance.',
  'artifactVerification':'See verification.json and visual-review.json, bound to exact output hashes.',
 },
 'retainedLimits':[
  '15 of 24 source assessments retain named access gaps; this review does not convert them to complete source access.',
  'COVID-OUT discussion/registry mismatch, MA.32 toxicity inconsistencies, adenoma percentage discrepancy and REVIVE protocol/method uncertainties are disclosed rather than silently repaired in the source literature.',
  'No human-reader usability study or assistive-technology session was performed; PDF remains untagged and not PDF/UA certified.',
  'No real independent clinician, human editor or legal/commercial approver has signed the edition; model review cannot create their identities or approval.',
 ],
 'decision':'review_complete_with_corrections', 'humanClinicalApproval':'pending', 'humanEditorialApproval':'pending', 'commercialLegalApproval':'pending',
}
write('review.json',review)
artifacts = {
 'productId':new['productId'], 'editionId':new['editionId'], 'version':new['version'], 'state':'private_reviewed_candidate',
 'supersedes':'metformin-20261104-candidate-1',
 'source':{'path':str(PRIVATE/'manuscript-source.json'),'sha256':sha(PRIVATE/'manuscript-source.json')},
 'buildManifest':{'path':str(PRIVATE/'output/build-manifest.json'),'sha256':sha(PRIVATE/'output/build-manifest.json')},
 'assets':[{'file':str(PRIVATE/'output'/name),**entry} for name,entry in manifest['assets'].items()],
 'assessmentCoverageSha256':sha(PREVIOUS/'coverage.json'),
 'modelReview':{'path':str(B/'review.json'),'sha256':sha(B/'review.json'),'decision':review['decision']},
 'independentClinicalReview':'pending','humanEditorialApproval':'pending','commercialLegalApproval':'pending',
 'release':'not_deployed_or_for_sale', 'pdfAccessibility':'Selectable text, links and bookmarks checked separately; untagged, not PDF/UA certified.',
}
write('guide-artifacts.json',artifacts)
write('guide-block-map.json',{
 'productId':new['productId'],'editionId':new['editionId'],'webSha256':manifest['assets']['web-manuscript.json']['sha256'],
 'blocks':[{'chapterId':c['id'],'block':i,'sourceIds':b['sourceIds'],
            'assessments':[str((PREVIOUS/'assessments'/f'{sid}.json').relative_to(B.parents[2])) for sid in b['sourceIds'] if (PREVIOUS/'assessments'/f'{sid}.json').exists()]}
           for c in new['chapters'] for i,b in enumerate(c['blocks'],1)],
})
print(json.dumps({'reviewedBlocks':len(audits),'newBlocks':2,'resolvedFindings':len(findings),'editionId':new['editionId']}))
