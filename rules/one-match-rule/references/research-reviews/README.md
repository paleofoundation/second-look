# Research reviews, free access and reader intake

This module packet supplements the [whole-site theme contract](../theme/README.md). Start from the active Microbiome Medicine theme; isolated matching modules within a redesigned shell do not satisfy G4T.

Introduced in One Match Rule 1.14 and extended to PepsAnon in 1.27; required under §§4–5, 8, 10–11 and gates GP/G4P/G5/G6. This packet supplies implementation references and acquisition inputs; it does not contain completed scientific reviews or a deployable authentication backend.

## Every cited paper has a review

Generate a site-wide cited-paper ledger from actual reader-facing references, including FAQs, tables and other review pages. Normalize paper identity and preserve report/study-family distinctions. Each cited research paper—including secondary scholarly research—gets one canonical dedicated review route shared by all citation occurrences. Non-research source types retain their appropriate source records. A book's untouched internal bibliography remains an acquisition lead list, not an assertion that the site reviewed those papers.

The ledger records paper/source versions, citation locations, review ID/route/version, source access, Q01–Q15 completion, appraisal/release state and missing work. An honest pending route is useful but not a completed review. Do not remove inconvenient cited studies or call them context solely to evade review. Report completed, pending and blocked reviews against the full cited-paper denominator.

Use [review-questions-and-inputs.json](review-questions-and-inputs.json) in the ingestion plan and Grokbot input packet **before** any file-request handoff or ingest. It mirrors the existing canonical Q01–Q15 definitions and maps them to fields and relevant companion sources. At receipt, require `review-inputs.jsonl` with paper/question IDs, fields, actual source file/hash/native locator, extraction basis, answerability/status, gap reason and next action. It is an input-readiness record, not worker-issued scientific approval.

Produce the project's full typed review schema before extraction: canonical IDs, separate study/experiment/arm/outcome/result records, numeric types/units/intervals, PDF or native HTML/EPUB locators, question answers, claim relationships, design-appropriate appraisal and exact-version approval. Validate locator/ID references and **one of every Q01–Q15**, not just fifteen array items. The old PepsAnon `launch/study-reviews/review.schema.json` is deliberately a draft with pending approval and limited result shapes; do not call it a production release schema. A keyed question map can enforce unique IDs, with semantic/source review still required.

The builder must distinguish data that were not reported after inspection from data not yet extracted, not checked, inaccessible or inapplicable. Review authors supply supported interpretation; human reviewers supply actual approvals where required. Different designs retain all question IDs with justified applicability: a protocol has no completed results, a secondary review needs search/eligibility/overlap/synthesis appraisal, and a cell experiment has biological versus technical replication rather than clinical participants.

## Microbiome Medicine presentation reference

The [source audit](microbiome-medicine/AUDIT.md) and [manifest](microbiome-medicine/manifest.json) pin `paleofoundation/microbiomemedicine` at `28ed85b6d510dfddf1720775b456771c7dc62763`. The repository default branch was rechecked on 9 October 2026. A source commit is not proof of the deployed site's current permissions.

Reuse the dedicated research route/article shell, question-led typography, metadata and source actions from `ResearchFeedView.reference.tsx`, `research-route.reference.tsx`, the design-system excerpt and relevant CSS. Preserve the four familiar opening questions:

1. What was studied?
2. Who was studied?
3. What were the most important findings?
4. What are the greatest implications of this study?

Map them and deeper Methods/Results/Limits/Sources content to the full Q01–Q15 contract. The four headings do not replace appraisal, harms, conflicts, independence or source-integrity answers. Record where every answer or justified non-answer is rendered. Keep the exact paper link, review author versus paper authors, dates and actual approval states clear. Use one canonical review record for the page, public preview and entitlement-filtered panel/catalogue views.

Port the source code and styles with documented dependencies and destination brand tokens. The source's native review and captured WordPress paths differ; select one destination implementation, sanitize imported content or use a structured renderer, and preserve citations and source locators. Never copy old author assignments, microbiome-only metadata or account data by default. Place the assigned review author's portrait and accessible bio on the right-hand side of the hero under master §7. Show the small green ORCID iD logo and visible identifier linked to that individual's verified canonical record through the shared ORCID renderer. Keep the whole author block inside the stacked mobile hero. Adapt historical CSS that hides author/context areas; do not duplicate the author block in the right sidebar. Existing PepsAnon table overlays and the single inline Research catalogue remain; the source's inline card is a formatting reference, not a second catalogue to add.

