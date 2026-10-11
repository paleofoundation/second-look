# Design source of truth — microbiomemedicine

**There is ONE correct design. Replicate it exactly; never redesign, "improve," or approximate.**
When building or reproducing any UI, open the canonical source first and copy its markup, classes, and
colors verbatim. Only deviate when Karen explicitly asks.

## Canonical sources (the truth, in priority order)
1. **The frozen mirror of the original site** — the archived read-only copy of microbiomemedicine.com
   (sanitized static mirror; private Vercel project). This is the design truth for *everything*.
2. **The endometriosis page** (`/conditions/endometriosis`, `content_items` id 998) — the most-developed
   page and the template every condition page must match. Dump it: `select content_html from content_items where slug='endometriosis'`.
3. The ported theme stylesheet `src/styles/theme-wp.css` (governs base typography, header, footer, article
   content). Do not fight it — match the classes it styles.

Before reproducing a component: view it on the mirror / endo page, copy the exact markup + classes, and if
a base utility class (e.g. `.btn`) carries styling that deviates from the canonical look, **override it to
match** — never ship the deviation.

## Palette (hard rules)
- Brand red: `--color-primary: #cc3333`, dark `#a02727`, light `#f7e6e6`. **NO PURPLE anywhere** — if any
  purple appears in captured markup, map it to red (`WpRender.dePurple`).
- Heading/title text is near-black navy `#1a1a2e` (e.g. homepage hero title), NOT red and NOT dark-red.
- In-article body links are **blue** (theme forces crimson via `p a[style]`; overridden in globals.css `.entry-content a`).
- Headings use Lora (serif); body uses Inter (sans).

## Fixed components (exact patterns — copy, don't reinvent)

### Citations + References
- Inline: `<sup><a class="rgbc-reference rgbc-tooltip js-rgbc-scroll-link" href="#ref-KEY" id="ref-KEY-back" data-title data-link data-link-name data-date data-review-link title=".wiki-ref-KEY">[n]</a></sup>`
- List: `<ol class="rgbc-references"><li class="rgbc-references__item" id="ref-KEY"><a class="rgbc-references__link" href="URL">TITLE</a> AUTHORS <span>(DATE)</span></li></ol>` — default WP ordered list, **no custom badge/counter CSS**.
- Each cited source also gets a hidden `<div class="tooltip wiki-ref-KEY">…</div>` (powers the hover tooltip via `Tooltips.tsx`).

### Tables & accordions
- Tables: `<figure class="wp-block-table"><table class="has-fixed-layout">…</table></figure>`. Metal names in the Metal\|Findings table use `<mark class="has-inline-color has-vivid-red-color">Iron</mark>`.
- Collapsible blocks: native `<details class="wp-block-details"><summary><span style="color:#1c43ad;">Question?</span></summary>…</details>`.

### Research Feed study cards  ⚠ I got this wrong once — do NOT repeat
Structure: `.research-feed.accordion` › `.research-feed__item.accordion__item` › header (`.research-feed__header-wrap.accordion__header` with ±toggle icons + `.research-feed__title`), `.research-feed__sub-header` (year / category), `.research-feed__excerpt` (italic, shown collapsed), `.research-feed__content.accordion__content` (4-section summary in **h4** + `.research-feed__graphs`), then `.research-feed__footer > div` with the actions. Toggle wired by `ContentAccordions` (ArticleView).
- **The Open / Link / Email actions are a QUIET GREY PILL** — transparent buttons, grey text+icons (`rgba(80,80,80,.9)`) on a `#f6f8fa` pill, red ONLY on hover. They are **NOT filled red `.btn`s.** The theme base `.btn` is red, so it MUST be overridden inside `.research-feed__footer` (see globals.css). This is a fixed design, not a choice.

### Signature chart
- Rendered by `MicrobiomeSignature`; the hero "Microbiome Signature" button (`data-modal-id="research-diagram-modal"`) + a sidebar nav entry appear automatically when `meta.signature.levels` exists. Don't hand-build it.

## Why this file exists
Karen built a deliberate, consistent system; small deviations read as broken, not as variation. See the
memory note `design-truth-fixed-components` and the skill `build-condition-page`. When unsure, copy the
canonical source exactly and ask before deviating.
