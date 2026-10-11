# Current prerequisite — owner intervention, 8 October 2026

Read ingestion-plan-v1.0.md/.json and ingestion-plan-readiness.json before every acquisition handoff/request, including scoping/direct workers, and before extraction/import. Mission Control records GP prospective PASS after retrospective B00 reconciliation; earlier first ingest/handoff did not satisfy the newly adopted ordering. Run check-ingestion-readiness.py from the project root with the actual operation/batch. Received sources need P2 receipts; imports need P3 candidate evidence. Internal drafting is not dispatch. Modeling extraction/import remains schema-extension HOLD; keep raw inventory separate. No new owner approval is added. Canonical v1.3 is adopted; v1.1 remains the frozen baseline.

# Second Look update runbook

Owner: this task's Mission Control. One integrator owns `site/`, source acceptance and deployment. This is a private research pilot; this runbook does not authorize scientific release, sales, emails, spending or new automations.

The frozen pilot contract remains `docs/one-match-rule-baseline.md`, v1.1, SHA-256 `01896e3c254f37483c226da52da0ef239b03eb7c762e5171675ae6dc302150d2`. Canonical rule v1.2 now includes the pilot-feedback protocol. Read `outputs/governance/baseline-versus-revised-rule.json` and `rule-sync-report.json`; do not replace the frozen baseline. Local rule synchronization does not update a separately uploaded ChatGPT file or release the site.

## Begin with the actual state

Read `outputs/mission-control.json` and `outputs/handoff/release-report.md` when present, then the last dated acceptance decision for the exact batch/version. Read `outputs/governance/independent-review.json`, `outputs/handoff/post-type-contract.json` and `outputs/governance/review-packet-index.json`. The review packet connects original source URLs/private files, extracted results, claims, Q01–Q15 appraisals and proposed page routes. Missing acceptance is HOLD, not an assumed PASS.

Record the checkout/source version, current Sites revision, audience, hostname and file hashes before changes. Site hosting identity is recorded in `site/.openai/hosting.json`; use the current Sites building/hosting workflow. Do not copy PepsAnon identity, users, credentials, database or merchant. Do not replace another integrator's newer files with an old worker packet.

## Refresh a bounded question batch

Use the exact protocol in `outputs/research/demand/searches.json`, `report.txt` and `topic-map.json`. Keep stable DR IDs, canonical discussion URLs, duplicates, date/access provenance and exclusions. Recent and historical counts remain separate. Recompute priorities with `outputs/research/demand/score_demand.py` only after reviewing its input/output arguments; compare the recent-only ranking and removal of the largest community. Incomplete access and within-protocol saturation are different conclusions. A question ranking is not evidence of efficacy or willingness to pay.

Record the newly asked question, the scientific scope needed to answer it and the affected pages. Do not invent extra questions to hit a count. The initial map has 36 supported clusters under a bounded protocol; it is not a Reddit-wide top list.

## Acquire and reconcile evidence

Use the full `outputs/handoff/grokbot-prompt.txt`, topic manifest and current schema. The earlier scoping prompt is historical. Log translated queries, sources, cutoffs, actual dates, filters, observed hits and zero results. Search the exact drug–indication–population–form/route–comparator–outcome question, including null, adverse and contradictory evidence. PRIMARY and CONTEXT remain separate.

Preserve raw arrivals unchanged under a new `work/evidence/raw/` batch directory. Before importing, inspect the manifest, rights, hashes, actual media type and completeness. Do not replace a failed download with a claim that a PDF was obtained. HTML, a partial tool snapshot, an abstract, a registry and a complete PDF have distinct access and extraction states. Keep copyrighted raw files private unless redistribution rights are verified.

Resolve DOI/PMID/title identities and report/study/experiment relationships before merging. Preserve stable IDs and previous reviewed material. Export unchanged accepted records byte-stably; reconcile received, accepted, duplicate, excluded, context, inaccessible and pending totals. Test repeat import on the same packet. The current pilot builder is a calibration generator, not a generic production ingest service: do not run `work/evidence/build_corpus.py` over later reviewed records without a controlled merge and the corresponding finalize step.

Priority source gaps remain in the source manifest and coverage records: exact COVID-OUT correction text; ACTIV-6 supplement/protocol; current treatment full reports and PAX LC; registry, backward/forward and complete trial-family reconciliation. REVIVE's original remains quarantined until the retraction/republication notice and replacement are reconciled. Do not reactivate supportive claims merely because an old abstract still appears in search.

## Extract, appraise and review

For each accepted report, retain exact source location, extraction basis, units, denominator type, timepoint and uncertainty. Randomized N is not an outcome's analyzed denominator. Use explicit missingness; do not turn inaccessible or unchecked data into zero or reassurance. Visually inspect tables/figures that support consequential numerical claims. Do not claim a PDF visual audit where no PDF was acquired.

