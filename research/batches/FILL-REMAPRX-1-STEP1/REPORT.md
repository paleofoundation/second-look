# FILL-REMAPRX-1 step 1 — source wiring candidate

October 26, 2026. **Technical PASS-CANDIDATE on the authorized live baseline.** This is source-association work, not scientific acceptance or release. Step 2 has not started.

The isolated branch is `codex/fill-remaprx-1-wiring`, based on exact live source `2004fbf0b6f58a652a867fd89972556bec510116` (tree `853c10dfaaded4503e037098b3588adad34187ec`). The original reviewed candidate `4106ef7e0c6db21c639d1bf9397cb5bd2b5b33e5` remains unchanged at `codex/fill-remaprx-1-wiring-reviewed-4106ef7`; its `46be52f8` sibling line is not integrated. No uncommitted application, evidence, pilot, D22 or governance work was copied from the original checkout. That checkout remains owned by “Check hydroxychloroquine page” and was never checked out, stashed, reset, cleaned, edited or committed by this runner.

## Result and applicability limits

Checked all **25 page/source candidates** for the eight ordered destinations against exact existing canonical metadata, locators and source-linked records. Wired **17 associations across seven profiles**, reusing 16 distinct source IDs. Twelve associations expose existing primary-report summaries in the single Research Feed; five expose background references without becoming primary studies. Seven actual, page-specific source-coverage events identify the October 26 changes as presentation events with existing assessments/review states unchanged.

Type 2 diabetes receives no new association: CP018 concerns diabetes medicines repurposed for sarcopenia. For aging, only the aged-mouse oral-health report is added. The seven other aging candidates have the wrong condition, population or endpoint, including generic autophagy experiments with no aging endpoint. This is not evidence that no other relevant literature exists.

The two COVID-OUT associations reuse the report identifying ivermectin and fluvoxamine, **not** the D01/metformin outcome row or its numerical effects. Acute infection is not established Long COVID. Myeloma aspirin research remains thromboprophylaxis, not tumor control. Itraconazole plus arsenic trioxide remains a combination in cells/mice. Mouse oral health, mouse lifespan and human healthspan remain distinct. PAX-D protocol remains background, not another outcome report or independent trial. The second sirolimus label preserves its separate product `setid`; no formulation or dose equivalence is inferred. Reviews and the textbook chapter stay secondary/context and may overlap primary reports.

All source records, source URLs/identifiers, existing prose, outcome/synthesis records, grades, trial/participant counts, review bodies, corrections, quarantine and scientific/release states are byte-preserved from the baseline. No new sources or medical-effect statements were authored. Existing short/title-only summaries and abstract-based locators remain limited; this wiring does not complete full-text extraction, Q01–Q15 reviews or condition-wide research. The 16 empty outcome tables remain for step 2.

Applicability verification here means reconciliation of existing records. No scientific source was newly retrieved or reopened, no new extraction/appraisal occurred, and no independent/human review is claimed.

## Exact candidate dispositions