## Reference defects that must not ship

Files named `audit-only` document boundaries to replace, not recommended production code:

- `abstract-seeding.audit-only.mjs` mechanically groups abstracts under four headings and marks records published. It does not establish a full-text review, numerical verification, appraisal or human approval. Use only as evidence of the historical layout, never as the completion path.
- `cosmetic-gate.audit-only.tsx`/CSS and `research-body-gate.audit-only.tsx` send protected text then obscure it. The public-read SQL also permits anonymous published-body reads. Their unchanged reuse fails login protection even if the screen looks gated.
- `signup-endpoint.audit-only.ts` auto-confirms email and stores incomplete/loosely validated role metadata. The ordinary login path bypasses that intake, and the existing profile editor does not edit the roles. Use the destination's supported identity provider and a validated private profile API instead.

The dashboard auth-boundary and server-session extracts illustrate an actual source-level server user check, but they are not a complete review authorization system. No deployed authentication, database policy, account isolation or intake behavior was tested by this rule update.

## Required access flow

For current PepsAnon, Second Look and new-build defaults, use `free_authenticated`. A permitted anonymous visitor gets bibliographic identity, review status, genuine concise preview, decisive limitations, original-source links and a free-account invitation. A trusted server session leads through first-login intake if needed, then returns to the exact same-site review/fragment. Eligible authenticated readers get all released full reviews without payment or sample quotas. Pending research remains pending; a logged-in reader is not a scientific approver. A protected editorial draft may be visible only where the project’s existing audience/release policy permits it, with conspicuous incomplete/not independently approved status and its actual Q01–Q15 gaps. Draft visibility, substantive review completion, approval and release remain separately counted; draft access cannot waive an existing scientific-release gate.

Authorize before reading/serializing the full body. Separate the public-preview and full-review serializers. Apply the policy to page HTML, server-component/hydration payloads, APIs/database/storage, search, metadata, feeds, exports and any panel/catalogue view. A client role flag, CSS wall or local `getSession` check is insufficient. Session-aware caching must not share protected responses with anonymous readers. A direct API or static full-body export cannot bypass the gate.

Connect the future entitlement adapter without making Stripe a dependency of current free access. A later paid phase requires the adopted pricing and transition terms, verified merchant/checkout/webhooks/entitlements and applicable scientific/commercial readiness. Connecting Stripe does not silently charge users or activate a paywall. Preserve existing hosting audience and PDF ownership. Do not copy inert “free trial” offers as functional billing.

## Intake contract

Use the role-dependent source form as a presentation reference, then implement the owner's expanded categories and minimal private persistence. Ask “How will you use this research?” with Clinician/healthcare professional, General reader/citizen, Researcher/academic, Industry/professional, Student/trainee, Other and Prefer not to say. Allow multiple roles, with Prefer not to say exclusive. An explicit decline completes intake without inventing a role. Add only useful optional fields; do not require employer/license or health narratives just to read research. Existing account identity fields need not be collected twice.

The [completed-profile schema](intake-profile.schema.json) is a portable storage/validation contract, not a running API. The server derives user ID, schema version and timestamps; accept only permitted role/preference fields from the client. A browser-supplied completion flag is not authorization. Keep draft or failed saves separate from persisted completion. Provide editable profile settings, same-user read/write/export/delete and a retryable error path. Explain the use of role information; do not infer marketing consent or professional verification.

Apply intake consistently across every configured login/signup/callback path and existing accounts missing the current intake. Preserve the original review destination throughout. A role never changes scientific conclusions, grants editorial/admin permissions or changes the current free price. Keep reader profile data out of evidence exports and public caches. Optional interest preferences belong to account settings, not the scholarly source schema.

## Required proof

Return the cited-paper/review ledger, Q01–Q15 answer/input coverage, source→destination code/style map, and actual rendered review/intake evidence. Test anonymous, expired-session, intake-incomplete, completed and declined intake, returning user, profile editing/save failure and cross-user denial. Inspect actual response content for leaks, including indirect overlay/search/exports. Verify free access without Stripe, safe return paths and preserved citation locators. A successful build, fifteen headings, a blurred body or a signup form alone cannot pass G5/G6. State any unexecuted destination tests as pending.
