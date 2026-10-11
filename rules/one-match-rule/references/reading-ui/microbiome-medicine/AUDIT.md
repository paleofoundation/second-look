# Microbiome Medicine FAQ source audit

Audited 2026-10-09 for the owner request recorded at 2026-10-09T09:42:54.215Z. Correct reference: **microbiomemedicine.com**, backed by the authenticated author-owned `paleofoundation/microbiomemedicine` repository. This is not microbialmetallomics.com.

The packet contains the exact shared FAQ helper, the exact FAQ CSS lines, and the canonical design-system FAQ excerpt from commit `28ed85b6d510dfddf1720775b456771c7dc62763` (2026-09-25T08:59:15Z). `manifest.json` records original Git blob IDs, independently recomputed SHA-256 hashes, and extraction line ranges. All nine inspected source blobs matched the Git tree's blob IDs. No scientific article text is included or endorsed.

## Observed implementation

- `src/lib/faqs.ts` emits framework-neutral inline HTML: one `.rgbc-faq-block` containing native `<details class="rgbc-faq-item">` items. Each `<summary>` contains the circle icon and question; the answer remains inline in `.rgbc-faq-a` and begins with **Quick answer:**. It is not a modal, remote drawer, separate FAQ page, or answer card grid.
- The source uses native independent disclosure controls, initially closed. It has no exclusive accordion `name` group and no custom click handler for the FAQ items; multiple answers may stay open simultaneously. Native keyboard interaction follows `<details>/<summary>` behavior. These conclusions come from source inspection, not a browser interaction test.
- The CSS shows a round outlined plus that changes to a minus, red serif question text, and an indented answer with a pale left border. Although a comment calls it a chevron, the actual CSS draws plus/minus bars. FAQ answers have no source-imposed max-height clipping.
- `docs/DESIGN-SYSTEM.md:194–204` requires entity-specific questions based on actual searches, preservation of superscript citation links as HTML, one authored FAQ block, and no re-escaping of typographic entities. It explicitly documents earlier duplicate-block and lost-citation defects.
- The shared helper preserves citation markup as `aHtml` and maintains a separate text `a`. It escapes plain-text questions and answers. `aHtml` is directly interpolated, so this is a trusted-content pipeline, not a sanitizer.
- The fallback generator only runs on input containing `id="h-faqs"`; it extracts existing substantive paragraphs from matching page headings. Its three-question cap, 40-character paragraph threshold, 700-character text truncation, and generic heading-to-question templates are migration heuristics. They are not a universal content policy or research method. The dosage template is not authorization to recommend doses.

## Renderer differences and actual limits

- `src/components/ArticleView.tsx:188–193` preserves existing authored blocks by checking for `rgbc-faq-block` before fallback generation. But its local older helper at lines 81–124 strips answer HTML/citations. Do not copy that stale local helper as the portable standard.
- `src/components/WpRender.tsx:196–214` imports the better shared helper but lacks the general authored-block guard (only a special `isStop` branch bypasses fallback). The shared `injectFaqs` itself is not idempotent. A repeat render can duplicate a block unless the caller or shared adapter guards it.
- The FAQ helper generates no per-question ID and no fragment-opening code. `WpInteractivity.tsx:77–106` scrolls sidebar section links using a fixed header offset but does not update the URL fragment or open a targeted native detail. Do not claim existing per-question deep links are implemented.
- `ContentAccordions.tsx` explicitly leaves native FAQ details alone; its JavaScript toggles other research-feed accordions. The large legacy WordPress stylesheet and the Supabase/auth handlers are not FAQ dependencies.
- Public rendered text was inspected at [the homepage](https://microbiomemedicine.com/), [Endometriosis](https://microbiomemedicine.com/conditions/endometriosis), and [Metformin](https://microbiomemedicine.com/interventions/metformin). The Metformin extraction showed one sidebar FAQs entry, one FAQs section and three Quick answer items with superscript citation links. This establishes visible page structure at inspection time; it does not establish that the pinned source commit is the deployed build, every route has deduplication, or live native interaction passes.

## Portable reuse recommendation

Reuse the exact native markup structure and the small CSS primitive through one shared FAQ renderer for all applicable post types. Keep page-specific authored questions and source-backed answers as data; preserve existing authored FAQ content instead of regenerating it. Adapt `--color-primary`, `--font-serif`, the answer border and text colors to the new site's design tokens. Native FAQ interaction needs no React, Next.js, Tailwind, Supabase, icon library, images or extra accordion JavaScript; the source project happens to use those elsewhere. Supply consistent box sizing and test theme inheritance.

Emit answer content with a structured safe renderer or an allowlist sanitizer that preserves permitted citation elements (`sup`, safe `a` links and the required citation class/attributes) and normal prose markup. Escape text nodes once. Validate citation targets and allowed link schemes; reject scripts, event handlers and unsafe HTML. Never pass untrusted Grok/Reddit/raw scraped HTML directly to the source helper's `aHtml` interpolation. Keep plain text for metadata consistent with the visible complete answer; do not inherit the helper's text-only truncation as a hidden difference.

The following are **explicit adaptations that complete the reusable behavior**, not features proven in this source: stable per-question IDs; open-on-initial-fragment and hash-change handling; a fixed-header-aware scroll/focus target; and a uniform existing-block guard in the shared renderer. If the site already has question navigation or question chips, bind them to the same canonical FAQ records and inline targets once. Do not create a second repeated set of questions/answers or a parallel FAQ section. The observed Microbiome sidebar has a section-level FAQs entry; this audit did not establish a shared per-question chip system there.

Keep source code in this packet unchanged as provenance. Make any new adapter a separate derivative so the source reference and improvements remain distinguishable. A neutral markup example (placeholders are not article content) is in `framework-neutral-markup.html`.

## Verification expected in a consuming site

Verify one FAQ block per page; preservation of authored answers; genuine citations still clickable; no literal escaped entities; keyboard/mouse/touch disclosure; multiple items open; long answers and citations not clipped; responsive layout; initial and changed URL fragments opening the intended answer; and existing question navigation pointing to the same answer once. These are proposed consuming-site checks, not tests completed by this audit. No site, rule, deployment, research corpus or user-owned task was changed.
