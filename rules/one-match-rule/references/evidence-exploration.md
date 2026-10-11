# Evidence exploration contract

Added with One Match Rule 1.15 after an authorized Examine benchmark. These are original implementation requirements and bounded adaptations, not Examine's code, corpus, grade algorithm or an affiliation. The master controls access, research review, source restrictions and release. Apply this contract to the declared edition; unfinished research stays explicit.

## Plan the inputs before acquisition

Extend the project's production schema and ingestion plan before the next affected file request or ingest. Reuse existing IDs and extracted fields. Do not recollect accepted files merely because the rule version changed.

| Reader function | Required inputs | Responsible step |
|---|---|---|
| Outcome finder | Canonical outcome IDs, labels/aliases, definitions, units/instruments, condition relationships; scoped synthesis IDs; population/model/design/assessment facets | Editorial scope map plus source-located extraction; aliases do not erase clinically different endpoints |
| Explain the finding | Direction, estimate/units/uncertainty/timepoint, comparator; clinical versus surrogate role; meaningful-change source or missingness; interpretation and limits | Worker extracts reported values; synthesis author interprets under the adopted method |
| Compare options | Matched scope dimensions; direct head-to-head study IDs or explicitly separate-trial support; indirect method/assumptions if performed | Integrator evaluates comparability; worker does not infer superiority |
| Evidence snapshot | Independent family/report IDs, participant denominators/overlap, design, integrated/pending state and search/review dates | Generated projection of canonical records, not a manually typed total |
| Interaction information | Resolved pair and context, confidence/evidence basis, potential severity, source locators, checked scope/date, explicit missing states | Evidence extraction plus domain-appropriate safety review |
| What changed | Old/new synthesis versions, affected claims/outcomes, source delta, conclusion/uncertainty change, actual review/release state | Integrator records a substantive accepted revision, not a file-import timestamp |

Every required field has source provenance or a responsible authoring/verification step and a missing-data state. Case reports and laboratory evidence retain their design limitations. Drug-specific safety searches must use appropriate authorized drug sources; a dataset omitting drug–drug pairs is not comprehensive. The initial one-sentence build must plan these inputs; they must not emerge as an avoidable second fetch after the UI is built.

## Shared reader behavior

Offer entity, condition and outcome starting paths into the same synthesis records. A stable filtered outcome view is acceptable when a standalone outcome article would be thin. Explain the selected outcome and retain its population/time scope. Selecting a condition must not combine every loosely related biomarker under an overall benefit claim.

Use semantic shared evidence tables and the existing PepsAnon-derived overlay. Finder controls filter records using actual supported facets; disable or omit inapplicable controls clearly. Show selected filters, result count, reset and useful empty states. Preserve public non-sensitive filter state in a durable URL or equivalent shareable route, with back/forward and reload. Support keyboard, narrow screens and labeled sort direction. Alphabetical or clearly defined relevance/date sorting is sufficient; no automatic efficacy leaderboard is required. Never drop unknown metadata silently or treat an unappraised record as Low.

Filtering source studies within a panel must not silently replace a published synthesis or recalculate its grade. Explain whether a count refers to displayed papers, independent studies or the full assessed scope. A new subgroup synthesis requires its own evidence and method. A paired comparison may show that the options cannot be compared directly; it need not manufacture a winner.

Keep the site's own certainty, magnitude and clinical interpretation distinct. Explain labels through accessible text/help linked to the actual method, including pending and unknown states. Do not copy Examine's letter grades, population bands, paid restrictions, daily production quotas, AI assistant or treatment protocols as universal defaults. Keep the owner's current free-authenticated full-review policy and public principal findings.

## Acceptance cases

These are synthetic adversarial scenarios to execute against the destination implementation and data contracts, not clinical findings or proof that a site was tested.

| Case | Expected result |
|---|---|
| Search an outcome alias, filter human studies/population, reload and use Back | Same canonical outcome/scope and selected filter state; correct linked records/counts and usable clear/empty states |
| A record lacks population metadata | Explicit unknown/unclassified treatment; no silently fabricated match or omission |
| A trial increases a marker whose desirability depends on population | Numeric direction and clinical interpretation remain separate; no automatic green benefit arrow |
| Only a surrogate or secondary symptom improves | The page cannot claim overall condition benefit without the required decision-relevant evidence/method |
| Drug A and B have different endpoints, populations or follow-up in separate trials | Not directly comparable; no superiority from bigger percentages, significance or grades |
| Two reports share a cohort and a meta-analysis includes it | No double-counted independent study or participant total; unknown overlap blocks a confident aggregate |
| An interaction has theoretical support and unknown clinical severity | Those states remain separate; not safe/cleared and not automatically severe |
| Pair is unmatched, unassessed or excluded by a provider's coverage | Explicit unchecked state, never a negative interaction result |
| A new paper is imported but synthesis has not been reviewed | Pending integration; prior valid review date retained, no false refreshed conclusion |
| New accepted evidence changes a conclusion | Reader-visible dated/versioned change note, affected claims and source reason; truthful reviewer status |
| Ingested-page renderer bypasses the normal article component | Route-level contract check fails despite the article component's separate tests passing |
| A correction makes earlier prose unsafe | Withhold/correct it and retain honest gaps; do not restore unsupported claims to pass visual tests |

Report rule conformance, scientific review and deployment independently. Screenshots alone do not test filtering or authorization; schema shape alone does not establish meaningful synthesis.
