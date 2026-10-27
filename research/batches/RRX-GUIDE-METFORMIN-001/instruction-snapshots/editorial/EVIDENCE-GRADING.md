# Outcome evidence grading

Second Look uses the three-level selected-source editorial method described by
[PepsAnon](https://pepsanon.com/methodology), adapted to drug × outcome × population
× comparison × timepoint. This is an AI-assisted editorial judgment, not formal
GRADE or independent clinical review. Source-review completion, publication
approval, magnitude and evidence strength remain separate states.

## Assessment step in generation

After extracting or updating a synthesis row, inspect its actual source findings,
methods, denominators, intervals, outcome hierarchy, limitations and source
access/correction state. Complete one record in `evidence-assessments.json` for
that exact outcome. Do not map a design name, p-value or sample size straight to
a grade. Do not copy grades from another outcome or reference website.

- **High:** direct, well-supported human evidence gives strong confidence in the
  specific finding. Meaningful precision and methodological support must be
  recorded; the label is not a recommendation or proof of no possible bias.
- **Moderate:** direct evidence is informative, but documented limitations leave
  material uncertainty about the specific result or its applicability.
- **Low:** sparse, indirect, uncontrolled, imprecise or otherwise substantially
  limited evidence gives weak support for a clinical inference. State exactly
  why. Computational-only support remains explicitly nonclinical.

Assess Study methods, Directness, Precision, Consistency and Source integrity
separately, with source IDs on every judgment and a locator for each source.
Write a concise outcome-specific rationale explaining the final grade. Describe
unknown methods as unknown; inaccessible information is not evidence of low bias.
A precise negative or harmful finding can receive High. Nonsignificance is not
equivalence. Multiple publications of one trial are not replication. Abstract
access may permit a limited editorial assessment without completing the source's
full review. An unresolved correction requires Low with the affected conclusion
still on hold; quarantined sources cannot support a grade.

Store the actual date and exact input fingerprint using
`assessmentFingerprint` in `scripts/evidence-assessments.mjs`, only after examining
the corresponding inputs. Never refresh a stale hash without reassessment.
Additional retrieval provenance can remain private in the editorial record.

Run `node scripts/evidence-assessments.mjs --write` to validate and compile the
public assessment projection, then `node scripts/check-evidence-grading.mjs`.
The production build runs `--check`: missing, duplicate, uncited, incomplete or
stale judgments stop publication. New rows cannot silently inherit Low or remain
all-pending in a purportedly completed generation. Genuine absence of eligible
evidence stays an empty coverage state, with no manufactured outcome or grade.

The raw extraction's formal-appraisal status remains unchanged. The shared
content adapter joins the validated editorial projection by canonical outcome
ID, so drug, condition, answer, comparison and filter views use the same grade.
The grade, outcome and evidence-count buttons open that row's source-cited
“Why this grade?” explanation, method, date, scope and findings.

## Verification

Check all outcomes and representative rendered routes. Test changed source and
scope rejection, missing rationale/domains/citations, quarantines, correction
holds, nonclinical boundaries and repeat generation. In a browser, open all
three trigger types, inspect matching rationale and citations, close with
Escape and restore focus. Verify mobile scrolling and preserve the prose-first,
three-column-table-last Evidence composition.
