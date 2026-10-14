# Second Look rule changelog

Record requirements when adopted, even if implementation is pending. Keep history append-only; describe supersession explicitly. Each entry needs source/date, scope, requirement, affected contracts, implementation/verification/release status and unresolved work.

## 2026-10-12 — SL-RULE-PHYSICIAN-PACKET: paid subscriber discussion tools

Source: owner's Drug Repurposing chat request for physician packets using “firm, but effective approaches” to discussing drug repurposing, specifying a logged-in paid-subscriber portal and print/email delivery, followed by a request for ten additional value ideas at $59/month membership and $39 per guide.

Adopted scope: preserve the subscriber physician-packet requirement in `docs/PROJECT-RULES.md`; use the stated prices as planning assumptions. The lung-cancer surgery example supplies product context, not a treatment recommendation. Additional features and package details remain recommendations awaiting selection. No existing research-review access rule is superseded, and no live price or billing change is made.

Status: requirement documentation only. Governance verification applies to the documentation; feature implementation, scientific review, print/email and entitlement verification, and release remain pending. This discussion does not send messages, ingest clinical studies or authorize individual treatment protocols. Upstream rule synchronization is not claimed.

## 2026-10-12 — SL-RULE-011: condition-first intervention roundups

Source: owner's Drug Repurposing correction: “This is for the condition, meaning we are investigating ALL of the potential drug repurposing interventions” and “the evidence table shows. A roundup of all of the drug repurposing interventions.” The owner requested an intelligent plan and necessary ingest-plan changes.

Adopted scope: condition parents investigate repurposed drugs across the condition, beyond the initial drug portfolio, and clearly show which scoped outcomes benefit and how certain the evidence is. Keep contrary/null/mixed/harmful findings and preclinical/no-result candidates distinguishable. Reuse exact-scope synthesis across drug and condition views. Candidate and Related links do not substitute for discovery, investigation or evidence. This repairs failure to enforce the condition-wide discovery already required by the pinned rule and historical briefs.

Planned implementation: condition-specific Overview / Interventions / Safety composition followed by the existing reader tail; drug rationales and comparisons remain attached to their relevant interventions; a compact Intervention / Outcome and finding / Evidence certainty / Evidence table. Preserve legacy anchors, cited scientific content, panel behavior and shared shell. This supersedes forced condition Options/Mechanism of Action/Comparisons modules and the universal three-column prescription for condition tables only. Exact design decisions are documented as the implementation plan, not as additional verbatim owner instructions.

Contracts changed: `docs/CONDITION-PAGES.md`, `docs/PROJECT-RULES.md`, `docs/RESEARCH-INGEST.md`, `docs/ARTICLE-NAVIGATION.md`, research entry/handoff instructions and prospective `research/batches/RRX-CONDITION-001/` plan/schema. This change does not edit existing RRX-INGEST-001 or RRX-GAP-001 plans, schemas or readiness/history receipts. A concurrent operation changed live RRX-INGEST-001 dependencies during planning, recorded for fresh reconciliation. New operational readiness must be checked before dependent condition acquisition/extraction/import; the planning addendum does not expand a closed packet retroactively.

Status: local diagnosis, reference inspection and planning changes completed; plan/schema validation is recorded with the new packet. New research, condition renderer/data migration, browser acceptance of that implementation and deployment remain pending. No scientific reassessment or release is claimed. Upstream, installed and exported One Match Rule synchronization remains pending through the existing integrator; the pinned snapshot and frozen baseline remain unchanged.

## 2026-10-12 — SL-RULE-007: implement reconciled research ingestion and fan-out

Source: owner's explicit “PLEASE IMPLEMENT THIS PLAN” request in the RemapRx research chat, adopting hybrid Codex/Grok, repair-before-expansion and MOA-01 within current targets. The complete adopted scope is in `research/batches/RRX-INGEST-001/PLAN.md`.

