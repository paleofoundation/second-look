# Sitewide Research Feed implementation

Date: November 3, 2026. Owner instruction: “Great. Execute sitewide.”
Base: published Sites version 53, source `3b21b523b53dab4407475ba532907b85845b0699`.

## Implemented behavior

- All article Research Feeds and the research library use the shared bordered card with circular plus/minus, visible finding excerpt, compact study type/year, relevant topic links and separate Open / Link / Email actions.
- Expanding a card shows the four Microbiome research questions, recorded study facts, source-bound findings and limitations, and one correction/integrity notice. The authoring source, source identifiers and scientific figures are unchanged.
- Available authorized opening answers are loaded from the existing private/no-store review endpoint. Cross-source full reviews remain on their dedicated page so opening a card cannot change article citation numbers.
- Dedicated source pages use a compact blue hero, original publication title/author list/DOI, the four-question public summary, source facts/locations, contextual topic links, genuine page history and numbered references. Background sources use a source summary without fabricated study questions.
- Released full reviews use Methods, Results, Safety, Limitations, Applicability, Context and Disclosures. Each canonical Q01–Q15 answer renders once with its stable fragment. Presentation mapping does not change the approved record, serialized data or hash.
- Pending, withdrawn, incomplete and unavailable reviews show explicit availability messages. Sign-in is offered as an unlock only when the existing server policy returns the appropriate released-review state.
- FAQs precede Research Feed through the shared article contract and corresponding citation plan. The separate Evidence drawer and the previously removed quick-search controls retain their intended behavior.

## Source mapping

Microbiome Medicine revision `28ed85b6d510dfddf1720775b456771c7dc62763`: `docs/DESIGN-SYSTEM.md`, `src/lib/researchFeedReveal.ts`, `src/components/ResearchFeedView.tsx`, and the research-feed CSS in `theme-wp.css` / `globals.css`. PepsAnon: shared catalog, disclosure and fragment behavior. Reference repositories were read only and its browser reference was retained.

Destination components: `components/article.tsx`, `components/study-source-content.tsx`, `components/study-page.tsx`, `components/review-answers.tsx`, `components/review-status.tsx`, `components/shared-theme/research-feed.css`, and the research route. `lib/study-presentation.ts` formats public source fields. `lib/study-review-plan.ts` maps immutable review answers to reading sections. No new model API is needed under the TypeSafe guidance.

## Verification

Passed: TypeScript; the new study presentation and Q01–Q15 mapping checks; all-profile reader checks (64 profiles); all 301 source pages (177 research and 124 background); article navigation/citations/history checks (68 articles); Evidence checks (64 profiles plus four other evidence guides); wiki-link checks; seven existing review-coverage tests; governance for 236 preserved rule/history/ingest files; production build; public/private source and built-payload boundary inspection.

The shared route change invalidated the conservative guide-marketing fingerprints. The existing generator refreshed all 66 candidate hashes; product content, availability and approval fields were preserved. No guide or paid feature was released.

Browser checks: desktop feed closed/open, separate Open navigation, exact publication identity, signed-out pending-review state, and mobile layouts at 390px and 320px. Both mobile widths reported document width equal to viewport width. Plus/minus visibility was checked after a specificity fix. Local mock account storage was unavailable; signed-out behavior and authorized synthetic full-review fixtures were verified. No live released full review was available to certify an authenticated production reading session. All 301 source-page SSR checks preserve original titles, unique IDs, local fragments, and the public/private boundary; missing source URLs do not create empty links.

Screenshots: [desktop feed](verification/research-feed/feed-desktop.png), [expanded feed](verification/research-feed/feed-expanded.png), [mobile feed](verification/research-feed/feed-mobile.png), [dedicated study page](verification/research-feed/study-desktop.png).

## Scientific and release boundaries

This is a presentation implementation over the existing source records. No new acquisition, extraction, research appraisal, source merge or evidence grading was performed. Scientific data, private reviews, review envelopes and approval/hash fields remain unchanged. Missing facts and unreleased appraisals remain explicit. Full-text completeness and numerical verification continue through the existing research workflow.

Publication is pending the exact-source package and native deployment result below. Existing public audience, indexing policy, scientific gates and free-authenticated review access are retained. The pinned One Match Rule package and separate reference projects were not changed.
