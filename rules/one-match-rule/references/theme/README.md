# One Match source theme

Start with the [packaged implementation releases](releases/README.md) when their verified scope fits the destination. They include the actual reusable site components and guide renderer; host services and remaining acceptance gates are explicit. The historical source kit below remains the provenance reference.

Use Microbiome Medicine's actual application as the **base theme**, then apply the named PepsAnon refinements and current One Match corrections. A new topic changes configuration, data and assets. It must not trigger another design exercise or a rewrite of shared markup.

This packet is a **verified source kit for extraction**, not yet a compiled, dependency-complete installable theme. The builder must produce that reusable theme as a build deliverable, verify it, and reuse it on subsequent sites. Existing FAQ/table/review packets supplement this kit; they cannot establish whole-theme completeness by themselves.

## Source and active rendering paths

- Base: `paleofoundation/microbiomemedicine`, commit `28ed85b6d510dfddf1720775b456771c7dc62763`. The manifest pins every included file to its Git blob and SHA-256. Original reference files retain source names/content; they are not destination settings or new governing instructions.
- Root shell: `src/app/layout.tsx` imports `globals.css` followed by `src/styles/theme-wp.css`, injects `HEADER_HTML`/`FOOTER_HTML` from `src/theme/themeHtml.ts`, then wires shared interactions. **Do not substitute the simpler, inactive SiteHeader/SiteFooter alternatives.** Preserve stylesheet order/cascade when extracting tokens.
- Home: `src/app/page.tsx` → `components/home/HomePage.tsx` and its CSS module. `src/theme/homeMain.ts` is another historical capture, not the active home entry.
- Articles: `ArticleView.tsx` → captured `wp_render.html` through `getWpHtml`/`WpRender`, otherwise its native fallback. `ResearchFeedView` also has captured and native paths. Inspect the actual route, not only the fallback code.
- The design document ranks `_migration/endo-live.html` and `x-cond.html` highly, but the pinned repository tree does not include `_migration/`. Captured per-page database HTML and binary assets are not bundled. Recover required layout evidence from the authorized source/export or a dated rendered reference, with provenance; do not claim missing captures were supplied. A captured reference is layout evidence, not destination research content.
- PepsAnon overlays: packaged evidence table/research panel plus the included homepage/brand source. The exact selected source version and each overlay must be recorded. Existing destination source, accounts and research are preserved through the migration.

## One reusable implementation

Create a versioned shared theme package/module with documented install/build commands, dependencies, assets, configuration schema and content/service adapter interfaces. Use the source markup, class relationships, CSS, typography, geometry and interaction code as the starting implementation. Extract the presentational dependency closure, not the entire old database/backend. Preserve the active theme's header/desktop menus/mobile navigation, footer, home, directories/search, article shells and rails, author presentation, glossary, research pages, account/profile/library and applicable product layouts.

Keep these layers separate:

1. **Shared theme:** global layout/CSS/font roles, reusable components, interactions and responsive rules. No topic-specific branching in the core.
2. **Site configuration:** identity/domain, main/accent/pale-accent and semantic tokens, logo/hero assets, assigned author profiles, navigation/taxonomy labels, post-type mapping, configured offers/access policy. Changing these must not require editing shared component markup.
3. **Canonical content:** topic entities, conditions, outcomes, citations, FAQs and reviews, with actual provenance and scientific state. Research cannot be synthesized by swapping labels on old content.
4. **Host adapters:** routing/link/image handling, search queries, authenticated session/intake, saved library, profile, review authorization, storage and any future commerce. Use supported infrastructure while preserving the visible journey and real functionality.

Before accepting a first extraction, save its usable package and a reproducible export. Subsequent One Match builds first locate the latest verified theme release and supply configuration/adapters/data, applying versioned migrations when needed. If only this source kit is available, perform and record the initial extraction once; do not call the kit an already working theme. Avoid repeated bespoke copies and patch series for each new site.

## Precedence and scoped overlays

Current explicit owner instructions and actual platform constraints govern. Existing scientific, accessibility, privacy/security and access requirements remain mandatory. Preserve the destination's chosen identity/data/author/audience unless explicitly changed. Apply the following scoped refinements over the Microbiome base; retain the base elsewhere.

| Surface | Required overlay |
|---|---|
| Homepage | PepsAnon composition and master §9: dominant main-color field, helpful topic art using accent/pale counterpart, warm ivory for yellow; keep artwork recognizable on mobile |
| Authored article shell | PepsAnon hero/Page Snapshot refinement and master §7 universal post-type rails; required real author portrait and hover/focus/touch bio in the right-hand hero section; every ORCID display uses the small green iD logo, visible identifier and verified individual link through one shared renderer; preserve stacked mobile access and remove duplicate body-sidebar author blocks |
| Evidence table and on-demand research | PepsAnon semantic table and right modal panel, with visible synthesis fields and corrected grades, counts, dates and focus handling |
| Second Look Evidence composition | One shared Evidence section begins with visible interpretive prose and ends with the compact three-column Outcome and study design / Grade / Evidence table. Preserve existing authored Benefits/Results/Evidence prose; keep full row findings, magnitude and limits in its matching right research panel. Outcome and source-count controls both open that panel. Preserve honest certainty, canonical counts, generated/imported inheritance, citation reading order and compatibility fragments without restoring a separate early findings view. |
| FAQs/reviews/citations | Microbiome presentation, populated question map, stable accessible inline disclosure, citation-safe rendering, substantive Q01–Q15 review mapping and exactly one Research catalogue |
| Accounts and products | Preserve source journey through destination services; master free authenticated reviews, persisted editable role intake, private saved library, and separate My guides; no automatic billing |
| PepsAnon peptide/stack detail pages | Omit the Connections body section and matching desktop/mobile section-navigation entry; keep this scoped override in shared contracts and generators. Preserve useful inline/component/context links, relationship data and the separate research overlay. Existing other sites/post types keep their adopted related-content design. |
| Topic-specific modules | Map to the equivalent semantic entity/condition/outcome/relationship data; omit only genuinely inapplicable modules with reasons, not required functions because data is unfinished |

