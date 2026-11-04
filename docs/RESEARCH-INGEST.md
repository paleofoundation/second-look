# Research ingestion — required collaborator runbook

**Read this before requesting research files, extracting sources or importing evidence.** This is the repository entry point for the owner's requirement that another researcher can continue without losing prior work. Read the complete [One Match Rule](../rules/one-match-rule/ONE-MATCH-RULE.md), especially sections 4–5, 8, 13 and 15, alongside the [project rules](PROJECT-RULES.md). This runbook maps those requirements to the actual Second Look files; it does not replace them.

## Start from the accepted state

The active continuation is [RRX-INGEST-001](../research/batches/RRX-INGEST-001/PLAN.md), adopted 12 October 2026. Use its current handoff/readiness and source resolver, not the stale pilot totals. It reconciles the original external acquisition/draft-science stores, later F00–F08 returns, the mechanism expansion and MOA-01 with the application. Its private checkpoint and scientific acceptance are distinct. The prospective plan must pass before dependent work; an inventory or recovered historical receipt is not that pass.

The October 12 condition-page correction adds the prospective [RRX-CONDITION-001 plan](../research/batches/RRX-CONDITION-001/PLAN.md) and [condition page contract](CONDITION-PAGES.md). Condition research starts from the condition and discovers eligible repurposed interventions beyond existing drug seeds. RRX-INGEST-001 recovery and RRX-GAP-001 repair retain their original scope and immutable receipts; they do not establish that all condition interventions have been investigated. The new addendum records planning requirements, not an acquisition/extraction/import PASS. Fill and validate its operational condition briefs, source access, schemas and worker packet before dispatch.

Pull the current branch, record the Git commit, inspect changes from other researchers and identify the integrator for the batch. Read `data/ingestion-status.json`, `data/acquisition-status.json` and relevant editorial ledgers. Determine the last **accepted** batch and exact source/record versions; the most recent file or historical PASS is not automatically acceptance. If acceptance cannot be established, keep that portion on HOLD while reconciling it. Do not restart the corpus or backdate readiness.

| Material to carry forward | Repository location |
| --- | --- |
| Current rule and research review input requirements | `rules/one-match-rule/ONE-MATCH-RULE.md` and `rules/one-match-rule/references/research-reviews/` |
| Current article/source records and evidence findings | `data/content.json`, `data/reader-evidence.json`, `data/review-envelopes.json`, `data/private-reviews.json` |
| Source aliases, corrected identities, exclusions and scope | `editorial/reader-source-aliases.json`, `editorial/reader-source-corrections.json`, `editorial/retired-background-outcome-rows.json`, `editorial/parent-guide-scopes.json` |
| Outcome assessments and method | `editorial/evidence-assessments.json`, `editorial/EVIDENCE-GRADING.md` |
| Bounded mechanism expansion plan and schema | `editorial/mechanism-expansion/ingestion-plan.json`, `mechanism-extraction-schema.json` in the same directory |
| Mechanism source receipt/extraction and Q01–Q15 inputs | `editorial/mechanism-expansion/fulltext-manifest.json`, `source-extraction-ledger.json`, `review-inputs.jsonl`, `review-question-input-map.json`, `coverage-ledger.json` |
| Wiki/source foundation plan and extracted records | `editorial/wiki-foundations/` |
| Prior portfolio plan, 30-drug/30-condition registries, search/coverage maps and return schemas | `research/prior-pilot/outputs/handoff/fetch-30x30/` |
| Original plan, readiness, ingestion chronology and update procedure | `research/prior-pilot/outputs/handoff/` and `research/prior-pilot/outputs/governance/` |
| Prospective original mechanism contract and adoption | `research/prior-pilot/outputs/mechanisms-ingest/` |
| Pilot checkpoints and original rule defects/instructions | `research/prior-pilot/outputs/mission-control.json`, `docs/rule-history/` |

`research/prior-pilot/` is a hash-preserved historical archive. Its original relative/absolute paths, older rule versions, prompt dates and acceptance claims are provenance. The files are available for reconciliation, **not authority to run an old generator over today's records or dispatch an old fetch prompt**. The current eight-drug mechanism plan is a bounded operation, not a replacement for broad portfolio coverage. No new corpus ingestion is performed by this repository handoff.

Raw papers/full texts are deliberately not bundled. Their manifests preserve names, hashes and source URLs; arrange lawful access through the integrator or retrieve permitted originals under the new plan. A path on the original researcher's computer is not access for a collaborator. Record unavailable sources as gaps; do not infer that a source was inspected because its extracted record exists.

