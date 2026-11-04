# RemapRx visual design system

## Footer layout repair — November 4, 2026

Source: owner's “Fix the footer” request and Screenshot 2026-11-04 at 4.32.24 PM.png. Repair the shared footer's cramped brand/legal copy and unused fifth column. Keep the existing RemapRx mark, blue background, copy and link destinations. With no newsletter, use one brand block plus the three existing navigation groups across the available desktop width; stack the brand above responsive menu columns on smaller screens. Legal links wrap as whole labels with consistent gaps and no orphan separators. Preserve visible yellow keyboard focus and comfortable link targets. This supersedes the inherited five-column allocation and shrinking legal-link row for this layout. Implementation choices are responsive CSS; no evidence, access or release-policy change is included. Verification and publication are recorded in `FOOTER-FIX-20261104.json`.

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

Use shared CSS tokens and `lib/theme/config.tsx`; component states must follow the same roles. Evidence grades use the brand palette defined below; preserve error colors and third-party identity marks where color conveys a distinct meaning. Keep readable text in print. Key measured contrast ratios: white/brand blue 7.29:1, yellow/brand blue 4.66:1, ink/yellow 9.94:1, muted ink/white 6.16:1. Gray is a supplied swatch, not the default text color.

## Illustration feel

Create original, quiet editorial illustrations: one recognizable subject, simple silhouettes, smooth rounded details, limited tonal blue planes and generous transparent space. Use light and mid blues (`#8FA4FF`, `#C5D0FF`, `#E2E8FF`, `#5674E8`, `#3455C8`) against the deep-blue hero. These are art-direction targets; generated pixels may vary. Avoid photographic texture, decorative dashboards, logos, packaging, text baked into art, dramatic lighting and visual claims of efficacy. Yellow belongs primarily to the surrounding interface.

The supplied SVGs establish a feel, not a requirement to copy their exact paths. The first original subjects are two generic unbranded tablets for Metformin and a lateral brain for Parkinson's disease. The tablets do not identify a specific commercial product, formulation, dose or pill imprint; the brain is a topic illustration, not diagnostic imaging. Future drugs and conditions each need an appropriate subject and an explicit canonical page mapping. No automatic reuse of a drug image on an unrelated condition.

## Files and metadata schema

The typed registry in `lib/hero-art.ts` is the source for both rendering and page metadata. Each record requires canonicalPath, src, srcSet, width, height, alt, title, caption, description, encodingFormat and a socialImage record (src, width, height, alt, encodingFormat). Alt text describes visible content succinctly; captions and descriptions identify its page context without keyword stuffing or unsupported clinical claims. Do not invent creator credentials, licenses or scientific review status.

Retain PNG masters in `assets/hero-art/` and deliver alpha-preserving WebP images in `public/art/`, at 512 and 1024 pixels. Use stable descriptive subject filenames. `scripts/export-hero-art.mjs` creates technical derivatives and records dimensions, bytes, transparency and SHA-256 hashes in `assets/hero-art/manifest.json`. Social previews are opaque 1200 × 630 PNGs on deep blue. Do not change artwork by merely altering metadata.

Use a real HTML image with alt, intrinsic dimensions, responsive srcSet/sizes and eager hero priority. The first two topic heroes show artwork in the left panel on desktop/laptop; at narrow mobile widths the image stacks above the title. Use contain, never crop meaningful subject details. Other pages retain their existing illustration until a topic asset is explicitly assigned.

Provide canonical RemapRx URLs, page-specific Open Graph and Twitter images, and ImageObject linked from WebPage.primaryImageOfPage for registered topic images. These fields prepare accurate descriptions for discovery; they do not guarantee search visibility. As of 2026-11-04, public hosts allow crawling, and only pages that pass the metformin-grade bar in `scripts/readiness.mjs` are indexable. Pages below that bar use `noindex,follow`. Remove temporary development-preview metadata from publication.

## References and implementation scope

