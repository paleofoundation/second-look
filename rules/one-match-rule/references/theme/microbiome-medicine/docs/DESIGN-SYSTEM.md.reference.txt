# Design System — the readme sheet (source of truth)

**There is ONE correct design. Replicate it exactly. Never redesign, "improve," approximate, or
ADD anything not specified here.** This file is the canonical spec for every reusable component
and interaction on microbiomemedicine.com. It exists because adding un-specced elements (e.g. a
"Read the full study summary →" link that was never part of the design) is a deviation that
breaks the system and wastes time.

## The process — do this BEFORE building or editing any UI

1. **Find the spec.** Locate the component below. If it is not yet specified here, STOP: open the
   canonical source (see "Canonical sources"), document the exact markup + behavior here first,
   then build. Never build from memory or from another *generated* page (generated pages may
   themselves have deviated — that is exactly how the research-feed link bug happened).
2. **Copy exactly.** Replicate the markup, classes, and behavior verbatim. Match the palette and
   the global rules below.
3. **Add nothing.** Do not introduce elements, links, labels, buttons, or copy that are not in the
   spec. If something seems missing or the design is ambiguous, ASK — do not invent.
4. **Never substitute for missing data.** If a canonical element's data is unavailable (a
   category, a full date, an author, an effect size), OMIT that element or ASK. Never fill the
   slot with an invented stand-in (e.g. a journal name where a category belongs, a placeholder
   label). Showing only the real data you have is correct; substituting is a deviation.
4. **Verify.** Render it and confirm it matches the canonical source, not just "looks reasonable."

## Canonical sources (truth, in priority order)

1. The frozen mirror / captured WordPress HTML in `_migration/` (e.g. `endo-live.html`,
   `x-cond.html`) — the design truth for markup + structure. Extract the real element, do not
   guess. Logged-out captures may show a `<div class="wall">` teaser where gated content is.
2. The endometriosis page (`/conditions/endometriosis`, `content_items` slug `endometriosis`) —
   the most-developed page; the template every condition page matches.
3. `src/styles/theme-wp.css` (base typography, header, footer, article content) + the shared
   renderers: `ArticleView` (generated pages), `WpRender` (captured pages), `ResearchFeedView`,
   and `src/lib/researchFeedReveal.ts` (the signed-in card body).
4. `DESIGN.md` and the component specs below.

---

## Global rules (apply everywhere)

- **Palette:** brand red `--color-primary #cc3333`, dark `#a02727`, light `#f7e6e6`. **NO PURPLE
  and NO magenta** (e.g. never `#fdf2f8`/`#9d174d`). Headings/titles are navy `#1a1a2e` unless a
  spec says brand red.
- **No bold, ever** (the theme forces weight 400). Emphasize with color, serif (Lora), and links.
- **No em dashes** in copy unless highly warranted (periods/commas/colons/parens instead). Middle
  dots (·) and en-dash numeric ranges are fine.
- **No lists** — body content is prose + canonical tables only. The only allowed list is the
  `<ol class="rgbc-references">` bibliography (and native FAQ `<details>`).
- **Internal-only blue links:** the blue in-content link style links ONLY to an internal
  microbiomemedicine page. External sources are `[n]` citations, never inline blue links. If a
  concept has no page yet, create it.