Adopted: reconcile current app and external private acquisition/scientific stores without summing overlapping history; retain the 30+30 portfolio, all 36 questions, current additions, eight-drug mechanism scope and mandatory D07 oncology. Preserve historical closed-packet restrictions. Use prospective hashed plans/schemas, logical source roots, immutable receipts, centralized identity ownership, exact outcome scope, isolated worker outputs, independent checks and a store-wide guarded importer. Reuse later verified tooling rather than overwriting current data with pilot generators. Require 24-report calibration, separate completion dimensions and honest release gates.

Scope: repository research infrastructure, private checkpoint reconciliation and bounded source-backed content candidates. Implementation/verification checkpoints and remaining scientific work are recorded in the batch handoff; this adoption entry does not claim those operations ran. No deployment or scientific release is implied. Reusable upstream synchronization remains pending; the pinned rule and historical receipts are preserved.

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


## 2026-10-12 — SL-RULE-008 publication receipt

The one-page itraconazole mechanism pilot was published as Sites version 24 from isolated source commit `8d7424bd9dca50a68c224144749aaa04392e4eb1`. Native deployment `appgdep_6accc2e541c081918f673ae6b95426f4` succeeded at 11:22:34 UTC. The live page verified the two visible pathways and nine condition rows, with no mechanism accordions. Exact source/archive identity and verification are in `MECHANISM-PILOT.md`. This release completes the requested pilot; it does not adopt the structure globally or grant scientific approval.

## 2026-10-12 — SL-RULE-009: blue/yellow design system and first topic illustrations

Source: owner’s Drug Repurposing chat request with palette05.png, ten health-topic SVGs and an Examine brain-hero screenshot. Adopt a RemapRx design schema, migrate the site palette first, then illustrate Metformin and Parkinson’s disease in coordinated blues for the left hero region. Prepare browser-friendly images with descriptive metadata and reusable conventions for future RemapRx/PepsAnon artwork.

Scope: shared visual tokens, existing brand assets, responsive topic hero rendering, two original illustrations, canonical image registry and image discovery metadata. Supersedes the previous navy/gold palette-preservation requirement within this scope. Contract: DESIGN-SYSTEM.md; verification and publication: DESIGN-VALIDATION.md. No scientific content, grade interpretation, access, robots/indexing or commercial release change. PepsAnon migration and remaining topic artwork are pending separate scope; upstream rule/installed skill synchronization is not claimed.

### SL-RULE-009 publication receipt

Theme and two hero illustrations published as Sites version 25 from source `cee0a45a7ceb49e44fd23afbcbbfd0590cdff4f7`, deployment `appgdep_6accc97796248191834ac96f48266aac`, succeeded 12 October 2026 at 11:50:39 UTC. Local checks and exact archive identity are recorded in DESIGN-VALIDATION.md. Existing indexing and scientific/commercial release gates remain unchanged.

## 2026-10-12 — SL-RULE-010: American English page language

Source: owner's explicit Drug Repurposing instruction: “Drug Repurposing pages must be written in American English with American English Spelling.”

Adopted: American English wording and spelling throughout authored reader-facing pages and future content generation/import, with `en-US` document language and prose date formatting. Preserve exact source titles, quotations, proper names, raw source wording and stable identifiers; use American English for surrounding prose and displayed status labels. This supersedes inherited British English wording and the Update History `en-GB` date locale. Contract: `PROJECT-RULES.md`, Language and spelling.

Implementation: correct identified spelling variants in current authored page copy, summaries, table labels, mechanism prose, guide/account messages and matching editorial copy; retain original published titles and compatibility aliases. Set the shared HTML language and Update History locale to `en-US`, update prose date labels and the existing date expectation. The CSBD population label is normalized in the shared reader adapter, preserving fingerprinted source records and their existing evidence assessments. Verification and publication results are recorded below after checks. No scientific reassessment or raw-source rewrite is implied. This is a local project requirement; upstream/installed/exported One Match Rule synchronization is not claimed.

Verification before packaging: governance integrity, canonical content, reader identity/source closure, unchanged evidence-assessment fingerprints, all 64 profile section renders, 68-article navigation/history rendering, TypeScript and whitespace checks passed in the isolated publication checkout. Guide marketing hashes were regenerated for the spelling-only presentation change; approval and release fields were preserved. Shared React copy/status display changes were reviewed for hooks, accessibility, typing and behavior. Production build, public payload checks and deployment are pending below; no browser comparison was needed for the copy-only change.

