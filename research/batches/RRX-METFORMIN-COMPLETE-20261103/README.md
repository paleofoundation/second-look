# Metformin guide completion, November 4, 2026

The private guide manuscript is written and rendered. This batch replaces the obsolete fixed-count readiness blocker with an exact source-disposition ledger. It does not declare every supplement available, independent review complete, or the guide approved for sale.

## Delivered

- 33 source dispositions: the original 30 references plus the actual COVID-OUT correction, REVIVE retraction/republication notice and replacement report.
- 24 substantive source assessments, each with Q01-Q15 and 67 explicit input fields: 360 answers and 1,608 inputs. Nine have no outstanding access fields in the assessed packet; 15 retain specific access gaps. These are not independent human approvals.
- Four official-context dispositions and two publication-integrity dispositions. Abrilla 2021 and El-Mir 2000 are excluded because a complete report was not recovered. The original REVIVE is excluded because it was retracted and replaced.
- One 15-chapter, 71-block private manuscript with 30 cited sources, producing a 26-page full PDF, seven-page sample, three-page summary and structured web candidate. The files are outside the application checkout. `guide-artifacts.json` records exact paths and hashes; `guide-block-map.json` binds each block to the source assessment.
- Imported private assessments, updated metadata, withdrawn original REVIVE review, and a catalogue status that reflects the completed manuscript. No independent/human approval or sales state was granted.

## Integrity decisions

COVID-OUT: the actual correction notice (DOI 10.1016/S1473-3099(23)00562-5) and current corrected appendix were inspected. Table S4, printed page 9/PDF page 10, is the declared numeric source: 35/564 versus 58/562 diagnoses; cumulative incidence 6.3% versus 10.4%; absolute difference 4.1 points (95% CI 0.9 to 7.4); HR approximately 0.59. The Discussion's 10.6% and current registry's 59 control diagnoses remain explicit discrepancies. The source-access blocker is resolved. The public diagnosis synthesis remains conservatively held for these discrepancies and independent verification, with an updated rationale; it no longer claims that the correction was not acquired.

REVIVE: the original DOI 10.7326/ANNALS-25-03959 stays excluded. The actual notice DOI 10.7326/ANNALS-26-03050 identifies omitted dose modification and futility stopping. Replacement DOI 10.7326/ANNALS-26-02144 is separately assessed. Its 750-mg and 500-mg twice-daily cohorts were not randomized dose comparisons, and its metformin result is inconclusive. Available protocol wording conflicts over the primary timepoint; the discrepancy is recorded. The replacement is not counted as a second randomized family.

Other limits remain source-specific. For example, some trials lack a separately recovered protocol or supplement; MA.32 contains discordant harm counts/percentages, so the guide does not calculate a precise extra-harm percentage from them. The Hosono 2010 pilot appears on PDF pages 5-10 of a mixed grant file, corresponding to printed pages 1077-1082. Those pages were visually inspected; the final reference page and supplement were not recovered. The mixed file's first four pages concern another paper and are not used for this assessment.

## Reproduction and source protection

The pinned prospective plan is `plan.v3.json`, with `review.v3.schema.json`, `readiness.v3.json` and `source-access.v3-input.json`. Earlier plans and inventories are historical snapshots. Retrieval request/receipt files preserve successes, failures and media checks. `source-access.json` describes the final available assets. Raw downloaded papers and the full guide manuscript are outside Git.

The `author_*.py` files serialize manually authored assessments, and `assessment_writer.py` enforces the 67-field mapping. They do not perform source appraisal automatically. `complete_dispositions.py` creates the final ledger. `integrate_reviews.py` imports pending private bodies; `reconcile_integrity.py` applies the specifically authored integrity and diagnosis reassessment. Do not run these mutation scripts over newer editorial work without reviewing their scope and diff. After approved data changes, compile with `node scripts/evidence-assessments.mjs --write` and regenerate marketing hashes as needed.

`verify_batch.py --guide <private-guide-directory>` checks the schema subset used here, exact input identities/statuses, source bytes, source dispositions, manuscript reference closure, PDF content parity, links, bookmarks and page geometry. It is structural verification, not independent scientific appraisal. `build_handoff.py` records private file hashes and block mappings without copying paid prose into Git.

The host PDF adapter now keeps short bibliography entries and worksheet prompts on one page. Vendored code is unchanged. The PDF manifest records both the vendor and host adapter hashes.

## Verification performed

- All 61 available source files matched their recorded byte hashes. All 24 assessments passed the pinned schema, 67-input identity and missingness checks.
- All 25 affected protected bodies/envelopes had matching hashes through the actual application hash function; all release/human/clinical approvals remain pending or withdrawn.
- Every final PDF page was visually inspected: full 1-26, sample 1-7 and summary 1-3. The final files have selectable text, intact margins, working source links/bookmarks, no missing glyphs, no clipped text and no split bibliography entries. They remain untagged and are not PDF/UA certified.
- Governance, content, reader, outcome-summary, evidence-assessment compilation, marketing hashes and guide-asset checks passed.
- Reusable renderer checks passed, including deterministic output, malformed input rejection, private-output isolation, content parity, link/bookmark destinations and geometry.
- TypeScript checking and production build passed. The build retained its bundle-size warning. Source and built-client privacy checks passed.

## Delivery and remaining work

Edition: `metformin-20261104-candidate-1`, version `2026.11.04-candidate.1`. Source code and research records are isolated on `codex/metformin-guide-completion-20261103`; the canonical working checkout has unrelated, concurrent changes and was not overwritten. No hosted deployment or public product release was attempted. Review/integration should preserve those changes and the private manuscript boundary.

The remaining work before commercial release is independent qualified clinical/scientific verification, human editorial and applicable legal approval, final accessibility acceptance and exact-edition publication/fulfillment checks. Source gaps can be recovered and reassessed without treating an arbitrary reference count as a gate. The current guide remains usable as a complete private review candidate within its stated source limits.
