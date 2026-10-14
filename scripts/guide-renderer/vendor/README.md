# Consumer Guide Theme 0.1.1

A private, versioned Python renderer for original evidence-reading guides. One implementation renders a full guide, selected preview and concise summary from editable JSON. The first manuscript preserves the eight-page Second Look teaching content, with a new edition identifier because layout and navigation changed. Two clearly synthetic topics exercise the same code through configuration/data alone.

This is a pre-1.0 private-draft renderer, not a publication, medical or legal approval system. It rejects a manuscript marked released. Pending reviewers are not shown as approved. All generated files remain drafts. No network calls, service activation or scientific acquisition are performed.

## Install and run

Python 3.10 or later is required. The verified dependency versions are pinned in requirements.txt. The converted Inter/Lora fonts and their OFL licenses are bundled; no platform-specific font paths or font conversion are needed by a recipient.

From this renderer directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python src/render.py --manuscript manuscripts/reading-guide.json --config config/second-look.json --out ../generated/reading
python src/render.py --manuscript fixtures/signals.json --config config/signals.json --out ../generated/signals
python src/render.py --manuscript fixtures/harbors.json --config config/harbors.json --out ../generated/harbors
python scripts/prove.py --out ../proof
```

The exact same src/render.py handles all three manuscripts. To check repeat generation, run the last command again unchanged and compare proof.json and output file hashes. Each proof invocation itself renders every variant twice and checks byte equality, unchanged renderer/data/fonts, links, summary limits and private status. PDF metadata is deliberately invariant; the editorial updated/cutoff dates come from manuscript data and are never inferred from a file timestamp.

For local visual inspection, install Poppler through the recipient's supported environment and use:

```sh
pdftoppm -scale-to 1100 -png ../generated/reading/evidence-reading-guide-0.4-draft-full.pdf ../generated/reading/page
```

No dependency install or network research was performed during this task. The implementation was tested using already-installed reportlab4.4.9, pypdf6.10.0 and Pillow12.3.0. The source-derived theme's authorized Inter and Lora binaries were converted locally once to TTF; their provenance and license notices are preserved.

## Edit content rather than copying layout

- manuscripts/reading-guide.json is the editable actual guide, source/claim ledger, summary and contributor assignment.
- fixtures/signals.json and fixtures/harbors.json are private fictional examples. They must never enter production evidence, indexes or sales.
- config/*.json holds identity, brand colors, geometry and typography. The default Second Look palette is navy183153, amberF6BC45 and palefff9eb. The synthetic second config changes identity and main color while using the same code.
- manuscript.schema.json documents the portable data contract. The renderer additionally performs local semantic checks without requiring a schema-validator dependency.
- Every generated render-manifest.json stores manuscript/config/renderer/font hashes and full/preview/summary hashes, bookmarks and link targets.

Supported blocks are paragraph, heading, kicker, callout, notice, source, linked contents, table, entry, original vector figure, FAQ, worksheet, bibliography and contributors. Long tables repeat their header on continuation pages and preserve cell units supplied in the data. Figure title/art/description/caption stay grouped. Headings keep with their following content. A repeated table fixture tests pagination rather than only a two-row example. A chapter normally starts on a new page; overflowing content reflows without a hard-coded per-topic page template.

The optional original diagram is a locally rendered Question-Source-Limits motif; its labels are theme artwork, not scientific data. No user commercial reference PDF, extracted reference text, source figure or prescription instruction is distributed.

## Accepted-evidence and website adapters

The host maps its accepted canonical record IDs to sources and claimLedger, preserving source tier, exact locators, review state and population/intervention/comparator/outcome scope. A receipt or a valid JSON field is not an approved claim. This renderer never fills missing facts or computes certainty. The retained guide uses the six existing methodological/regulatory CONTEXT sources; its arithmetic example remains fictional.

The host uses productId plus edition.id and all three asset hashes when constructing its product/edition model. Keep previews separate from protected full manuscripts. previewChapterIds is a proper subset; internal contents links only target chapters present in that variant. Omitted chapter titles are labeled as full-guide content. A summary includes the exact manuscript notice and every decisive limit automatically; it also includes source references that resolve without the full document.

The destination supplies correctionRoute and optional policyRoute as canonical HTTP(S) destinations. The first guide binds corrections, educational-use policy and the free worksheet to the existing host routes in config/second-look.json and manuscript provenance; scientific and product release approval remains separate. Host review records, authentication, entitlements, secure download delivery, subscription rights, billing and publication policies remain outside this renderer. No paid file should be promoted by filename alone.

## Boundaries and release holds

The actual edition remains a complete private evidence-reading draft, not a clinical repurposing handbook. Public/commercial release requires exact-version editorial, qualified independent clinical/safety and applicable legal review, reader testing, accessible delivery and host commerce acceptance. Existing scientific/ingestion gaps are unchanged.

PDFs have embedded fonts, selectable text, bookmarks and links. They are untagged; PDF/UA, semantic reading order and screen-reader suitability are not certified. Those are explicit accessibility holds, despite passing geometry and visual inspection. Clinical, legal, accessibility, renderer, account and commerce acceptance are separate.

## ORCID credit contract (0.1.1)

Every supplied contributors[].orcid is rendered by the same OrcidCredit flowable: a 12-point #A6CE39 vector iD mark, visible identifier, and one HTTPS ORCID link covering both. Raw ORCID text in manuscript blocks is rejected to prevent unbranded duplicate credits. Supply only an owner-provided ORCID; synthetic authors in the bundled fixtures have no assigned ORCID and none is invented. Missing ORCID values produce no identity link. This correction changes presentation only and does not approve authorship, reviews, or release.
