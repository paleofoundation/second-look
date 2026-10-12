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

## 2026-10-12 — SL-RULE-010: American English page language

Source: owner's explicit Drug Repurposing instruction: “Drug Repurposing pages must be written in American English with American English Spelling.”

Adopted: American English wording and spelling throughout authored reader-facing pages and future content generation/import, with `en-US` document language and prose date formatting. Preserve exact source titles, quotations, proper names, raw source wording and stable identifiers; use American English for surrounding prose and displayed status labels. This supersedes inherited British English wording and the Update History `en-GB` date locale. Contract: `PROJECT-RULES.md`, Language and spelling.

Implementation: correct identified spelling variants in current authored page copy, summaries, table labels, mechanism prose, guide/account messages and matching editorial copy; retain original published titles and compatibility aliases. Set the shared HTML language and Update History locale to `en-US`, update prose date labels and the existing date expectation. The CSBD population label is normalized in the shared reader adapter, preserving fingerprinted source records and their existing evidence assessments. Verification and publication results are recorded below after checks. No scientific reassessment or raw-source rewrite is implied. This is a local project requirement; upstream/installed/exported One Match Rule synchronization is not claimed.

Verification before packaging: governance integrity, canonical content, reader identity/source closure, unchanged evidence-assessment fingerprints, all 64 profile section renders, 68-article navigation/history rendering, TypeScript and whitespace checks passed in the isolated publication checkout. Guide marketing hashes were regenerated for the spelling-only presentation change; approval and release fields were preserved. Shared React copy/status display changes were reviewed for hooks, accessibility, typing and behavior. Production build, public payload checks and deployment are pending below; no browser comparison was needed for the copy-only change.

## 2026-10-12 — SL-RULE-012: internal links without underlines

Source: owner's request with the Metformin introduction screenshot: “Remove the underline style from this website. internally-linked pages should show up without underline.” Adopted in `docs/DESIGN-SYSTEM.md`: no underlines for internal page and fragment/citation links in normal or interaction states, preserving blue links and keyboard focus. Supersedes inherited wiki-link and hover underline styles. Consulted Microbiome Medicine theme styles and PepsAnon prose/theme styles; current owner instruction takes precedence.

Implementation: shared global internal-destination CSS override; no content or target changes. Verification and publication pending. Upstream/reference projects unchanged.

## 2026-10-12 — SL-RULE-GRADE-COLORS: brand evidence-grade palette

Source: owner's evidence-table screenshot and explicit request that evidence grades use the website's colors. Adopted in `docs/DESIGN-SYSTEM.md`: replace inherited teal badges with the RemapRx blue scale and neutral ungraded treatment, preserving labels and evidence semantics. Supersedes the prior grade-color preservation exception for badge styling only. Shared `reading-modules.css` is the implementation; no evidence records or grading logic are changed. Verification/publication receipt follows locally after deployment; reference sites and upstream rules remain unchanged.

## 2026-10-12 — SL-RULE-GRADE-BARS: evidence strength icons

Source: owner's request to add the screenshot's small strength bars beside grades using the blue colors. Adopted in `docs/DESIGN-SYSTEM.md`; implemented in the shared evidence table using the existing `.grade-bars` styling and PepsAnon `components/peptide/evidence.tsx` reference. Three ascending bars encode High/Moderate/Low/Very low as 3/2/1/0 filled; ungraded evidence has no strength icon. Visible labels, accessible button names, blue palette and grade-panel actions are preserved. No scientific record or grading logic changes. Verification/release receipt follows locally.

## 2026-10-12 — SL-RULE-PAGE-SNAPSHOT: author ORCID and page-scoped research counts

Source: owner's Microbiome Medicine screenshot and explicit request for an ORCID-logo-only link beside the name, plus study and investigated-drug counts on conditions and study and investigated-condition counts on drugs. Adopted in `docs/DESIGN-SYSTEM.md`; supersedes the visible full ORCID string and generic Research sources hero block. The implementation reuses verified author identity and public canonical citation/study/relationship records, groups recorded study identities, and excludes unsupported candidate-only counts. Study-count identity coverage follows available canonical metadata; no independent-trial audit or scientific reassessment is implied.

Implemented in the shared author/article components, `components/page-snapshot.tsx` and `lib/page-snapshot.ts`. `scripts/check-page-snapshot.mjs` covers duplicate reports, multi-family syntheses, background/uncited exclusions, disputed references, unsupported candidates, zero coverage and both directions on all 64 profiles. TypeScript and all-profile SSR checks pass. Browser and publication receipts will be recorded after verification. Upstream/reference repositories and scientific release gates are unchanged.

Verification before publication: Page Snapshot tests pass for all 64 profiles, including study identity deduplication, multi-study separation, cited-only counts, zero coverage and source-supported investigation counts. All-profile section SSR, 68-article navigation/citation/history checks, TypeScript, governance and whitespace checks pass. Browser preview returns HTTP 200; Metformin and Long COVID render the correct metric labels, the official ORCID icon is beside the name and points to the existing verified URL, biography opening/closing works, study-count links target Research Feed, and the labeled information popover opens with the included entities. Visual inspection passed at the browser's 985px width; requested 390px viewport was ignored by the browser provider, so narrow-mobile visual acceptance is unverified. React review confirms stable hook order, separate sibling button/link controls, decorative icons, accessible link/button labels and no new data requests.

