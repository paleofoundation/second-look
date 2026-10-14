# Gated STOPCOVID2 PDF materialization

`materialize_zip.py` implements the prospective ZIP-member contract. Only synthetic archives have been used during implementation. `materialization-plan.proposed.json` is a proposal, not permission to run it. The integrator must adopt exact current control hashes and record `remaprx-gp-readiness-v1` / `GP_PLAN` / `PASS` for the adopted plan SHA before real materialization. Preserve earlier plans and receipts when scope or inputs change.

The executable requires the plan schema, manifest, itself, its tests, the metadata inventory helper, the existing ZIP contract, ingestion CLI/contracts, and current app instructions to appear in the plan's `inputs`. Every input hash is checked and rechecked, as are the whole archive and readiness bytes. The three proposed manifest asset IDs and report identity remain distinct and unchanged. The CLI archive path is a local resolver convenience; its exact bytes and SHA, not a historical host path, establish identity.

The approved output root must be an absolute symlink-free path outside the application repository. If any Git checkout encloses it, every output must be ignored and the entire raw root must contain no tracked paths. The integrator must first add an appropriate ignore entry in that enclosing checkout. The app root alone is not a sufficient Git boundary. Public, `dist`, and `.git` destinations are forbidden. A future enclosing repository or ignore-file change is checked again at execution.

Every archive entry is checked by `inventory.py` before writing: safe normalized names, collisions, entry types, encryption, supported compression, byte/ratio limits, complete member hashes/CRCs/PDF signatures and physical page counts. The whole observed member set must equal the approved manifest; extra or missing members hold the operation. Each member must have its own unique source ID and SHA-named destination. Page-unit declarations must exactly enumerate its physical pages. This operation counts pages with `pdfinfo`; it does not extract scientific body text, render figures, assess evidence or grant source readiness.

An exclusive output-root lock serializes preparation. Directory descriptors with no-follow opens protect destination traversal. Files are written with exclusive creation and mode 0600 into same-directory temporary files, flushed, and atomically hard-linked into place without overwriting an existing destination. Temporary links are removed. Exact existing files are reused; different bytes, links, nonregular files, occupied locks, changed controls or changed output identities produce HOLD. The receipt records the parent, members, identities, hashes, byte/page totals, destinations, original per-file results, preparer, time, control hashes and private-boundary check.

This is not a multi-file transaction. An interrupted run may leave exact private members or temporary files, but cannot grant source readiness. Do not auto-delete a stale lock: establish that its owner is no longer running, preserve the failed run output, inspect partial files, and obtain integrator disposition. A normal failed run emits a HOLD report to stdout and releases its own lock. An approved retry can reuse exact partial members and finish the receipt. No existing different file or receipt is replaced. A completed unchanged repeat preserves all member/receipt bytes and file timestamps and reports `changedFiles: 0`; the transient lock is still used. A receipt is valid only with its exact bound controls and member hashes. New controls require a separately approved receipt path/plan, not rewriting history.

Runtime dependencies: Python 3.11+, `git`, `pdfinfo`, and the pinned jsonschema requirement in `scripts/research_ingest/requirements.txt`. Use an environment containing that requirement; no host-specific dependency path is embedded in the executable.

After an actual GP, invoke from the application root with all explicit paths:

```sh
python3 research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/next-tranche-preflight/materialize_zip.py \
  --root "$PWD" \
  --plan /absolute/path/to/adopted-plan.json \
  --readiness /absolute/path/to/adopted-readiness.json \
  --manifest "$PWD/research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/next-tranche-preflight/archive-members.prospective.json" \
  --archive /absolute/private/path/to/the/pinned/archive.zip \
  --out-root '/Users/kmfp/Documents/ChatGPT/Drug Repurposing/private-research/RRX-INGEST-001/CAL-T1-20261012'
```

Save the stdout result, including a failure result if any. After PASS, separately prepare a new source map and finalized assignment referencing the readable PDFs and archive lineage. A fresh source-review GP is still required before substantive inspection. No real materialization readiness, scientific acceptance, canonical integration, human approval or release is supplied by this implementation.

Synthetic verification command:

```sh
python3 -m unittest discover \
  -s research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/next-tranche-preflight \
  -p test_materialize_zip.py -v
```