### SL-RULE-010 publication receipt

Published as Sites version 26 from source `f0d929b67c8c74b23601c59565080729fa6d1f06`; deployment `appgdep_6acccb256f5081919d372b6884a09bff` succeeded on October 12, 2026 at 11:57:50 UTC. Archive SHA-256: `5972ea8ce0f945e5a30722c02119976380e35f2a12c20f01d941ec1d96dfa9d9`. Production build and built public-payload boundary checks passed (30 payloads). Independent diff review confirmed exact source records, titles, stable identifiers, evidence values, grades and assessment fingerprints were preserved. Existing public audience and scientific/access/commercial release gates are unchanged. The American English requirement and identified current-copy corrections are implemented and published; ongoing content must follow the language contract.

## 2026-10-12 — SL-RULE-012: internal links without underlines

Source: owner's request with the Metformin introduction screenshot: “Remove the underline style from this website. internally-linked pages should show up without underline.” Adopted in `docs/DESIGN-SYSTEM.md`: no underlines for internal page and fragment/citation links in normal or interaction states, preserving blue links and keyboard focus. Supersedes inherited wiki-link and hover underline styles. Consulted Microbiome Medicine theme styles and PepsAnon prose/theme styles; current owner instruction takes precedence.

Implementation: shared global internal-destination CSS override; no content or target changes. Verification and publication pending. Upstream/reference projects unchanged.


## 2026-10-12 — SL-RULE-HERO-ROLLOUT: complete the blue topic illustration set

Source: owner request, “Let's create matching hero images for the remaining drug and condition pages on remaprx.com, using the same blue style and metadata setup.”

Adopted scope: extend the existing Metformin/Parkinson illustration system to all current drug and condition routes, including canonical discovery pages. Preserve original blue art direction, left hero placement, transparent responsive WebP assets, individual social previews and accurate descriptive metadata. This supersedes the first pass's pending remaining-topic artwork scope; PepsAnon migration remains separate. Contract: `DESIGN-SYSTEM.md`; exact prompts/master provenance: `assets/hero-art/*-generation.json`; verification and publication: `HERO-ROLLOUT-VALIDATION.md`.

Implementation underway in a checkout synchronized with live Sites version 26, source `f0d929b67c8c74b23601c59565080729fa6d1f06`. The merged route inventory has 64 topic pages (32 drugs and 32 conditions), requiring 62 new originals. Scientific prose, evidence grades, access, indexing and commercial release are unchanged. Final asset coverage, validation and deployment must be recorded before marking this rollout complete. No upstream/installed/exported rule synchronization is claimed.

### SL-RULE-012 verification and publication receipt

Governance, canonical wiki-link/SSR checks, whitespace checks, production build and built public-payload boundary validation passed in the isolated live-source checkout. Published as Sites version 27 from `01577a3c655c4fbc637b27d6cfce860743cd187b`; deployment `appgdep_6accd1e91df48191bf3dac97a2cfb029` succeeded October 12, 2026 at 12:26:42 UTC. Archive SHA-256: `5e5eaba3fe5682c44a1d00c06a8405c11e862dd9523ded381e0872d543570dd9`. No browser visual comparison was performed. Existing audience and release gates preserved; unrelated workspace changes excluded.

## 2026-10-12 — SL-RULE-GRADE-COLORS: brand evidence-grade palette

Source: owner's evidence-table screenshot and explicit request that evidence grades use the website's colors. Adopted in `docs/DESIGN-SYSTEM.md`: replace inherited teal badges with the RemapRx blue scale and neutral ungraded treatment, preserving labels and evidence semantics. Supersedes the prior grade-color preservation exception for badge styling only. Shared `reading-modules.css` is the implementation; no evidence records or grading logic are changed. Verification/publication receipt follows locally after deployment; reference sites and upstream rules remain unchanged.


## 2026-10-12 — SL-RULE-ATLAS-IDENTITY: owner-sketched enclosing Rx arrow

