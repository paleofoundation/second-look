from assessment_writer import write_review, SOURCES

write_review('P-COVIDOUT-2023','COVID-OUT: long COVID prevention after treatment of acute infection',[
('Methods: Study design; appendix Table S8, printed pp17-18',[
'Evaluate whether early outpatient metformin, ivermectin or fluvoxamine reduces later provider-diagnosed long COVID.',
'Long COVID was added during recruitment in April 2021; the corrected appendix traces its initial primary-outcome listing, later secondary status, and pre-unblinding analysis-plan timing.',
'The relevant claim is prevention of a later diagnosis after acute-infection treatment, not treatment of established long COVID.'
],'The evolving endpoint must be described rather than presented as an unchanged original primary outcome.'),
('Methods: Participants; Results; Table; Figure 1',[
'Human adults aged 30-85 with overweight or obesity and a recent SARS-CoV-2 infection.',
'Six US sites recruited remotely; symptoms under 7 days, positive test within 3 days, no known previous infection. Pregnancy was permitted for metformin randomization.',
'1431 randomized; 1323 in the acute modified intention-to-treat population; 1126 entered this long-term analysis, including 564 assigned metformin and 562 matched placebo.'
],'The 1126 participants are a selected follow-up population, not all randomized participants.'),
('Methods: Procedures and Randomisation and masking',[
'Oral metformin tablets; the related acute report identifies immediate release, not an extended-release comparison.',
'The studied course used 500 mg on day 1, 500 mg twice daily on days 2-5, then 500 mg morning and 1000 mg evening through day 14.',
'A factorial design included ivermectin, fluvoxamine or their matched placebos; other treatments after enrollment were recorded.',
'Acute follow-up was 28 days; long-term surveys continued to day 300.'
],'These are study exposures, not a recommended self-treatment schedule.'),
('Methods: Randomisation and masking; appendix Figures S1-S2',[
'Identical metformin placebo, with concurrently randomized controls.',
'Equal allocation to available arms, stratified by site; women pregnant or lactating entered only the metformin/placebo comparison.',
'A pregenerated mass-weighted urn sequence was implemented through a password-protected application; allocation was concealed except from the responsible statistician and pharmacists.',
'Participants, investigators, treating clinicians and outcome assessors were masked; matched pills, opaque packaging and coded packets supported concealment.',
'Recruitment ran December 2020 to January 2022; the factorial arms opened and closed at different dates.'
],'Balanced factorial assignments support the metformin contrast; reports of different outcomes remain one trial family.'),
('Methods: Outcomes; appendix Table S7 and Table S8',[
'Long COVID diagnosis was a prespecified secondary outcome by the final pre-unblinding protocol; acute severe COVID was the primary outcome.',
'Participants reported whether a medical provider had diagnosed long COVID and the approximate date; medical records were requested.',
'Diagnoses were assessed through 300 days, with diagnosis questions in surveys from day 180 onward.',
'A clinical diagnosis outcome, not direct enumeration of every persistent symptom or a biological cure.',
'NA: No continuous symptom-scale minimal important difference applies to the binary diagnosis endpoint.'
],'Diagnosis depends partly on access to care and recognition; it is not interchangeable with symptom-based long COVID definitions.'),
('Current Results; corrected appendix Table S4, printed p9 / PDF p10',[
'Table S4 reports day-300 cumulative incidence 6.3% (95% CI 4.2-8.2) for metformin and 10.4% (7.8-12.9) for placebo.',
'Observed diagnoses were 35/564 for metformin and 58/562 for placebo; the observed proportions 6.2% and 10.3% differ from the Kaplan-Meier estimates.',
'The reported absolute reduction is 4.1 percentage points (95% CI 0.9-7.4); unadjusted HR 0.587 (0.386-0.893), rounded in the main Results to 0.59 (0.39-0.89).',
'Between randomized treatment assignments; the adjusted HR is 0.599 (0.393-0.911), not a second independent result.',
'The confidence interval excludes an HR of 1 for this endpoint, but does not establish the same benefit for every subgroup.'
],'Use the concordant current Results and corrected Table S4. The Discussion retains a discordant 10.6% placebo value; do not silently erase it or calculate from it.'),
('Methods: Statistical analysis; Results follow-up paragraph',[
'28/564 metformin and 24/562 placebo participants were lost before day 270.',
'1074/1126 completed at least 9 months or reported a diagnosis; those without a diagnosis were censored at their final completed survey.',
'At least one received dose was required for the original modified intention-to-treat analysis; exact complete-course adherence is not quantified in this long-term report.',
'People never receiving a dose and people not entering qualifying long-term follow-up were excluded from this analysis.',
'Modified intention-to-treat followed by a consenting long-term analysis cohort; it is not a full randomized-population estimand.',
'The individual participant is the unit; repeated surveys and factorial comparisons do not increase independent sample size.'
],'Censoring and selection can bias estimates if related to unobserved long COVID risk. Similar measured attrition does not prove missingness was noninformative.'),
('Current Results and Discussion; acute report safety cross-reference',[
'Long-term report refers safety ascertainment to the acute companion publication.',
'The 1126 long-term respondents are not automatically the correct denominator for every acute adverse-event analysis.',
'The current registry lists non-COVID adverse events through day 14 and serious events through day 28, with nonsystematic ascertainment for listed nonserious events. It records zero participants with serious drug-related adverse events in all six allocation arms and one all-cause death in the metformin-plus-ivermectin arm; this must not be interpreted as zero treatment risk.',
'Current NCT04510194 results report 14-day all-cause drug discontinuation by six allocation arms: metformin only 56/284, double placebo 49/295, ivermectin only 25/206, fluvoxamine only 32/159, metformin plus fluvoxamine 50/175, and metformin plus ivermectin 29/204. These are allocation-arm counts, not three independent comparisons or all drug-attributable harms.',
'The drug exposure lasted 14 days, whereas diagnosis follow-up extended to 300 days.'
],'This prevention report cannot establish comprehensive or long-term drug safety; it also cannot override prescribing-label contraindications.'),
('Methods; Results; Discussion; appendix Table S8',[
'Masking and concealed allocation reduce some biases; selective entry into long-term follow-up and provider-diagnosis ascertainment remain important concerns.',
'Randomization reduces baseline confounding; adjusted models included other trial drugs and vaccination status.',
'Outcome status changed during the trial, as documented in Table S8; original protocol/SAP versions have not all been directly re-read here.',
'Subgroup estimates are low-powered and numerous; an earlier-start subgroup is not proof that timing modifies treatment effect.',
'Only 93 total diagnoses occurred; subgroup estimates are especially imprecise.',
'Current Discussion says 10.6% placebo incidence, versus Results and corrected Table S4 10.4%. The current registry also lists 59 placebo diagnoses versus 58 in corrected Table S4, with 35 metformin diagnoses in both. The guide uses the identified corrected report estimates and retains these source discrepancies; it does not silently reconcile participant-level differences.'
],'A positive secondary outcome is informative but should not be turned into universal prevention advice.'),
('Participants; Discussion applicability limitations',[
'Most directly relevant to early outpatient treatment in adults with overweight/obesity and no known previous infection.',
'The studied immediate-release course does not establish equivalence to extended release or a different duration.',
'Prevention of a provider diagnosis differs from treating fatigue or other symptoms in established illness.',
'Younger adults, normal-BMI adults, recurrent infection, current variants and heavily boosted populations were not all represented adequately.'
],'Present the result next to the later prevention and established-illness trials, with their different populations and endpoints.'),
('NCT04510194; main article references; current 30-reference guide inventory',[
'S-COVIDOUT-2023 / NCT04510194.',
'COND-C02-COVIDOUT-2022 reports acute outcomes and MF-COVID-VIRAL-2024 reports viral load from the same trial.',
'These overlapping reports must not be counted as three independent clinical trials.',
'This reconciliation covers the current guide inventory and retrieved publisher records, not an exhaustive new systematic search.'
],'The viral-load companion may support mechanism; it cannot independently replicate the clinical prevention outcome.'),
('Byline; Declaration of interests; Acknowledgments; Role of funding source',[
'Carolyn T. Bramante and colleagues, including the COVID-OUT Study Team added by correction.',
'Investigator-initiated multicenter US decentralized trial.',
'Parsemus Foundation, Rainwater Charitable Foundation, Fast Grants and UnitedHealth Group Foundation; investigators also disclose institutional/NIH support. Funders reportedly had no design, data or writing role.',
'Apotex supplied fluvoxamine/placebo and Edenbridge supplied ivermectin/placebo; the report does not identify these donations as metformin supply.',
'The report lists multiple author financial relationships, including consulting, grants and holdings for J. Buse, and consulting for M. Puskarich; it does not say all authors had no conflicts.'
],'Disclosures inform scrutiny but neither prove nor disprove the randomized result.'),
('Correction DOI 10.1016/S1473-3099(23)00562-5; corrected appendix cover and Table S4',[
'Published report with online correction effective September 1, 2023.',
'Current publisher HTML, the correction PDF, the corrected appendix and a prior main-report PDF were obtained.',
'Corrected appendix cover explicitly identifies September 1, 2023; Table S4 was visually inspected on PDF page 10.',
'NCT04510194; the appendix gives the protocol/SAP change chronology, but full original version files are not all inspected in this assessment.',
'The actual correction adds study-team authorship and corrects the appendix. It is not a retraction and does not itself specify every changed appendix cell.',
'Publisher content was retrieved November 3, 2026 and numerical reconciliation completed November 4, 2026.'
],'Correction content and its implications are now assessed. The surviving Discussion discrepancy remains explicitly documented, not an unknown correction hold.'),
('G-METFORMIN infection/long COVID chapter; corrected Table S4',[
'C-PREVENT-CO: fewer later provider diagnoses after early acute treatment in this trial.',
'Supports a bounded prevention signal; does not support treatment of existing long COVID, universal prevention, or equivalence of formulations.',
'Observed estimates are distinct from the authors\' implementation advocacy; the editorial interpretation retains endpoint, cohort and applicability limits.'
],'The guide can cite the corrected-table estimates with an explicit note about the residual Discussion inconsistency.'),
('Synthesis of this assessment',[
'COVID-OUT supplies a randomized prevention signal in a selected acute-infection population.',
'Benefit for current recurrent-infection populations, symptom-defined long COVID and established illness is not established by this report.',
'Independent contemporary trials with complete follow-up, clear endpoint definitions and prespecified analyses could strengthen or weaken the prevention conclusion.'
],'Do not infer an individual treatment decision from this study alone.')
], 'The correction is reconciled at the source level. Current Results and corrected Table S4 agree; their estimates can be quoted as reported, with the remaining Discussion discrepancy visible. Selection into long-term follow-up and the changed endpoint history limit interpretation. The current registry safety and discontinuation results were reconciled by allocation arm. All historical protocol versions and participant-level discrepancies have not been independently audited.', assets=SOURCES['P-COVIDOUT-2023']['assets']+SOURCES['COVIDOUT-CORRECTION']['assets'])

