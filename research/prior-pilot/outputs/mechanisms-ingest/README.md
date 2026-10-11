# Mechanism ingestion addendum 1.0

The schema, coverage obligations and validator are adopted prospectively in Mission Control. See `adoption-record.json` and `adoption-validation.json` for the exact registered versions and 24 integration checks. **Mechanism extraction, scientific acceptance and publication remain HOLD.** This task performed no new scientific extraction, acquisition, web search, import, site edit or external dispatch.

The existing portfolio is **30 generic drugs, 30 distinct conditions and 126 candidate drug–condition pairs**. Those pairs are search/coverage obligations, not established indications or mechanism findings. The separate drug and condition axes are retained; no 900-pair matrix is invented. Itraconazole remains an owner-required cancer target, separated by exact cancer type and setting. Additional recorded drug/question scopes remain visible without inflating either target count.

## What the next ingestion must capture

For each drug, retain its source-reported original-use mechanism separately from the rationale for each proposed condition. A known target in one use does not establish that target's relevance in another. The record must identify:

- Target or pathway, and the source-reported action/direction: binding, activation, inhibition, increased/decreased marker, mixed result or no detected change.
- Original-use mechanism and exact proposed-condition rationale, each supported independently; unverified regulatory status remains unverified.
- Species/model, cell line or tissue where printed, human population and relevant condition subtype/stage; formulation/route, dose or concentration, duration and comparator where reported. Experimental exposure is descriptive research information.
- Whether the claim is a direct measurement, author inference/hypothesis, computational prediction, secondary description or regulatory description. These labels belong to each claim, since one paper can mix measured results and hypotheses.
- Target-engagement evidence: assay and what it measures, binding/occupancy versus a downstream marker or phenotypic change, relevant timepoint/exposure, comparison, uncertainty and whether engagement was actually measured. A downstream change does not automatically demonstrate direct binding or target engagement.
- Causal evidence: the reported perturbation, knockdown/knockout, rescue, dose response, temporal evidence or other test, including controls and the authors' stated interpretation. Correlation, expression similarity or docking is not upgraded to a demonstrated causal pathway.
- Negative/null/contradictory observations, failed target engagement, conflicting mechanisms and decisive applicability/exposure/measurement limitations. Preserve competing explanations.

Every factual field links to a source-reported claim. Every claim and typed number links to a durable locator in the exact file hash. PDF locators retain physical page, printed page or explicit absent pagination, section and table/figure/row/column anchor. HTML/XML/EPUB locators require native path and fragment/XPath. Exact source IDs, filenames, printed DOI or `DOI NOT PRINTED`, authoritative manifest metadata, report identity and study-family uncertainty remain separate.

The schema includes explicit `not_extracted`, `not_reported`, `not_accessible`, `not_applicable`, `not_checked`, `not_identifiable` and `conflicting` states. `not_reported` requires a fully inspected source; missing extraction or inaccessible full text cannot be recast as absent reporting. Numbers never default to zero. Percentage, percentage points, relative change, dose, concentration, sample count and model score remain separate quantity types.

Mechanistic plausibility is not evidence of clinical efficacy. Human, animal, cell/ex-vivo, computational and context tiers remain distinct. A mechanistic observation in patients does not itself establish patient benefit. Original-use description, a review's rationale, primary mechanistic results and clinical outcome synthesis remain linked but separate. The intake schema deliberately has no certainty-grade or efficacy-verdict field and fixes candidates to **pending verification / pending human review / draft publication / Not appraised**. All candidates are excluded from accepted scientific support until the separate acceptance process.

## Preserve governing history

The active future acquisition packet is plan **SL-INGEST-3.1-FETCH30**, packet 2.1. It is acquisition-only. This addendum does not edit it or authorize dispatch.

Actual Worker B and the Worker A F00 subset receipts cite the immutable **SL-INGEST-3.0-FETCH30** plan and schema. Validate those returns under their own governing versions. Missing new mechanism fields are future-work gaps, not retroactive 3.0 schema failures. The inspected local record covers A's F00 cross-reference subset; it does not prove F01/F02 ingestion.

