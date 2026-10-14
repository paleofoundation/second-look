# Itraconazole mechanism presentation pilot

Owner authorization: 12 October 2026, Drug Repurposing chat. Apply the proposed structure on one page, then assess it before canonical adoption. Only D07 at `/drugs/itraconazole` adopts this structure. Other mechanism records retain their current format.

## Scoped presentation contract

Use one connected cited opening paragraph describing original action and repurposing rationale. Follow with two visible shared pathway explanations and a table headed Condition / Mechanism and rationale / What was tested / Limits. Rows become labeled cards when the article column is 640px or narrower, including desktop layouts with narrow reading columns. Preserve semantic table roles and headers at both sizes. Put clinical outcome details in the existing Benefits/Evidence sections and retain a link to Evidence below the table.

The existing canonical mechanism record gains `presentation: pathway-table-pilot`, `pathways` and `rationales`. Each pathway preserves its stable ID, title and cited prose. Each rationale contains a stable ID, condition label, canonical condition link and three cited prose fields: `rationale`, `tested`, `limits`. Cited prose retains `text`, `sourceIds`, and source-mapped `sentences`. Citation collection follows the rendered order through all fields; the shared wiki-link and citation renderers remain in use. The previous eleven disclosure IDs now identify the two visible pathway blocks and nine table rows. No new fixed question or row quota is established for other drugs. Historical generators must not overwrite this reviewed pilot without explicit reconciliation.

## Existing-source mapping

This is an editorial reorganization of existing page records, including their source previews and study-design fields. It adds no external acquisition, extraction or import. The two detailed pathway explanations are retained verbatim. Introductory definitions summarize those existing explanations; row limits describe the inference boundaries of the recorded designs and models, not new study results.

| Original fragment | Destination | Existing sources |
| --- | --- | --- |
| `hedgehog-cellular` | Visible pathway prose | MECH-D07-HEDGEHOG-2010 |
| `cholesterol-transport` | Visible pathway prose | MECH-D07-CHOLESTEROL-2010, MECH-D07-NPC1-2017 |
| `ovarian` | Ovarian clear cell carcinoma row | COND-C03-ITRA-2014, P-D07-PANCREAS-2015 (shared rationale only) |
| `prostate` | Prostate cancer row | P-D07-PROSTATE-2013 |
| `lung` | Non-small-cell lung cancer row | P-D07-LUNG-2013 |
| `colorectal` | Colorectal cancer row | P-D07-CRC-2018 |
| `pancreatic` | Pancreatic cancer row | P-D07-PANCREAS-2015 |
| `melanoma` | Melanoma row | P-D07-MELANOMA-2017 |
| `bcc` | Basal cell carcinoma row | P-D07-BCC-2014 |
| `aml` | Acute myeloid leukemia row | P-D07-AML-2026 |
| `myeloma` | Multiple myeloma row | P-D07-MYELOMA-2016 |

The original-action statement retains CTX-D07-LABEL. Each opening sentence carries the existing sources supporting its scope. No efficacy grade, source access status, review release or clinical recommendation is changed. Scientific source appraisal remains subject to the existing gates.

## Verification and release

Passed TypeScript checking; content, reader, all-profile SSR (64 profiles), article navigation (68 articles), wiki-link, Evidence composition and governance checks. Verified that D07 is the only changed mechanism record and all context records are unchanged. The production build passed with the existing large-chunk advisory. Browser checks at 1600px show a four-column table; at 1280px the narrow article column uses cards; at 390px cards retain full-width headings and produce no document overflow. All nine rows and both pathway explanations are present, and legacy row deep links scroll to the matching content. Table citations open the existing source popover. Local screenshots are in `artifacts/mechanism-pilot/` in the working checkout.

Concurrent research-ingestion work was detected in the shared checkout during validation. The publication candidate isolates this pilot's files and documentation changes from those unrelated edits. Owner assessment and canonical adoption remain pending regardless of technical check results.


## Published pilot receipt — 12 October 2026

Sites version 24 published successfully at 11:22:34 UTC (14:22:34 Asia/Nicosia). Source commit: `8d7424bd9dca50a68c224144749aaa04392e4eb1`. Saved version: `appgprj_6ac734459a508191a425263c7645a0be~appgver_df633ca84b1c81919beff200e9979c97`. Deployment: `appgdep_6accc2e541c081918f673ae6b95426f4`. Archive SHA-256: `21109d2408dc400863fb88629ea5203dbac79c95482ce01cc93de0472090ddaa`.

The isolated source candidate passed all-profile SSR and TypeScript checks, then the Sites production build and built-payload privacy checks (30 payloads). The live page at https://remaprx.com/drugs/itraconazole#mechanisms was opened and confirmed to contain two visible pathway explanations, nine condition rows and zero mechanism disclosures. Existing public audience and scientific release/access gates were preserved. Browser citation dismissal by Escape restored focus to its trigger. Desktop/mobile screenshots represent the same pilot layout. Canonical adoption remains pending owner assessment.


## Metformin pathway accordion pilot — October 12, 2026

Owner requested a local metformin preview of FAQ-style pathway accordions before canonical adoption. The three existing pathway titles remain declarative headings, each inside a native summary with the shared FAQ plus/minus icon and disclosure styling. Explanations have no “Quick answer” label. Independent panels start collapsed; the introduction and condition table remain visible. Existing pathway IDs, citations and text are preserved. The opt-in is scoped to `G-METFORMIN` in the shared article renderer; itraconazole and other guides retain their current behavior. No research data changed.

Consulted Microbiome Medicine `docs/DESIGN-SYSTEM.md` FAQ contract and `ContentAccordions.tsx`, PepsAnon `reveal-anchor.tsx`, and this app’s `InlineFaqs` and article fragment reveal. Kept the PepsAnon browser reference available. React review: native disclosure state, stable keys, semantic headings, decorative icons and existing fragment handling; no added listeners or dependencies.

Verification: TypeScript, all-profile SSR (64 profiles), article navigation (68 articles), citation order/closure, legacy fragment and governance checks passed. Browser confirmed three initially collapsed panels, click/Enter/Space toggles, retained citations and direct-link automatic expansion at `#autophagy-causality`. The 399px preview has no horizontal overflow. Requested desktop viewport override did not change the in-app browser’s actual width, so desktop visual verification remains unconfirmed. Preview: parent workspace `artifacts/metformin-accordion-pilot/preview.png`. Local-only pilot; owner assessment, site-wide canonical adoption and hosted publication remain pending.
