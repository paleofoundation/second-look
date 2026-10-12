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

Concurrent research-ingestion work was detected in the shared checkout during validation. The publication candidate isolates this pilot's files and documentation changes from those unrelated edits. Publication receipt pending. Owner assessment and canonical adoption remain pending regardless of technical check results.
