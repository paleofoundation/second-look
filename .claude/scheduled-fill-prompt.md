# Scheduled fill run (RemapRx)

Do exactly one of the following per run, then stop.

## A. Fix PRs 17 and 18 first
If PR 17 (metformin) or PR 18 (ivermectin) is still open: the ops gate ruled both FIX because they delete the itraconazole rationales block (about 430 lines) from data/public-mechanisms.json. Rebuild the change on that PR's branch so every existing rationale is preserved exactly. Add a check script or test that fails if any existing rationale key is removed. Push to the PR's own branch.

## B. Otherwise fill the next gap
Pick the highest-ranked open item from the completeness outlines in this repo (metformin and ivermectin outlines, condition rosters) that is thin or missing. Write only that section.
- Use cited primary sources from PubMed, PMC or Europe PMC open access.
- Cite every finding sentence with a PMID, DOI or NCT number that resolves. Never invent a reference.
- No em dashes.
- Preclinical or mechanistic papers go only in Mechanisms and are labelled non-clinical.

## C. Scope
One drug per run, max 25 papers. Open a PR on its own branch `claude/fill-<drug>-<YYYY-MM-DD>`. The PR body lists the outline items closed and the papers used.

## D. Hard rules
Never merge. Never touch secrets. Never deploy. Stop after opening or updating the PR. The ops gate (Elon) reviews and merges on green CI.
