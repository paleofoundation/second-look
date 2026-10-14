# Metformin actual source-return checkpoint

October 12, 2026. Root accepted acquisition v1.1 GP at 14:20 UTC before first acquisition. The exact request ZIP is `research-delivery/RRX-GUIDE-METFORMIN-001-1.1-request.zip`, SHA-256 `efe3262f9f47253706e2c9f4e5a91aed77d602fa71022a4c2e7bcf83d855abec`. No external worker was dispatched. The direct local route used the approved private staging directory and left the earlier corpus and RRX-GAP-001 unchanged.

## Actual result

**Twelve source assets, 3,442,289 bytes: seven main reports, one MASTERS corrigendum, two MA.32 metabolic PDF supplements, one exact Time Cap label and one dated FDA page.** Fourteen assignment dispositions: two acquired, seven partially acquired, five inaccessible. Files, embedded source identity, hashes, media and PDF structure were checked by the acquisition worker; independent root receipt acceptance subsequently passed; see `direct-acquisition/root-acceptance.json`. Acquisition is not scientific assessment. All 165 question entries remain `not_extracted`; new completed scientific extractions, assessments, human approvals, syntheses and guide releases are **zero**.

Private staging: `/Users/kmfp/Documents/ChatGPT/Drug Repurposing/private-research/RRX-GUIDE-METFORMIN-001/ACQUIRE-1.1/`. Its manifest SHA-256 is `ad5ad726a0e4785952bb10cf6d06338eff5b929ed836f79b42505673dec1e796`.

Private portable return: `/Users/kmfp/Documents/ChatGPT/Drug Repurposing/private-research/RRX-GUIDE-METFORMIN-001/RRX-GUIDE-METFORMIN-001-1.1-return.zip`. SHA-256 `b93fbf5319bdc9b007aef1528f8b71a61378187df9b0ed494eba4f0a9fc65c98`, 8,121,769 bytes, 207 members. Readback verifies every member. It contains the twelve source assets and private retrieval provenance, including unsuccessful/metadata-only responses clearly excluded as scientific source files. No raw paper is copied into the application checkout or public bundle.

`direct-acquisition/receipt.json` is the portable metadata inventory; `return-package-receipt.json` records the archive; `validation.json` records validation. `coverage-after-acquisition.json` overlays the frozen 24-reference baseline, preserving its identity-confidence distinctions and holds.

## Newly held material — do not request again

| Article reference | Actual new source |
|---|---|
| MF-METPREVENT-2025 | Published 10-page PDF, DOI 10.1016/j.lanhl.2025.100695, from Newcastle repository 305174; first landing request timed out, its linked published PDF succeeded |
| MF-MASTERS-2019 | Full XML, DOI 10.1111/acel.13039, PMID 31557380 / PMC6826125, plus actual linked corrigendum DOI 10.1111/acel.13098, PMID 32141718 / PMC7059173 |
| MF-SCHIZOPHRENIA-PARENT-2023 | Full XML, DOI 10.1038/s41398-023-02616-x, PMID 37821461 / PMC10567690 |
| MF-NRG-LU001-2021 | Full served PMC HTML, DOI 10.1001/jamaoncol.2021.2318, PMID 34323922 / PMC8323052 |
| MF-ALMERA-2021 | Full served PMC HTML, DOI 10.1001/jamaoncol.2021.2328, PMID 34323924 / PMC8323053 |
| COND-C15-MA32-2022 | Full served PMC HTML, DOI 10.1001/jama.2022.6147, PMID 35608580 / PMC9131745 |
| COND-C15-MA32-METABOLIC | Full served PMC HTML, DOI 10.1038/s41523-021-00275-z, PMID 34103538 / PMC8187713; both MOESM1 and MOESM2 PDF supplements, recovered from complete Europe PMC ZIP |
| MF-LABEL-2025 | Article-linked DailyMed Time Cap product, setid 542cec22-eeae-4704-9bb6-4176640e5ea8, revised 2/2025, updated 2025-02-10; 29-page PDF. Distinct from held Zydus IR/Glumetza ER labels |
| MF-FDA-GENERICS | Actual official HTML, content current as of 2021-11-01, retrieved 2026-10-12 |

These are new report-identity/byte candidates, not newly completed studies. Figures embedded as remote HTML images and table/figure scientific content were not audited. The metadata baseline's seven exact identity matches and two title/URL leads remain separate from these seven newly acquired main-report identities. Do not add source-file counts to study counts or regard the resulting article inventory as a comprehensive search.

## Exact remaining acquisition work

The following main sources remain missing after real publisher/metadata attempts. Ordinary publisher access, an authorized library or an owner-provided lawful file is needed; no bypass, purchase or author contact occurred.

