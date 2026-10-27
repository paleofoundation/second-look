# RRX-CONDITION-001 planning validation

Checked 2026-10-12T12:07:18.432753+00:00. This is schema/planning verification, not GP readiness or scientific acceptance.

## Passed checks

- Both JSON contracts parse; the coverage schema passes Draft 2020-12 meta-schema validation with `jsonschema.Draft202012Validator`.
- The explicitly labeled `example.synthetic.json` validates with format checking. Its `.invalid` URLs, synthetic IDs and dates are illustrative only; it is excluded from production research and counts.
- The 31 target condition IDs match the inspected canonical inventory; the separate aging goal is not counted as a condition.
- Coverage-schema hash and pending operational-state flags match the saved plan.
- Eight invalid-record probes were rejected:
  - Unknown stage count without missingness reason.
  - Coverage-only packet changes publication to released.
  - Unsupported scoped completion.
  - Planned query claims executed timestamp and returned results.
  - Included candidate has unresolved repurposing eligibility.
  - Duplicate lacks canonical duplicate target.
  - Candidate has no discovery source link.
  - Pending candidate omits next action.

## Concurrent input changes

6 of 10 initially observed reference hashes still matched at the recorded check. The remaining references changed during active work by the research integrator:

- `research/batches/RRX-INGEST-001/plan.json`: changed_after_initial_inspection.
- `research/batches/RRX-INGEST-001/readiness.json`: missing_during_concurrent_update.
- `research/batches/RRX-INGEST-001/schemas/candidate.schema.json`: changed_after_initial_inspection.
- `research/batches/RRX-INGEST-001/grok/RRX-GAP-001/plan.json`: changed_after_initial_inspection.

Exact old/observed hashes and timestamp are preserved in `plan.json` → `referenceReconciliation`. The initial all-reference pin check failed, and a later check encountered a temporarily absent readiness file. No existing plan, schema or receipt was altered by this packet. Live dependency reconciliation remains pending; no operational GP PASS is claimed.

## Limits

The schema checks structural fields, missingness and selected incompatible states. Exact source identity, eligibility, search completeness, cross-record links, direction/interpretation agreement, independent-family counts and scientific relevance still require the semantic checks listed in `plan.json` and source review. No searches, acquisition, extraction, source audit, appraisal, import, UI implementation or release were performed by this planning task.

Validation command used the already available `jsonschema` package via `PYTHONPATH=/Users/kmfp/Documents/Codex/2026-10-08/one-match-drug-repurposing/work/evidence/python`; no dependency installation or network access was needed.
