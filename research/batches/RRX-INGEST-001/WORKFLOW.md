# Continuing RRX-INGEST-001

Start with `HANDOFF.md`, `checkpoint-final/closeout.json` and the repository
research runbook. The root source plan/readiness describe the completed CAL-07
operation; subsequent shared-document changes make direct reuse hold. Prepare
a fresh plan/readiness for any new work. The plan hash, input hashes and actual source bytes
must match before dependent work. A PASS in `history/` describes that operation
only. Plans and receipts are immutable once used; preserve a superseded version
before preparing another. One integrator owns canonical integration. Workers
return into their assigned directories and a different worker audits them.

## Environment and source access

Use Python 3.11+ with the packages pinned in
`scripts/research_ingest/requirements.txt`; Node dependencies follow the existing
application lockfile. Do not install dependencies into a historical research
checkout. Raw source access is an explicit prerequisite, independent of this Git
repository. The location registry gives logical roots, relative paths, archive
members, byte counts and SHA-256 hashes. `inventory/README.md` describes inventory
regeneration. On another host, make a local copy of `source-locations.json`,
replace only its logical root paths, and hash-resolve each assigned file. Do not
change historical receipts or assert access merely from a URL.

```sh
python3 -m scripts.research_ingest resolve --source-map LOCAL_SOURCE_LOCATIONS --source-id SOURCE_ID
python3 -m scripts.research_ingest resolve --source-map LOCAL_SOURCE_LOCATIONS --source-id ARCHIVE_ID --archive-member MEMBER_PATH
```

For extraction, `--source-file LOCAL_FILE` supplies the alternate file location;
the expected source hash and assignment remain unchanged. Archive members can be
resolved and hashed without extraction. If a member must be opened, copy it only
to an explicit private source directory outside Git/public assets. A missing or
changed file is HOLD, not a reason to substitute another report silently.

Concurrent app work was present during this checkpoint. `app-inputs/` contains
preserved snapshots for replay. Reconstruct those inputs only in an isolated
checkout when reproducing an old receipt. Never overlay them onto current app
data. Integration into a newer checkout requires a new current-base plan, diff
and acceptance; the archived snapshot cannot authorize resetting newer work.

## Bounded extraction and verification

`calibration/assignments.json` fixes 24 report packets in three tranches of eight.
The packet includes companions, immutable report/version identities, source
access, owner, verifier and stop conditions. Held diagnostic packets return the
hold and its evidence without results or claims. Existing source tags do not
establish a study design, efficacy, identity or destination page. Coordinate
overlapping study families centrally before dispatching a second owner.

```sh
python3 -m scripts.research_ingest validate-source \
  --root . --plan research/batches/RRX-INGEST-001/plan.json \
  --readiness research/batches/RRX-INGEST-001/readiness.json \
  --schema research/batches/RRX-INGEST-001/schemas/candidate.schema.json \
  --assignment research/batches/RRX-INGEST-001/calibration/assignments.json \
  --candidate CANDIDATE
```

Use `--mechanism-schema` with the pinned executable
`schemas/mechanism-candidate.schema.json` for a non-null mechanism payload. The
older descriptive mechanism field list is not an executable validation schema.
The source validator verifies structure, relationships, assignments and bytes;
it does not independently certify the author's reading log or scientific claims.
The verifier must read the actual source, inspect relevant figures/tables and
record the exact candidate/source hashes independently.

Every scholarly source carries Q01–Q15 once each. `partial`, `not_extracted`,
`not_accessible` and `not_checked` remain unfinished. `not_reported` requires an
adequate inspection showing that the source does not report the field. A partial
candidate can pass structural checks while its scientific review stays pending.

`scripts/research-audit-sample.py INPUT.json` provides a deterministic audit
selection. Its input contract is in the script docstring. Save the input, seed
and output with the batch. All calibration reports, public numerical claims and
launch sources are mandatory. Other full-text report versions are sampled at
ceil(10%) within each worker/design/format stratum. A material error expands the
affected dimensions, and an unknown extent expands the whole set. Selection is
not an audit result. A source/version must appear only once in that denominator.

