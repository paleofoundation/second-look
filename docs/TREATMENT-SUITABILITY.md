# Treatment suitability and contraindications

Owner requirement, October 12, 2026: show who should not be considered for a treatment, including contraindications, on the website and physician packets. Preserve existing substantive sections and use clear tables where appropriate. This extends the physician packet contract and does not authorize a fabricated specialist identity or clinical approval.

## Reader contract

Distinguish formal contraindications and indication-specific label restrictions from precautions, interactions and limits of trial applicability. A trial exclusion or lack of evidence does not automatically establish a contraindication. Preserve exact product, formulation, indication, jurisdiction, thresholds and conditional exceptions. Cite the supporting label or primary source near each statement. Never imply that absence from the short list establishes eligibility or that these summaries replace a complete medication/label review.

All current drug pages retain their Contraindications destination and existing cited prose. Add the explicit “Who should not be considered?” subheading. Condition Safety sections link to the contraindications of drugs actually represented in that condition's evidence. The two NSCLC sample drugs additionally share structured, cited tables with the NSCLC Safety section and packet.

## Structured data and packet contract

`data/treatment-suitability.json` supplies website rows, classification and exact page mappings. `lib/treatment-suitability.ts` exposes the rows and their source identities. Render through the shared semantic table, citation planner and source drawer; keep citation numbers in first-appearance order. Raw captures and editorial review records stay outside public payloads.

Physician packet schema version 2 requires an eligibility table with cited, uniquely identified rows and an explicit drug identity for every study. Every repurposed drug in the studies must have suitability coverage; a combination's full regimen still requires clinical review. The sample fixture's eight rows must equal the website dataset. An old version-1 packet fails validation and must be revised and reapproved before release; no real packet entries have been released. Approval remains bound to exact structured-content and PDF hashes.

The seven-page NSCLC sample, edition 3.0, adds one treatment-suitability page each for itraconazole and metformin between study findings and consultation. Each has a two-column table and care-team assessment space. Retain treatment-context limits, selected-source scope, blank credit/contact fields, review status and source links. Print, PDF and member preview use the same claims. The downloadable design sample remains outside the production release catalog.

## Source scope and provenance

[RRX-SAFETY-001](../research/batches/RRX-SAFETY-001/PLAN.md) records prospective scope, schema, GP Plan readiness, eight source-checked candidates, exact label locators, source versions and capture hashes. Fresh checks cover metformin oral tablets and SPORANOX itraconazole capsules only. All 32 drug pages already had contraindication prose; the other 30 receive presentation changes, not a claim of fresh label verification or complete contraindication coverage. Existing NSCLC trial findings and Q01–Q15 limitations remain unchanged. Independent clinical review remains pending.

## Verification and release

Verify packet/website row parity, per-drug coverage, citation closure and rejection of missing/invalid safety rows. Preserve membership, exact-edition approval, withdrawal, integrity and privacy checks. Check all public article profiles, condition links, mobile table width, the seven rendered PDF pages, selectable text and source links. Record build and publication separately from scientific approval. See `research/batches/RRX-SAFETY-001/HANDOFF.md` for the executed checks and release receipt.
