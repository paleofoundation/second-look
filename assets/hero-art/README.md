# Original blue hero illustrations

Created on 12 October 2026 for RemapRx using the built-in image-generation tool, after the new palette rendered successfully. The owner supplied ten flat purple health-topic SVGs, a brain-hero screenshot, and palette05.png as visual references. No supplied reference asset is embedded in the published site.

Masters retain the generated alpha channel. `scripts/export-hero-art.mjs` creates browser derivatives, social PNGs and a manifest. See `docs/DESIGN-SYSTEM.md` for the reusable design/metadata contract and `lib/hero-art.ts` for canonical page assignments. Masters are source assets, not public route files.

Reusable brief: a single, original, recognizable medical editorial subject; flat silhouettes and smooth rounded contours; restrained tonal blues #8FA4FF, #C5D0FF, #E2E8FF, #5674E8 and #3455C8; transparent background intended for #1027B8; generous margins; legible at 200px. No brand marks, embedded text, photorealism or visual efficacy claim. Metformin uses two generic oblong tablets with a simple score line. Parkinson's disease uses a lateral brain with simplified gyri, cerebellum and short brainstem.

The reference images establish art direction, not a license or attribution claim about the new images. No clinical expert approval is claimed.

## Complete topic set

The October 12 follow-up extends this system to all 64 current drug and condition pages: 32 drug guides and 32 condition guides, including the Tadalafil and Aging discovery pages. The original Metformin and Parkinson's disease illustrations remain intact; the other 62 are individually generated originals.

Exact final prompts, visible subject descriptions, route assignments and tool provenance are saved in `drug-generation.json`, `root-drug-generation.json`, `condition-a-generation.json` and `condition-b-generation.json`. The initial two metadata records are retained in `initial-metadata.json`. Source-generation records stay outside public assets and runtime metadata.

Run `node scripts/build-hero-catalog.mjs` to create `data/topic-hero-art.json`, then `node scripts/export-hero-art.mjs` and `node scripts/check-hero-art.mjs`. Publication requires the complete catalog; `--partial` is only for local work in progress. The exporter retains compositions and alpha while producing 512/1024 WebP heroes and 1200×630 PNG social images. `scripts/check-hero-http.mjs --origin=https://remaprx.com` verifies served metadata and image delivery after publication.

Drug subjects are generic medication forms, without commercial branding, product identification, dose or treatment claims. Condition subjects are simplified anatomy or respectful topic symbols. Alt text describes the actual illustration. Full validation and publication provenance are recorded in `docs/HERO-ROLLOUT-VALIDATION.md`.