| Destination | Existing source | Disposition | Applicability and limit |
| --- | --- | --- | --- |
| /conditions/multiple-myeloma | `CP019-R01` | Wire: secondary_context | Existing sampleDescription explicitly identifies multiple-myeloma cell lines. Review is bibliography context, not an independent myeloma trial or evidence for simvastatin. |
| /conditions/multiple-myeloma | `CP020-R01` | Wire: secondary_context | Existing sampleDescription explicitly identifies a leflunomide multiple-myeloma study. Does not transfer its findings to other drugs or create a primary result. |
| /conditions/multiple-myeloma | `MF-MYELOMA-MODELS-2018` | Wire: preclinical_report | Exact disease/model match; retains nonhuman experimental scope and existing abstract locators. No human benefit inference. |
| /conditions/multiple-myeloma | `P-D07-MYELOMA-2016` | Wire: preclinical_combination_report | Exact myeloma combination, not itraconazole monotherapy or clinical response. |
| /conditions/multiple-myeloma | `P-D20-MYELOMA` | Wire: preclinical_report | Exact cell-line and condition match; no patient survival or treatment-effect claim. |
| /conditions/multiple-myeloma | `P-D23-MYELOMA` | Wire: supportive_care_report | Relevant to myeloma treatment context only. Clot prevention is not an antimyeloma response or survival endpoint. |
| /conditions/vitiligo | `CP027-CH25` | Wire: textbook_context | Chapter title and existing REF-CP027-CH25-P031 explicitly establish vitiligo context. Secondary account overlaps primary evidence and adds no trial or participant count. |
| /conditions/vitiligo | `P-D14-VITILIGO-2013` | Wire: uncontrolled_report | Exact drug and condition; no randomized comparator and no transfer of findings to other autoimmune diseases. |
| /conditions/vitiligo | `P-D16-VITILIGO-2014` | Wire: active_comparator_report | Exact condition/regimens; both-arm changes do not establish superiority and there is no placebo comparison. |
| /conditions/vitiligo | `P-D20-VITILIGO` | Wire: randomized_report | Existing title/design/population match. Feed reuses the recorded title-only summary; no new outcome claim or grade is supplied. |
| /drugs/sirolimus | `AGING-PEARL-2025` | Wire: randomized_report | Rapamycin is the existing sirolimus alias in this corpus. Compounded formulation, completer analysis and healthspan endpoint remain distinct from commercial tablets and human lifespan. |
| /drugs/sirolimus | `AGING-RAPA-MICE-2009` | Wire: animal_report | Exact molecule alias; mouse survival does not establish human longevity. |
| /drugs/sirolimus | `AGING-SIROLIMUS-LABEL` | Wire: label_context | Existing official sirolimus label has a distinct product setid from CTX-D06-LABEL. Preserve identity; do not assume label dose or formulation equivalence to PEARL. |
| /conditions/aging | `P-D06-PERIODONTAL-2020` | Wire: animal_report | Aging research goal includes later-life health/function; this record directly studies aged mice. It is not a human periodontitis trial or a lifespan experiment. |
| /conditions/aging | `COND-C31-MANAGEMENT` | Reject | Different condition and endpoint; management of diabetes does not establish an aging intervention. |
| /conditions/aging | `CP017` | Reject | Wrong condition and population; cognition in young schizophrenia patients does not establish aging outcomes. |
| /conditions/aging | `MECH-D06-AUTOPHAGY-2009` | Reject | Generic cell mechanism has no aging or lifespan endpoint; retain on existing mechanism/drug destinations. |
| /conditions/aging | `MECH-D31-PASTIS-2022` | Reject | Different drug/condition and mechanistic endpoint; cannot become longevity evidence. |
| /conditions/aging | `P-D06-CML-2008` | Reject | Same molecule but wrong disease/population/endpoint for aging. |
| /conditions/aging | `P-D06-PROSTATE-2010` | Reject | Cancer target inhibition does not measure aging, human lifespan or healthspan. |
| /conditions/aging | `P-D06-RECTAL-2015` | Reject | Different condition, combination and endpoint; no aging inference. |
| /drugs/ivermectin | `COND-C02-COVIDOUT-2022` | Wire: randomized_report | Existing source explicitly names the exact drug. Source association only; D01 metformin synthesis and effects are NOT reused. No Long COVID treatment/prevention or cancer effect is imported. |
| /drugs/fluvoxamine | `COND-C02-COVIDOUT-2022` | Wire: randomized_report | Existing source explicitly names the exact drug. Source association only; D01 metformin synthesis and effects are NOT reused. No Long COVID treatment/prevention or cancer effect is imported. |
| /drugs/pramipexole | `COND-C09-PAXD-PROTOCOL` | Wire: protocol_context | Exact intervention and trial match; protocol remains context and adds no independent trial result beyond the existing PAX-D outcome report. |
| /conditions/type-2-diabetes | `CP018` | Reject | Title refers to diabetes drugs as the original-use category; proposed indication and outcomes are sarcopenia. Cannot establish a repurposed treatment for established type 2 diabetes. Existing disease context retained unchanged. |

## Reproducibility and verification

`source-mappings.json` preserves each decision, drug/regimen, actual condition, population/model, endpoint, existing-record locators and canonical-source fingerprint. `apply.py` changes only the declared source associations and page history; the public projection and existing parent-scope copies receive the same associations. It cannot create sources, outcomes, grades or review states. Repeat apply changes zero bytes.

Run from the repository root:

```sh
python3 research/batches/FILL-REMAPRX-1-STEP1/apply.py
node research/batches/FILL-REMAPRX-1-STEP1/verify.mjs
```