Consulted the Microbiome Medicine ArticleView, image/hero styles and design-system reference; PepsAnon's peptide hero source and live site; and the owner's supplied images. Keep shared article navigation, citations, source panels and author identity intact. Root design changes supersede the earlier instruction to preserve the old navy/gold palette only within this visual scope. The pinned One Match Rule and reference projects are not edited.

## Verification and release

The color migration was rendered and checked before generating the two topic illustrations. Source-level CSS parsing and key contrast checks passed. Final type/build, governance, source-boundary, image HTTP/metadata and responsive browser checks are recorded in `DESIGN-VALIDATION.md`. Publication is recorded separately from scientific approval. This preserves the initial two-page pass; subsequent authorized expansion is recorded separately.

## Internal link presentation

Owner instruction, October 12, 2026: internal page links display without underlines, including hover, active, visited and keyboard-focus states. Apply the same treatment to internal fragment/citation anchors. Retain link color, native navigation and visible keyboard focus outlines. This supersedes inherited wiki-link and internal-link hover underlines; external source-link styling remains unchanged.

## Evidence-grade colors

Owner correction, October 12, 2026: evidence-grade badges use RemapRx colors. This supersedes the earlier exception preserving inherited teal grade colors. High uses deep blue with white text; Moderate uses brand blue with white text; Low uses a 22% brand-blue tint with ink text; Very low uses pale blue with ink text; Not graded uses the neutral surface and muted ink. Preserve the literal grade labels, assessed/unassessed distinction, grading logic and research-panel interactions. Color changes do not change scientific assessments.


## Owner sketch refinement — October 12, 2026

The owner selected the chunkiness and weight of initial concept 02 as the styling reference, then supplied two hand-drawn Rx sketches to correct the route geometry. The arrow wraps around the entire Rx, rather than only beneath it. One supplied sketch continues the lower-right stroke of the x into the enclosing arrow; the other uses a separate open circular arrow with a gap near the upper right. Preserve both as comparison options until the owner selects the final shape.

The two faithful vector drafts, wordmark and small-size previews are in `assets/brand-concepts/sketch-round-2/`. These supersede the underswoop-only interpretation for this refinement. They do not constitute final logo approval. Preserve the existing blue/yellow palette. Site-wide identity integration, favicon production and publication remain pending the choice; unrelated implementation remains paused while the logo is clarified.

Owner follow-up, October 12, 2026: add the screenshot's three ascending strength bars before evidence-grade labels. High fills three, Moderate two, Low one, Very low zero; Not graded omits the strength icon to distinguish unassessed evidence. Bars inherit the badge foreground against the established blue backgrounds (white on dark blue, ink on pale blue); unfilled bars are subdued. Keep the labels and mark redundant bars decorative for assistive technology.

## Remaining topic illustration rollout — October 12, 2026

The owner requested matching hero images for all remaining drug and condition pages, using the accepted blue style and metadata. This expands the first two-page pass to the entire current canonical route inventory, including discovery entries for Tadalafil and Aging & longevity. The merged registry contains 32 drug and 32 condition pages; 62 new originals join the two approved masters. The implementation uses a distinct asset for each topic, with generic medication forms for drugs and neutral anatomy or topic imagery for conditions. These are editorial illustrations, not photographs of commercial products, diagnostic images or treatment claims. PepsAnon remains outside this rollout.

`data/topic-hero-art.json` is the public descriptive catalog. `lib/hero-art.ts` derives the typed rendering, responsive files and social records from it. Internal generation records and exact prompts remain in `assets/hero-art/*-generation.json`, separate from runtime metadata. `scripts/build-hero-catalog.mjs` requires every canonical drug and condition page to have an explicit assignment and rejects duplicate or unknown routes. Its `--partial` option is for local work in progress only. Final publication requires complete coverage.

