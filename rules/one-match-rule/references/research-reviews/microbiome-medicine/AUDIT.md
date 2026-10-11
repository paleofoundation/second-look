# Microbiome Medicine research reviews and account intake

Read-only source audit, 9 October 2026. Correct reference: **microbiomemedicine.com**, repository `paleofoundation/microbiomemedicine`. The default branch was rechecked and still points to `28ed85b6d510dfddf1720775b456771c7dc62763` (25 September 2026, 08:59:15 UTC). All 29 inspected file contents independently match their original Git blob hashes; `manifest.json` also records SHA-256 and exact extract ranges. No scientific article bodies, environment files, secret values, account records or author biographies are packaged.

**Finding:** reuse the reference's dedicated research-page presentation, universal question headings, inline study-card connection and role-dependent intake. **Do not reuse its cosmetic content wall as access protection or its abstract seeding as a completed scientific review.** The new owner requirements need explicit corrected implementations.

## Observed research structure

`src/app/research-feeds/[slug]/page.tsx` delegates to `ResearchFeedView`. That server component resolves a published research-feed record, canonicalizes its slug and prefers captured WordPress HTML through `WpRender`. Otherwise it renders a native React article shell: title and original-paper link; editorial-author metadata; conditions; save/share actions; left navigation; a central HTML body; and a contextual right rail. `meta.feed` supplies location, sample site, species and paper URL. Those microbiome-specific fields require topic-aware mapping, not automatic copying to every drug study.

The canonical universal questions are:

1. What was studied?
2. Who was studied?
3. What were the most important findings?
4. What are the greatest implications of this study?

`_generator/lib/feeds.mjs:22–65` establishes these headings and formats them as H3 plus prose on dedicated pages. `docs/DESIGN-SYSTEM.md:60–124` specifies H4 versions inside an inline study card. The card header toggles inline content; its title is plain text, and the footer's **Open** action reaches `/research-feeds/<slug>`. **Link** reaches the original paper; **Email** composes a share email. This is an observed source convention, not a mandate to replace PepsAnon's existing research overlay or add another independent study catalogue.

The card uses topic metadata, an excerpt and the same authored review content. Its generator and `researchFeedReveal.ts` share this presentation; the latter reveals existing card bodies when called by an authenticated render. A dedicated review URL exists independently of the card. Public archive/search code exposes bibliographic titles and excerpts and links to these pages.

### What the source does not establish

- The generator mechanically buckets abstract sentences into four sections; unstructured text is placed under the first heading. Missing abstracts can fall back to a title. It creates records with `status: "publish"`. This is a draft-seeding mechanism, not full-text review, appraisal, correction verification or human approval. The generator README explicitly describes authored refinement as future work.
- Four headings alone do not satisfy the One Match Rule's richer universal appraisal questions. Keep those questions and their stable IDs, including methods, comparator, estimates/uncertainty, bias, harms, conflicts, applicability and source integrity. A readable four-part opening may sit above the deeper appraisal without discarding it.
- Source reuse is based on exact/normalized titles and slugs; it is not robust DOI/PMID/report/study-family identity reconciliation. The title index also describes duplicate migrated records. Do not infer that every cited paper has one complete review, or deduplicate source reports merely by title.
- In the drawer source a comment claims every underlying study was reviewed, but the generator has mechanical seeds. Neither comment nor route existence demonstrates corpus-wide review completeness. Audit actual citation-to-review coverage and actual review state.
- The renderer uses raw stored HTML. Preserve citation markup through safe canonical structured rendering/sanitization, not unsanitized external HTML interpolation. Keep current sentence-level source locators and corrected/quarantined states.

## Access boundaries: cosmetic wall versus actual authorization

