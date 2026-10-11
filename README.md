# Second Look — drug repurposing evidence

**Research collaborators: start with [Research ingestion — required runbook](docs/RESEARCH-INGEST.md).** It maps the actual plans, schemas, source ledgers, review obligations and handoff checkpoints. Preserve these records with each batch so research can resume without losing accepted work.

Second Look is a research website for examining proposed uses of existing drugs. It connects drug, condition and outcome pages to source records, shared evidence assessments and research disclosures. Research acquisition and independent review remain incomplete; guide sales have not launched.

This is the source build for the private collaborator repository [paleofoundation/second-look](https://github.com/paleofoundation/second-look). Repository access includes internal editorial records and protected review drafts. The website's public projections and account permissions are a separate boundary from GitHub access.

## Start with the project instructions

Read these before changing content, behavior or research methods:

1. [AGENTS.md](AGENTS.md) — entry point for contributors and coding agents.
2. [Project rules](docs/PROJECT-RULES.md) and [rule changelog](docs/RULE-CHANGELOG.md) — Second Look requirements and their history.
3. [Canonical One Match Rule](rules/one-match-rule/ONE-MATCH-RULE.md) — the preserved reusable research and publishing method.
4. [Collaborator handoff](docs/COLLABORATOR-HANDOFF.md) — architecture, data changes, verification, services and remaining work.

Keep new requirements in the repository: update the applicable rule and its changelog in the same pull request as the implementation. A chat, a personal skill installation or a local file outside this checkout is not sufficient preservation. The original [v1.1 pilot baseline](docs/one-match-rule-baseline.md) and its [hash record](docs/baseline-record.json) are historical records; do not silently replace them with newer rules.

## Run locally

Requirements: Git, Node.js **22.13.0 or newer**, and npm. Python 3 is needed only for the editorial import/generation scripts. The application uses React 19, TypeScript, Vinext/Vite and Cloudflare Workers with D1/R2 bindings.

```sh
git clone https://github.com/paleofoundation/second-look.git
cd second-look
npm run install:ci
npm run dev
```

Open the loopback URL printed by the server, normally `http://localhost:5173`. No application API key is required for local public-page development. A clean clone selects the portable execution profile automatically. Keep local previews on loopback; change the port with `npm run dev -- --port 5174`.

To build and preview the compiled Worker:

```sh
npm run build
npm start
```

`npm start` serves the existing build through local Wrangler; it does not deploy. Pass `npm start -- --port 8788` for a different port. Account/library features need the local database migrations described in the [handoff](docs/COLLABORATOR-HANDOFF.md#local-database-and-sign-in).

## Check a change

Run from the repository root after installing dependencies:

```sh
node scripts/content-check.mjs
node scripts/reader-check.mjs
node scripts/check-reader-sections.mjs --all-profiles
node scripts/check-evidence-section.mjs
node scripts/check-evidence-grading.mjs
node scripts/check-wiki-links.mjs
npm run build
node scripts/verify-reader-boundary.mjs
```

These commands are existing source, rendering and evidence-integrity checks, not a claim that every current change has passed them. The last command inspects `dist/client`, so run it after a successful build. Also use `npm run lint` and `npx tsc --noEmit --incremental false` for code changes, and inspect affected interactions in a browser. The handoff explains what each check covers.

## Where to work

| Path | Purpose |
| --- | --- |
| `app/`, `components/`, `styles/`, `lib/` | Routes, shared rendering, styles and application logic |
| `data/` | Canonical research records, public projections, review envelopes and protected drafts |
| `editorial/` | Corrections, assessments, source ledgers and extraction provenance |
| `scripts/` | Validation, content updates, dependency installation and runtime helpers |
| `db/`, `drizzle/` | D1 schema and ordered SQL migrations |
| `public/` | Public assets, fonts and explicitly public guide previews/resources |
| `docs/`, `rules/` | Durable project instructions, methods, decisions and handoff material |
| `.openai/hosting.json`, `build/`, `vite.config.ts` | Existing Sites hosting association and Worker build integration |

The committed source does not include production database contents, private R2 assets, a production authentication service or the complete downloaded research corpus. Hosted operation depends on the existing Sites environment. Publishing, review approval and commercial launch remain separate from merging code.