write_review('REVIVE-REPLACEMENT','REVIVE: the corrected report of treatment for established long COVID fatigue',[
('Methods; formal retraction/republication notice',[
'Test whether metformin or fluvoxamine improves fatigue in established long COVID.',
'Adaptive trial with prespecified interim rules; the replacement restores a safety-driven dose amendment and the metformin futility stop omitted from the old report.',
'The metformin comparison concerns treatment of fatigue after illness, not prevention during acute infection.'
],'The revised report, not the withdrawn original analysis, is the evidentiary unit.'),
('Methods: Study Design and Participants; Results; Figure 1; Table 1',[
'399 adults in Brazil with new/worsening fatigue attributed to long COVID; 111 metformin, 150 fluvoxamine and 138 placebo.',
'22 outpatient sites, October 2023-February 2025; eligibility described fatigue 90 days to 24 months after infection and FSS at least 3.',
'Metformin comprises 71 participants at 750 mg twice daily and 40 at 500 mg twice daily; all 111 remained in the intention-to-treat analysis.'
],'The two dose cohorts are sequential and not an independently randomized head-to-head dose comparison.'),
('Methods: Interventions and Follow-up',[
'Both metformin cohorts received the same extended-release formulation.',
'750 mg twice daily for the earlier cohort; 500 mg twice daily for later enrollees after the April 2024 amendment; 60-day treatment.',
'Fluvoxamine was a separate randomized arm, not combined metformin treatment.',
'Follow-up through day 90; no participant switched between the two metformin dose cohorts.'
],'The dose amendment must not be described as every treated person tapering to a lower dose.'),
('Methods: Randomization and Masking',[
'Matching placebo, shared within the platform.',
'1:1:1 allocation to active arms or placebo; eligibility could restrict allocation to metformin.',
'Central web randomization with site stratification and variable blocks.',
'Participants, site staff, investigators and outcome assessors were blinded; tablets and packaging were matched.',
'Metformin stopped September 18, 2024; fluvoxamine continued until its later superiority stop in February 2025.'
],'Calendar-time and eligibility comparability of shared controls require attention when reviewing the detailed analysis code.'),
('Methods: Outcomes',[
'Primary: change in fatigue severity from baseline to day 60. Day 90 fatigue, quality of life and recovery were secondary.',
'Fatigue Severity Scale: mean of nine 1-7 items; EQ-5D-5L for quality of life.',
'Baseline, treatment to day 60, and follow-up to day 90.',
'Patient-reported symptom and quality-of-life measures, not proof of viral clearance or reversal of underlying disease.',
'The sample-size rationale targeted a 0.45-point FSS reduction; recovery was FSS below 3.'
],'A design target is not automatically a validated minimal important difference for every long COVID population.'),
('Replacement Tables 2-4',[
'Day-60 FSS treatment effects versus placebo: -0.02 (95% credible interval -0.48 to 0.44) for 750 mg twice daily and -0.04 (-0.63 to 0.54) for 500 mg twice daily.',
'The dose cohorts contain 71 and 40 randomized participants respectively; the shared placebo group contains 138.',
'Effects are FSS-point differences in change versus placebo; negative favors metformin. Day-90 estimates were -0.00 (-0.50 to 0.50) and -0.12 (-0.75 to 0.50).',
'Overall recovery risk ratios were 1.09 (0.83-1.41) at day 60 and 0.96 (0.78-1.17) at day 90; quality-of-life contrasts also crossed no difference.',
'These are Bayesian credible intervals; all metformin dose-specific primary intervals include zero and clinically relevant effects remain possible.'
],'The corrected conclusion is inconclusive. The null-centered estimates do not prove absence of benefit, and dose-cohort estimates are exploratory.'),
('Figure 1 caption; Statistical Analysis',[
'One participant in each metformin cohort was lost after randomization; scheduled attendance was 70/71 and 39/40.',
'Missing data were handled with 20 chained-equation imputations and pooling of posterior draws; placebo/fluvoxamine missed visits were also imputed.',
'Gastrointestinal intolerance caused withdrawals and triggered the dose change; a complete individual adherence distribution is not provided in the main report.',
'All randomized participants reportedly remained in the intention-to-treat analysis; attendance is not the analysis denominator.',
'Intention-to-treat analysis with models adjusted for baseline FSS, site, age and sex.',
'The participant is the unit; repeated FSS items/timepoints and dose analyses are not extra independent trials.'
],'Missing-at-random assumptions and the treatment of concurrent controls need verification against the unavailable companion code.'),
('Safety Monitoring; Table 5',[
'Physical examination, vital signs and structured adverse-event queries at follow-up; CTCAE version 5 grading and blinded review of serious events.',
'Table 5 uses 111 metformin participants (71 higher dose; 40 lower dose) and 138 placebo participants.',
'Any adverse event: 49/111 (44.1%) metformin versus 49/138 (35.5%) placebo; dose cohorts 32/71 (45.1%) and 17/40 (42.5%). No grade 3/4 metformin events are tabulated.',
'The DSMC reported a 9% gastrointestinal-event withdrawal rate prompting dose reduction; it was followed by a futility stop.',
'60 days of treatment and surveillance through day 90.'
],'The dose change is a consequential tolerability finding despite few severe events. Lower-dose tolerability cannot be proven superior by sequential cohorts.'),
('Methods; Tables 1-5; formal notice',[
'Masking and randomized allocation are strengths; early stopping, dose amendment and original reporting errors require careful scrutiny.',
'Between-dose comparisons are confounded by calendar time and different participants; Table 1 shows differences in vaccination and sites.',
'The original report omitted changes that affected the metformin analysis. The replacement describes them; full protocol/code verification remains incomplete.',
'Multiple outcomes and exploratory dose/subgroup analyses are not confirmatory evidence of responders.',
'The small lower-dose cohort and early stop leave wide intervals around metformin effects.',
'The main report excludes diabetes for metformin but Table 1 lists two lower-dose participants with diabetes; stated infection timing also does not neatly match all Table 1 ranges. These are retained as internal questions.'
],'The replacement fixes a major historical error without removing every remaining methodological uncertainty.'),
('Eligibility; Interventions; Discussion',[
'Adults with established long COVID fatigue treated in Brazilian outpatient settings.',
'Extended-release metformin over 60 days; not equivalent evidence for the short immediate-release course in COVID-OUT.',
'Fatigue and quality-of-life treatment, distinct from a new long COVID diagnosis after acute treatment.',
'Other symptoms, longer follow-up, mechanistic effects and generalization to excluded populations remain uncertain.'
],'The guide must explain the prevention-versus-treatment distinction before comparing trial directions.'),
('NCT06128967; notice references 1-2',[
'S-REVIVE-2026 / NCT06128967.',
'Original P-REVIVE-2026 DOI ANNALS-25-03959; notice ANNALS-26-03050; replacement ANNALS-26-02144.',
'One trial with a withdrawn report and a corrected replacement, not an additional independent trial.',
'Checked publisher notice, replacement and current guide inventory on November 3-4, 2026; no exhaustive new systematic search claimed.'
],'Keep the original identifiable for transparency while excluding its superseded efficacy analysis.'),
('Byline; Role of Funding Source; Author/Article/Disclosure Information',[
'Gilmar Reis and the REVIVE Investigators, with Brazilian, Canadian, US and other collaborating institutions.',
'Multicenter Brazilian outpatient trial.',
'Latona Foundation funded the trial.',
'NR: Specific manufacturer/supplier details are not established from the main text inspected.',
'GAP: Individual disclosure forms linked by the article have not been obtained; absence of conflicts is not assumed.'
],'The named funding source is recorded without treating it as a validity score.'),
('Replacement editor note; notice entire body; source download receipts',[
'October 6, 2026 republication, DOI 10.7326/ANNALS-26-02144; not the March original.',
'Complete publisher HTML and formal notice text were saved through normal browser access.',
'GAP: Protocol recovered from the registry and key sections 2.1, 3.3.2 and 12 inspected; journal supplement, analysis code and separate final SAP remain unavailable. The English protocol has inconsistencies: section 2.1 identifies day 60 and a 1-point effect, section 12.5 says day 90, and power calculations use 0.45 points. Do not claim complete prespecification concordance.',
'NCT06128967 current registry and posted English translation inspected. Cover identifies original amendment April 11, 2024, ethics approval April 14, 2024 and English translation April 7, 2026. Registration first posted November 13, 2023, after October 18 enrollment start. Protocol section 3.3.2 confirms dose reduction following 9% mild-event dropout.',
'The formal notice says the dose reduction and futility stop occurred in the trial but were omitted from analysis/reporting; metformin is now inconclusive and fluvoxamine results are reported unaffected.',
'Publisher inspection November 3, 2026; assessment November 4, 2026.'
],'Original quarantine is resolved to permanent exclusion of its superseded analysis. The replacement has a separate source-limited assessment, not inherited quarantine or invented approval.'),
('G-METFORMIN established-long-COVID chapter',[
'The guide\'s established-illness treatment statement must refer to the replacement and its inconclusive metformin result.',
'Contradicts treating the withdrawn result as definitive proof that metformin does not work; also provides no demonstrated metformin benefit.',
'Observed estimates and tolerability findings are separated from the authors\' fluvoxamine conclusion and the editorial metformin interpretation.'
],'No efficacy statement may use the original report merely because it shares the same trial identity.'),
('Assessment synthesis',[
'REVIVE does not establish metformin benefit for long COVID fatigue; its corrected finding is inconclusive.',
'Dose-specific effects, tolerance, durability and responses in distinct long COVID phenotypes remain uncertain.',
'An adequately powered, prospectively specified trial with stable dosing, transparent concurrent controls and complete source materials could change the conclusion.'
],'The original reporting error is resolved by version-specific handling, not by pretending the remaining evidence is definitive.')
], 'The original report is permanently excluded from efficacy synthesis. The verified notice and replacement resolve why it was retracted and what changed. A substantive main-report appraisal is complete, but unavailable final SAP, code, journal supplement and disclosure files prevent labeling the full packet independently verified.',assets=SOURCES['REVIVE-REPLACEMENT']['assets']+SOURCES['REVIVE-NOTICE']['assets'])