| Boundary | Observed source | What it means |
|---|---|---|
| Dedicated native review | `ResearchFeedView.tsx:98–102,238` calls `isLoggedIn` but sends full `contentHtml` for both states; logged-out markup gains `data-gated` | Full review text is delivered before visual gating |
| Captured WordPress review | `WpRender.tsx:248–262` adds `data-gated` to the center then emits full HTML | Same cosmetic boundary |
| Browser wall | `AccessGate.tsx` calls browser `getSession`, adds blur/overlay and explicitly says the text stays in the DOM for indexing | CSS/local session controls visibility only; disabling/removing it exposes delivered text |
| Inline feed reveal | `WpRender.tsx:221–224` calls `revealResearchFeedWalls` only when server `isLoggedIn()` is true | This particular transformation conditionally includes card bodies; the helper itself does not authenticate, and other paths remain public |
| Data reader | `lib/supabase.ts` creates an anonymous client; `lib/content.ts:127–154` selects full published records | Auth is not required to retrieve the body through this source client |
| Database migration | `0001_initial_schema.sql:66–78` allows select on published `content_items`, including `content_html`; media reads use `true` | Source-defined RLS allows anonymous published-body access. Actual deployed database policies were not inspected |
| Request proxy | `src/proxy.ts` refreshes auth tokens, catches errors and continues serving public pages | It is not a research-route authorization guard |
| Dashboard | `dashboard/layout.tsx:10–13` verifies the user server-side and redirects when missing | This is a real source-level server gate for the dashboard, not for research pages |

An unauthenticated reader may be shown a sign-up overlay; that does not mean the review was withheld. Reusing the wall without replacing these boundaries would fail the owner's login requirement. The source's `revalidate = 3600` is also not an authorization strategy; review session-dependent caching rather than copying it blindly.

