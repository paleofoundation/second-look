# Outcome benefit assessment

Method: `selected-source-benefit-v1` · adopted October 12, 2026.

The owner requested an A–F assessment of how likely the intervention is to benefit a specific outcome, drawing on trial number, consistency, strength of the observed effect and the limits of the evidence. This is RemapRx's transparent editorial implementation of that requested meaning. It is not Examine's proprietary formula, a formal GRADE assessment, a probability estimate, a prescribing recommendation or a human scientific approval.

The new letter assessment is separate from the retained High/Moderate/Low confidence assessments. Those older records are not converted into letters, deleted or reinterpreted. They remain available with their original rationale and exact source scope in the research panel.

## Scale

| Letter | Meaning | Required interpretation |
| --- | --- | --- |
| A | Benefit well supported | Multiple independent, directly relevant randomized trials show consistent clinically important benefit, with adequate precision and no decisive unresolved integrity limitation. |
| B | Benefit likely | Direct randomized evidence supports benefit, including a substantial well-conducted trial or convergent trials; remaining limits do not overturn the benefit interpretation for the exact outcome. |
| C | Possible benefit | A positive randomized result or limited convergent evidence is promising, but replication, precision, bias, duration or practical importance remains a material concern. |
| D | Benefit uncertain | Mixed findings, uncontrolled observations or indirect comparisons cannot establish whether the intervention itself helps. Positive signals and important contrary results must both be explained. |
| E | Benefit not demonstrated | Direct clinical comparisons have not demonstrated benefit; uncertainty can still permit benefit or harm. This is not proof of equivalence or a label for missing research. |
| F | Benefit unlikely or harm observed | Direct evidence weighs against a meaningful benefit for the specified endpoint or indicates harm. Explain whether this reflects a precise negative result or a harmful signal; preserve uncertainty about its magnitude and generalizability. |

No letter is assigned for computational nominations, purely mechanistic associations, feasibility/safety-only questions, or a material unresolved source correction that prevents a settled benefit judgment. Display the concrete reason. Missing research is never F. Neither sample size, statistical significance, a design name nor an old confidence category automatically supplies a letter. A large trial may be E, a smaller positive trial C, and a harmful result F while its original confidence remains Moderate.

The current records are selected-source AI-assisted assessments. They do not claim an exhaustive search, completed full-text appraisal, Q01–Q15 review completion, independent human review or publication approval. No A or B is forced into a small or incomplete evidence base merely to populate the visual scale.

## Synthesis and effect

Each summary maps stable existing synthesis identities and sources. A drug page groups once by health condition; a condition page groups once by intervention. Separate measurable outcomes appear below the group. Prevention after acute infection and treatment of established Long COVID remain different questions under one Long COVID group. Acute-COVID complications remain an acute-COVID outcome. A paper reporting both phases is not two independent trials.

Combine only compatible endpoints, clinical purposes, interventions and populations, with a written aggregation rationale. Retain endpoint-specific timepoints and estimates in the panel. The itraconazole NSCLC progression rows describe different summaries of progression in the same trial and are displayed together; the two minocycline six-month MS-conversion rows are duplicate source aliases for the same trial and outcome. Original rows and reports remain intact.

Effect expresses the size and direction of observed change independently of the letter. Use a supported compact numerical contrast where possible. Label uncertainty when the interval includes benefit and harm. A study's response percentage without a concurrent control is an observed response, not an improvement attributable to the drug. Do not manufacture pooled estimates across incompatible outcomes or label a numerical change small or large without a defensible clinical threshold. If none is established, report the estimate rather than inventing a magnitude category. Keep a separate interpretation field for benefit, harm, mixed, uncertain or not applicable; a numeric increase is not automatically benefit.

## Evidence counts

Count independent randomized trial families, not publications, endpoints or sources. Keep companion reports/aliases attached to the same trial. The public Evidence cell's participant number is the reconciled reported population for those trials, with the denominator basis retained beside the record. Prefer randomized N when known, or explicitly label an analyzed/eligible or reported-trial denominator. Do not infer randomization from every enrolled N. A clinical comparison within a three-arm trial can use the two relevant arms when their denominators are explicitly present; the whole trial population is retained in study detail.

If a valid comparable number is not present in the accepted records, use null with its reason. Zero RCTs denotes a recorded nonrandomized/nonclinical evidence base; it is not a search-completeness claim. Randomized dose comparisons and trials of two drug-containing regimens count as randomized trials but their inability to isolate drug benefit stays prominent. The group total deduplicates families across outcomes and repeated reports; it does not add the same trial population twice. No meta-analysis is added to its component trial count.

## Provenance and validation

The bounded prospective plan and readiness are in `research/batches/RRX-OUTCOME-SUMMARY-001/`. The authored public records are `data/outcome-summaries.json`; private rationale inputs, source locators, identity decisions and exact input/output hashes are in `editorial/outcome-summary/`. `lib/outcome-summary.ts` provides the shared projection. New relevant sources, meaningful source-status changes or changed findings invalidate these assessments and require reassessment, not a hash refresh. Adding or correcting a source identifier, including a DOI on an existing source, changes the fingerprinted source record in the same way. Re-examine the finding, effect, trial count and letter against the grading scale. Keep the existing letter only when that review shows the result is unchanged. Store the reviewed `assessedInputSha256`, then run `python3 editorial/outcome-summary/build.py`. The compiler refuses to rebuild while that fingerprint is stale and does not invent a new letter.

Run `node scripts/check-outcome-summaries.mjs`. It verifies every input row is mapped exactly once, source membership, grade scope, participant-family agreement and preserved input fingerprints. The integrator separately verifies rendered drug/condition rows, exact research-panel sources, citation order, keyboard/touch interaction and release state. A successful data check does not confer clinical approval.