Worker B's current-state reconciliation is explicitly retrospective: its original pre-ingestion planning gate was not satisfied. The later source revalidation does not backdate compliance. The three private outcome candidates and seven candidate outcome entries remain unapproved and outside the canonical scientific store. The remaining extraction queue is not mechanism-complete. Retracted REVIVE and unlinked replacement records, unresolved correction/identity links and existing numerical conflicts retain their exclusions/holds.

See `governing-version-reconciliation.json` for exact paths, hashes and scope. Counts are copied from recorded receipt/reconciliation metadata; this task did not re-open all scientific sources or independently repeat archive verification.

## Files and execution

- `mechanism-ingestion-addendum-v1.0.json`: prospective contract, dependencies and release boundaries.
- `mechanism-record.schema.json`: machine-readable candidate record schema.
- `coverage-requirements.json`: all 60 target records, 126 sparse pair obligations and preserved ancillary scopes. “Not extracted” means not mapped under this new mechanism contract; it does not claim that no accepted source contains mechanism information.
- `mechanism-records.pending.json`: empty real candidate envelope, with zero new findings.
- `synthetic-fixture.EXCLUDED.json`: clearly fictional null mechanistic example. It is not a paper, real drug result or production seed.
- `validate_mechanisms.py`, `test_contract.py`, `validation.json`: schema and graph validation plus adversarial checks.
- `NEXT-INGEST-INSTRUCTIONS.txt`: copy-ready **internal continuation** instructions. It is not an external acquisition request and must not be sent as a fetch job.
- `readiness.json`, `gaps.json` and `input-fingerprints.json`: precise readiness scope, unresolved work and preserved input hashes.
- `adoption-record.json`, `test_adoption.py`, `adoption-validation.json`: prospective Mission Control adoption and narrow integration proof; `adoption-before/` preserves the exact prior instruction/controller versions.

Run from this project:

```sh
python3 outputs/mechanisms-ingest/test_contract.py
python3 outputs/mechanisms-ingest/validate_mechanisms.py
```

A later nonempty real batch also requires `--source-manifest` pointing to an independent receipt-matched identity manifest. That JSON maps source ID to the corresponding source object fields. The validator checks filename/hash/printed and authoritative DOI, governing plan, receipt, collection/tier, quarantine and correction state against it. The operational plan must pin that manifest's hash; a worker's self-declared source list alone is insufficient. The isolated synthetic fixture is allowed only with `--allow-fixture`.

The checks cover schema, links, classifications and preservation. They cannot prove that a sentence accurately paraphrases its source, that a measurement is valid or clinically relevant, or that a human review occurred. The later source audit must inspect the actual passages and important tables/figures. Do not substitute a validator PASS for those steps.

## Current readiness

Contract validation passes and the mechanism requirement is adopted prospectively. `outputs/mission-control.json` → `mechanismIngestionRequirement`, the appended AGENTS/current runbook instructions and the shared preflight now register it. The exact addendum/schema/coverage hashes are unchanged. No file-specific extraction operation, source assignment, source audit or scientific release is asserted. Before the next compatible scientific operation, its plan must incorporate the adopted `mechanism_contract` hashes, reconcile its actual receipt/source assignments and pass P2/P3 as applicable. The shared preflight reports the requirement without granting extraction/import readiness under the existing acquisition-only3.1 contract. This is a planning dependency, not an additional owner-permission request.

Reuse accepted source-located mechanism facts first. Add a mechanism mapping where supported; do not redo completed ingestion or silently replace existing claims. Any truly missing source goes to a separately authorized future acquisition gap. Unchanged inputs must create zero duplicate canonical mechanism records on repeat import. UI implementation and the universal **Mechanisms → Mechanism of Action** section are owned by root and are not claimed complete by this package.
