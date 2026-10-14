# Prospective full-report review contract

This contract was created for the October 12, 2026 continuation. It does not change or reclassify historical CAL07 extraction records. One canonical report has one full review, referencing its main version and all assigned required companions. Optional alternative representations do not create another review obligation.

`full-review-assignment.schema.json` identifies the report, review and all assets. Each available asset has its exact identity, hash, byte count, media type and an enumerated inspection-unit inventory. PDF units use consecutive physical page numbers starting at one. Native HTML units use the assigned stable section/figure or document location. Images use their assigned image location. Required missing assets remain explicit and prevent completeness. The integrator and independent reader must assess whether the assigned unit inventory covers the actual source; this validator cannot infer scientific coverage from a nonempty log or from PDF/HTML signatures.

`full-review.schema.json` separates 67 input fields from 15 written answers using the pinned `rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json`. A written answer does not close unfinished inputs. `reported`, `not_reported`, `not_applicable` and `assessed` are closed input states. `partial`, `not_extracted`, `not_accessible`, `not_checked`, `not_identifiable` and `conflicting` remain unfinished. An identity that remains unidentifiable after a completed, bounded investigation may be recorded as `assessed`, with the actual negative finding, inspected scope and specific rationale; unresolved identity work stays `not_identifiable`.

Reported facts already read in the main report may remain closed in a draft while a required companion is pending. Absence assertions require the entire required source packet to be inspected and included in that field's assessed-asset list. Actual source limitations—such as unreported randomization, qualified measurements or a byline difference between versions—can be explained after inspection. Do not normalize conflicting metadata into one invented value or use missing work as a scientific limitation.

Each inspection unit needs an actual timestamp, reading method and notes. Complete assets require every assigned unit. Image inspection is visual; consequential figure/table numbers also require visual inspection. Every required unit has a `resultCoverage` disposition linking its results or a source-located explanation that it has no applicable result. This includes methods/metadata units, which can honestly carry the latter disposition. Unfinished coverage prevents completion.

Preserve source → experiment → arm/outcome/result → claim relationships. Complete original-report candidates require nonempty experiment, result and claim arrays; every experiment has results, every result reaches a claim and source-unit coverage, and numeric claims resolve to their input field and scoped result. Reuse prior IDs for the same findings, including the earlier CAL07 R/CL IDs. Do not infer study-family identities or merge overlapping reports from acquisition labels. Mechanism-specific downstream payloads remain separate from full-review completion.

Numerical values in this first contract are exact reported scalars only. Preserve units, source locators, reported text and declared precision. A qualified quantity such as “approximately 800 nM” may retain its literal `reportedText`, `value: null` and a specific limitation without inventing an exact scalar. `graph_estimate` and `calculated` entries must retain null numerical values and explicit limitations; calculation intent also requires provenance. This contract does not authorize graphical estimates, rounding, conversions or derived estimates. A future numerical contract can add them prospectively. Textual answers remain subject to independent verification of every numerical statement; the validator cannot recognize every quantitative assertion embedded in prose.

Source integrity has five distinct dated checks: version, access, supplements, registration and corrections/retractions. Each closed check requires actual source-located evidence, its precise permitted scope and limitations. A checked closed packet does not imply a current web search. Inaccessible or conflicting required checks stay unfinished.

The generated `full-review.template.json` is an uninspected draft of the current assignment. Its zero `planSha256` and placeholder author must be replaced by the actual prospective GP plan hash and author identity. It contains no performed inspection, scientific answers or invented experiment/result/claim identities. Regenerate from `scripts.research_full_review.make_template` if the assignment changes; do not reuse the template's old assignment hash.

Run from the application repository with the declared Python dependencies installed:

```sh
python3 scripts/research_full_review.py \
  --root . --plan SOURCE_PLAN --readiness SOURCE_GP \
  --assignment ASSIGNMENT --candidate CANDIDATE \
  --schema research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/schemas/full-review.schema.json \
  --question-map rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json \
  --source-map LOCAL_SOURCE_LOCATIONS
```

The prospective plan must allow `full-review-validate` and pin the assignment, all three executable schemas, question map, validator, `scripts/research_ingest/cli.py` and `scripts/research_ingest/source_validation.py`. A local source map is an optional remappable path binding: its exact invocation hash is returned, and resolved identities/bytes must still match the pinned assignment. The source map may change roots without changing candidate or assignment authority. Without it, assignment paths are local conveniences. Validation detects changes to controls and source files during the operation.

`PASS` with `completionState: draft` means structurally valid unfinished work. `candidate_complete` requires all required assets fully inspected, all 67 inputs closed, 15 substantive source-located answers with appraisal rationale, complete result accounting and closed integrity checks. These remain author assertions requiring independent source verification.

`full-review-audit.schema.json` is a separate later receipt. Passing it via `--audit` requires a complete candidate, exact candidate/plan/assignment/question-map/source hashes, actual hashed audit evidence and a different auditor identity (ignoring letter case). It may yield `accepted_private`. It never grants human approval, publication, complete study-family knowledge or clinical certainty. `humanApproval`, `released` and `performedImport` remain false; no canonical or public files are written.