The [public research index](https://microbiomemedicine.com/research-feeds) and [one linked review](https://microbiomemedicine.com/research-feeds/characterizing-the-gut-microbiota-in-females-with-infertility-and-preliminary-results-of-a-water-soluble-dietary-fiber-intervention-study) were read through the web tool. The crawler extraction includes the review's substantive question sections and intake labels, consistent with the code's indexing design. A cached extraction is not a live authentication test, deployed-commit proof or audit of current database/storage permissions. No account was created and no protected endpoints were probed.

## Existing intake and deficiencies to avoid copying

`WaitlistForm.tsx` has three mutually exclusive roles: `clinician`, `researcher`, `int_ind` (Interested Individual). All see name, email, country and areas of interest. Clinicians see clinic, specialty, optional license and practice country; researchers see institution, academic role, research focus and optional ORCID/ResearchGate; interested individuals see a reason-for-interest field. Role selection reveals the corresponding group. No industry role exists in this source; Citizen is not its current literal label.

`api/waitlist/route.ts` accepts these fields, stores them in auth `user_metadata`, and creates an account with a server-only service-role API. It sets `email_confirm: true`, allowing immediate password sign-in without proving mailbox ownership. The packet includes the exact code as an **audit-only negative reference**, containing environment variable names but no values. Do not treat this behavior as verified-email enrollment or an automatically authorized credential policy.

Other source gaps:

- Unknown role values silently become `int_ind`. Most form-required fields and role-specific requirements are not validated server-side; the endpoint only checks a basic email pattern and password length, then bounds nonempty metadata strings to 500 characters.
- The role is self-declared user metadata. It is not a verified clinical credential, scientific approval, editorial permission, administrative role or payment entitlement.
- `/login` has a separate direct signup path with email/password only; magic-link enrollment is another path. Both bypass the role-dependent form. Account creation through one intake screen does not ensure complete role intake across auth paths or existing accounts.
- `dashboard/profile/page.tsx` edits only `profiles.display_name` and `bio`, not the stored intake role/fields. The audited repository has only the content/media initial migration; it does not establish deployed `profiles` schema/RLS or a durable editable role-profile contract. Do not claim role editing or cross-user isolation verified.
- Signup/login normally navigate to `/dashboard`; the modal refreshes in place. The full review's originating URL is not uniformly carried through login/email callback. Add a validated same-site return path, preserve review fragments, and verify it through password and email-link flows.
- The subscription page contains an inert free-trial button, and the dashboard advertises a trial. No Stripe/paid entitlement enforcement was established. Do not copy misleading trial labels into the owner's current free phase.
- The interested-person reason placeholder solicits personal/family health context. The new requirement can be satisfied with role/intention intake without requiring sensitive health narratives, license numbers or employer data. Keep optional profile context proportional and private.

## Recommended portable implementation contract

These are new implementation recommendations for the owner requirement, not claims about existing Microbiome functionality:

1. **One canonical review per cited research report.** Use canonical paper/report identity, preserved aliases and a stable review URL. Link every cited research paper to its dedicated universal-question review while retaining the original source link. Multiple reports in one study family may have separate report reviews with a shared family link; do not inflate independent-study totals. Distinguish research papers, secondary reviews, registries, guidelines and commercial/context sources. A metadata-only/pending record is visible as pending and does not satisfy completed-review coverage. Missing/full-text-restricted evidence must remain an explicit review limit; no fabricated answer to fill a required heading.
2. **Keep the review data and presentation shared.** Source the dedicated review, overlay summaries and inline catalogue from the same canonical IDs/results. Preserve the four familiar opening questions and the complete One Match appraisal contract. Keep review author, paper authors, AI assistance and actual independent approval separate. Reuse the reference's question-led reading hierarchy and source/author/context layout without copying medical answers, topic metadata or assigned people.
3. **Free authenticated full reviews for the current phase.** Public permitted visitors can see citation identity, accurate preview, source link and account CTA, plus essential guide findings/safety allowed by the existing site audience. A verified server session unlocks the full review with no checkout or paid subscription requirement now. Enforce authorization before body delivery in HTML, server-component payloads, API/JSON responses, exports/downloads, search responses and caches; secure database/storage access as appropriate. Do not ship the full review to the browser and blur it. Keep free access separate from the existing scientific release policy. Future Stripe wiring does not itself authorize activating charges or changing free entitlements.
4. **Role intake across every enrollment path.** Add owner-requested citizen/interested-person and industry options to clinician/researcher, with a useful Other or unspecified path where appropriate. Store stable audience-role values and minimal optional context in a private, user-owned profile with validation and access controls; expose editing and handle existing/magic-link users. Preserve existing accounts. Audience role must never grant editorial/clinical authority or change access pricing. Do not copy the auto-confirm shortcut without an explicitly chosen supported auth policy.
5. **Preserve the originating research journey.** Signup/login, confirmation, expired-session retry and sign-out must preserve accurate access state. Return to the requested review/anchor after authentication with validated same-site redirects; allow free signed-in users access; show useful errors when auth is unavailable. Keep source/PDF links honest about separate publisher rights.

The packet is deliberately not a runnable application. The renderer depends on Next/React, content loaders, canonical slugs, author/profile mappings, safe text/link transformation, metadata and shared rails. Intake depends on React, the destination auth system and server validation. CSS extracts depend on project tokens, base typography and form primitives. They contain historical mobile rules hiding rails/author regions; adapt these to the One Match requirement to preserve usable author/context/navigation on phones. Do not import all reference dependencies or change the destination stack just to match a source file.

## Acceptance evidence required in the destination

Reconcile all actual cited research IDs to live dedicated review routes and substantive answered/unresolved universal questions; test shared review generation on a second paper/type. Verify original source locators, appraisal states and study-family counts. Test logged-out, signed-in free, expired-session and unavailable-auth states, password and email-link enrollment, each audience role and existing-account profile completion. Inspect anonymous HTML/payloads/API/download responses and caching to prove the full review is absent, not blurred; confirm one user's profile cannot be read/edited as another user. Verify no charge/trial is required now and no future Stripe behavior is represented as live. Render desktop/mobile review and intake states, keyboard operation, return anchors, source links and author identity. Report unexecuted tests as pending. This audit executes none of those destination checks and grants no scientific approval.
