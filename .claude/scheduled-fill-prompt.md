# Scheduled fill run (RemapRx)

Do exactly one unit per run, then stop.

## A. Pick the unit
Take the oldest deposit in `paleofoundation/hmi-evidence-deposits` under `remaprx/RRX-GAP-*/` that has a MANIFEST.csv, at least one PDF, and no `status/BUILT/<unit>` marker. If none is ready, stop without opening a PR.

## B. Build
- Read the deposit's `evidence.md` and the PDFs. Write only what those papers report; quote numbers exactly as the paper gives them. Never invent a reference or a value.
- Add or update the guide in `data/content.json` and `data/public-content.json` (same object in both). Every sentence's `sources` must be source records that carry the paper's `doi`.
- Copy the deposit MANIFEST.csv (no PDFs) to `research/deposits/<unit>/MANIFEST.csv`.
- Preserve every existing object. Never delete existing rationales, guides or sources.
- American English. No em dashes. Preclinical papers go only in Mechanisms and are labelled non-clinical. No patient data, no supplier data.

## C. Check and open the PR
- `node scripts/check-governance.mjs` (includes the citation gate) and `npm run build` must pass.
- Branch `fill/remaprx-<slug>-<YYYY-MM-DD>`, label `evidence-fill`, PR body lists the unit id, the DOIs used and the sections written.

## D. Hard rules
Never merge, never deploy, never touch secrets. The evidence-gate workflow merges green page PRs and dispatches the deploy.
