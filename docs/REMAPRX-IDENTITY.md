# RemapRx identity and atlas homepage

## Approved direction

October 12, 2026: the owner approved `assets/brand-concepts/mapping-round-4/`, requested application of that logo and favicon, and explicitly authorized publication of the identity and homepage category claim. The owner prioritizes the mapping meaning over perfect minification. Preserve the close heavy Rx, concentric open rings, crosshair marks, radial connectors and flat direction arrow. The x sits at the target center. The earlier simplified round 3 is superseded, not selected.

Category: **The drug repurposing atlas**. Tagline: **RemapRx: Mapping new targets for approved medications.** Promise: make the evidence behind each connection understandable and traceable. No open-source claim or unsupported competitor comparison.

Homepage copy:

- Eyebrow: “The drug repurposing atlas”
- Headline: “Mapping new targets for approved medications.”
- Supporting copy: “Explore how existing medications are being studied for new uses. Follow the proposed mechanisms, examine the findings, and map each connection to its sources.”

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


### Publication receipt — October 12, 2026

Published as Sites version 34, source `a4dc664fd2644d9c4d46d6846d9a546bdf4b8c4c`, saved version `appgprj_6ac734459a508191a425263c7645a0be~appgver_9adfb5d53bd08191bfda711110250af5`. Deployment `appgdep_6acce58359408191a60c223d56d142db` succeeded at 13:50:33 UTC. Custom domain: https://remaprx.com. The generated Sites hostname remains `https://second-look-evidence.kmfp.chatgpt.site`; it is a preserved hosting identifier, not reader-facing branding. Local tar SHA-256: `ba99cf0002421f23d617c55b13af446e74a71cb3d9a60799a6d3311bf20295ae`. Sites archive-storage content hash: `3773c4bb17b3d4807fa506772cd73294a6947a01e061560a9d885efb1a1cfc23`.

The final production rebuild and 30 built public-payload boundary checks passed. Live verification passed seven representative pages and seven identity assets, including byte-for-byte SVG/ICO/touch-icon/wordmark comparisons, new category copy and absence of current Second Look branding. Live robots/noindex behavior is preserved. The live browser confirms the new title, logo, headline and complete mapping hero at 1440 pixels with no horizontal overflow. Screenshots and machine-readable local/live verification receipts are in the parent workspace `artifacts/remaprx-identity/`.

Bounded code/assets were applied to the canonical `second-look-navigation` working tree after a clean patch check; concurrent edits were preserved, documentation was appended and marketing hashes were recomputed locally. This completes the requested identity/homepage release. The earlier source-linked mechanism/preliminary-evidence work remains separate pending work.


Local integration note: the broad TypeScript command in the dirty canonical working tree also scans preexisting copied source files under `research/batches/RRX-INGEST-001/app-inputs/`, whose adjacent modules are absent. It reports missing-module/implicit-any diagnostics in those handoff snapshots. These snapshot files were not included in the published checkout, whose full TypeScript check passed. No research snapshot or compiler configuration was edited to silence them. A separate application-only diagnostic pass excludes those copied handoff source roots; its result is recorded below.

Application-only integration diagnostics passed with 12 copied research handoff source files excluded; the published checkout passed the normal full TypeScript command. The live homepage browser reported no captured console errors or warnings. Both task-owned local preview servers were stopped after publication.


### Brand vocabulary correction — October 12, 2026

Owner correction: use “and map each connection to its sources” in the hero. Map, mapping and remap are the preferred vocabulary for current brand copy. This supersedes the earlier “trace each connection” hero wording. The About description, Open Graph/Twitter descriptions and default social artwork use the same mapping language. Scientific source-traceability terms and historical records retain their precise meanings. This is a copy-only correction; publication and verification are recorded below after completion.


Mapping-copy publication: Sites version 35, source `70c19536f84d40153053cb4607a752dbad901c15`, saved version `appgprj_6ac734459a508191a425263c7645a0be~appgver_af7ab1f07d648191b22b56a9374221fe`. Deployment `appgdep_6acceb2643ec81918ad299fff1d2073a` succeeded October 12, 2026 at 14:14:23 UTC. Production build, governance and 30 built public-payload checks passed. The live browser at https://remaprx.com confirms the exact new hero clause and matching Open Graph/Twitter descriptions, with noindex/nofollow preserved. Copy changes and the regenerated social image were applied to the canonical working tree with bounded replacements; concurrent work remains intact. Receipt and live screenshot: parent workspace `artifacts/remaprx-map-copy/`.


### Mapping headline correction — October 12, 2026

Owner follow-up: “why not mapping new targets for approved medications.” Adopt “Mapping new targets for approved medications.” as the homepage headline and matching brand tagline. This supersedes “New targets for approved medications.” in current copy. Apply the wording to the footer, page descriptions, social-image description and default social artwork. Preserve prior publication receipts. Implementation is a bounded copy change. Governance passed; the updated homepage headline and footer were verified in the local browser, with readable wrapping at 1280 and 390 pixels. The regenerated social image was visually inspected. Production build, public-payload validation and publication passed; see the receipt below.


Mapping-headline publication: Sites version 39, source `9750e7a59486527f8ec18bf17c79a074421bbaf8`, saved version `appgprj_6ac734459a508191a425263c7645a0be~appgver_41e0fa8336548191841c56e648ec6c4f`. Deployment `appgdep_6acd1ebe6f148191bd5cde37a1d30b52` succeeded October 12, 2026 at 17:54:30 UTC. Governance, production build and 36 built public-payload checks passed. Local browser verification confirmed readable wrapping at 1280 and 390 pixels; the social image was visually checked. The live browser at https://remaprx.com confirms the new H1 and footer after refresh. Existing public audience is preserved. Exact receipt: parent workspace `artifacts/remaprx-mapping-headline/publication.json`. Bounded copy, artwork and contract changes are synchronized to the canonical working tree; concurrent work is preserved.


### Favicon optical centering — October 14, 2026

Owner request: center the heavier Rx lettering in the favicon and offset the lighter circle to the right. This supersedes centering the complete target artwork within the square favicon. Scope: SVG favicon, ICO at 16/32/48 pixels and matching touch icon; header/footer symbols, wordmarks and social artwork keep their approved framing. The generator applies a favicon-only `translate(103.49 76.4) scale(.86)` transform: the Rx bounds (44–413, 148–372) have their midpoint at (300, 300), with the target center to the right and all outer marks inside the 600-pixel canvas. Preserve blue/yellow colors and target details. Increment icon URL versions so browsers request the revised assets. Verification: SVG/ICO structure and 16/32/48-pixel raster outputs checked; before/after and native-size previews visually inspected; governance and TypeScript passed. Production build passed; publication pending.
