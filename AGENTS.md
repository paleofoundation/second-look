# Second Look contributor instructions

## Routine fixes include live publication — November 4, 2026

Owner instruction: “ALWAYS update when I request fixes like these.” A request to fix the existing website, including layout, styling, navigation presentation or an ordinary bug, authorizes implementing and validating the bounded correction, synchronizing its source to the existing production repository and publishing it to the current live site. Do not stop after local changes or ask for publishing approval again for that requested fix. Preserve the current audience, unrelated work and existing scientific, research, protected-content, billing and access gates; this standing instruction does not approve unrelated changes or waive required verification. Record exact publication results with the work. Current production is GitHub `paleofoundation/second-look` main, deployed by `.github/workflows/deploy-cloudflare.yml` to Cloudflare Worker `remaprx`; updating the old Sites origin alone does not update `remaprx.com`.

This is the source repository for Second Look, the Drug Repurposing project. Read `docs/PROJECT-RULES.md` and `docs/RULE-CHANGELOG.md` before changing it. For evidence work, read `docs/RESEARCH-INGEST.md` **before acquisition requests, extraction or import**, then the complete `rules/one-match-rule/ONE-MATCH-RULE.md` and the applicable plan/schema. Do not assume chat memory or a locally installed skill supplies these instructions to another researcher.

This is the source repository for Second Look, the Drug Repurposing project. Read `docs/PROJECT-RULES.md` and `docs/RULE-CHANGELOG.md` before changing it. For evidence work, read `docs/RESEARCH-INGEST.md` **before acquisition requests, extraction or import**, then the complete `rules/one-match-rule/ONE-MATCH-RULE.md` and the applicable plan/schema. Do not assume chat memory or a locally installed skill supplies these instructions to another researcher.

## Preserve instructions with the work

Record each new explicit requirement or confirmed rule correction in the applicable project contract and `docs/RULE-CHANGELOG.md` in the same commit/PR as related work, even when implementation is pending. Record date, source, scope, superseded behavior, implementation/verification/release status and remaining work. A conversation-only decision is not a durable handoff. Update research plans, schemas and handoff checkpoints when ingestion requirements change. Preserve previous accepted records and decisions.

Current explicit user instructions govern their actual scope; Second Look deltas in `docs/PROJECT-RULES.md` take precedence over the imported rule's generic defaults. `rules/one-match-rule/` is a pinned upstream snapshot, not a competing editable global master. Propose reusable corrections upstream and record pending synchronization; refresh the complete package and its manifest deliberately. Never overwrite `docs/one-match-rule-baseline.md` or historical receipts to make old work appear compliant.

## Functional references

The user requested Microbiome Medicine and PepsAnon as code and behavior references. Before implementing or changing navigation, guide layouts, condition links, research disclosures, citations or related interactions, consult `references/README.md` and relevant packaged source references. Compare rendered behavior when needed; keep the PepsAnon reference tab available during comparison. Apply current Second Look requirements: the references can have different interaction patterns. Preserve changes in their separate repositories.

## Working and release boundaries

Use the existing shared rendering and canonical data paths. Do not run historical corpus generators over current reviewed work. Make bounded branches/PRs, inspect concurrent changes, and record exact-version acceptance. Keep raw research files, credentials and reader account data out of Git; keep editorial provenance out of public client payloads. Do not treat a successful build, GitHub push, AI assessment or authentication as human scientific approval, except through the citation gate below.

## Citation gate and automatic release (decided 2026-11-04, Karen Pendergrass)

The citation gate replaces per-page human sign-off for page PRs. A page PR (label `evidence-fill`, or branch `fill/*` or `claude/remaprx-fill-*`) merges automatically when the `governance` status check from Rules and research continuity has succeeded and `scripts/check-citation-gate.mjs` passes. The evidence-gate workflow runs the readiness and search-indexing tests in its gate job and waits for that governance status check before auto-merge. A failing, cancelled, or missing governance check blocks the merge. The gate requires every cited source on every sentence, question, FAQ and section of each new or changed guide to carry a DOI that is present in `research/deposits/**/MANIFEST.csv` or `research/corpus/**`, resolves on Crossref and has no Crossref retraction, withdrawal or removal notice. Merges to `main` deploy to Cloudflare Workers through `.github/workflows/deploy-cloudflare.yml`, which replaces the manual hosted deploy. That deploy skips its steps when `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, or `REMAPRX_D1_DATABASE_ID` is unset, so missing credentials do not fail the workflow. The evidence gate uses `GITHUB_TOKEN` only. Builders still write only what the deposited full texts report, with no claims beyond the source, and copy the deposit `MANIFEST.csv` (no PDFs) into `research/deposits/<unit-id>/`.

The scheduled fill action receives `DEPOSITS_READ_TOKEN` when that secret exists, shows full action output, and limits tools to the allowlist in `.github/workflows/claude-scheduled-fill.yml`. `Bash(gh secret:*)` and `Bash(gh pr merge:*)` stay disallowed. A missing deposits token does not stop a run; the in-repo deposit inbox remains the fallback.

Public search indexing follows the same gate. `remaprx.com` and `www.remaprx.com` allow crawling. A LIVE drug or condition page is added to `https://remaprx.com/sitemap.xml` and rendered without `noindex` only when `scripts/readiness.mjs` says it is metformin-grade, as described in `docs/READY.md`. Pages below that bar use `noindex,follow`. A fill does not edit robots or the sitemap; the next build picks up a page that newly passes. Other hosts stay `Disallow: /`.

Run `node scripts/check-governance.mjs` for rule changes and the relevant checks in `docs/COLLABORATOR-HANDOFF.md` for code/content changes. Check in the requirements, source mappings, validation results and unresolved work needed by the next researcher.
