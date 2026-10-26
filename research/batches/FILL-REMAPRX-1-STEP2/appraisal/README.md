# Exact-source appraisal continuation

Elon’s October 26, 2026 07:58 OPTION 1 authorizes this continuation of draft PR #3. The starting audit and its zero-row state remain historical, including `../inventory.json`, `../input-manifest.json`, `../VALIDATION.json` and commit `bbe952a2`. They are not the current result. The inventory generator now explicitly reads its fixed wiring revision so a repeat cannot overwrite that starting record with today’s filled profiles.

The prospective `plan.json`, `candidate.schema.json`, `source-access.json` and GP Plan `readiness.json` were saved before source extraction. No new scientific source retrieval occurred. Existing acquisition metadata was matched by exact identifiers/title, then actual local original/companion bytes were checked against the recorded hashes. Six exact source IDs support eight new synthesis rows; 16 of the 86 audited source IDs have verified local originals. Metadata marked `abstract_only` without a recovered abstract file is identity metadata, not an inspected scientific abstract.

The outcome projection contains **8 rows and 8 actual selected-source five-domain assessments (40 domain judgments)** under the unchanged `editorial/EVIDENCE-GRADING.md` and `scripts/evidence-assessments.mjs`. Actual assessment date: October 26, 2026. All formal body-of-evidence, independent/human source review and release states remain pending; this is an AI-assisted selected-source editorial draft. An A–F benefit letter is separate from High/Moderate/Low confidence. The three nonclinical rows have actual Low confidence assessments and no clinical benefit letter; this is not the rejected unassessed-canonical option.

| New canonical row suffix (`SYN-FILL2-`) | Exact scope | Confidence | Benefit | Evidence basis |
| --- | --- | --- | --- | --- |
| D02-ACTIV6-RECOVERY | Higher-dose fluvoxamine, acute COVID-19 sustained recovery through day 28 | Moderate | E | HR 0.99, 95% Bayesian CrI 0.89–1.09; 1208 randomized, 1175 analyzed |
| D02-COVIDOUT-COMPOSITE | Fluvoxamine, acute 14-day composite | Moderate | E | OR 0.94, 95% CI 0.66–1.36; 661 in relevant modified intention-to-treat arms |
| D08-COVIDOUT-COMPOSITE | Ivermectin, acute 14-day composite | Moderate | E | OR 1.05, 95% CI 0.76–1.45; 808 in relevant modified intention-to-treat arms |
| D06-AGING-VAT | Compounded rapamycin, primary 48-week visceral adiposity | Low | E | Wide improvement OR intervals; primary benefit not demonstrated |
| D06-AGING-LEAN | Compounded rapamycin 10 mg/week, secondary female lean-tissue percentage change | Low | C | +6.194 percentage points versus placebo, 95% CI 0.8773–11.5105; small subgroup |
| D06-PERIODONTAL-MICE | Aged female mice, 8-week periodontal bone | Low | No clinical letter | Controlled mouse cohorts, no human RCT or patient effect |
| D08-CRC-XENOGRAFT | WNT-TCF-dependent colorectal xenograft growth | Low | No clinical letter | Cell/mouse finding; negative TCF-independent and rescue controls retained |
| D10-NSCLC-XENOGRAFT | A549 NSCLC xenograft size/weight over 12 days | Low | No clinical letter | Mouse finding; no human efficacy or safe-dose inference |

PEARL remains one trial with 125 randomized and 114 completers; its null primary outcome and positive secondary female subgroup are separate. Neither establishes lifespan extension or treatment of diagnosed sarcopenia. Commercial sirolimus exposure is not assumed equivalent to the compounded preparation. The 24-week result in the same women is not replication.

COVID-OUT remains the existing `S-COVIDOUT-2023` family. Its historical 1431-person whole-trial basis and prior outcomes are preserved. Optional, explicitly scoped comparison identities select 661 or 808 modified intention-to-treat participants for these new drug comparisons, while retaining distinct complete-case event denominators and the original whole-trial randomized N in study detail. A shared family counts once; incompatible overlapping comparison populations produce an unknown combined participant total, never a sum. The only two additional RCT families are higher-dose fluvoxamine ACTIV-6 and PEARL, increasing the registry from 43 to 45. New summary dates are record-specific; historical summaries and their dates are unchanged.

