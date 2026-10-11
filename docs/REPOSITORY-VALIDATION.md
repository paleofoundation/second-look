# Repository handoff validation — 11 October 2026

Scope: preserve the current Second Look application/history and add collaborator instructions, rule preservation and research-ingestion continuity. Application source baseline at validation: `68b2afe` (including preexisting evidence-grading work). This handoff does not deploy the site or certify scientific completion. The Git commit containing this report identifies the documentation/package version.

## Passed locally

- `node scripts/check-governance.mjs`: 233 preserved rule/history/ingest files match their manifests; frozen v1.1 baseline and researcher entry points are intact.
- Isolated negative fixture: modifying a copied frozen baseline causes the governance check to fail; the real baseline is unchanged.
- `git diff --check` and onboarding Markdown file-link checks.
- `node scripts/content-check.mjs`: canonical IDs/routes/citations/source classes and draft boundaries.
- `node scripts/reader-check.mjs`: parent coverage, relationships, source closure and negative cases.
- `node scripts/check-reader-sections.mjs --all-profiles`: 64 profiles / 396 questions, SSR and citation/fragment checks.
- `node scripts/check-evidence-section.mjs`: 64 profiles plus four additional evidence guides; 124 rendered rows, scoped/empty fixtures and repeat generation.
- `node scripts/check-evidence-grading.mjs`: 56 outcomes and stale/missing/invalid-assessment rejection fixtures.
- `npm run build`: production Worker build completed. Existing bundle-size warning remains.
- `node scripts/verify-reader-boundary.mjs` after build: eight projections, 15,926 fields and 29 payloads checked.
- Credential-pattern scan: 643 existing history blobs and current non-runtime files; no matched private-key or common credential patterns. This is a bounded scan, not a general security certification. The imported reference archives were separately inspected for credentials/raw research materials.

## Existing failing check and remaining limits

`node scripts/check-wiki-links.mjs` fails at its “Evidence prose uses the shared linker” assertion (line 190 at inspection). Its SSR fixture expects finding/magnitude links in the initial EvidenceTable markup, while those details are rendered when the right-side panel is selected. The current implementation places those details in the panel under the adopted compact-table contract. This handoff does not change that test or claim its interaction path passed; reconcile the fixture and inspect the actual panel in a separate bounded UI verification.

No browser UX parity, production account/D1/R2 operations, fresh raw-source ingestion, human scientific review, commerce release or deployment was performed for this repository handoff. Historical plan/readiness records remain historical; raw full texts and hosted database/private assets remain external access dependencies.

The GitHub workflow runs the dependency-free governance check on pushes and pull requests. Its presence is not branch protection or a claim that every application/research check runs in CI. New instructions still require deliberate recording and review in the same PR.
