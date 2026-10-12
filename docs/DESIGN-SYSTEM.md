# RemapRx visual design system

Adopted 12 October 2026 from the owner's palette05.png, ten supplied health-topic SVGs, and Examine brain-hero screenshot. This is the RemapRx implementation contract. The illustration conventions are reusable for PepsAnon; this change does not migrate or publish PepsAnon. Existing scientific content, evidence semantics, account access and release gates remain in force.

## Color roles

| Role | Color | Use |
| --- | --- | --- |
| Brand blue | `#1736F5` | Article hero center, brand links, active controls |
| Yellow | `#FFC709` | Primary accent, calls to action, focus against dark blue |
| Gray | `#808080` | Decorative neutral; not small body text on white |
| Light gray | `#DEDEDE` | Dividers and neutral borders |
| Deep blue | `#1027B8` | Hero illustration and author panels, footer |
| Pale blue | `#EFF2FF` | Tinted surfaces and text on deep blue |
| Ink | `#17204D` | Body text and text on yellow |
| Muted ink | `#5B6175` | Secondary readable text |
| White | `#FFFFFF` | Reading surface and text on blue |

Use shared CSS tokens and `lib/theme/config.tsx`; component states must follow the same roles. Preserve scientific grade colors, error colors and third-party identity marks where color conveys a distinct meaning. Keep readable text in print. Key measured contrast ratios: white/brand blue 7.29:1, yellow/brand blue 4.66:1, ink/yellow 9.94:1, muted ink/white 6.16:1. Gray is a supplied swatch, not the default text color.

## Illustration feel

Create original, quiet editorial illustrations: one recognizable subject, simple silhouettes, smooth rounded details, limited tonal blue planes and generous transparent space. Use light and mid blues (`#8FA4FF`, `#C5D0FF`, `#E2E8FF`, `#5674E8`, `#3455C8`) against the deep-blue hero. These are art-direction targets; generated pixels may vary. Avoid photographic texture, decorative dashboards, logos, packaging, text baked into art, dramatic lighting and visual claims of efficacy. Yellow belongs primarily to the surrounding interface.

The supplied SVGs establish a feel, not a requirement to copy their exact paths. The first original subjects are two generic unbranded tablets for Metformin and a lateral brain for Parkinson's disease. The tablets do not identify a specific commercial product, formulation, dose or pill imprint; the brain is a topic illustration, not diagnostic imaging. Future drugs and conditions each need an appropriate subject and an explicit canonical page mapping. No automatic reuse of a drug image on an unrelated condition.

## Files and metadata schema

The typed registry in `lib/hero-art.ts` is the source for both rendering and page metadata. Each record requires canonicalPath, src, srcSet, width, height, alt, title, caption, description, encodingFormat and a socialImage record (src, width, height, alt, encodingFormat). Alt text describes visible content succinctly; captions and descriptions identify its page context without keyword stuffing or unsupported clinical claims. Do not invent creator credentials, licenses or scientific review status.

Retain PNG masters in `assets/hero-art/` and deliver alpha-preserving WebP images in `public/art/`, at 512 and 1024 pixels. Use stable descriptive subject filenames. `scripts/export-hero-art.mjs` creates technical derivatives and records dimensions, bytes, transparency and SHA-256 hashes in `assets/hero-art/manifest.json`. Social previews are opaque 1200 × 630 PNGs on deep blue. Do not change artwork by merely altering metadata.

Use a real HTML image with alt, intrinsic dimensions, responsive srcSet/sizes and eager hero priority. The first two topic heroes show artwork in the left panel on desktop/laptop; at narrow mobile widths the image stacks above the title. Use contain, never crop meaningful subject details. Other pages retain their existing illustration until a topic asset is explicitly assigned.

Provide canonical RemapRx URLs, page-specific Open Graph and Twitter images, and ImageObject linked from WebPage.primaryImageOfPage for registered topic images. These fields prepare accurate descriptions for discovery; they do not guarantee search visibility. The existing noindex/nofollow and robots disallow gates remain unchanged pending the separate scientific/indexing release decision. Remove temporary development-preview metadata from publication.

## References and implementation scope

Consulted the Microbiome Medicine ArticleView, image/hero styles and design-system reference; PepsAnon's peptide hero source and live site; and the owner's supplied images. Keep shared article navigation, citations, source panels and author identity intact. Root design changes supersede the earlier instruction to preserve the old navy/gold palette only within this visual scope. The pinned One Match Rule and reference projects are not edited.

## Verification and release

The color migration was rendered and checked before generating the two topic illustrations. Source-level CSS parsing and key contrast checks passed. Final type/build, governance, source-boundary, image HTTP/metadata and responsive browser checks are recorded in `DESIGN-VALIDATION.md`. Publication is recorded separately from scientific approval. Future illustration expansion and the PepsAnon rollout remain outside this first two-page pass.

## Internal link presentation

Owner instruction, October 12, 2026: internal page links display without underlines, including hover, active, visited and keyboard-focus states. Apply the same treatment to internal fragment/citation anchors. Retain link color, native navigation and visible keyboard focus outlines. This supersedes inherited wiki-link and internal-link hover underlines; external source-link styling remains unchanged.