Update results first, then claims, review Q01–Q15 and page sentences. Keep original findings, author interpretation and reviewer interpretation distinct. Use an appropriate versioned appraisal method only after its domains have actually been completed. Preserve funding/conflicts and source-integrity check dates. A completed original draft is not a human-reviewed appraisal or formal certainty grade.

Use `outputs/governance/review-packet-index.json` to review the exact source, extraction, proposed claim, rationale and page change together. Record accept/reject/correct/adjudicate with the relevant record version/hash, reviewer and date. Preserve prior decisions. Any consequential change invalidates dependent approval until rechecked. Include new entity, condition, glossary and practical-guide prose in review; passing the four-page calibration corpus does not automatically approve every website route.

Public factual release requires human editorial approval of the exact version. Clinical safety interpretation and paid health products also require an appropriately qualified independent reviewer, with qualifications/conflicts and edition/hash recorded. The guide's five-reader test requires at least four of five representative readers to state the main conclusion and locate its source within two minutes. Do not fabricate those results or mark an agent audit as human review.

## Validate before adapting the site

From this project root, the implemented evidence validator is:

```bash
python3 work/evidence/validate.py
```

It reads the current canonical corpus and synthetic fixture, runs schema/relationship/hash/numeric checks and deliberate failures, and refreshes the evidence validation report. Review the generated report; a command exit alone is not scientific approval. Its four fixed numerical effect checks are calibration checks, not a general audit of future numbers. Add source-backed expectations and appropriate invariants as new designs arrive. Keep synthetic and malicious fixtures outside production evidence.

Record the corpus/schema hashes used. Check record uniqueness, study-family relationships, Q01–Q15, null reasons, event/denominator consistency, units, source locators, page/claim/review references, citation order and exact-version approval. Repeat changed failure cases rather than rerunning unrelated checks without cause.

The integration adapter is `work/sync-content.py`; inspect its current version before use. It normalizes routes/context sources and writes `site/data/content.json`. Use the reviewed `outputs/governance/practical-guide-adapter.json` for the practical page, preserving its exact sentence source mapping and separate worksheet download. Do not mechanically flatten PDF pages or erase citations, lists and worksheet structure. An adapter must preserve IDs, review/access state and source/claim links; compare before/after output.

## Verify the implemented experience

The site package currently provides `build`, `lint`, `dev` and `start` scripts. Run the current Sites build workflow in `site/`; do not invent legacy PepsAnon test commands. The root integrator's `outputs/handoff/route-validation.json` records local route/fragment inspection, not production authentication or scientific approval.

Check the exact new version at approximately 320, 390, 768 and 1280 pixels and at 200% zoom. Test every demonstrated type, the longest guide, a comparison with no direct combination evidence, an abstract-only record, a quarantined source, a page with no accepted studies and an account/error flow. Confirm keyboard operation, focus visibility, Escape/focus return, readable superscripts and decimals, no overflow, stable sticky offsets and print layout.

Exercise first and repeated fragment navigation, back/forward, closed references opening to a citation and FAQ hashes opening the actual answer. Verify one canonical guide Research catalogue, separate context references, truthful counts, no orphan targets and no duplicate public IDs. Check live source URLs with appropriate handling of temporary blocks. Review `post-type-contract.json` for implemented/deferred differences; a shorter bounded type variant needs an explicit recorded scope decision and must not conceal safety gaps.

## Accounts, products and privacy

Use supported Sites identity and site-scoped persistence. Test signed-out rejection, sign-in, exact safe return path, save, reload, private note edit, export, deletion and sign-out. Use two independent test users to establish cross-user isolation. Local header fixtures cannot prove deployed authentication. Protect private data on every read/write/export/delete and keep it out of public HTML, search, analytics and caches.

My guides is separate from Saved research. Commerce is not launched; an honest empty not-launched response is not a purchase test. Before enabling an actual product, complete `outputs/governance/fulfillment-specification.json` against the correct merchant in test mode. Check signed/replayed webhooks, idempotency, delayed/failed/cancelled payments, server-owned price/currency, exact product+edition rights, refunds/disputes, missing files, download isolation and safe login returns. A success redirect never grants an entitlement. Expired research membership must retain valid independently purchased editions.

The complete guide, preview, worksheet and summary are private drafts identified by `guide-release-manifest.json`. Keep paid file bytes private and match them to the reviewed edition hash. Public free resources need their separate editorial gate and should not wait for a merchant. No email collection, campaign, spending or new recurring service is enabled by this runbook.

## Release, correction and rollback

Record exact source/build revision, evidence/product hashes, intended audience/origin and each applicable gate decision before deployment. Save the prior Sites revision and export/back up persistent data using the platform's authorized mechanism; record restore verification. No backup or rollback is claimed merely because this procedure exists. Keep private account state out of shareable source archives.

Use Sites for deployment and verify the actual deployed revision and audience. Distinguish saved source, local preview, private deployment and public availability. Keep factual public pages and commercial release on HOLD until their respective review gates pass. A public sitemap, noindex tag or successful build does not establish indexing, private access or production readiness.