## 2026-10-12 — SL-RULE-HERO-ROLLOUT: complete the blue topic illustration set

Source: owner request, “Let's create matching hero images for the remaining drug and condition pages on remaprx.com, using the same blue style and metadata setup.”

Adopted scope: extend the existing Metformin/Parkinson illustration system to all current drug and condition routes, including canonical discovery pages. Preserve original blue art direction, left hero placement, transparent responsive WebP assets, individual social previews and accurate descriptive metadata. This supersedes the first pass's pending remaining-topic artwork scope; PepsAnon migration remains separate. Contract: `DESIGN-SYSTEM.md`; exact prompts/master provenance: `assets/hero-art/*-generation.json`; verification and publication: `HERO-ROLLOUT-VALIDATION.md`.

Implementation underway in a checkout synchronized with live Sites version 26, source `f0d929b67c8c74b23601c59565080729fa6d1f06`. The merged route inventory has 64 topic pages (32 drugs and 32 conditions), requiring 62 new originals. Scientific prose, evidence grades, access, indexing and commercial release are unchanged. Final asset coverage, validation and deployment must be recorded before marking this rollout complete. No upstream/installed/exported rule synchronization is claimed.

SL-RULE-HERO-ROLLOUT implementation complete before packaging: 62 new original illustrations, 64-route public catalog, responsive WebP/social PNG derivatives, exact prompts and hashes. Source was reconciled onto `f4804463e383f0bcf44b9b51fa691056278208dc`, preserving newer link and evidence-badge updates. Complete source, local HTTP metadata/image and responsive browser checks passed; production build/publication receipt belongs in `HERO-ROLLOUT-VALIDATION.md`.

## 2026-10-12 — SL-RULE-GLOSSARY-HERO: Hedgehog pathway first illustration

Source: owner's explicit request, “Glossary pages need images. Hedgehog Pathway should be your first attempt.” Adopt the blue illustration/metadata system for individually assigned glossary pages, with Hedgehog pathway as the first pilot. This supersedes the drug/condition-only image catalog scope, while retaining all 64 existing assignments and leaving unassigned glossary entries on their existing layout. Contract: `DESIGN-SYSTEM.md`; provenance: `assets/hero-art/glossary-generation.json`; verification/release: `GLOSSARY-HERO-PILOT.md`.

Implementation starts from published Sites version 31 (`066b45cf47f11b08e05bc1f1ef6688748b722eac`), preserving the recent author/Page Snapshot update. Add one conceptual signaling illustration, glossary catalog support and shared image structured data in the glossary branch. Existing definition, citations, research and access/indexing gates are unchanged. This is the first visual attempt; other glossary illustrations remain unassigned. No upstream rule synchronization is claimed.

## 2026-10-12 — SL-RULE-GLOSSARY-COMPLETE: remaining glossary illustrations

Source: owner's explicit request to create matching images for the remaining glossary pages using the same blue style and metadata setup. Scope: all 20 remaining entries, completing 21 glossary illustrations and 85 illustrated drug/condition/glossary routes. Preserve the accepted Hedgehog pilot and all existing topic art. Supersedes optional glossary image coverage; catalog and asset checks now require all canonical glossary entries. Contract: `DESIGN-SYSTEM.md`; exact prompts: `assets/hero-art/glossary-generation.json`; verification/publication: `GLOSSARY-HERO-ROLLOUT.md`.

Implementation begins from live Sites version 32, source `7f6138d5297a0fdc99197860676208a91dee6991`. Biological and statistical subjects follow the existing definitions and are conceptual illustrations, without measured results or treatment claims. Existing prose, references, audience and scientific/access/indexing gates are preserved. Publication and verification results follow in the rollout record. No upstream rule synchronization is claimed.


## 2026-10-12 — SL-RULE-ATLAS-IDENTITY: approved mapping identity and homepage publication

Source: owner's explicit approval of mapping round 4, instruction to apply its logo/favicon and mapping visual to the hero, and reminder to replace Second Look and the old “A familiar drug. A different question.” copy and go live. Scope: shared identity, current reader-facing branding/metadata, homepage atlas claim and generic mapping illustration. Supersedes preview-only status and the simplified mark. Production code/assets and contract are in `REMAPRX-IDENTITY.md`; earlier concepts are preserved.

Implemented against live version 33 in an isolated checkout to preserve concurrent published work. The approved icon and wordmarks, SVG/ICO favicon, touch icon and default social image use the adopted blue/yellow palette. Readable HTML mapping labels, target geometry and solid/dashed routes retain the category visual. No evidence records, review approvals, clinical grades, audience or indexing gates change. Relevant checks, browser review, source integration and exact publication receipt are recorded in `REMAPRX-IDENTITY.md`. Earlier mechanism work is not included or declared complete. No upstream/installed/exported One Match Rule synchronization is claimed.
