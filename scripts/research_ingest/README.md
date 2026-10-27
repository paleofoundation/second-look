# Guarded research ingestion

Python 3.11+ and the pinned packages in `requirements.txt` are required. Run from
the application repository root: `python3 -m scripts.research_ingest --help`.
The engine does not acquire papers, extract scientific findings, assign grades,
approve reviews or publish. Only the integrator runs `apply`.

This implementation adapts the guarded staged-file importer, identity resolver
and exact-version preflight from the preserved SL-F01/F02 lineage. Original code
and receipts remain unchanged. The source lineage is in
`One Match Rule/work/ingest/SL-F01-F02-20261011/engine/` and the corresponding
original research project's `outputs/ingest/SL-F01-F02-20261011/governance/`.
Those source locations are provenance, not runtime dependencies.

## Contracts

`contracts.py` defines executable JSON Schema Draft 2020-12 contracts. Export one
without mutating anything:

```sh
python3 -m scripts.research_ingest schema --kind plan
```

The plan contains `schemaVersion: remaprx-ingest-plan-v1`, `planId`, explicit
`operations`, exact repository-relative `allowedTargets`, and `inputs` containing
repository-relative paths and SHA-256 hashes. Additional scientific planning
metadata is supported, including a `contract` object. An allowlisted directory
does not authorize all its contents: list every target file. Targets are JSON or
JSONL; pinned inputs cannot also be targets.

The candidate manifest contains `schemaVersion: remaprx-candidate-v1`, `planId`,
the byte hash `planSha256`, `batchId`, `author`, and `files`. Every file contains
`target` (repository-relative), `path` (packet-relative), `sha256`, and
`baseSha256` (null only when the destination did not exist). Paths cannot traverse
parents or symlinks. Each target and payload path must occur exactly once.

The candidate digest hashes canonical JSON of the complete manifest: sorted keys,
UTF-8, compact separators, no NaN/Infinity, and one final newline. `validate` and
`diff` print it. The plan hash always hashes the original saved plan bytes.

`stage` and `apply` require a GP readiness file with schema version
`remaprx-gp-readiness-v1`, `status: PASS`, `scope: GP_PLAN`, matching `planId` and
`planSha256`, and a timezone-qualified `checkedAt` timestamp. `preflight` performs
validation plus this readiness check. `validate` and `diff` alone do not claim GP
readiness or permit extraction.

`apply` additionally requires an acceptance file with schema version
`remaprx-acceptance-v1`, `status: PASS`,
`scope: technical_candidate_integration`, matching plan/batch/digest/author,
a distinct `auditor`, timezone-qualified `reviewedAt`, and exactly one hashed
report for each kind: `schema`, `identity`, `source_integrity`, `preservation`,
`idempotence`, `independent_audit`. These are technical acceptance records and
must never be represented as human scientific approval.

Each report must contain `status: PASS`, the exact `candidateDigest`, the complete
candidate `targets` list, `inputHashes` mapping candidate packet paths to hashes,
and nonempty named `checks` whose values are true. Independent audit additionally
requires matching `author`/`auditor` and nonempty `evidence` pins (packet-relative
`path` and `sha256`). Other reports may also pin supporting evidence. These fields
must describe checks actually performed; the engine verifies identity/bytes and
structure, not the truth of scientific or reviewer judgments.

## Commands

Supply `--root` with the application repository and `--packet` with the candidate
packet directory. The explicit plan/manifest/readiness/acceptance file arguments
may be absolute or relative to the current working directory.

```sh
python3 -m scripts.research_ingest validate --root APP --packet PACKET --plan PLAN --manifest MANIFEST
python3 -m scripts.research_ingest preflight --root APP --packet PACKET --plan PLAN --manifest MANIFEST --readiness GP
python3 -m scripts.research_ingest diff --root APP --packet PACKET --plan PLAN --manifest MANIFEST
python3 -m scripts.research_ingest stage --root APP --packet PACKET --plan PLAN --manifest MANIFEST --readiness GP --out STAGING
python3 -m scripts.research_ingest apply --root APP --packet PACKET --plan PLAN --manifest MANIFEST --readiness GP --acceptance ACCEPTANCE
```

`stage` writes a separate exact-byte candidate snapshot and manifest. It does not
copy audit reports or readiness/acceptance; use the original complete packet when
applying, or explicitly transfer and verify those contracts with a moved snapshot.
`diff` reports create/replace/unchanged files with before/after hashes. Canonical
files may match only the declared base or the exact already-imported candidate.
Unchanged repeat imports are no-ops. Every canonical apply repeats preflight
inside one store-wide lock and caches the approved bytes before writing.

