# Second Look rule changelog

Record requirements when adopted, even if implementation is pending. Keep history append-only; describe supersession explicitly. Each entry needs source/date, scope, requirement, affected contracts, implementation/verification/release status and unresolved work.

## 2026-10-11 — SL-RULE-001: durable collaborator repository

Source: owner request in the Drug Repurposing chat: the Second Look website needs a GitHub repository for research collaborators, including all canonical instructions and One Match rules so rules created on this build are not lost. Owner selected private `paleofoundation/second-look`.

Adopted: preserve the existing app/history, vendor a hash-verified portable rule snapshot and original pilot history, add root agent instructions and a same-PR rule maintenance requirement. Repository visibility is private. This does not authorize website deployment or scientific approval. Implementation: repository documentation and integrity check. Verification: see `docs/REPOSITORY-VALIDATION.md`. Upstream rule snapshot version/hash: `rules/one-match-rule/snapshot-manifest.json`. Global rule edits and ChatGPT uploaded-copy synchronization are not claimed.

## 2026-10-11 — SL-RULE-002: research ingest handoff is mandatory

Source: owner follow-up: “research ingest rules are critical. If another researcher comes, the rules for ingest need to be made available to them so that we do not lose ground.”

Adopted: ingestion instructions are a required onboarding entry point, linked from README and AGENTS. Preserve actual plan/schema/source/identity/coverage/checkpoint records with the build; carry new rules into those records and the next research handoff. Existing accepted work must survive repeat import and collaborator changes. Implementation: `docs/RESEARCH-INGEST.md`, `research/`, versioned editorial inputs and PR checklist. Verification: repository integrity check covers the instructions and archived plan/schema files; scientific completion remains operation-specific. Historical plans are not fresh approvals.

## 2026-10-11 — SL-RULE-003: existing local reader correction retained

Source: owner requirements recorded in `docs/rule-history/reader-rule-correction.md`; that preserved source contains the exact request and its bounded implementation report.

Adopted for Second Look: Benefits prose followed by canonical question accordions; substantive original-use and condition mechanisms; supported safety answers; no internal unfinished-work prose substituted for answers. These locally applicable requirements are in `PROJECT-RULES.md`. Implementation/verification: preserve the source report's bounded claims; this repository handoff does not independently verify all affected reader journeys. Reusable upstream wording remains pending reconciliation; importing the current master must not discard the local correction.

## 2026-10-11 — SL-RULE-004: sidebar icons, article order, study summaries and update history

Source: owner request in Drug Repurposing, accompanied by `Screenshot 2026-10-11 at 12.43.50 PM.png` and `Screenshot 2026-10-11 at 12.43.56 PM.png`, and the live Examine endometriosis sidebar inspected during this change. The explicit request adds small sidebar icons to the site and One Match Rule, puts FAQs after Evidence in sidebar and body, assigns study summaries to Research Feed, and requires Update History using the Microbiome Medicine repository.

Adopted: shared decorative outline icons; retain scientific modules; align the terminal section order as Evidence, Research Feed, FAQs, Update History, References; separate References from the Research child menu; provide canonical inline study summaries without bypassing full-review access; add durable dated change entries using the Microbiome timeline structure. This supersedes the FAQ-before-Evidence drug template, Research → Studies/References menu, missing icon configuration and Updates link to a source-count snapshot. Legacy fragment targets remain compatible.

Affected contracts: `PROJECT-RULES.md`, `ARTICLE-NAVIGATION.md`, shared article composition/citation plan, semantic icon map, page update records, and the refreshed upstream One Match Rule snapshot. Implementation and exact verification results are recorded in `ARTICLE-NAVIGATION.md`. Source synchronization/publication was blocked by automatic approval review because the Sites workflow could export the private repository and publish it; no hosted release is claimed. Scientific review completion is unchanged.
