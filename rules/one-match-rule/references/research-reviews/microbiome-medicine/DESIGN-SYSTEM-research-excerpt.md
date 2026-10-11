## Component: Research Feed card  ⚠ got this wrong once — the spec is now locked

**Canonical source:** `_migration/endo-live.html` (`.research-feed__item`) +
`src/lib/researchFeedReveal.ts` `cardBody()`. **Renderers:** generator
`_generator/pages/*/build.mjs`; signed-in reveal `researchFeedReveal.ts`.

**Structure (exact):**
```html
<div class="research-feed__item accordion__item">
  <div class="research-feed__header-wrap accordion__header">
    <div class="research-feed__toggle-icon-wrap">
      <span class="research-feed__toggle-icon research-feed__toggle-icon--plus">…+ svg…</span>
      <span class="research-feed__toggle-icon research-feed__toggle-icon--minus">…− svg…</span>
    </div>
    <div class="research-feed__title">Study Title</div>  <!-- a plain DIV, NOT a link -->
  </div>
  <div class="research-feed__sub-header">
    <div class="research-feed__sub-header-item research-feed__sub-header-item--date">Date</div>
    <!-- date / category ONLY when the study has an assigned category (a link to /categories/<slug>).
         Do NOT substitute the journal name. If there is no category, show the date item alone. -->
    <div class="research-feed__sub-header-item">/</div>
    <div class="research-feed__sub-header-item"><div class="research-feed__categories">
      <div class="research-feed__category-wrap"><a href="/categories/<slug>/">Category</a></div></div></div>
  </div>
  <div class="research-feed__excerpt">One finding-led sentence.</div>
  <div class="research-feed__content accordion__content">
    <div class="research-feed__graphs">Location / Sample Site / Species</div>
    <h4 class="wp-block-heading">What was studied?</h4><p>…</p>
    <h4 class="wp-block-heading">Who was studied?</h4><p>…</p>
    <h4 class="wp-block-heading">What were the most important findings?</h4><p>…</p>
    <h4 class="wp-block-heading">What are the greatest implications of this study?</h4><p>…</p>
  </div>
  <div class="research-feed__footer"><div>
    <a class="btn" href="/research-feeds/<slug>">Open</a>
    <a class="btn" href="<paper_url>" target="_blank">Link</a>
    <a class="btn" href="mailto:…">Email</a>
  </div></div>
</div>
```

**Behavior (verified against the live endometriosis card, 2026-07-03):**
- The **title is a plain `<div class="research-feed__title">`, NOT a link.** It has no `href` and
  no color of its own: collapsed it inherits the dark body text (black); when the card is
  expanded the whole header-wrap turns brand red, so the title reads red in the active state.
  This is the canonical behavior — the endo card does exactly this. Do not make the title an
  `<a>` and do not give it its own color rule.
- **The header-wrap (`.accordion__header`) is the toggle.** Clicking anywhere on the header
  expands the accordion in place (`ContentAccordions` toggles `accordion__item--active`, no
  `preventDefault`), hiding the excerpt and revealing the content: the Location/Sample Site/
  Species graphs + the 4-section summary as **red `<h4 class="wp-block-heading">`** headings.
- **The ONLY navigation to the summary page is the footer "Open" button** (`/research-feeds/
  <slug>`). The title does not navigate anywhere; the summary is revealed inline.
- Footer actions are the QUIET GREY PILL (transparent buttons, grey text+icons, red on hover) —
  NOT filled red `.btn`s (overridden in globals for `.research-feed__footer .btn`). Open →
  internal summary page, Link → external paper, Email → mailto.

**DO NOT:** make the title an `<a>` / a colored link (that was the deviation — it turned the
title blue inside `.entry-content` and made clicking navigate away instead of toggling the
accordion). Do NOT add a "Read the full study summary →" link. Do not dump the 4-section summary
as `<p><strong>` (use `<h4>`). Do not render the card content from the raw abstract when an
authored summary exists.

**How this was gotten wrong (so it isn't again):** the card markup was written from memory / a
generated page instead of the live canonical. The truth is the endometriosis card in the DB —
inspect it (`/conditions/endometriosis`, `.research-feed__item`) before touching feed markup.