| Priority | Missing actual document and verified locator |
|---|---|
| COVID-OUT integrity | **Correction notice DOI 10.1016/S1473-3099(23)00562-5, PMID 37666258**. Europe PMC explicitly links it to original DOI 10.1016/S1473-3099(23)00299-2 / PMID 37302406. Publisher API delivered metadata only; publisher page returned 403. Obtain actual notice and amended report/supplement trail; reuse held original, acute/viral companions and protocol. |
| Established Long COVID | DOI 10.7326/ANNALS-25-04883 / PMID 41771135: full report; publisher-linked Supplementary Material (5.08 MB), Study Protocol and Statistical Analysis Plan (969.86 KB), Data Sharing Statement (67.46 KB), registry KCT0009342/version chain. Publisher returned 403. Search-visible primary text is not a delivered full source. PubMed's free-article label differs from Europe PMC's subscription metadata; do not label it definitively paywalled. |
| Pancreatic cancer | DOI 10.1016/S1470-2045(15)00027-3 / PMID 26067687: exact full report and linked companions. DOI landing was redirect-only HTML; ScienceDirect returned 403. |
| Adenoma recurrence | DOI 10.1016/S1470-2045(15)00565-3 / PMID 26947328: exact full report and linked companions. DOI landing was redirect-only HTML; ScienceDirect returned 403. |
| Crypt-foci trial | DOI 10.1158/1940-6207.CAPR-10-0186 / PMID 20810669: exact full report and linked companions. Publisher returned 403. |

For newly held main reports, obtain only still-required companions:

- **MET-PREVENT:** linked appendix; protocol/SAP (repository names investigator contact as route, no contact authorized); ISRCTN29932357 history. Main report need not be obtained again.
- **MASTERS:** `ACEL-18-e13039-s001.docx` through `s005.docx`; NCT02308228 history/SAP comparison. Reuse existing B-R0057 protocol/Word companion. Direct files returned HTML, two Europe PMC archive attempts were incomplete/timed out and were rejected.
- **Schizophrenia parent:** `41398_2023_2616_MOESM1_ESM.pdf` reporting checklist and `41398_2023_2616_MOESM2_ESM.docx` supplemental material/protocol; NCT03271866 history/SAP. Direct links returned HTML and supplement ZIP transfers were incomplete. Keep CP017 as the same trial family, not independent replication.
- **NRG-LU001:** `jamaoncol-e212318-s001.pdf`, `s002.pdf`, `s003.pdf` and source-specific protocol/SAP/registry version audit.
- **ALMERA:** `jamaoncol-e212328-s001.pdf`, `s002.pdf`, `s003.pdf` and source-specific protocol/SAP/registry version audit.
- **MA.32 clinical:** `jama-e226147-s001.pdf` through `s004.pdf`; NCT01101438 history/protocol/SAP shared with metabolic report. The ten JAMA companion links returned HTML; the Europe PMC API explicitly declined the three non-OA article supplement bundles. Preserve those limitations.
- **MA.32 metabolic:** both linked PDF supplements are held. Audit content/required protocol relations and shared NCT01101438 before deciding further acquisition. It is not the separate sex-hormone report B-R0030.

ACTIV-6 journal DOI 10.1093/cid/ciag335 and REVIVE notice DOI 10.7326/ANNALS-26-03050 / PMID 42832813 remain in the unchanged **RRX-GAP-001-1.1** request. No duplicate fetch or dispatch occurred. Preserve ACTIV-6 preprint/journal distinction and REVIVE quarantine.

## Work needed even with source files present

1. Root independently accepted the byte/identity return on October 12 (`direct-acquisition/root-acceptance.json`). Prepare matching source-pinned extraction readiness next; this acceptance does not approve scientific claims. No new plan was needed to receive the unchanged acquisition scope.
2. Inspect the actual MASTERS corrigendum against its original and record affected fields. Preserve COVID-OUT's correction hold until its notice and changed version are reconciled. A notice's presence does not itself resolve scientific consequences.
3. Complete Q01–Q15 source-located inputs for all guide-cited scholarly reports, not only these seven; reconcile trial/report families, missing companions and source versions; audit numerical results and consequential tables/figures; apply design-appropriate appraisal and independent review. Existing STAMPEDE, Parkinson, schizophrenia companion, mechanism and COVID-OUT materials still need the work listed in the baseline handoff.
4. Map current drug-specific public safety/formulation content against exact official product/jurisdiction versions. FDA generic context does not establish IR/ER therapeutic equivalence or investigational benefit.
5. Screen the existing overlapping D01 inventory for relevant omitted evidence and document exclusions. It is not a demand to ingest the entire site's backlog.
6. Stage/diff an idempotent canonical candidate reusing source/result/review IDs, then obtain required scientific/editorial/clinical/legal approvals. Only after metformin ingestion and assessment complete should the substantive versioned consumer manuscript, PDF, sample and summary be authored. Sales and membership remain held by the product release gates.

Validation passed the accepted schema, exact input hashes, all fourteen dispositions, all twelve actual source-byte hashes, 165 question statuses, ZIP readback and thirteen negative packet probes. Four PDFs parse with 10/1/4/29 pages respectively. This is source receipt validation, not visual scientific review of every source page or guide PDF release verification.