Run the catalog builder, exporter and `scripts/check-hero-art.mjs` in order after creating artwork. Retain original alpha and compositions; technical resizing and PNG/WebP exports use the existing pipeline. The validator checks every rendered topic, all file dimensions, actual transparency and hashes, unique masters and descriptive metadata. Record responsive browser checks and the exact deployment in `HERO-ROLLOUT-VALIDATION.md`. Existing layout, navigation, scientific content, access and indexing gates remain in force.

## Author ORCID and Page Snapshot

Owner instruction, October 12, 2026, with the Microbiome Medicine author/snapshot screenshot: display only the official green ORCID iD logo beside the author name, linked to that author's canonical ORCID record. Retain an accessible name, keyboard focus, the verified identity and the biography interaction. Do not display the long identifier as hero text or place the link inside the biography button.

The hero card is labeled Page Snapshot. Drug pages show studies referenced and conditions investigated; condition pages show studies referenced and drugs investigated. Counts are page-scoped and recomputed from public canonical data. Count cited primary research, including laboratory and disputed reports, rather than every background reference. Group explicit family identities and identical DOI/PMID records; a multi-family synthesis does not merge its studies. Where no shared identity is recorded, a distinct primary record remains separately counted. Do not claim independent-trial verification.

Count distinct opposite-type entities supported by an explicit synthesis pairing with a cited primary source, or an existing canonical candidate relationship supported by primary-cited investigation prose/mechanisms or a primary study shared by both profiles. Bare candidates, related-reading links, uncited sources, safety-only mentions and original-use labels do not add investigations. Keep broad canonical entity boundaries; do not invent new medical mappings from similar wording. The information control explains the count and lists included linked entities. Zero is a page-coverage count, not a claim that no research exists. Other article types show the study count without an invented drug/condition metric.

Implementation: `lib/page-snapshot.ts`, `components/page-snapshot.tsx`, shared article/author rendering and CSS. Reference: Microbiome Medicine `OrcidIcon.tsx`, `ArticleView.tsx` and `PageSnapshot.tsx`; PepsAnon reference remains separate. The existing brand palette, scientific values and release gates are preserved.


## Simplified Rx target preview — October 12, 2026

The owner supplied a new Rx/target/direction-arrow screenshot and requested the simplified version in blue on white, with a blue-on-yellow favicon shown before application to the site. This becomes the active refinement direction, superseding the earlier two enclosing-arrow alternatives as the immediate comparison task. Preserve the heavy Rx weight; retain one open outer arc and a flat arrow. Remove the inner ring, crosshair ticks, diagonal connectors and shading. Use the adopted blue `#1736F5` and yellow `#FFC709`. Give the favicon a thicker arc and larger arrow gaps for small-size readability.

Editable vector drafts, white-background rendering, square favicon exports and the comparison sheet are in `assets/brand-concepts/target-round-3/`. The sheet includes actual 16/32-pixel samples against light and dark surroundings. This is a review preview, not final identity approval. No site identity, metadata or public favicon is changed by this work; application and publication await the owner's assessment of the shown preview. Earlier concept files remain preserved.

## Glossary hero illustration pilot — October 12, 2026

Owner request: “Glossary pages need images. Hedgehog Pathway should be your first attempt.” Extend the existing blue hero and metadata conventions to explicitly registered glossary entries, starting with `/glossary/hedgehog-pathway`. This pilot covers one entry; remaining glossary illustrations are not yet assigned. Keep complete coverage of the 64 drug/condition pages while treating glossary artwork as individual assignments.

Hedgehog pathway uses a conceptual membrane-to-nucleus cell-signaling illustration, based on the existing glossary definition and its NCI reference. Keep the restrained blue palette, transparent background, generous margins and small-screen legibility. Avoid an animal pun, invented molecular labels or activation states, and treatment-benefit imagery. Retain exact generation prompts separately from public metadata. The image conveys a glossary concept; it is not a complete molecular mechanism diagram.

