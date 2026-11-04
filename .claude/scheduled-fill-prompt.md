# Scheduled fill run (RemapRx)

Do exactly one unit per run, then stop.

## A. Pick the unit
Take the oldest deposit in `paleofoundation/hmi-evidence-deposits` under `remaprx/RRX-GAP-*/` that has a MANIFEST.csv, at least one PDF, and no `status/BUILT/<unit>` marker. If none is ready, stop without opening a PR.

Access: the deposits repo is private. If `DEPOSITS_READ_TOKEN` is set, read it with `GH_TOKEN="$DEPOSITS_READ_TOKEN" gh api repos/paleofoundation/hmi-evidence-deposits/contents/...` (never print the token). If that env var is missing or the call fails, DO NOT stop: use the staged deposits in this repo at `research/deposit-inbox/<unit>/` (evidence.md + MANIFEST.csv), taking the lowest unit that has no `research/deposits/<unit>/` folder yet and no open `fill/` PR. Read the full papers from their open-access PMC copies (`https://pmc.ncbi.nlm.nih.gov/articles/<PMCID>/` or Europe PMC `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML`) using the PMCIDs in evidence.md.

Tools: you have Bash for git, gh, node, npm, curl, python3 and WebFetch. Never exit after only reading; a run that finds a ready unit must end with an open PR (`git push` then `gh pr create --label evidence-fill`). If a check fails, fix and rerun it. Use the methylene-blue fill (PR #22) as the shape of a good fill.

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
