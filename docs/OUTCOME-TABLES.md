# Outcome evidence tables and research sidebar

Adopted October 12, 2026 from the owner's five Examine screenshots and explicit request to fix the drug/condition tables and their underlying aggregation.

## Reader contract

Owner correction, October 29, 2026: remove the article Evidence section’s “Explore and compare recorded outcomes” link and the “Begin typing to filter evidence” quick-search box shown in the supplied screenshot. Apply through the shared article renderer. Preserve the Evidence introduction, grouped outcome table, Filter outcomes disclosure, URL-based filters, research sidebar and standalone `/outcomes` catalog. This supersedes the article-local link and quick-search presentation only.

Condition pages use **Intervention / Outcome / Grade / Effect / Evidence**. Drug pages use **Health condition / Outcome / Grade / Effect / Evidence**. Intervention identifies the tested repurposed drug or exact regimen. Health condition identifies the studied condition or goal. Outcome names the measurable endpoint. A condition/drug appears once as an expandable group; compatible reports for an outcome contribute to one shared summary row. The same summary identity, benefit assessment, effect and count appear in both directions.

The owner adopted an A–F likelihood-of-benefit grade, considering independent trials, consistency and strength of observed effects. This supersedes the three-column table and the four-column condition plan, and supersedes using High/Moderate/Low certainty as the table's Grade. Underlying source-specific certainty assessments remain accessible in the sidebar. RemapRx documents its own editorial rubric; it does not claim access to Examine's proprietary calculation. A label cannot be obtained by relabeling an earlier confidence rating. New assessments are stored separately with their actual source scope, rationale and input fingerprint. Unknown, nonclinical, background-only and held evidence must not receive invented clinical grades. The method and data-validation contract are in `editorial/OUTCOME-BENEFIT-GRADING.md`.

Effect describes the size of the observed change across compatible trials. Use numerical contrasts and uncertainty when an outcome-specific small/moderate/large threshold is not supported. Do not turn statistical significance, likelihood of benefit, confidence, or report counts into an effect size. Do not invent a pooled estimate. Preserve meaningful differences in prevention/treatment, population, formulation/route, comparison, endpoint and follow-up.

Evidence counts independent randomized controlled trials and their relevant participants. Companion reports, follow-ups, repeated outcomes and mechanistic substudies retain separate report identities but never duplicate a trial or its participants. Do not add systematic-review totals to their included trials. Source-verified analysis/comparison denominators must remain distinguishable from overall enrollment. An unknown or irreconcilable denominator remains explicitly unavailable. Other human, nonclinical, background and excluded sources remain inspectable, with no implication that zero RCTs means no other evidence.

Long COVID appears once as a condition group. Prevention during acute infection and treatment of established Long COVID are different outcomes/questions inside that group; acute COVID outcomes are a separate condition group. Different outcomes must not be averaged into a single condition-wide efficacy score.

## Research sidebar

Outcome, Grade and Evidence controls open the right overlay for that exact summary. A group Evidence control opens all summaries in that drug/condition group with overlap-aware counts. Keep the article in place, dim its backdrop, trap focus, lock background scrolling, independently scroll the panel, close with X/Escape/backdrop, and restore focus to the actual opener.

The panel holds the benefit rationale, quantitative findings, populations/comparators/timepoints, original certainty rationale, proposed mechanisms, what the mechanism studies measured, limits, and expandable study summaries. Preserve source-bound tested/proposed/inferred language. Mechanistic plausibility does not increase a clinical trial count or establish benefit. Background and excluded sources are separate from clinical study reports. Keep original source and dedicated review links, source access/correction status and existing full-review authorization. No protected review body is added to a public projection.

Move condition-specific rationale tables into the relevant evidence sidebar, keeping shared original-action/pathway explanation in Mechanism of Action. Preserve legacy rationale and synthesis fragments. Where no mapped outcome exists, retain the source-bound rationale in the article until a supported evidence destination exists; do not lose it or invent a clinical row.

## Implementation and verification

Shared paths: `lib/outcome-summary.ts`, `data/outcome-summaries.json`, `components/shared-theme/evidence-table.tsx`, `components/article.tsx`, `lib/mechanisms.ts` and `lib/citation-plan.ts`. Existing accepted raw synthesis and certainty identities remain unchanged. Filters select complete authored summaries; they never recalculate a grade from an arbitrary subset. Table effect citations follow default rendered group order, and opening the sidebar never renumbers the page.

References consulted: Microbiome Medicine `ConditionsTable.tsx` / `StudyDrawer.tsx`; PepsAnon `evidence-table.tsx` / `research-panel.tsx`; owner-supplied Examine condition, intervention, tooltip and study-panel screenshots. Preserve RemapRx branding. Source repositories are read-only references.

Acceptance covers all drug/condition and existing answer/comparison branches; shared summary identity in both directions; duplicate-report and participant counting; unrelated/preclinical/held evidence; search, expand/collapse and empty results; drawer scope; mechanism/source closure; citation order and old fragment destinations; desktop/mobile geometry and keyboard dismissal; public payload boundaries; production build. Exact results and release receipt are recorded below after execution. Scientific review, commercial approval and comprehensive literature coverage remain separate.

## Acceptance — October 12, 2026

The shared projection maps 62 retained syntheses to 60 authored summaries and 43 independent randomized trial families. Two duplicate-outcome/report pairs are combined; three participant totals are explicitly unavailable. Eight nonclinical, safety-only or correction-held outcomes remain ungraded. No A/B assessment was manufactured. Raw evidence is preserved.

Passing checks: outcome source/fingerprint/denominator validation; evidence tables across 64 profiles and four answer/comparison pages; shared identities in both directions; mechanism source closure and unmapped rationale preservation; navigation and frozen citations across 68 articles; wiki links; all-profile prose checks; governance preservation; TypeScript; scoped React lint; production build and public bundle boundary. Browser checks on the drug and Long COVID condition pages cover one Long COVID group, row/group trial deduplication, expandable studies, proposed mechanisms, source links, header tooltip, search/reset/empty result, expand/collapse, legacy outcome fragments, keyboard focus containment and Escape restoration. At 390px the table scrolls within its 342px container with no page overflow and the drawer fits the viewport; the desktop table uses available right-rail space.

The Sites release starts from live version 38 and preserves the concurrent branding update at `9750e7a59486527f8ec18bf17c79a074421bbaf8` by a normal merge. The bounded runtime update includes the existing accepted metformin evidence expansion needed by the 62-row input and its mechanism records. The independent local-only metformin pathway accordion pilot is preserved in the canonical workspace and excluded from this publication. Its release-check branch verifies the current visible pathway headings instead. Updating the public Methods copy regenerated candidate guide marketing hashes after a reviewed clarification: all 66 guide products remain pending, the membership offer remains disabled, and no edition approval, release state or transaction changed.

This accepts data integration and UI behavior only. No fresh source acquisition, complete literature search, correction clearance, clinical peer review or commercial guide approval is claimed. Publication receipt is recorded separately after deployment.


## Publication receipt

Sites version 40, source `122bfe19acb975a4da3ea0444cc34d22fb4f89f5`, deployment `appgdep_6acd1f7bbd408191958d0c3a667f5b45`, succeeded at 2026-10-12T17:57:39Z. The live custom-domain Metformin and Long COVID pages were verified after publication. The live drug page has one Long COVID group and its drawer shows three independent randomized trials; the condition page uses Intervention and the same outcome summaries. Receipt: `OUTCOME-TABLES-DEPLOYMENT.json`. Live screenshot: `artifacts/outcome-tables/live-study-sidebar.jpg`.