- **Right-rail connections: max 3, globally.**
- **Sidebar labels are short + universal per post type** (e.g. "FAQs", never "Frequently Asked
  Questions").
- **LLMO content structure** (see `docs/CONTENT-RULES.md`): front-load a ~50-word answer, sentences
  under ~20 words, one idea per paragraph, question-based FAQ headings.

---

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

---

## Component: Conditions table (taxon pages)

**Renderer:** `src/components/ConditionsTable.tsx` + `StudyDrawer.tsx` (CSS `.mbio-cond*`/
`.mbio-drawer*` in globals.css). Fed by `meta.conditions` (generator).

- Columns: **Condition · Direction · Grade · Effect · Evidence**. Header row brand red.
- **Grade** = a rounded badge whose fill is a **gradient of brand red** (deep red = strong, pale
  pink = weak), driven by the study's methodology weight; letter A–D inside.
- **Direction** = Enriched (red ↑) / Depleted (blue ↓) / Mixed (↕), matching the signature
  convention (enriched=red, depleted=blue).
- **Effect** = 1–3 arrows encoding evidence-strength (a proxy, NOT a measured effect size — the
  corpus has none). Up=enriched red, down=depleted blue.
- **Evidence** = "N Studies" + "Participants: N"; the row opens a right slide-in `StudyDrawer`
  with the setting/notes. "N Study" text = Direction size (0.92rem); "Participants" = effect
  caption size (0.74rem).
- Header **info icons** are small superscripts (`.mbio-info`, `vertical-align: super`, 13px,
  `cursor: pointer` NOT `help`) so labels stay on one baseline; hover/focus shows a white tooltip.
- The summary stats live in the **Page Snapshot**, not a table band. No aggregate-evidence clutter.

## Component: Page Snapshot (hero)

**Renderer:** `src/components/PageSnapshot.tsx` (`.snapshot--brand` in globals). On-brand red card:
darker header bar + red body + per-row SVG icons. Rows: `N references on this page` /
`N participants in N studies` / `N conditions`. Links are clickable but do NOT underline on hover.
The captured migration CSS flattened `.snapshot` to translucent-white with 📄 bullets — the
`--brand` class restores the branded card.

## Component: Section sidebar (left nav)

**Renderer:** `SectionNav` (auto-built from the page's `h2`/`h3` headings via `ArticleView`).
Order = heading emission order. Labels are the headings (keep them short + universal: "FAQs",
"Overview", "Conditions", …). Icons from `public/wp-content/themes/rgbcode/static_media/*.webp`.

## Component: Right rail / Connections

**Renderer:** `RightRail`. Up to **3** connection links (blue, capitalized), then Send feedback,
Highlights, Join the Roundtable. Connections come from `meta.connections` (curated) or auto-ranked
internal links, conditions-first.

## Component: Hero (`.research-hero`)

**Renderer:** `ArticleView`. Red hero: left illustration + "Did you know?"; center breadcrumb +
italic serif `<h1>` + excerpt + tag buttons (Interventions/Research Feed/Share); right author
photo(s) + "Researched by:" + ORCID + "Last Updated" + Page Snapshot. Every content page shows an
author (default Karen Pendergrass).

## Component: Tables, citations, FAQs (canonical)

- **Tables:** `<figure class="wp-block-table"><table class="has-fixed-layout">…</table></figure>`;
  red `thead`; metal names in `<span class="has-inline-color has-vivid-red-color">`.
- **Citations:** inline `<sup><a class="rgbc-reference rgbc-tooltip js-rgbc-scroll-link" …>[n]</a>`
  (first-appearance numbering, dedupe) + `<ol class="rgbc-references">` list + hidden hover
  cards. External source URLs live ONLY here, never as inline blue links.
- **Citation hover card (exact, from `_migration/endo-live.html` `.rgbc-reference-tooltip`):**
  ```html
  <div class="tooltip rgbc-reference-tooltip wiki-<hash>">
    <div class="tooltip__content rgbc-reference-tooltip__content">
      <p>Authors, et al.</p>
      <a href="<DOI>" target="_blank">Paper title.</a>   <!-- title hyperlinked to the DOI -->
      <p>Journal. (date)</p>
      <a class="rgbc-reference-tooltip__btn btn btn--rounded" href="/research-feeds/<slug>/">Read Review</a>
    </div></div>
  ```
  The card is authors → title-linked-to-DOI → journal/date → optional "Read Review" button (only
  when the study has our internal review page; OMIT it for foundational refs that lack one). Do
  NOT use a "Reference [n]" header or a "View source" link — that was a wrong hand-rolled format.
- **FAQs:** heading "FAQs"; `.rgbc-faq-block` › `.rgbc-faq-item` `<details>` with the chevron icon
  and "Quick answer:". **FAQs are page-specific**, written around the questions people actually
  search for that entity (e.g. "Is X good or bad?", "What causes high X?", "How do you lower X?").
  They are NOT a template repeated across pages. Answers may carry inline `cite()` citations
  (proper `<sup><a class="rgbc-reference">` superscript links), so the answer is emitted as HTML,
  not `esc()`'d. `ArticleView` auto-builds FAQs ONLY for pages with no `.rgbc-faq-block` (older
  migrated pages); it must never rebuild over a real block (that duplicated it and re-escaped
  `&ldquo;`→`&amp;ldquo;` and stripped `[n]` citation links to plain text).
- **No raw HTML typographic entities in generated content.** Use real Unicode characters (" " · →
  – ₂), never `&ldquo;`/`&rdquo;`/`&rarr;`/`&middot;`/`&ndash;`/`&#8322;`. Entities render fine as
  content but reappear as literal text the moment any feature extracts and re-escapes them.
- **Study drawer (`StudyDrawer`) study name:** we reviewed every study, so the study title is a
  link to OUR internal `/research-feeds/<slug>` summary (not the external paper), placed BELOW the
  Study Summary block (and caveat), not above it.
- **Update History:** `.mbio-update-history` card; entries only for material changes.

---

## Extending this file

When you build or touch a component not fully specified above, first document it here from the
canonical source, then build to the spec. This file only grows; it is never deviated from.
Related: `DESIGN.md`, `docs/CONTENT-RULES.md`, `docs/IMAGE-CONVENTIONS.md`, `docs/EVIDENCE-GRADING.md`.

## Component: Homepage (approved layout, 2026-09-09)

The user's four screenshots of `microbiome-medicine-home.kmfp.chatgpt.site`
(the prototype at commit `26acaae`) specify the homepage body layout: light-gray
split hero with the evidence-mapping image and search, three bordered topic cards,
light-gray validation section with three numbered steps, research rows, and signup.
The user explicitly requires existing site typography, font sizes, and colors.
Use the theme's Inter/Lora fonts and 400 weight, its responsive h2/h3 scale, the
original `.search__title` h1 size, `.search__description` intro size, and
`.categories__link` / `.categories__more` link sizes. Accents use the shared
`--color-primary`; the original homepage background is `#f7f8fa`.

Implement only the body in `HomePage.tsx` and its scoped CSS module. The captured
navbar, megamenu, footer, shared styles, and other page layouts remain intact.
Use existing internal destinations and shared search / subscription handlers.
The red hero and endometriosis spotlight from the later prototype are not the
approved homepage layout.

Homepage link typography (2026-09-25): use the existing listing components
instead of custom display rows. Topic destinations use `.rgbc-archive__link`
from the Conditions directory: Inter 16px/1.4, body text color, 8px vertical
padding, and underline on hover. Do not add circular bullets or row dividers.
“See all” is a plain 16px brand-red text link.

Research entries use the canonical research directory markup:
`.rgbc-content__details-content` containing an anchor with its title in a `p`,
followed by `.rgbc-content__details-meta` and `.rgbc-content__details-date`.
The shared stylesheet supplies the red 1.2em Inter title (19.2px/24px), with 14px
muted metadata in normal capitalization. Do not add numbered columns or arrows.
Retain the homepage section structure, main headings, shared header/footer,
search, subscription handlers, and destinations.

Homepage correction (2026-09-25, clarified by the user): omit the five decorative
labels above the hero and section headings: “Microbiome Medicine”, “Explore
microbiome signatures”, “A transparent validation method”, “Latest research”, and
“Microbiome Insider”. Keep the headings, section content, and current layout. All section h2 headings, including Explore,
validation, research, and signup, share Lora at clamp(28px, 3.2vw, 40px), line-height
1.25. This replaces the prior mix of 40px, 20px, and 24px mobile section headings.
The hero title has a 32px minimum and retains its 60px desktop maximum. Below
640px, supporting prose and topic links use 16px, topic and method titles 22px,
while research entries retain the shared directory typography. Remove forced heading line breaks on phones, keep
20px page gutters, and use 48px section spacing. Signup content aligns left on
phones. Preserve the approved section order, shared header/footer, links, search,
and subscription handlers.

