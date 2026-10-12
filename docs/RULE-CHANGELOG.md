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

## 2026-10-11 — SL-RULE-004 release resolution

Source: owner reply “Approve source sync and publication” to the request to synchronize the updated private source to the existing Sites project and publish at `second-look-evidence.kmfp.chatgpt.site`.

The earlier publication block is resolved. Exact source commit `29166f85abbb12a2ff53f0cd3b77dcfdc9615b95` was synchronized and published as Sites version 23. Native deployment `appgdep_6acb8b392c648191b4809d48feccb0af` returned `succeeded` on 2026-10-11 at 13:12:49 UTC with the existing site URL. `ARTICLE-NAVIGATION.md` records the version, archive hash, prior verification and limits. Public audience and scientific access/release gates are unchanged. This follow-up records the release outcome; it does not grant scientific approval or claim that uploaded ChatGPT rule copies were refreshed.

## 2026-10-11 — SL-RULE-005: activate the RemapRx apex domain

Source: owner request to finish connecting `remaprx.com` after confirming its GoDaddy A and validation TXT records in public DNS. Scope: verify the existing custom hostname on Sites, confirm Active hostname and issued SSL, report exact additional DNS requirements if any, preserve nameservers, and leave `www` unchanged unless necessary and disclosed.

Adopted in `PROJECT-RULES.md`; the hosting identity, records and verification receipt are retained in `CUSTOM-DOMAIN.md`. This completes the pending apex connection and supersedes its earlier pending/error state. The Sites refresh returned domain, provider and SSL statuses `active` at 13:40:27 UTC. The homepage loaded in the browser, and a separate certificate-validating HTTPS request returned HTTP 200. No additional DNS records, nameserver changes or `www` setup were needed. Existing public audience, application source version and scientific release gates were preserved. Implementation, live activation and domain verification are complete; no remaining domain work is claimed.

## 2026-10-11 — SL-RULE-006: mechanism scope and canonical presentation assessment

Source: owner reports two introductory sentences and eleven Mechanism of Action disclosures, asks whether all belong there, and requests a canonical style that a generator can complete, with a table suggested as a possibility. Page identity was not supplied; local itraconazole record D07 matches both counts (metformin D01 also has eleven disclosures but three introductory sentences).

Requirement recorded in `PROJECT-RULES.md`: establish section-specific scope and a canonical generator presentation; eleven is not a fixed generation quota. This clarification does not yet supersede the accordion renderer with a table. Local content inspection finds nine condition-specific rationale entries and two underlying pathway explanations in D07. Recommendation under discussion: connected visible explanation, shared pathway explanations without duplication, and a condition-rationale table identifying mechanism, experimental basis and limits with citations. Detailed clinical results remain primarily in Benefits/Evidence. No scientific source reappraisal, content rewrite, generator/schema change, upstream synchronization or deployment was performed. Verification: governance integrity check for the documentation changes; final layout selection and implementation remain pending.

## 2026-10-12 — SL-RULE-008: one-page mechanism presentation pilot

Source: owner follow-up, “implement that structure on one page. If it works, we make it the canonical structure.” Scope: itraconazole (`/drugs/itraconazole`, D07), matching the page assessed in SL-RULE-006. Authorizes the proposed visible prose, shared pathway explanations and condition-rationale table on one page; does not adopt a global generator default. It supersedes the pending implementation status for this one page only.

Implemented in the existing shared mechanism renderer and `data/public-mechanisms.json`, with sentence-bound citations, nine condition rows, two visible pathway explanations, all eleven legacy fragment IDs, responsive labeled cards and a page-scoped presentation history entry. Existing records and source IDs are reused; no research acquisition or scientific reappraisal is claimed. Contract, source mapping, checks and release status are recorded in `MECHANISM-PILOT.md`. Owner evaluation, global canonical adoption, and upstream/installed/exported rule synchronization remain pending.

## 2026-10-12 — SL-RULE-009: blue/yellow design system and first topic illustrations

Source: owner’s Drug Repurposing chat request with palette05.png, ten health-topic SVGs and an Examine brain-hero screenshot. Adopt a RemapRx design schema, migrate the site palette first, then illustrate Metformin and Parkinson’s disease in coordinated blues for the left hero region. Prepare browser-friendly images with descriptive metadata and reusable conventions for future RemapRx/PepsAnon artwork.

Scope: shared visual tokens, existing brand assets, responsive topic hero rendering, two original illustrations, canonical image registry and image discovery metadata. Supersedes the previous navy/gold palette-preservation requirement within this scope. Contract: DESIGN-SYSTEM.md; verification and publication: DESIGN-VALIDATION.md. No scientific content, grade interpretation, access, robots/indexing or commercial release change. PepsAnon migration and remaining topic artwork are pending separate scope; upstream rule/installed skill synchronization is not claimed.