Source: owner's selection of initial concept 02's chunkiness/weight, request to pause for a drawing, and subsequent IMG_6541.heic / IMG_6542.heic sketch attachments in the RemapRx atlas implementation chat. Scope: logo shape refinement only. Adopt the whole-Rx enclosing arrow as the visual reference; preserve both the x-connected wrap and separate open-ring interpretations for comparison. This supersedes treating the arrow as only an underswoop beneath Rx.

Affected contract: DESIGN-SYSTEM.md. Related work: two original editable SVG concept families and rendered comparison/small-size previews in assets/brand-concepts/sketch-round-2. Status: drafts created and visually inspected; SVG parsing passed. Owner selection, production identity/favicons, integration and publication remain pending. No clinical, research, access or scientific-release changes are made in this refinement. The main application repository and isolated atlas checkout both retain this requirement; upstream rule synchronization is not claimed.

### SL-RULE-GRADE-COLORS publication receipt

Published as Sites version 28 from `6660a08e1ede47e4cf38c6eb9593c5a5f374d79f`; deployment `appgdep_6accd3b0d6f481919f92a95ea038a615` succeeded October 12, 2026 at 12:34:16 UTC. Governance, evidence-section SSR, evidence-grading integrity, whitespace, production build and built public-boundary checks passed. All five foreground/background combinations exceed 4.5:1 text contrast (minimum 5.65:1). No browser visual comparison performed. Scientific values, audience and release gates are unchanged.

## 2026-10-12 — SL-RULE-GRADE-BARS: evidence strength icons

Source: owner's request to add the screenshot's small strength bars beside grades using the blue colors. Adopted in `docs/DESIGN-SYSTEM.md`; implemented in the shared evidence table using the existing `.grade-bars` styling and PepsAnon `components/peptide/evidence.tsx` reference. Three ascending bars encode High/Moderate/Low/Very low as 3/2/1/0 filled; ungraded evidence has no strength icon. Visible labels, accessible button names, blue palette and grade-panel actions are preserved. No scientific record or grading logic changes. Verification/release receipt follows locally.

### SL-RULE-GRADE-BARS publication receipt

Sites version 29, source `f4804463e383f0bcf44b9b51fa691056278208dc`, deployment `appgdep_6accd465f1a4819188f78037ad62aeb4` succeeded October 12, 2026 at 12:37:17 UTC. Governance, evidence-section SSR (64 profiles), TypeScript, whitespace, production build and built public-boundary checks passed. No browser visual comparison performed. Scientific grades and existing audience remain unchanged.

## 2026-10-12 — SL-RULE-HERO-ROLLOUT publication receipt

Completed 62 new original blue hero illustrations across all 64 current topic pages (32 drugs, 32 conditions), preserving the two approved originals. Published Sites version 30, source `4606f88a6b5fc1843b616a4db5602f877c576b38`, version `appgprj_6ac734459a508191a425263c7645a0be~appgver_90e4a05781b48191bb514f59b3138b10`, deployment `appgdep_6accd6249c08819187ae009fa7b34e03`, at https://remaprx.com. The rollout was reconciled with newer internal-link and evidence-grade presentation updates before release. Production build, reader-boundary, TypeScript, governance and article-navigation checks passed. Full asset validation passed 256 hashes; live verification passed 64 topic pages and 128 image downloads, including canonical/Open Graph/Twitter/ImageObject metadata. Existing scientific and indexing gates remain in force. Bounded source/assets were synchronized to the canonical repository without overwriting concurrent identity, condition or research edits. Details: `docs/HERO-ROLLOUT-VALIDATION.md`.

## 2026-10-12 — SL-RULE-PAGE-SNAPSHOT: author ORCID and page-scoped research counts

Source: owner's Microbiome Medicine screenshot and explicit request for an ORCID-logo-only link beside the name, plus study and investigated-drug counts on conditions and study and investigated-condition counts on drugs. Adopted in `docs/DESIGN-SYSTEM.md`; supersedes the visible full ORCID string and generic Research sources hero block. The implementation reuses verified author identity and public canonical citation/study/relationship records, groups recorded study identities, and excludes unsupported candidate-only counts. Study-count identity coverage follows available canonical metadata; no independent-trial audit or scientific reassessment is implied.