Focused verification renders all eight actual Articles through the shared components/adapters and checks each added reference, original-source link and primary-feed disclosure, background exclusion from primary studies, one feed per page, exact allowed data deltas, unchanged scientific/indexing inputs and repeat application. No new TSX/component/layout changes are included. Existing source reference implementations consulted: Microbiome Medicine ConditionsTable/StudyDrawer and PepsAnon GuideResearch; no interaction or parity change is claimed.

Original-candidate results are preserved in `VALIDATION.json` as a historical receipt, including the gates that existed then. Current live-baseline results and exact commands are recorded in `VALIDATION-LIVE-BASE.json`. The initial focused verifier encountered Node's default child-process output buffer limit while reading baseline JSON; its buffer was increased and the corrected check passed. That failure was in the new verification harness, not the site or source data. No failure is silently labeled PASS.

## Authorized integration and delivery

Elon's October 26 06:52 gate answer explicitly authorized exact live source `2004fbf0b6f58a652a867fd89972556bec510116` for a separate source-sync draft to main, then only the reviewed wiring delta on top. [Source-sync draft #1](https://github.com/paleofoundation/second-look/pull/1) has exact head `2004fbf0b6f58a652a867fd89972556bec510116`, targets observed main `3da9279bbed757ab9a063ab8626db3985bf33da2`, and separately accounts for 1,340 historical source/asset/record differences by top-level folder. It contains no new wiring or D22 uncommitted work. Nothing is merged or deployed.

The wiring draft targets `sync/remaprx-live-baseline`: **stacked on sync PR; retarget to main after it lands**. All hunks of the original reviewed patch applied cleanly with `git apply --check` followed by `git apply`; there were zero rejected hunks, conflicts or manual hunk resolutions. All five changed data/projection files are byte-identical to the reviewed candidate. Only packet baseline/provenance, preservation tests, validation receipts, resolved-gate reporting and the new explicit integration instruction were adapted. Every scientific record and unrelated exact-live file, including current favicon assets, citation formatting, shared code and indexing policy, is preserved.

The fresh branch starts at the exact live source. The old candidate branch was renamed and retained rather than reset, rebased or rewritten. No cherry-pick or merge of the `46be52f8` sibling line occurred. The separate native Git pushes are ordinary new-branch/fast-forward pushes with existing authentication. No new credentials or alternative transport is authorized. The review packet's `source-mappings.json.reviewedReference` retains the original commit, baseline and patch hash. `verify.mjs` rejects any unrelated source delta and checks the reviewed data bytes against portable SHA-256 fingerprints; it also checks the unchanged reference anchor when that local branch is available. A fresh collaborator does not need the unpublished reference branch to run the data-preservation checks.

Read-only live-source evidence is preserved in `LIVE-BASELINE-PROOF.json`: native Sites version 46/source/deployment/custom-domain provenance, four matching static-public asset hashes, three matching actual article text hashes and all 381 ordered sitemap URLs. This identifies the Sites-managed Cloudflare Worker `site---6ac734459a508191a425263c7645a0be`, rather than guessing origin from edge headers. A public application build ID was unavailable and was not invented. Raw live-site evidence remains in the runner's adjacent `live-baseline-0614/` directory; the reviewed original gate packet remains preserved rather than rewritten.

Original D22 work continues in the canonical checkout and is not part of either draft. Do not overwrite it at later integration. The adopted October 16 publishing plan was read as a governing instruction, not copied or rewritten; its actual original-input hash is preserved in the historical validation receipt. New source retrieval, extraction, appraisal and independent/human review remain outside this wiring operation.

The earlier two direct bridge-write approval rejections remain respected: no direct or workaround bridge write was attempted afterward. The 06:14 and 06:52 entries explicitly permit local STATUS relay through CONDUCTOR. Exact draft URLs, heads, base, hunk result and validation are saved in the adjacent delivery receipt and `bridge-status.txt`. There is no need to mint credentials or change access to complete that relay.

Robots blocking is deliberate source configuration: `app/robots.ts` returns Disallow `/`, `app/layout.tsx` sets `index: false, follow: false`, and `docs/COLLABORATOR-HANDOFF.md` explicitly describes the current blocked-index state. Both source files and live assets are byte-preserved. No indexing, hosting/Vercel, audience, login, production data, credential, outbound messaging, PR merge, deployment or publication change occurred.

Both PRs remain drafts and require Elon's acceptance. Step 2 waits for the wiring PASS; creating a draft or passing technical checks does not authorize it or supply scientific/release approval.