## Before acquisition or extraction: persist the plan

Create a versioned packet under `research/batches/<batch-id>/` using the [handoff template](../research/INGEST-HANDOFF-TEMPLATE.md). The template is not a passed plan. Reconcile the existing source/identity/coverage records into the actual operation. The saved plan must specify:

- Drug, condition, question and outcome scope; distinct target registries; discovery versus closed-packet restrictions; inclusions/exclusions and PRIMARY versus CONTEXT tiers.
- For condition roundups: an open candidate universe beyond the initial 30 drugs; condition synonyms/subtypes and condition-wide discovery as well as drug-specific follow-up; source-backed original/proposed-use eligibility; candidate dispositions; exact drug–condition–purpose–population–route–comparator–outcome–timepoint mappings; positive, null, mixed, harmful, preclinical and no-result coverage; separate search, receipt, extraction, appraisal, synthesis and release progress. Search logs and dispositions must support any coverage claim. A candidate link, completed recovery packet or absence from the owned corpus cannot establish completeness or no evidence.
- Real worker-readable inputs and source access; named search/full-text locations, question-specific queries, actual cutoff and permitted sources. Preserve explicit owner targets separately from observed demand and scientific efficacy.
- Machine-readable schema/version, stable identity rules, file manifest/hash layout, exact numerical and claim locators, missingness states and source integrity/correction handling.
- Original-use and condition mechanisms, tested/proposed/inferred steps, model, exposure and translation limits. Every cited research paper needs a Q01–Q15 input map, including secondary research.
- Batch ownership, calibration, validation, bounded output location, merge strategy, repeat-import check, preservation of accepted editorial work, rollback and downstream page/review/synthesis mappings.
- A real delivery method and receiver-accessible layout. External Grok returns must include actual manifests and a filled `CHATGPT-INGEST-PROMPT.txt`; source URLs alone do not prove delivered files.

The integrator records GP Plan PASS with plan/schema hashes, date, scope and reasons **before** acquisition/file-request handoff and before substantive extraction/import. Recheck material changes. Missing or mismatched plans hold dependent work; independent inventory/design can continue. This is a planning check, not another routine owner approval or scientific approval.

## Receive and extract without changing history

1. Inventory raw arrivals immutably outside public assets and Git. Verify actual filenames, bytes, hashes, media types, rights, supplements and manifest totals. Failed downloads, abstracts, registry records and full texts remain distinct.
2. Resolve canonical paper IDs from verified DOI/PMID/exact title with an audited alias map. Preserve separate paper/report, study-family, experiment, outcome, claim and review identities. Do not collapse separate DOI reports or count overlapping participants twice.
3. Reconcile accepted, duplicate, context, excluded, inaccessible, unreadable and pending entries. Preserve packet-specific metadata authority and literal missing markers. In closed-packet mode, do not repair absent facts from the web or memory.
4. Extract each eligible source with exact file/hash and page/table/figure or stable native section/paragraph locators. Preserve units, numerator/denominator, population/model, comparator, timepoint, uncertainty and extraction basis. Visually inspect consequential numeric tables/figures. Do not confuse randomized and analyzed N, percentages and percentage points, within-arm change and between-arm effects.
5. Retain `not_reported`, `not_extracted`, `not_accessible`, `not_applicable`, `not_checked` and `not_identifiable` as different states. Unperformed work is never a zero or evidence of no effect. Track every unfinished eligible source and its next action.
6. Carry corrections, retractions and quarantines forward. A changed source reopens dependent claims, assessments, reviews and products. Never reactivate held conclusions merely because an older abstract is available.

## Merge, review and publish through separate gates

For resumed private downstream mappings, resolve every current guide ID against the current canonical registry and record its content hash, title and route. A legacy identifier can name another drug in the current registry. Preserve historical packets; correct only the affected current candidate through a versioned prospective amendment and exact re-audit. Source locators must directly support each repeated numerical estimate in every result group, and typed fields must cover their complete source scope. When a typed record has one primary native locator, explicit additional source locators may carry the remaining direct support. Source fidelity, mapping fidelity and scientific acceptance remain separate. This source-specific correction arose from CAL07 root findings F01-F03 on October28; its original and corrected versions are retained.