Use the same master/WebP/social exports, alt text and canonical/OG/Twitter metadata. Registered glossary pages must also emit the shared WebPage/ImageObject structured data. Preserve the glossary prose, citations, source access and all release gates. Verification and publication are recorded in `GLOSSARY-HERO-PILOT.md`.


## Mapping meaning restored — October 12, 2026

Owner correction after reviewing the simplified preview: it lost the mapping visual. Keep the map/target detail even when it diminishes at favicon size; bring R and x closer together and restore the “x marks the spot” idea. This supersedes the prior instruction to remove the inner ring, crosshairs and radial connectors. The x should sit at the target center, with concentric open rings and registration marks making the mapping concept visible. Preserve heavy letters, the flat arrow and the adopted blue/yellow colors. Small-size stroke adjustments may strengthen the design but must retain the mapping features.

The updated blue-on-white logo and blue-on-yellow favicon previews are in `assets/brand-concepts/mapping-round-4/`, alongside editable SVGs and actual 16/32-pixel inspection samples. This remains a preview for owner assessment before site application; earlier drafts are retained. No production identity or deployment changed.

## Complete glossary illustration set — October 12, 2026

Owner request: “Let's create matching images for the remaining glossary pages, using the same blue style and metadata setup.” Extend the approved Hedgehog pilot to the other 20 current glossary entries, giving all 21 their own illustrations. This supersedes the glossary pilot's opt-in coverage limit. The complete catalog must cover all current drug, condition and glossary routes (85 at adoption); retain the 65 accepted images unchanged.

Use the existing definitions to choose restrained conceptual subjects: cellular and microbial forms for biological terms, simple visual metaphors for trial and statistical concepts. Do not invent precise protein structures, measured estimates, clinical effects or authoritative labels inside the artwork. Alt text describes the actual visible subject. Retain exact built-in ImageGen prompts and original PNG masters, and export the same responsive WebP/social PNG derivatives with canonical/OG/Twitter/ImageObject metadata. Existing scientific prose, citations and release gates remain unchanged. Verification: `GLOSSARY-HERO-ROLLOUT.md`.


## Approved RemapRx atlas identity — October 12, 2026

The owner approved the mapping-round-4 Rx mark and authorized its logo/favicon application and the category-claiming homepage to go live. Preserve the close heavy Rx, open concentric target rings, crosshairs, radial connectors and flat arrow; retain mapping features even at favicon size. Blue on white is the header identity, reversed white on blue the footer, and blue on yellow the favicon. The hero repeats this map geometry with distinct established/investigated routes and readable research-type labels. Category is “The drug repurposing atlas”; headline is “New targets for approved medications.” Replace current reader-facing Second Look branding and the old familiar-drug headline while preserving historical records, routes and existing topic illustrations. Contract, exact copy, production assets, scope and verification/release: `REMAPRX-IDENTITY.md`. This supersedes the preview-only status and the over-simplified round-3 design.


## Hero sidebar alignment — November 4, 2026

Owner request, with Screenshot 2026-11-04 at 4.31.04 PM.png: the dark illustration and author sidebars in topic heroes must have the same widths and vertical boundaries as the article sidebars below. Use one shared responsive column definition for both grids: the existing reading-grid columns above 1199px, and 220px / flexible center / 260px from 992px through 1199px. Stack the hero only below the reading grid’s 992px desktop breakpoint. Preserve the existing tablet/phone illustration, author, snapshot and reading order. This supersedes the independent 25%-left/280px-right hero columns and its earlier 1199px stacking threshold.


## Footer legal-link separation — November 4, 2026

Source: owner's follow-up and Screenshot 2026-11-04 at 7.09.38 PM.png: Privacy, Terms and Educational disclaimer are cramped against the paragraph above. Give the shared legal-link group its own 1.25rem top margin at every viewport. This supersedes the flush paragraph/link adjacency while preserving the accepted responsive columns and intact labels. Implement and publish under the standing routine-fix authorization. Verification/publication: `FOOTER-LEGAL-SPACING-20261104.json`.