Implemented in the shared author/article components, `components/page-snapshot.tsx` and `lib/page-snapshot.ts`. `scripts/check-page-snapshot.mjs` covers duplicate reports, multi-family syntheses, background/uncited exclusions, disputed references, unsupported candidates, zero coverage and both directions on all 64 profiles. TypeScript and all-profile SSR checks pass. Browser and publication receipts will be recorded after verification. Upstream/reference repositories and scientific release gates are unchanged.

Verification before publication: Page Snapshot tests pass for all 64 profiles, including study identity deduplication, multi-study separation, cited-only counts, zero coverage and source-supported investigation counts. All-profile section SSR, 68-article navigation/citation/history checks, TypeScript, governance and whitespace checks pass. Browser preview returns HTTP 200; Metformin and Long COVID render the correct metric labels, the official ORCID icon is beside the name and points to the existing verified URL, biography opening/closing works, study-count links target Research Feed, and the labeled information popover opens with the included entities. Visual inspection passed at the browser's 985px width; requested 390px viewport was ignored by the browser provider, so narrow-mobile visual acceptance is unverified. React review confirms stable hook order, separate sibling button/link controls, decorative icons, accessible link/button labels and no new data requests.

### SL-RULE-PAGE-SNAPSHOT publication receipt

Published as Sites version 31 from `066b45cf47f11b08e05bc1f1ef6688748b722eac`, after merging illustration release 30 (`4606f88a6b5fc1843b616a4db5602f877c576b38`). Deployment `appgdep_6accd895acc8819180a03959170119a9` succeeded October 12, 2026 at 12:55:11 UTC. Archive SHA-256: `5b83584dd8ba381a47a9daa3f93606825f4ada33a3a3aeac8d3421b1cdddf4a0`. Merged snapshot/governance/TypeScript checks, production build and built public-boundary validation passed. Live Metformin shows Page Snapshot with 19 studies referenced and 10 conditions investigated, and the author icon points to `https://orcid.org/0000-0002-2348-7259`. Local Long COVID shows 5 studies and 2 drugs; itraconazole source checks show 13 studies and 9 conditions. Counts follow recorded identity links, with no claim that all unmapped companion reports have been reconciled. Mobile viewport verification remains limited as recorded above. Existing audience, newer artwork and scientific/access/commercial release gates are preserved.


## 2026-10-12 — SL-RULE-ATLAS-IDENTITY: simplified Rx target preview

Source: owner's Rx/target screenshot and explicit request to make the simplified version, showing the blue logo on white and the blue-on-yellow favicon before applying them to the site. Scope: one refined identity preview. This supersedes the earlier two-wrap comparison as the active design direction without declaring final production approval. Contract: `DESIGN-SYSTEM.md`, Simplified Rx target preview.

Implemented editable outlined SVG drafts, separately weighted favicon geometry, PNG inspection sizes and a comparison sheet in `assets/brand-concepts/target-round-3/`. Preserved the heavy Rx, outer arc and flat directional arrow; removed internal target detail. The adopted blue/yellow palette is retained. Rendered sheet and actual 16/32-pixel samples were inspected on light and dark surroundings. SVG parsing, asset dimensions and governance verification are recorded with this local preview. No application component, public asset, scientific record or deployment is changed. Owner assessment, final identity production, site integration and publication remain pending.

## 2026-10-12 — SL-RULE-GLOSSARY-HERO: Hedgehog pathway first illustration

Source: owner's explicit request, “Glossary pages need images. Hedgehog Pathway should be your first attempt.” Adopt the blue illustration/metadata system for individually assigned glossary pages, with Hedgehog pathway as the first pilot. This supersedes the drug/condition-only image catalog scope, while retaining all 64 existing assignments and leaving unassigned glossary entries on their existing layout. Contract: `DESIGN-SYSTEM.md`; provenance: `assets/hero-art/glossary-generation.json`; verification/release: `GLOSSARY-HERO-PILOT.md`.

