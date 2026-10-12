# Complete blue topic hero set — October 12, 2026

Owner request: create matching hero images for the remaining drug and condition pages on remaprx.com using the existing blue style and metadata setup. See SL-RULE-HERO-ROLLOUT and DESIGN-SYSTEM.md.

## Scope and source

The isolated publication checkout began at live Sites version 26, source `f0d929b67c8c74b23601c59565080729fa6d1f06`. The canonical and discovery route inventory contains 64 topic pages: 32 drugs and 32 conditions. The two approved Metformin/Parkinson originals are preserved and 62 new illustrations extend the same system. Scientific content, source records, evidence grades, authentication, scientific release status and indexing gates are unchanged. PepsAnon is a reference only.

Original transparent PNG masters and exact built-in ImageGen prompts are retained in `assets/hero-art/`. Runtime metadata uses `data/topic-hero-art.json`; the typed image registry derives responsive and social paths from this catalog. Each topic receives a distinct master, descriptive alt/title/caption/description, 512/1024 WebP heroes, 1200×630 social PNG, canonical metadata, Open Graph/Twitter metadata and linked WebPage/ImageObject structured data. No search-ranking result is claimed.

## Verification

- Independent integration review found canonical/discovery merge precedence, all 64 route assignments, the 62-page update-history entry, responsive paths and existing metadata consumers consistent.
- All generated illustrations are visually inspected against the deep-blue background. A second contact-sheet review checks subject suitability, anatomy, text, backgrounds and consistency. A plain torso candidate for breast cancer was replaced by an awareness ribbon for clearer topic recognition.
- Mobile colorectal-cancer hero at 390×844: image loads from the responsive 512 WebP, is 200px wide, and stacks above the title; document width equals viewport width (390px).
- Longest condition title, persistent genital arousal disorder/genitopelvic dysesthesia, at 1024×768: image loads, title wraps, actions remain visible, no horizontal overflow.
- TypeScript passed after the registry refactor. Article navigation validation passed all 68 articles, canonical sections and legacy fragments. Governance validation preserved 236 rule/history/ingest files and the frozen baseline.

Final full asset validation, production build, served metadata checks and publication receipt are appended after completion.

Source reconciliation: while artwork was being created, the live source advanced through internal-link presentation and evidence-grade color/bar updates. The source helper fast-forwarded the isolated checkout to `f4804463e383f0bcf44b9b51fa691056278208dc`; artwork changes were restored and both documentation sections merged, preserving the newer behavior. The rollout uses the unique rule identifier `SL-RULE-HERO-ROLLOUT` to avoid the concurrently assigned link-rule number.

Final prepublication checks: all 64 route assignments, actual rendered topic heroes, unique masters, alpha extrema, dimensions and 256 file hashes passed. Served local checks passed all 64 pages, canonical/Open Graph/Twitter/ImageObject metadata, unchanged noindex/nofollow and 128 hero/social image downloads. Responsive 512 WebP files average 23,285 bytes (range 15,128–41,202); the largest 1024 WebP is 107,712 bytes. Desktop Rituximab and final Breast cancer ribbon also render correctly at 1280px without overflow. Post-reconciliation TypeScript, all 68 article navigation checks, governance integrity and whitespace checks passed. The exporter now compares content hashes when reusing derivatives, so Git timestamp changes cannot invalidate or incorrectly validate the cache.

The production build and reader-boundary verification run as ordered required steps in the Sites packaging workflow; deployment receipt and live HTTP checks follow after publication.