Record each adaptation's source/hash, destination, reason and verification. Valid reasons are a specific owner/current-rule override, semantic topic mapping, a demonstrated defect, accessibility/security correction, or a verified host incompatibility. “Looks cleaner,” a preferred UI library and “new topic” do not justify replacing the design system. Preserve Inter/Lora roles, source scale/width/spacing/borders/icon treatment and breakpoints unless a documented reason changes that exact property. Do not copy source colors, people, logos, content, pricing, historical claims or site URLs as universal values.

## Required manifests and dependency treatment

Before dependent theme implementation, resolve and give workers an accessible immutable source/theme release and these records (equivalent durable formats are fine):

- `theme-manifest.json`: base repository/commit, package version/hash, overlay versions, all applicable route families/templates and their source rendering paths.
- `theme-dependencies.json`: local imports, style cascade/tokens/fonts, icons/media, packages and runtime services. Each is included, mapped to a verified destination adapter, intentionally excluded with reason, or unresolved. No unexplained missing dependency may pass.
- `theme-overrides.json`: source-to-destination mapping, narrow reason, affected tokens/templates/states and proof for every departure.
- `site-theme.config.*`: validated topic/brand/author/navigation settings and service/content bindings, with no secrets or source account data.
- `theme-acceptance.json`: exact version, reference/destination screenshots by route/state/width, interaction results, independent review and unresolved work. Separate source readiness, theme parity, research completeness and release status.

The included manifest records this kit's known boundaries. `researchFeedCategories.ts` is omitted topic data and must be supplied by a destination category adapter. `wp_render` captures, fonts/media and services need deliberate resolution. Do not hotlink stale source assets or depend on the old site's data/auth backend. Never copy cosmetic AccessGate/full-body blur, auto-confirmed signup, anonymous full-review policies or the abstract-seeding generator as production behavior. Preserve required error/loading/empty states and do not expose old identities/content while testing a new topic.

## Acceptance: a theme, not a resemblance

First compare actual reference and destination pages at approximately 320, 390, 768 and 1280px for every unique applicable template. Match shell, menu/footer, typography, width/spacing/density, article hero/rails, directories/search, FAQs/tables/panels/reviews, author and account layouts, allowing only recorded overlays. A generic shell containing three copied widgets fails.

Exercise navigation/search/filter/back/reload, section/citation links and disclosures, both table panel openers, close/focus/scroll, author controls, login→intake→requested review, persisted save/library/profile and applicable guide journeys. Check real service results and server payload protection. A visual button with no service is incomplete.

**Topic-swap proof:** render a second clearly synthetic topic using the same theme package and a different configuration/fixture dataset, without editing shared markup/styles or scientific policy. Keep fixtures private and out of production indexes. Verify that source branding, authors, topic labels and evidence do not leak, while all applicable shells/interactions remain. This tests reusability; it does not create a second real site or fabricate research.

**Repeat-run proof:** importing unchanged configuration/content causes no duplicate layouts/FAQ/catalogues or source edits. Verify generated/ingested/alternate routes inherit the same theme. Save the verified reusable artifact, install instructions and version so the next topic can consume it. Report any necessary bespoke change as a classified rule/theme gap, not a silent workaround.

## Required v1.19 product/theme corrections

Implement the master's demand-ranked topic/entity megamenu with clear text triggers, neutral reader-facing groups and accessible grouped mobile navigation. Owner/editorial selection provenance stays private and must not leak through configuration serialized to the browser. Add the [consumer-guide contract](../consumer-guides.md): product/edition/offer configuration, storefront/preview, private My guides, subscription and independent-purchase rights, and a reusable manuscript/PDF renderer. Prove the same code handles a second synthetic topic. These are explicit corrections/extensions of the source theme; do not attribute them to the captured historical source. Reader-confidence cells must explain their actual outcome and limits; repeated workflow labels cannot substitute for synthesis.

Every drug article inherits Mechanisms → Mechanism of Action through the shared typed content/section contract. Preserve original-use and condition-specific source mapping, scientific uncertainty and primary/context distinctions. Use a reader-safe projection for navigation, products, article data and exports; do not expose owner preferences or internal worker/ingest commentary. See [the mechanisms and reader-copy contract](../mechanisms-and-reader-copy.md).

## Parent scope and primary directory inheritance

The shared navigation/configuration and content adapters must enforce the [parent-topic and directory contract](../topic-scope-and-directories.md). Expose the site's named primary collections as first-level desktop/mobile choices with complete directories. Build broad parents from the canonical coverage graph; scoped pilot/ingest content cannot silently become the whole parent. Repeated generation and a second-topic configuration-only proof must preserve these properties. Route existence, menu component availability and a populated title/table alone do not establish acceptance.
