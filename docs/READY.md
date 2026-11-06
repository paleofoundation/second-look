# Metformin-grade ready line

`/drugs/metformin` is the reference ready page. A drug or condition page is indexed only when `scripts/readiness.mjs` passes. The sitemap and the page `noindex` use that same result. Passing this bar is a technical depth check. It is not scientific or clinical approval.

Run `node scripts/readiness.mjs` to print which pages pass and the gap on every page that does not.

## What the bar requires

All of these are required:

- Substantive body of at least 5,000 words. The count uses reader-facing prose: sections, questions, FAQs, mechanism pathways, suitability, the evidence table, study summaries, and references. Navigation, update history, and the generic quality sentence about bioequivalence are left out. Benefit questions already covered by the evidence table are left out because they are not rendered.
- At least 15 distinct valid DOIs. A DOI counts once, from the source record or from a DOI in its URL. Quarantined, retracted, withdrawn, or removed sources do not count.
- Mechanism of Action with at least three named subsections, each with a real explanation. On metformin those are insulin and growth signaling, AMPK and mTOR, autophagy and mitochondria, and complex I.
- Evidence grouped into an outcome table with at least two condition or intervention groups.
- Dosing drawn from cited trial schedules: a dose, a schedule, and a trial or study, in at least 250 words.
- Safety with contraindications and interactions populated, each cited.
- Study summaries for at least eight primary sources, together at least 1,200 words.
- A Quality section that names a formulation or product difference, not only the generic bioequivalence sentence.

## Why the DOI floor is 15

A count of DOI strings in the live page file was about 44 for metformin, 16 for methylene blue, and 24 for melphalan. That file repeats each identifier. Counted once, the current pages have 18, 8, and 12 distinct valid DOIs. Fifteen is the indexing floor metformin clears and the two thinner pages do not. Thirty distinct valid DOIs stays in the gap report as the deepening target for fills.

Methylene blue (2,112 substantive words, 8 distinct valid DOIs, three cited mechanism subsections, a cited dosing section of 465 words, cited contraindications and interactions, a cited Quality section, no evidence groups) and melphalan (about 2,100 substantive words, 12 distinct valid DOIs, no mechanism subsections) fail the indexing bar. The dosing rule is unchanged. `/drugs/itraconazole` is the page that still fails it: 17 cited dosing words, under the 250-word line. The safety rule is unchanged. `/drugs/melphalan` is the page that still fails it: contraindications and interactions are empty. The quality rule is unchanged. `/drugs/melphalan` is the page that still fails it: no drug-specific Quality section. Only `/drugs/metformin` passes today.
