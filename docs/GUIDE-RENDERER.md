# One manuscript, four reading formats

Implemented October 12, 2026 for the owner's metformin-first guide plan. This is a working private draft pipeline with a synthetic proof, not a completed metformin guide or a commercial release approval.

## Canonical source and outputs

`scripts/guide-renderer/build.mjs` reads a versioned `remaprx-guide-source-1` JSON file. Its `manuscript` field is validated by the actual `lib/guide-manuscript.ts` schema used by the protected web reader. The wrapper supplies the topic slug, audience, synthetic flag and explicit block selections:

- `previewSelections`: `{chapterId, blockIndexes}` pairs for the public sample candidate.
- `summarySelections`: pairs for the printable summary's substantive blocks.
- `sharedLimitSelections`: plain paragraph/callout blocks included in both derivatives. These are required in addition to the manuscript's shared medical notice. The summary selector must not duplicate them.

Selections resolve against the source's stable chapter identities and zero-based block positions. Invalid/duplicate indices, nonexistent citations, unsafe reference URLs, malformed tables, unsafe edition filenames, and a sample or summary containing the complete manuscript are rejected. Reordering blocks requires a new source review and generated hashes. A code-valid selector does not establish scientific appropriateness; the approving reviewer still assesses whether the selected sample and summary retain decisive context.

The pipeline produces:

| File | Purpose |
| --- | --- |
| `web-manuscript.json` | Complete schema-valid protected web edition |
| `sample-candidate.json` | Only selected sample blocks, mandatory limits and their references |
| `summary-candidate.json` | Only selected summary blocks, mandatory limits and their references |
| `*-full.pdf` | Full manuscript, linked contents, sources, credits and edition history |
| `*-preview.pdf` | Selected sample, with independent contents and references |
| `*-summary.pdf` | Printable questions/content, shared notice/limits, sources and credits |
| `build-manifest.json` | Product/edition/version/cutoff, source/adapter/schema hashes and exact asset hashes |
| `pdf-manifest.json` | Exact renderer/config/font hashes, PDF page/link/bookmark records and accessibility hold |

The full text is not copied into public JSON to hide it with CSS. References for omitted blocks are omitted from sample/summary candidates. The source medical notice, evidence cutoff, version and actual structured contributor fields are carried into the formats. Block text is escaped before reaching the reusable PDF engine; the protected web data remains plain text. Studied-regimen interpretation, evidence assessment and author/reviewer identity verification remain editorial responsibilities.

## Reusing the existing renderer

The pinned `rules/one-match-rule/references/theme/releases/consumer-guide-theme-0.1.1.zip` remains unchanged. `scripts/guide-renderer/vendor/` contains an exact bounded extraction of its renderer, schema, documentation, font assets, licenses and metadata. `PROVENANCE.json` records the original archive and each extracted member's SHA-256. The private project-owned renderer does not carry a separately asserted public redistribution license; the bundled Inter/Lora SIL OFL notices are preserved verbatim.

The adapter maps the web schema's paragraph, callout, list, table and questions blocks into the engine's existing components. It invokes the same unmodified `render_variant` for each format. RemapRx's original configuration uses blue `#1736F5`, yellow `#FFC709`, dark body text, a pale blue callout fill and the existing embedded Inter/Lora fonts. It does not copy the Examine PDF's content, artwork or layout assets.

## Run privately

Use the bundled Python runtime with ReportLab, pypdf and pdfplumber (or an equivalent local environment). The local runtime path is machine-specific and is not hard-coded in the scripts:

```sh
node scripts/guide-renderer/build.mjs \
  --source /private/location/topic-source.json \
  --out /private/location/topic-edition \
  --python /path/to/python3

node scripts/check-guide-renderer.mjs --python /path/to/python3
```

`REMAPRX_PYTHON` can supply the Python command instead. The output directory must be outside the application checkout, including when it resolves through a symlink. New output directories are mode 0700 and generated content files are mode 0600. No generated manuscripts/PDFs enter `/public`, application imports or Git. Real source manuscripts also belong in private editorial storage; only a clearly fictional software fixture is versioned under `scripts/guide-renderer/fixtures/`.

The three selected formats are rendered from one immutable input in one invocation. The manifest supplies the web/PDF/summary hashes required by the host's exact-edition approval records. A sample can be promoted to public storage only after its actual sample bytes and marketing presentation receive the applicable release approvals. `sampleApproval` remains `pending`; this pipeline has no public upload, storage promotion, checkout or release command.

## Verification receipt

`node scripts/check-guide-renderer.mjs` passed using the bundled Python runtime on October 12, 2026. It checks vendor/font integrity; actual web-schema validation; source/web/PDF version and block-content consistency; sample/summary omission sentinels; mandatory limits; malformed selections and references; rejection of public-checkout output; private asset permissions; repeat generation with identical hashes; all PDF bookmark and link destinations; every-page text bounds and selectable text.

The synthetic fixture rendered a four-page full guide, four-page sample and one-page summary. Each of those nine pages was rendered with Poppler at a 1200-pixel maximum dimension and visually inspected. Body text, table columns, callout fill, worksheet lines, citations, headings, headers/footers and margins were legible and unclipped. White space reflects short software-fixture chapters; these counts are not content-depth targets. Linked contents resolved to the included chapters, citation links used their recorded HTTPS destinations and the sample contained neither the omitted passage nor its reference. The dated, hash-bound receipt is `scripts/guide-renderer/proof/synthetic-acceptance.json`. PDF/PNG proof artifacts remain outside the repository.

## Remaining release work

The inherited 0.1.1 engine deliberately prints private-draft/synthetic labels and rejects released manuscripts. This extension retains that behavior. A later renderer release mode must be validated before producing a commercially released edition; removing a watermark does not create editorial approval. The current outputs are reviewable candidates, not a ready-to-sell product.

PDFs have embedded fonts, selectable text, bookmarks and links, but are **untagged**. Semantic reading order, screen-reader suitability and PDF/UA are not certified. Every real manuscript/renderer change still needs fresh every-page visual review and appropriate accessibility acceptance. Synthetic tests establish software behavior only; they do not establish metformin evidence completeness, scientific/clinical/legal approval or substantive guide depth. No invented metformin material or reviewer credentials were added.