The existing `/conditions/aging` guide retains its ID, route, research-goal label and prose. It moves from the discovery list into the canonical guide registry to satisfy the unchanged grader’s exact parent identity checks. No page or condition identity is invented. Drug/condition parents reuse the same rows; the other affected reciprocal condition pages are acute COVID-19, periodontitis, colorectal cancer and NSCLC.

The final browser consistency check found an inherited D02 dosing sentence that omitted the first-day titration. The exact already-inspected ACTIV-6 Abstract, Interventions specifies 50 mg twice on day 1, followed by 100 mg twice daily for 12 more days. The bounded projector now corrects only that sentence and its source-bound sentence projection, without changing source identity, outcome findings, appraisal fingerprints or clinical advice. Historical reader-batch inputs are retained; do not rerun historical corpus generators over the current bounded projection.

## Access, gaps and integrity

All **93 starting page/source associations and 86 source IDs** are reconciled in `source-dispositions.json`; `profile-accounting.json` records each of the 16 original profiles. Five have selected-source rows: fluvoxamine, sirolimus, ivermectin, fenbendazole and aging. Eleven retain truthful empty tables: guanfacine, maraviroc, rituximab, memantine, sildenafil, ME/CFS, PGAD, multiple myeloma, type 2 diabetes, fluconazole and tadalafil. This is not an assertion that their literature lacks outcomes.

`REED-QUEUE.csv` is an **offline queue only**, containing 76 lines for 72 distinct source IDs: 74 missing-original association lines covering 70 source IDs, plus two source-specific companion lines for ACTIV-6 and COVID-OUT. Each line retains drug/regimen, condition/population, outcome, source ID/URL/locator, missing file/field and known corpus identity matches. Context-only work is labeled as such. No acquisition request or message was sent.

Accessible but inapplicable inputs are not hidden as access failures: cellular autophagy is mechanism context; healthy hypoxia, Candida-isolate experiments and vascular perfusion reports lack an exact existing condition/outcome parent for this bounded task; the itraconazole experiment cannot supply fluconazole benefit. Two fenbendazole liver-injury reports remain safety evidence and cannot become cancer-efficacy results or causal incidence estimates. No new condition IDs are created to force rows.

The existing local `P-D08-HCC-2022` XML contains the linked 2026 retraction notice (DOI 10.1002/prp2.70222, PMID 41689298). The original is quarantined, its source/profile disclosure is corrected, and it supports no synthesis or grade. Existing REVIVE quarantine is preserved. No current comprehensive integrity search is claimed.

## Reproduction and review handoff

`candidates.json` retains exact authored row/public-row scope, findings, uncertainty, domain judgments, source-native locators and actual original-file bindings. `assessments.json` records the resulting exact assessment fingerprints. Downloaded full texts and derived full-text copies remain outside Git/public assets. Source verification depends on the local corpus paths listed in `source-access.json`; a clone without those holdings must report the missing dependency rather than substitute a web fetch or claim the source hash check ran.

Run from the application root:

```sh
python3 research/batches/FILL-REMAPRX-1-STEP2/appraisal/project.py
node scripts/evidence-assessments.mjs --write
python3 editorial/outcome-summary/build.py
python3 research/batches/FILL-REMAPRX-1-STEP2/appraisal/account.py
node research/batches/FILL-REMAPRX-1-STEP2/verify.mjs
node scripts/check-outcome-summaries.mjs
```

The bounded projector refuses a changed existing candidate rather than silently replacing or rehashing a prior assessment. The repeat check verifies zero byte changes in projected records/accounting. Existing 62 raw/public syntheses and certainty assessments and 60 public/private summaries remain deep-equal to the wiring baseline. The original audit’s synthetic missing/unappraised rejection checks remain active, with new comparison/date/nonclinical regressions. `validation.json` records final commands and actual results; `browser-validation.json` records local interaction checks separately. Neither is independent/human scientific acceptance or release authorization.

Next safe work after exact draft acceptance: arrange the explicitly queued missing artifacts through the authorized researcher; perform remaining source/condition coverage and independent/human reviews under fresh applicable readiness; obtain separate merge/release decisions. PR #3 stays stacked on PR #2 and draft. No merge, deployment, Sites write, indexing-policy change, credential creation or D22 import is part of this continuation.

Local browser outcome/drawer/citation checks passed with explicit runtime limitations: Vinext RSC prefetch setup errors and a missing guide-library JavaScript preload chunk were observed. The required outcome flow remained functional; no error-free browser, account/library acceptance or broader runtime repair is claimed. The source-reference link updates the correct hash, with the matching target visible after closing the research drawer. See `browser-validation.json`.