Implementation starts from published Sites version 31 (`066b45cf47f11b08e05bc1f1ef6688748b722eac`), preserving the recent author/Page Snapshot update. Add one conceptual signaling illustration, glossary catalog support and shared image structured data in the glossary branch. Existing definition, citations, research and access/indexing gates are unchanged. This is the first visual attempt; other glossary illustrations remain unassigned. No upstream rule synchronization is claimed.


## 2026-10-12 — SL-RULE-ATLAS-IDENTITY: restore mapping detail and tighten Rx

Source: owner's rejection of the over-simplified mark as losing the mapping visual, explicit acceptance of small-size detail loss, and request to bring Rx closer together and restore “x marks the spot.” Scope: logo/favicon refinement only. This supersedes removing internal target detail for favicon simplicity. Contract: `DESIGN-SYSTEM.md`, Mapping meaning restored.

Implemented a closer Rx arrangement centered on restored concentric target rings, crosshairs, registration marks and radial connectors in `assets/brand-concepts/mapping-round-4/`. The blue-on-white symbol and blue-on-yellow favicon retain the heavy letters and flat arrow. Favicon strokes are strengthened while all mapping features remain. Comparison render, native 16/32-pixel samples, SVG parsing and PNG dimensions checked; governance verification applies to this documentation update. Prior drafts are preserved. Owner assessment, production identity integration and publication remain pending. No site code, scientific records or public assets are changed.

### SL-RULE-GLOSSARY-HERO publication receipt

Published the Hedgehog pathway first glossary illustration as Sites version 32, source `7f6138d5297a0fdc99197860676208a91dee6991`, deployment `appgdep_6accdd34add081918658c2ffcc6215aa`, at https://remaprx.com/glossary/hedgehog-pathway. Retained original transparent PNG and exact built-in ImageGen prompt; generated 512/1024 WebP and social PNG; added accurate glossary metadata and shared ImageObject structured data. Desktop and mobile previews, TypeScript, governance, article navigation, production build and reader-boundary checks passed. Full validation passed 65 image mappings and 260 hashes; live verification passed 65 pages and 130 image downloads. Bounded changes are synchronized to this canonical repository; no scientific or indexing release changed. Full receipt: `GLOSSARY-HERO-PILOT.md`.

## 2026-10-12 — SL-RULE-GLOSSARY-COMPLETE: remaining glossary illustrations

Source: owner's explicit request to create matching images for the remaining glossary pages using the same blue style and metadata setup. Scope: all 20 remaining entries, completing 21 glossary illustrations and 85 illustrated drug/condition/glossary routes. Preserve the accepted Hedgehog pilot and all existing topic art. Supersedes optional glossary image coverage; catalog and asset checks now require all canonical glossary entries. Contract: `DESIGN-SYSTEM.md`; exact prompts: `assets/hero-art/glossary-generation.json`; verification/publication: `GLOSSARY-HERO-ROLLOUT.md`.

Implementation begins from live Sites version 32, source `7f6138d5297a0fdc99197860676208a91dee6991`. Biological and statistical subjects follow the existing definitions and are conceptual illustrations, without measured results or treatment claims. Existing prose, references, audience and scientific/access/indexing gates are preserved. Publication and verification results follow in the rollout record. No upstream rule synchronization is claimed.

## 2026-10-12 — RRX-CAL-T1: resume complete scientific calibration

Source: owner request in the research chat, “Continue with calibration. Finish the itraconazole packet’s full scientific review, then work through the remaining first-tranche reports.” Scope: CAL-07 first, then CAL-01–CAL-08 in the preserved assignment matrix; historical holds, canonical identities and previous receipts remain intact. Completion requires substantive Q01–Q15 review and input coverage, full report/required companion inspection, source-version/integrity checks and independent audit. AI-authored scientific review completion remains separate from human approval, scientific release and deployment. Narrow lawful retrieval of missing CAL-07 figures/supplement and dated integrity metadata uses a separate prospective acquisition packet; historical closed packets do not gain retrospective web enrichment. Operational plans, schemas, readiness and progress: `research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/`. New work is pending those readiness passes. No public application change is authorized by this continuation.
