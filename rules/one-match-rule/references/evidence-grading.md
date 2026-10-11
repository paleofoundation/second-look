# Selected-source editorial outcome grading

Method version: `selected-source-editorial-v1` · adopted 11 October 2026.

This contract implements the owner’s explicit request for PepsAnon-style outcome
grades and a source-backed grading rationale in Second Look’s right research
sidebar. Other sites can adopt this declared editorial profile; do not silently
replace an existing domain-specific or formal certainty method. The implementation
contract is mirrored by Second Look’s `editorial/EVIDENCE-GRADING.md`.

## Meaning and scope

Assess confidence in the exact selected-source finding for intervention × use ×
population × formulation/route where relevant × comparison × outcome × timepoint.
This is a bounded editorial judgment, AI-assisted when applicable, not formal
GRADE, an exhaustive review, a completed Q01–Q15 paper review, independent clinical
review or publication approval. Preserve those distinct states and the full
underlying categories of any separately completed formal method. A grade measures
evidence strength, not effect size, benefit direction, safety or recommendation.

- **High:** direct, well-supported human evidence gives strong confidence in the
  specific finding. Record adequate methods and meaningful precision; do not
  infer low bias from unavailable information.
- **Moderate:** direct evidence is informative, but documented limitations leave
  material uncertainty about the specific result or its applicability.
- **Low:** sparse, indirect, uncontrolled, imprecise or otherwise substantially
  limited evidence gives weak support for the clinical inference. State the
  actual reasons; unknown status alone is never a grading rule.

A precise null or harmful result can receive High. Statistical nonsignificance
is not equivalence; a large estimate is not strong evidence. Do not require a
particular grade distribution or copy values from PepsAnon. Multiple papers from
one trial are not replication. Separate outcome judgments even when they use the
same study, and do not pool incompatible scopes through filters.

## Assessment required during generation

After extracting or updating a synthesis row, inspect its actual source findings,
methods, denominators, uncertainty, outcome hierarchy, limitations and source
access/correction state. Complete one assessment for that exact canonical row.
Do not map a design name, P value or sample size straight to a label. Identify
what was not reported, not extracted or inaccessible separately from what was
actually assessed. Retain source versions and retrieval/check provenance.

Each record requires:

1. Canonical outcome/row ID and the declared method version.
2. Actual grade and concise outcome-specific rationale explaining why it follows
   from the cited evidence and the decisive limits.
3. Exactly five domain judgments in order: **Study methods, Directness, Precision,
   Consistency, Source integrity**. Each has meaningful explanatory text and
   source IDs matching the selected eligible sources.
4. Every selected source accounted for, with at least one usable locator in that
   source; do not invent pagination or cite an unrelated report.
5. Actual assessment date, exact scope, source/row input fingerprint, and truthful
   authoring/review status. Keep additional retrieval provenance private when it
   is not useful reader content.
6. Explicit integrity state: intact/access assessed, limited access, unresolved
   correction, or nonhuman-only evidence as appropriate to the data contract.

Abstracts can support a limited editorial judgment with incomplete methods and
precision clearly considered; they do not complete full-text source appraisal or
Q01–Q15 coverage. A public URL does not prove full-text access. A source’s
not-yet-completed formal review must stay pending even when its selected outcome
receives this narrower editorial judgment.

An unresolved correction requires Low **and** preservation of the affected
conclusion’s hold, with the correction explained. It does not make the original
claim safe to reuse as settled evidence. Quarantined, retracted or excluded
reports cannot support an assessment; reconcile the eligible row and coverage
before grading it. If no eligible evidence remains, show an honest empty coverage
state without manufacturing an outcome, study count or grade.

Computational-only or other nonhuman evidence can receive a completed Low
judgment specifically about **clinical inference** only when its limitations are
assessed and the nonhuman state remains explicit. Do not represent that label as
human efficacy evidence or silently convert a preclinical/unknown state into Low.
A source-specific appraisal of the experimental result is a separate question.

## Compilation, display and invalidation

Store editorial judgments separately from immutable scientific extraction and
formal source-review status. Bind each to the actual input rows, selected sources
and reader projections through a stable fingerprint. New findings, scopes,
source versions, correction states or consequential projected text changes
invalidate affected judgments. Never refresh a stale hash without reassessing
the corresponding inputs. A build date is not an assessment date.

Validate and compile one reader-safe assessment projection by canonical row ID.
Tables, outcome filters, drug/condition guides, scoped answers, comparisons and
panels consume the same record. Show the grade in its existing compact cell;
make it an accessible control opening the row’s right panel alongside outcome
and evidence-count controls. The panel exposes **Why this grade?**, the cited
rationale and five domains, method, assessment date, exact scope and source
locators, together with findings, magnitude, uncertainty and important limits.
Keep substantive source corrections and nonhuman boundaries visible. Preserve
page-local citation numbering and real-source destinations.

In the current Second Look adapter, `scripts/evidence-assessments.mjs --write`
validates and compiles the public projection after editorial assessment, while
`--check` verifies the stored projection without changing it. Its
`assessmentFingerprint` binds scientific and reader inputs, and
`scripts/check-evidence-grading.mjs` exercises acceptance. Other hosts implement
equivalent behavior rather than pretending these exact paths exist.

Production generation must reject missing or duplicate assessments, incomplete
rationales/domains/date/scope, unknown or mismatched citations, absent locators,
quarantined support, stale input fingerprints and stale public projections.
New outcomes cannot silently inherit a label or stay all-pending in a generation
claimed complete. A failure prompts actual assessment or explicit unfinished
scope; it does not permit fabricated grades. Build checks supplement, rather than
replace, substantive source review.

## Acceptance and release boundaries

Check every outcome, selected source and locator against the canonical records.
Exercise changed source/scope rejection, missing rationale/domain/citation,
quarantine, correction-hold and computational-only fixtures; confirm unchanged
repeat generation is stable. Inspect representative rendered routes and every
changed renderer branch. In a browser, use the grade, outcome and evidence-count
openers, confirm matching cited rationale and source identity, dismiss with Escape,
restore focus to the actual opener, and check narrow-screen table/panel scrolling.
Preserve Second Look’s prose-first, three-column-table-last Evidence composition.

Report technical tests, AI-assisted editorial assessment, source-review
completion, independent review and deployment separately. This contract does not
waive a project’s release policy, qualify an agent as a clinician, approve
protected review access, or authorize a new scientific publication claim.