Local state lives in `.research-ingest/` at the application root. Each file replace
is atomic and fsynced; the whole multi-file operation is **not** atomic. Intent
journals and durable backups precede writes. Caught failures roll back exact
written bytes; concurrent edits are preserved and produce HOLD. A process crash
leaves a visible unfinished journal and possibly a stale lock.

```sh
python3 -m scripts.research_ingest recover --root APP
python3 -m scripts.research_ingest recover --root APP --journal JOURNAL --rollback
python3 -m scripts.research_ingest recover --root APP --clear-stale-lock
```

Recovery is read-only by default. Rollback verifies all before/after hashes and
backups before restoring anything, and refuses a live lock owner. Clearing a
stale lock without rollback is allowed only when no incomplete journal exists.
Do not delete local recovery state while an operation is pending.

Source availability uses the shared inventory without creating another inventory:

```sh
python3 -m scripts.research_ingest resolve --source-map source-locations.json --source-id SOURCE_ID
python3 -m scripts.research_ingest resolve --source-map source-locations.json --source-id ARCHIVE_ID --archive-member MEMBER_PATH
python3 -m scripts.research_ingest resolve --existing known-identities.json --incoming proposed-identities.json
```

Source resolution verifies actual file/member bytes; it does not imply the source
was scientifically inspected. ZIP members are streamed without extraction.
Identity files are JSON arrays with `id` and optional `doi`, `pmid`, `sha256` and
`canonicalId`. The resolver proposes existing matches/conflicts, never performs
merges or treats shared file bytes as proof of report identity. The integrator
resolves new IDs and ambiguous/conflicting matches before integration.

Scientific candidate validation consumes the adopted source schema and the exact
assignment bundle pinned by the GP plan:

```sh
python3 -m scripts.research_ingest validate-source --root APP --schema SOURCE_SCHEMA --candidate SOURCE_CANDIDATE --assignment ASSIGNMENTS --plan PLAN --readiness GP
```

The assignment may be a single object or a bundle containing nested per-file
assignments. Exactly one record must match the candidate's `assignment_id` and
`source_id`; it carries `canonical_report_id`, `batch_id`, `sha256`, `bytes`,
`media_type`, actual `path`, and any `integrity_hold`. `--source-file` remaps source
access without changing the expected source hash. A non-null mechanism payload
requires `--mechanism-schema` pointing to an executable schema also pinned by the
plan. The candidate/schema shape preserves the recovered snake_case scientific
contract; it is distinct from the camelCase file integration manifest.

This check validates actual assigned bytes, Q01–Q15 uniqueness, result/claim
relationships, source-bound locators, numeric quotations and table/figure visual
check assertions, partial versus full-source reading logs, and quarantine/context
boundaries. True `not_reported` requires full-source inspection. It neither
completes unanswered questions nor proves that a read log, quotation or scientific
judgment is correct; independent source audits remain required.

Mechanism payloads require the executable `RRX-MECHANISM-CANDIDATE-1.0`
schema; descriptive field lists and empty schemas are rejected. The validator
checks assigned source/report/hash identity, unique mechanism/step IDs, result
references and exact result locators for tested steps. A complete mechanism
cannot retain unextracted fields or partial-source inspection. Proposed/inferred
steps remain explicitly distinguished from tested steps and clinical benefit.

Each non-null numeric value must equal its reported scalar. Normalization accepts
Unicode decimal digits, mathematical minus, middle-dot decimals, conventional
comma thousands grouping and scientific notation. It does not convert units or
percentages, infer thresholds, or parse ranges/ratios. Those forms stay on HOLD
until an explicit derived/qualified-value contract exists; units are a separate
field and the unmodified reported scalar must appear in its source quotation.

## Verification

```sh
python3 -m unittest discover -s tests/research_ingest -v
```

Tests use isolated temporary directories and synthetic fixtures. They exercise
repeat imports, source/plan/acceptance hashes, independent audit binding, GP gates,
traversal and symlinks, concurrent edits, cross-batch lock contention, interrupted
writes, rollback and recovery, identity conflicts and source availability.
The clinical extraction, Q01–Q15, numerical and app-specific schema/reader checks
remain separate required checks for actual research integration.
