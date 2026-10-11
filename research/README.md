# Research continuity records

Start with [the required ingestion runbook](../docs/RESEARCH-INGEST.md). Current application data and editorial ledgers live in `data/` and `editorial/`.

`prior-pilot/` preserves selected original planning, schema, portfolio, source-identity, readiness and mechanism-adoption records with a per-file hash manifest. They are historical evidence and migration inputs; their original source paths may not exist on another host. The current website has later work. Reconcile these records against the current corpus, rule snapshot and the exact next operation before using them.

Raw full texts, original database state and all past work directories are not included. Source manifests identify access/retrieval dependencies; preserved legacy Python validators may depend on that original workspace and are not advertised as runnable clean-clone checks. Do not execute old generators or use historical PASS decisions as fresh readiness. The modern app checks are listed in the runbook.

For each future operation, save a concrete plan, schema, receipt, acceptance and completed [handoff](INGEST-HANDOFF-TEMPLATE.md) under `batches/<batch-id>/`. A template is not a plan or evidence that work ran. Commit these records with related changes so the next researcher can resume.
