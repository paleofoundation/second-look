# Metformin guide review, November 4, 2026

**The model evidence, numerical, clinical-content, editorial and artifact review is complete. Eight findings were corrected in `2026.11.04-candidate.2`.** All 71 original content blocks and the two added safety blocks have individual review records. The 30-reference bibliography is preserved; there is no 24-source ceiling.

The reviewed full guide is [27 pages](../../../../private-guides/metformin-reviewed-20261104/output/metformin-2026.11.04-candidate.2-full.pdf), with a [seven-page sample](../../../../private-guides/metformin-reviewed-20261104/output/metformin-2026.11.04-candidate.2-preview.pdf) and [three-page printable summary](../../../../private-guides/metformin-reviewed-20261104/output/metformin-2026.11.04-candidate.2-summary.pdf). These local private assets are outside Git and the deployment tree. Their structured web counterpart, exact paths and SHA-256 values are in [guide-artifacts.json](guide-artifacts.json).

## Findings fixed

| Finding | Correction |
| --- | --- |
| High: omitted contraindications | Added metformin hypersensitivity and acute/chronic metabolic acidosis, including diabetic ketoacidosis, alongside severe kidney impairment. |
| Moderate: incomplete risk-management wording | Made the annual renal-check minimum, hepatic avoidance, mitochondrial-disease recommendation and potentially fatal lactic-acidosis risk explicit. |
| Moderate: vague interaction discussion | Added label-backed drug classes and examples, with individualized pharmacist/clinician review. |
| Moderate: missing special-population limits | Added pregnancy/lactation uncertainty, possible ovulation and product-specific pediatric limits. |
| Moderate: undefined ACTIV-6 primary outcome | Distinguished self-reported day-180 symptoms or death from a clinician's Long COVID diagnosis; explained the trial's primary success threshold. |
| Moderate: unclear REVIVE score context | Added the Fatigue Severity Scale range, direction and exact dose-specific credible intervals. |
| Low: imprecise hazard-ratio explanation | Distinguished the rate among people not yet diagnosed from cumulative risks and raw fractions. |
| Low: future edition timestamp | Replaced the hardcoded timestamp with the actual UTC generation time in the new edition. |

Safety corrections use the inspected current [immediate-release label](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=30658e19-8e6e-49aa-a007-e414224797c5) and [extended-release label](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=96c8a89d-99db-24b1-e053-2a95a90ac2b8), including sections 4, 5, 7 and 8. Product-specific recommendations have not been generalized into a universal regimen.

## Evidence integrity

COVID-OUT uses corrected appendix Table S4: 35/564 versus 58/562 diagnoses and estimated cumulative incidences of 6.3% versus 10.4%. The reported 4.1 percentage-point difference and interval match that table. The separate Discussion and registry discrepancies remain attributed and visible; the guide does not invent a historical change log that the correction notice does not supply.

REVIVE's retracted original remains excluded. The formal notice and replacement report were checked, including the safety-driven dose amendment and futility stop. The sequential 750 mg and 500 mg extended-release cohorts are not described as a randomized dose comparison, and the metformin findings remain inconclusive. Current web-tool DOI requests failed, so this review used the previously acquired, hash-verified publisher notice and replacement full text rather than treating a failed request as verification.

Cancer, neurological, mechanistic and physical-function claims were reconciled against the prior source assessments and targeted re-reading of original outcomes/methods. The scanned Hosono colorectal pilot was visually reread at printed pages 1077–1082. Major null and adverse findings, surrogate limits, shared trial families, missingness and uncertainty remain prominent. This was not a fresh exhaustive systematic search or replication of patient-level analyses.

The prior packet still contains 24 Q01–Q15 study assessments: nine cover their available packets without outstanding access fields; 15 retain named access gaps. This review does not relabel unavailable supplements, analysis code or protocol history as inspected. Abrilla 2021, El-Mir 2000 and the retracted REVIVE original remain excluded from claim support.

## Verification

- All 29 planned input hashes, 61 retained source-file hashes and six candidate-1 assets were verified; historical files were preserved.
- Every original block and both new blocks have source/locator judgments in [review.json](review.json); output mappings are in [guide-block-map.json](guide-block-map.json).
- Structured web, full PDF, sample and summary pass exact text-parity and citation-closure checks. No excluded source supports the new edition.
- All 37 PDF pages were visually inspected. The revised outcome and safety pages and summary were also inspected at full page size. No clipping, table collision, broken glyph or split bibliography-entry defect was found.
- The PDFs have selectable text, 335 validated link annotations and 23 bookmarks with valid internal destinations. This checks annotation targets and structure; it is not a claim that every external publisher URL responds to every browser or tool.
- Governance, per-topic offer checks and generated portfolio freshness passed. The portfolio now registers candidate 2. No application renderer, access-control, payment code or public medical prose changed during this review.

Receipts: [verification.json](verification.json), [visual-review.json](visual-review.json), [repository-checks.json](repository-checks.json).

## Remaining release decisions

This review was performed by **Codex (OpenAI)**. It is a substantive model review, not an independent human credential or signature. The existing [topic-guide contract](../../../docs/TOPIC-GUIDES.md) says: “Clinical and legal approval identity, scope, qualifications, conflicts, decision and dates remain mandatory.” Human editorial approval is also required by the exact-edition release implementation.

The named clinical, human editorial and legal/commercial approvals are still unsigned. [pending-approvals.json](pending-approvals.json) supplies the exact asset and marketing bindings for those decisions without fabricating approval. The PDFs are untagged; PDF/UA, assistive-technology and real-reader acceptance remain unverified. Publication also retains the existing merchant/payment/fulfillment requirements.

No production release, Stripe mutation, payment or deployment was performed. The review work is complete within its stated scope; the guide has not been falsely marked approved or purchasable.

## Reproduce deterministic checks

Use the bundled Python with `pypdf` and `pdfplumber` available to run `verify_review.py`. The source and assessment paths in the plan must exist locally. This validates the current artifacts without rebuilding or changing their timestamps. Do not rerun the private authoring script merely to verify an edition, since a new timestamp changes its bytes and requires a new review binding.