Prepare a candidate/diff before changing canonical records. Reuse existing IDs and previously accepted material; preserve raw evidence and editorial decisions. Re-importing the same unchanged packet must not duplicate papers, claims, modules, citations or counts. Compare the proposed merge against current `main` immediately before integration; resolve concurrent work explicitly. Historical calibration builders are not safe full-corpus reset tools.

Update linked results → claims → scoped synthesis → Q01–Q15 reviews → page/FAQ/mechanism records. Preserve parent breadth and source restrictions. Regenerate public projections through the current shared pipeline; never patch only a visible copy while leaving the generator to restore an old finding. Keep private process fields out of reader pages and payloads.

For condition pages, reconcile all relevant accepted syntheses and every discovered candidate disposition against the condition coverage ledger. Reuse the same scoped findings and assessments on drug and condition pages, with explicit applicability for broader/narrower condition mappings. A grade for one outcome is not a drug-wide grade; preclinical or registry support is not clinical benefit. Check the whole parent description, overview, intervention explanations, safety, FAQs and right rail for accidental single-drug scope. No condition-completeness claim passes solely from source counts, populated headings or correct reverse links.

Scientific assessment is separate from extraction status, human approval and release. Selected-source High/Moderate/Low ratings require the adopted method, scoped source-backed rationale and current evidence fingerprint. They are not automatic design scores, formal GRADE, completed full-text reviews or independent clinical approval. Every cited scholarly paper retains exactly one canonical review and its Q01–Q15 coverage, with incomplete reviews honestly pending.

Run relevant checks from the app root:

```sh
node scripts/check-governance.mjs
node scripts/content-check.mjs
node scripts/reader-check.mjs
node scripts/check-reader-sections.mjs --all-profiles
node scripts/check-evidence-section.mjs
node scripts/check-evidence-grading.mjs
node scripts/check-wiki-links.mjs
npm run build
node scripts/verify-reader-boundary.mjs
```

Also validate the actual batch against its declared schema and relationships, hashes, receipt totals, repeat import and numerical/source checks. Existing app checks do not certify arbitrary packet schemas. Inspect affected rendered drug/condition/question/review routes, citation order, exact evidence-panel sources and public/private payload boundaries. Record exact commands and results; do not mark an unexecuted check PASS.

Report acquired, extracted, verified, appraised, human-reviewed, synthesized and released counts separately. Neither a GitHub push nor a build releases a scientific claim. Preserve the site's existing audience, human-review gates, protected-review access and commercial gates.

## Required handoff to the next researcher

Commit the batch plan/schema, receipt and reconciliation, changes to canonical records, acceptance evidence, unresolved gaps and a filled handoff checkpoint together. The checkpoint names input/output hashes and Git revision, stable IDs, actual source access, completed versus pending scope, correction/quarantine state, exact tests, responsible integrator and the next safe action. Record new ingestion rules in `docs/RULE-CHANGELOG.md` and this runbook or the specific schema/contract immediately. Include proposed reusable corrections and their upstream sync status.

Do not rely on a chat summary, a local filesystem path, a source-count total or the outgoing researcher's memory. The receiving researcher must be able to read these instructions and identify the next safe operation from the repository and its explicitly documented external source-access dependency.

## First-tranche calibration continuation

The owner’s October 12 continuation prioritizes the full CAL-07 itraconazole review, then the remaining first-tranche reports. Use the versioned `research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/` scope, source/companion inventories and current readiness. Preserve earlier partial reviews as history; a completed source inspection may conclude that a field is not reported, while an unavailable or unchecked required input still blocks review completion. Acquisition, report review, independent acceptance, human approval and release remain separately counted.

## Outcome summaries and benefit grades

The October 12 owner correction in [OUTCOME-TABLES.md](OUTCOME-TABLES.md) adds a separately versioned clinical benefit summary above retained synthesis records. New or changed evidence must update the summary's compatible outcome/purpose mapping, independent trial identity, report membership, relevant comparison/analysis participant denominator and basis, overlap disposition, effect/uncertainty, benefit rationale and input fingerprint. Never infer an A–F likelihood-of-benefit grade from High/Moderate/Low certainty or merge prevention with established-disease treatment. Carry both assessments forward. Effect-size categories require an outcome-specific basis; otherwise preserve numerical results and unclassified magnitude. Run the outcome-summary check with the existing evidence and source-boundary checks. Current implementation packet: `research/batches/RRX-OUTCOME-SUMMARY-001/`; its status applies only to its recorded existing-source scope, not condition-wide discovery.
