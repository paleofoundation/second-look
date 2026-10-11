# Second Look collaborator handoff

Prepared 11 October 2026 for the private [paleofoundation/second-look](https://github.com/paleofoundation/second-look) repository. This document describes the application and source files inspected at handoff. Validation reports and future pull requests should state which checks actually ran and against which revision.

## Instructions and durable decisions

Research collaborators must read [RESEARCH-INGEST.md](RESEARCH-INGEST.md) before file requests, extraction or import. It maps current editorial records and the preserved original plan/schema/portfolio packets under `research/`, and defines the required continuity checkpoint for each future batch.

Read [AGENTS.md](../AGENTS.md), [PROJECT-RULES.md](PROJECT-RULES.md), [RULE-CHANGELOG.md](RULE-CHANGELOG.md) and the [canonical One Match Rule](../rules/one-match-rule/ONE-MATCH-RULE.md). Record new rules and accepted changes in the relevant canonical document and changelog in the same pull request as the code or content that adopts them. Follow their precedence instructions when requirements differ.

The [v1.1 pilot baseline](one-match-rule-baseline.md) is intentionally frozen; [baseline-record.json](baseline-record.json) records its original hash. Later canonical rules and accepted project changes must be separately recorded. Historical absolute paths in provenance records describe where material was obtained; they are not dependencies that collaborators must recreate.

The project uses Microbiome Medicine and PepsAnon as functional references. Consult the repository's reference instructions before changing navigation, guide layouts, condition links, research disclosures, citations or related interactions. Their patterns differ: a study drawer and an inline research disclosure are distinct behaviors. Record what was consulted, apply the current Second Look requirement, and preserve changes in the separate reference projects.

## Runtime and commands

The application is React 19 and TypeScript using Vinext's Next-compatible routing on Vite and Cloudflare Workers. The `next` dependency and `next.config.ts` do not make this a conventional standalone Next.js deployment. `build/sites-worker.ts` provides the Worker entry point; `vite.config.ts` wires Vinext, local service bindings and the private-source boundary.

| Command | Purpose |
| --- | --- |
| `npm run install:ci` | Install the committed npm lockfile with development and optional dependencies included |
| `npm run dev` | Start portable Vinext development with HMR, normally on loopback port 5173 |
| `npm run build` | Validate required content boundaries and build the Sites Worker artifact |
| `npm start` | Serve the already-built Worker locally using `dist/server/wrangler.json` |
| `npm run lint` | Run the configured ESLint checks |
| `npx tsc --noEmit --incremental false` | Check TypeScript without writing incremental build metadata |
| `npm run db:generate` | Generate Drizzle SQL migrations after intentional schema changes |

Use Node.js `>=22.13.0` and npm. Python 3 is needed for editorial scripts, not ordinary app startup. Run commands from the repository root. Do not overlap dependency installers.

`scripts/execution-profile.mjs` defaults a clean clone to `portable`. A Sites-managed environment may choose `managed-linux` in ignored `.sites-runtime/execution-profile.json`; that profile needs Bash, `flock`, `curl`, `sha256sum` and GNU `timeout`. Use the installed Sites workflow to configure or run its managed preview. Its internal `terminal.local` address is not a public site URL.

The portable installer preserves host HOME, cache, proxy and temporary-directory configuration. If npm's configured cache is unwritable, choose a writable cache with `npm_config_cache` for that install. Runtime helpers keep Wrangler/Miniflare state local. `.sites-runtime/`, `.wrangler/`, `.vinext/`, `node_modules/` and generated builds are not source artifacts to share.

`npm run dev -- --port 5174` changes the development port; keep portable previews on loopback. Vinext records its running server in ignored `.vinext/` state and ordinarily rejects a duplicate launch. `npm start -- --port 8788` changes the built-preview port. The built preview does not provide development mock sign-in.

Local Request.cf metadata uses Miniflare placeholders by default. `CLOUDFLARE_CF_FETCH_ENABLED=true` opts into fetching that metadata. Local Wrangler metrics are disabled unless `WRANGLER_SEND_METRICS=true`. These are local tool settings, not application credentials.

## Local database and sign-in

`.openai/hosting.json` declares the D1 binding `DB` and R2 binding `BUCKET`. `vite.config.ts` supplies local simulation. Database tables are defined in `db/schema.ts`; they include saved items, corrections, reader profiles, guide orders, memberships and edition approvals.

Build once to create `dist/server/wrangler.json`. For a fresh local database, apply the four committed migrations in this order:

```sh
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0000_fancy_skullbuster.sql
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0001_reader_profiles.sql
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0002_lonely_molly_hayes.sql
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0003_complete_blue_shield.sql
```

On an existing local database, apply only migrations that have not already been applied. These commands execute SQL files directly; do not replay them as an idempotent setup routine. Use `.wrangler/state`, not `.wrangler/state/v3`. Rebuild after changing bindings. Local migration commands do not migrate the hosted database.

During portable `npm run dev`, visit `/signin-with-chatgpt?return_to=/` to use the local test identity `local_seedy` (`seedy@sites.test`, display name `Seedy`). Visit `/signout-with-chatgpt?return_to=/` to sign out. Mock authentication is limited to loopback development, is disabled for managed Linux and is absent from production builds.

Hosted sign-in is owned by Sites dispatch. `app/chatgpt-auth.ts` reads trusted identity headers and provides the application helpers. Use its stable site-specific user ID as the database key; email and full name are display fields. Full name is optional. Sign-in and sign-out must be top-level navigations using the helpers and validated same-origin return paths. Dispatch owns `/signin-with-chatgpt`, `/signout-with-chatgpt`, `/callback`, OAuth cookies and identity injection; do not implement competing app routes.

Sign-in establishes identity, not workspace membership or access to a particular protected record. Preserve server-side authorization and private response caching headers. Outside the Sites dispatch environment, an equivalent trusted identity boundary would need to be designed before using these headers for access decisions.

## Research records and rendering

| Layer | Main files | Role |
| --- | --- | --- |
| Canonical source and guide content | `data/content.json`, `data/reader-evidence.json` | Internal source records, canonical guide structure and extracted outcome rows |
| Public reading projections | `data/public-content.json`, `data/public-reader-evidence.json`, `data/public-mechanisms.json`, `data/public-evidence-assessments.json` | Reader-facing records consumed by shared application adapters |
| Routes and topic coverage | `data/topics.json`, `data/discovery-pages.json`, `data/ingestion-status.json`, `data/acquisition-status.json` | Question inventory, discovery entries, coverage notices and acquisition gaps |
| Outcome identity | `data/outcome-registry.json`, `data/outcome-sentence-maps.json`, `editorial/parent-guide-scopes.json` | Shared row IDs, mappings and canonical parent scopes |
| Evidence assessments | `editorial/evidence-assessments.json`, `editorial/EVIDENCE-GRADING.md`, `scripts/evidence-assessments.mjs` | Source-linked editorial judgments and validated public compilation |
| Source audit trail | `editorial/reader-corrections/`, `editorial/mechanism-expansion/`, `editorial/wiki-foundations/` | Correction packets, extraction records, manifests, locators and provenance |
| Review access | `data/review-envelopes.json`, `data/public-review-metadata.json`, `data/private-reviews.json` | Preview/access metadata and protected draft review bodies |
| Guide products | `data/guide-catalogue.json`, `lib/guide-access.ts` | Product descriptions, proposed pricing, edition hashes and release checks |

`lib/content.ts` combines public content and discovery entries, joins editorial assessments to outcome IDs, and exposes common records for drugs, conditions, answers, comparisons and filters. Reuse the same outcome row across relevant parent pages. Do not create a second independent grade or result for a different view of the same row.

`components/article.tsx` and `components/shared-theme/` provide common reading and evidence interfaces. `lib/citation-plan.ts`, `lib/wiki-links.tsx` and `lib/related-reading.ts` resolve shared citations and internal links. Changes to these paths can affect many page types; use the broad profile checks and representative browser comparisons.

Private reviews are loaded by the server repository after access evaluation. `build/private-source-boundary.ts` also blocks selected private source paths during development. Public projections must remain free of internal production/provenance fields. Repository access itself permits collaborators to read internal records, which is why the GitHub repository is private.

## Updating evidence and content

Preserve source IDs, study-family identities, outcome scopes, actual locators, denominators, timepoints, correction holds and review states. Adding a source or rendering its summary does not complete acquisition, independent appraisal or publication approval.

Existing update scripts include:

- `python3 scripts/apply-reader-corrections.py <batch.json> [...]` for source-checked guide/source/mechanism corrections.
- `python3 scripts/apply-reader-outcomes.py <batch.json> [...]` for outcome batches and their related canonical/public records.
- `python3 scripts/reconcile-reader-sources.py` for source identity reconciliation and alias remapping.
- `python3 scripts/apply-wiki-content.py` for the committed wiki/foundation and mechanism additions.
- `node scripts/evidence-assessments.mjs --write` to validate assessments and compile the public assessment projection after actual reassessment.

These scripts mutate tracked data. Read the script and its input format before running it, inspect the diff, and include the source packet and affected projections in the same pull request. They are not setup steps or a general request to regenerate every dataset.

The grading method is documented in [editorial/EVIDENCE-GRADING.md](../editorial/EVIDENCE-GRADING.md). It is a three-level selected-source editorial assessment. Formal appraisal, independent review and publication approval are distinct states. Reassess changed source/scope inputs before updating assessment fingerprints; do not refresh hashes merely to pass a check. Use `node scripts/evidence-assessments.mjs --check` to test whether the compiled projection is current.

Full-text HTML/XML/text downloads under `editorial/mechanism-expansion/` are excluded from Git. The source ledger and full-text manifest preserve retrieval details and hashes, and committed extracted records support ordinary builds. Re-running `editorial/mechanism-expansion/build-packet.py` requires the corresponding source files. Broader historical corpus files and private guide manuscripts/assets may also require an explicit handoff from the maintainer; a clone is not a complete research archive.

## Verification

These commands were verified to exist in the inspected checkout. Their listing is not a test result. Run relevant checks against the actual revision and include results and any failures in the pull request.

| Command | Coverage |
| --- | --- |
| `node scripts/content-check.mjs` | Canonical IDs/routes, sidebar labels, citation and sentence closure, source classes and draft boundaries |
| `node scripts/reader-check.mjs` | Parent coverage, shared outcome identity, source links, extraction status and negative boundary cases |
| `node scripts/check-reader-sections.mjs --all-profiles` | Actual article SSR, section population, fragments, citations and all canonical profiles |
| `node scripts/check-article-navigation.mjs` | Matching icon navigation/body order, Research Feed summaries, dated page history, protected-summary rendering fixtures and citation stability |
| `node scripts/check-evidence-section.mjs` | Evidence section composition and shared outcome/table rendering |
| `node scripts/check-evidence-grading.mjs` | Compiled grading projection and rejection of invalid/stale assessments |
| `node scripts/check-wiki-links.mjs` | Wiki links, shared registry, related reading and rendered references |
| `node scripts/verify-reader-boundary.mjs --source-only` | Public data projections and source privacy constraints |
| `node scripts/update-guide-marketing-hashes.mjs --check` | Catalogue marketing hash freshness |
| `node scripts/verify-guide-assets.mjs` | Preview hash identity and absence of the protected full guide in public downloads |
| `npm run lint` | ESLint diagnostics |
| `npx tsc --noEmit --incremental false` | TypeScript diagnostics |
| `npm run build` | Required content checks followed by the Worker build |
| `node scripts/verify-reader-boundary.mjs` | Source checks plus built `dist/client` payload inspection; requires a successful build |

The build currently invokes evidence-assessment checking, source-only reader-boundary validation, marketing hash checking and guide asset validation. A successful build does not replace other content checks, built-payload inspection or browser verification.

For affected reading interactions, check desktop and mobile layouts, navigation, citation fragment reveals, evidence drawer/disclosure behavior, Escape handling and focus restoration. For account/storage changes, verify persistence, anonymous rejection, per-user isolation, error states, export/delete behavior and the intended return path. Keep the PepsAnon comparison tab available during reference-based interaction work.

## Hosted services and current limits

`.openai/hosting.json` records the existing Sites project association and the `DB`/`BUCKET` bindings. Preserve that association when continuing this build. A GitHub push is source collaboration; it is not a production deployment. Use the authorized Sites publishing workflow and record the deployed revision and verification outcome when publishing.

| Area | Current boundary or outstanding work |
| --- | --- |
| Hosted database | Production D1 contents, user notes, profiles and order records are not in Git. Schema migrations are included. |
| Authentication | Production identity and access policy depend on Sites dispatch. The local mock does not test the real sign-in service. |
| Private assets | Production R2 contents and protected full guides are not in the checkout. Public previews/resources are under `public/downloads/`. |
| Research completeness | Acquisition ledgers retain missing sources, unresolved identities/corrections and pending review. Do not replace these states with a general claim of completion. |
| Review access | Draft review bodies and metadata exist; preserve genuine release and role/intake conditions. A source record is not independent review approval. |
| Commerce | Guide products and proposed prices are present, but releases are pending and sales/membership offers are disabled. Genuine fulfillment and required approvals remain separate work. |
| Search indexing | Robots disallow crawling and page metadata requests no indexing. This is the current build state, not evidence of production release readiness. |
| Raw source archive | Downloaded full texts and broader historical research materials are only partly represented by manifests/extractions in this repository. |

Do not commit credentials, `.env*`, local databases, browser sessions, caches or downloaded full texts merely to make another checkout match this machine. Share application source, rules, provenance ledgers and reviewable changes; arrange external service access and any missing source archive with the maintainer as needed.
