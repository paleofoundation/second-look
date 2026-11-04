# Scheduled fill run (RemapRx)

Do exactly one unit per run, then stop. A unit is one section on methylene blue or melphalan while either page is below the bar, or one new page after both pass. The ready line is metformin-grade. Read `docs/READY.md` and run `node scripts/readiness.mjs` before choosing work.

## A. Pick the page and the section
1. Run `node scripts/readiness.mjs`. The first lines list every page that passes. The queue lists the gaps.
2. If `/drugs/methylene-blue` fails, deepen that page. Otherwise if `/drugs/melphalan` fails, deepen that page. Do not open a new drug or condition page while either one fails. On the chosen page, deepen the first failing check, in this order: mechanism subsections, evidence table, dosing, safety, quality, study summaries, body words, distinct DOIs. One section only. If the page already passes the indexing bar but still has fewer than 30 distinct valid DOIs, add cited papers toward that deepening target.
3. If both of those pages pass, take the oldest unused deposit and start one new page. Write it toward the bar in `docs/READY.md`, not as a thin stub: include every section the deposited papers actually support. If no deposit is ready, stop without a PR.

Access: the deposits repo is private. If `DEPOSITS_READ_TOKEN` is set, read it with `GH_TOKEN="$DEPOSITS_READ_TOKEN" gh api repos/paleofoundation/hmi-evidence-deposits/contents/...` (never print the token). If that env var is missing or the call fails, DO NOT stop: use the staged deposits in this repo at `research/deposit-inbox/<unit>/` (evidence.md + MANIFEST.csv) and the copies already in `research/deposits/<unit>/`. For methylene blue use the RRX-GAP-0582 deposit. For melphalan use RRX-GAP-0352. Read the full papers from their open-access PMC copies (`https://pmc.ncbi.nlm.nih.gov/articles/<PMCID>/` or Europe PMC `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML`) using the PMCIDs in evidence.md.

Tools: you have Bash for git, gh, node, npm, curl, python3 and WebFetch. Never exit after only reading; a run that finds a page to deepen must end with an open PR (`git push` then `gh pr create --label evidence-fill`). If a check fails, fix and rerun it. Use the metformin page as the depth target and the methylene-blue fill (PR #22) as the file shape.

## B. Deepen that section
- Read the deposit `evidence.md` and the papers already cited on the page. Write only what those papers report; quote numbers exactly as the paper gives them. Never invent a reference, a DOI, a grade, or a value.
- Guide prose goes in `data/content.json` and `data/public-content.json` (the same guide object in both). Mechanism subsections go on that drug's `pathways` in `data/public-mechanisms.json`, with a title and a cited explanation. Study summaries are the source `preview`, design, and population on the source records in both content files. Contraindications and interactions can also be rows in `data/treatment-suitability.json` when a cited label supports them.
- Do not invent an A-F outcome grade or a new outcome row. If the evidence table is empty because no assessed row exists, deepen the cited Evidence prose and leave the failing check in the gap report.
- Every new sentence's `sources` must be source records that carry the paper's `doi`.
- Copy a deposit MANIFEST.csv (no PDFs) to `research/deposits/<unit>/MANIFEST.csv` when that folder is not already present.
- Preserve every existing object. Never delete existing rationales, guides, or sources.
- American English. No em dashes and no en dashes. Preclinical papers go only in Mechanisms and are labeled non-clinical. No patient data, no supplier data.

## C. Check and open the PR
- `node scripts/readiness.mjs` must run. Paste its full output into the PR body so the gap per page is visible, and name the section you deepened and the DOIs you used.
- `node scripts/check-governance.mjs` (includes the citation gate) and `npm run build` must pass.
- Branch `fill/remaprx-<slug>-<YYYY-MM-DD>`, label `evidence-fill`.

## Shell style
Run one simple command per Bash call (no `cd x &&` chains, no `VAR=value cmd` prefixes; use `export` in a separate call). Prefer Read/Write/Edit/Grep over shell for files.

## D. Hard rules
Never merge, never deploy, never touch secrets. The evidence-gate workflow merges green page PRs and dispatches the deploy. Do not edit robots, the sitemap, or indexing metadata. A drug or condition page enters the public index on its own when `scripts/readiness.mjs` reports that it passes.