Do not scale beyond calibration until all 24 packets have accepted dispositions
and no unresolved major extraction errors. Begin production at 20 packets;
increase to 30 only after two accepted batches without unresolved major errors.
Measure source reading, extraction, independent audit, repairs and integration
separately. Do not estimate completed full-review throughput from a partial packet.

## Evidence fan-out

`python3 -m scripts.research_fanout --contract` prints executable binding,
authorship and independent audit contracts. A separate read-only fan-out plan
pins the source plan/readiness, validated candidate, exact authorship and audit,
scientific relevance bindings, current application inputs and identity mapping.
The helper emits private proposals only. It never writes the reader application.

Bindings select actual result and claim IDs at an exact population, outcome,
comparator, formulation/route and timepoint. Broad claims cannot be silently
narrowed: a narrower independently audited restatement records its parent claim,
included results and excluded dependencies. The same scoped record is referenced
from drug and condition parents. Question destinations require an exact verified
scope. Mechanistic experiments stay distinct from clinical benefit findings.

The output includes shared records, source-located Q inputs, page-specific history
proposals and dependent assessments/reviews/approvals requiring revalidation if
the proposal is later integrated. Proposal dates are not publication dates.
Actual reader integration requires a new explicit allowlist and scientific gates.

## Validate, stage, diff, apply

The integration manifest lists exact candidate payloads and target paths, expected
source hashes and current base hashes. Never authorize a whole directory. The
engine rejects stale inputs, duplicate keys/targets, unsafe paths, symlinks,
unresolved journals, concurrent stores and self-acceptance. See the engine README
for acceptance report contracts and recovery commands.

```sh
python3 -m scripts.research_ingest validate --root . --packet PACKET --plan PLAN --manifest MANIFEST
python3 -m scripts.research_ingest stage --root . --packet PACKET --plan PLAN --manifest MANIFEST --readiness GP --out STAGED_PACKET
python3 -m scripts.research_ingest diff --root . --packet PACKET --plan PLAN --manifest MANIFEST
python3 -m scripts.research_ingest apply --root . --packet PACKET --plan PLAN --manifest MANIFEST --readiness GP --acceptance ACCEPTANCE
```

Only the integrator runs the last command. Its acceptance binds schema, identity,
source integrity, preservation, actual repeat-import test and independent audit
reports to the exact candidate digest. Repeat the same unchanged candidate and
save the zero-change result. Multi-file integration is journaled, not globally
atomic. After interruption, inspect `recover --root .`; do not delete a lock or
journal to get past a HOLD. The rollback operation verifies both saved and current
bytes and preserves unrelated concurrent edits.

## Grok transfer

The bounded `grok/RRX-GAP-001/` packet targets only diagnosed source-version and
correction gaps. Its GP is separate from closed-packet source extraction. The
owner transfers the prepared attachment and request to Grok manually. Grok returns
actual downloadable files, a hash manifest, queries/search and screening logs,
explicit gaps, flat Q input records and a filled `CHATGPT-INGEST-PROMPT.txt`.
No connector, dispatch or receiving access is assumed.

Download the returned ZIP to a private directory outside this application and
confirm that the receiving Codex session can read it. Then run:

```sh
python3 scripts/verify-research-gap-return.py --help
```

Use its explicit archive, plan, readiness and schema arguments. The receiver
checks file bytes, member paths, query/gap coverage and input relationships without
extracting or importing. A receipt PASS is not a source identity adjudication,
scientific extraction or review approval. Reconcile new report versions centrally
and issue a fresh extraction plan before assigning them to workers.

## Close each batch

Run the source/batch tests, research runbook checks, build and private-boundary
checks; inspect affected rendered journeys and mobile evidence panels for any
reader change. Save actual outputs and limitations. Update the handoff with
separate received, extracted, verified, appraised, human-reviewed, synthesized and
released counts, with units and denominators. Commit the plan, schemas, candidates,
audit/acceptance, canonical private outputs, unresolved gaps and next assignment.
Keep human review, free authenticated access, deployment and scientific release
as separate gates.
