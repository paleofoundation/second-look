# RemapRx identity and atlas homepage

## Approved direction

October 12, 2026: the owner approved `assets/brand-concepts/mapping-round-4/`, requested application of that logo and favicon, and explicitly authorized publication of the identity and homepage category claim. The owner prioritizes the mapping meaning over perfect minification. Preserve the close heavy Rx, concentric open rings, crosshair marks, radial connectors and flat direction arrow. The x sits at the target center. The earlier simplified round 3 is superseded, not selected.

Category: **The drug repurposing atlas**. Tagline: **RemapRx: New targets for approved medications.** Promise: make the evidence behind each connection understandable and traceable. No open-source claim or unsupported competitor comparison.

Homepage copy:

- Eyebrow: “The drug repurposing atlas”
- Headline: “New targets for approved medications.”
- Supporting copy: “Explore how existing medications are being studied for new uses. Follow the proposed mechanisms, examine the findings, and trace each connection to its sources.”

## Implementation

The approved blue `#1736F5` mark appears on white in the shared header and in white on the blue footer. Outlined Inter lettering accompanies the symbol. The favicon uses the approved blue-on-yellow `#FFC709` design with all mapping features retained and strengthened strokes. `scripts/build-brand.mjs` reproducibly builds editable SVG symbols/wordmarks, an SVG favicon, a 16/32/48-pixel ICO, a 180-pixel touch icon, and the default social image. `assets/brand/remaprx-lettering.json` contains outlined glyphs from the existing licensed `public/fonts/Inter-Regular.woff2`; rendering requires no remote font service. Public assets are in `public/brand/` and the conventional favicon/touch-icon paths. Metadata version-qualifies icon URLs to refresh prior browser caches.

`components/remapping-map.tsx` replaces the paper/lens art with a generic approved-medication hub and established/investigated destinations. The illustration repeats the approved target rings, crosshairs and x marks. Solid and dashed routes, HTML destination labels, an evidence key (human, animal, laboratory/in vitro, computational) and a visible caption distinguish connection types without color alone. The map is conceptual, not a claim about an actual drug–condition pair. The hero stacks on narrow screens, keeps artwork uncropped, and retains search and quick links.

Approval language is specific: approval for one use does not establish safety or effectiveness for another. Reference: [FDA explanation of unapproved use](https://www.fda.gov/patients/learn-about-expanded-access-and-other-treatment-options/understanding-unapproved-use-approved-drugs-label), inspected October 12, 2026. Existing detailed disclaimers remain in force.

Reader-facing Second Look branding is replaced in the shared shell, breadcrumbs, metadata/site descriptions, About/editorial/disclaimer copy, search tool description, guide presentation and missing-page view. Stable identifiers, routes, export filenames, historical records, published PDF editions and the existing drug/condition/glossary illustrations remain unchanged. Guide marketing hashes change with shared copy; product approval/release fields are preserved.

## Integration and scope

Started from live Sites version 33, source `b0a05596eb665f479bddb9f7517d1a8253f0877f`, in isolated `remaprx-identity-live` on `codex/remaprx-identity-live`. Existing 85 topic/glossary images, author ORCID, Page Snapshot, grade bars and link treatment are preserved. Source comparison used Microbiome Medicine's `SiteHeader.tsx` and design system, PepsAnon's `components/peptide/header.tsx` and live reference tab, plus the currently adopted shared shell. Current owner requirements govern the new identity.

This release implements the owner's latest identity/homepage instruction. Earlier preliminary-evidence and metformin–sarcopenia mechanism work remains separate unfinished work in `remaprx-atlas`; it is not represented as complete or silently included in this visual release. No new extraction, mechanism mapping, clinical count or certainty change is made here.

Public Sites audience, D1/R2 bindings, account/access behavior, noindex/robots settings, scientific review status and commercial release gates are preserved. Publication authorization is explicit; another logo approval is not required.

## Verification and release

Completed before publication: approved-symbol geometry preserved; SVG/ICO validation; native 16/32-pixel samples inspected on light and dark backgrounds; outlined header logo inspected; content, reader-identity/source closure, article navigation, evidence rendering/grades and TypeScript checks pass. React review found no added hooks, data requests or effect listeners; static map components remain top-level, decorative SVGs are hidden from assistive technology, HTML labels provide meaning, and link names remain accessible.

Browser: 390-pixel layout has no horizontal overflow; artwork stays within the figure. Mobile menu opens with Enter and closes with Escape, restoring focus to its trigger. Homepage search for `metformin` navigates to `/search?q=metformin` and displays 37 matching items. Desktop (1280 and 1440 pixels), tablet (768 pixels) and mobile (390 pixels) were visually inspected, with no horizontal overflow. The complete figure and approval note remain in the page flow; desktop uses two columns and tablet/mobile stack. Desktop Drugs navigation opens with Enter and closes with Escape, restoring trigger focus. Search returned 37 matching items. Existing citation/navigation/all-profile checks, wiki-link validation and production build passed. Final packaging rebuild, built public-payload check and exact publication receipts follow after completion.