After a consequential correction, identify dependent results, claims, pages, review versions and guide editions. Withdraw unsupported supportive claims while preserving the original record and correction trail. Restore the previous approved Sites revision if a technical release is defective; retain immutable owned editions and make any product withdrawal/support action explicit under the adopted policy. Recheck affected account/storage behavior after rollback. Do not overwrite a later approved version or erase a prior editorial decision.

## Keep the rule feedback auditable

Append each real observation to `outputs/governance/rule-gap-log.json`: frozen clause, failure/ambiguity, evidence, classification, correction and retest. Record extra owner instructions with exact provenance. Ordinary unfinished work, observed implementation defects, tool limits and external review/merchant dependencies do not become reusable rule defects by default.

For confirmed reusable corrections, follow current canonical §15. Re-read the master, update log, sync checkpoint and latest exact relevant task messages; hash before writing and preserve concurrent changes. Update one canonical master, installed skill and ZIP only through the authorized integrator/existing updater. No-op if unchanged. Record a reviewable patch and pending destination when synchronization is unavailable. Keep baseline-versus-revised comparisons and rule-package release separate from site/product release. Do not create a duplicate updater or touch/deploy PepsAnon.

Proposed cadence: monthly saved-query/retraction review and prompt triage of source corrections, scaled to actual capacity. No new Second Look monitoring automation has been enabled by this worker. Record only real measured events, source failures, correction rates, review time and publication lag; do not promise unattended monitoring until authenticated draft writes/readback and source access have been demonstrated.


Current2026-10-09 repair: use fetch-30x30/ingestion-plan-v3.1.json and second-look-fetch-30x30-v2.1-input.zip (prepared, not dispatched). Attach the ZIP to Grok then paste the entire grokbot-prompt.txt. Require returnedZIP(s), deliveryreceipt and fully filled CHATGPT-INGEST-PROMPT.txt. Scientific ingestion awaits receiver verification and a compatible downstream plan.


## Active completeness repair —9October2026

Use `outputs/completeness/review-index.json` and `outputs/handoff/post-type-contract.json` for the current scopes. Preserve `history/private-v2/`,the frozenv1.1rule and prior corpus records. The active fetch is packet2.1/plan3.1; its exact hash is in `fetch30-final-verification.json`. Do not rerun historical generators. Use the prepared reverse-ingest prompt and validate actual receipts before any future extraction; UI deployment does not authorize scientific release. Current owner-private commit:8896f49d2635f891866042485a0da496df2e2129.


## Adopted mechanism requirement for the next scientific operation — 9 October 2026

This section is the current additive instruction for mechanism data; it does not rewrite historical fetch or receipt versions. Read `outputs/mechanisms-ingest/adoption-record.json` and the exact `mechanismIngestionRequirement` hashes in Mission Control. Contract `SL-MECHANISMS-ADDENDUM-1.0`, schema `SL-MECHANISMS-1.0`, is adopted prospectively for the next compatible source extraction/corpus import across30drugs,30conditions and the126existing candidate pairs.

1. Reuse already accepted source-located facts. Preserve raw files, source/report/family IDs, declared tiers, exclusions and review states. Keep original-use mechanism distinct from each proposed condition; never infer clinical efficacy from mechanistic plausibility.
2. Before new scientific extraction, record the actual received-source manifest, exact assigned files, allowed source classes and versioned operational plan. Its `mechanism_contract` must name the adopted plan ID and exact plan/schema/coverage SHA-256 values. Verify hashes and source accessibility; do not fabricate assignments or treat this adoption as P2 readiness.
3. Follow `outputs/mechanisms-ingest/NEXT-INGEST-INSTRUCTIONS.txt`. Capture target/pathway and source-reported direction/action, model/population/exposure, original-use mechanism, condition rationale, target-engagement/causal tests, uncertainty and contrary results. Each fact/number has a file/hash and exact PDF/native locator. Human, animal, cell/ex-vivo, computational and context remain separate.
4. Validate a candidate with `python3 outputs/mechanisms-ingest/validate_mechanisms.py CANDIDATE --source-manifest RECEIPT_MATCHED_MANIFEST`, using real operation paths. Synthetic fixtures are excluded. Preserve explicit missingness; full-source `not_reported` differs from unprocessed or inaccessible fields. Run actual source/number audit and independent review. A successful shape check is not scientific approval.
5. For import, record the existing candidate acceptance checks plus `checks.mechanisms.status = PASS` and its actual `evidence_path`. Match the plan, receipt, source hashes and accepted base; prove idempotent additive mapping. Pending mechanism records do not become released claims.

The shared `outputs/handoff/check-ingestion-readiness.py` now exposes the adopted mechanism requirement and checks its incorporation for scientific operations. The active fetch3.1 checker remains acquisition-only and cannot grant extraction/import readiness. Old3.0 A/B receipts are validated under3.0; CP28 remains2.0. Do not retrospectively fail returns for fields they were not asked to supply or backdate earlier planning compliance. No acquisition, extraction, import or release is performed by this adoption.
