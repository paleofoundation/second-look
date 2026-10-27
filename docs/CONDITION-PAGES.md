# Condition pages: repurposed-drug evidence roundups

Date: October 12, 2026. Source: the owner's Drug Repurposing chat correction that a condition page investigates **all potential drug-repurposing interventions for that condition**, and its Evidence table is the intervention roundup. Requirement adopted as SL-RULE-011. This is the implementation plan; application changes, new research and deployment have not been performed by this planning change.

## Product and scope

A condition page answers: **Which repurposed drugs have been investigated for this condition, what might they help, in whom, how convincing are the findings, and what limits or risks matter?** The condition determines the research scope. The first available drug study must not determine the scope of its parent page.

Drug pages look across conditions for one drug. Condition pages look across drugs for one condition. Both use the same accepted, precisely scoped synthesis records. Drug–condition question pages provide deeper treatment, prevention, population or outcome detail. One shared visual shell supports these different editorial structures.

“All” requires an open candidate universe and a reproducible condition-led search, including drugs outside the initial 30-drug portfolio. It does not mean every imaginable molecule, all 900 initial drug–condition combinations, or a claim that a finite search found every possible intervention. Record the actual sources, search cutoff, eligibility and unresolved coverage. The 30 drugs and 30 conditions remain initial research priorities, not a ceiling on condition findings.

Make supported benefits easy to identify, while retaining mixed, inconclusive, null and harmful findings. A favorable result on one symptom or biomarker is not proof that a drug treats the entire condition. Separate established treatment context, repurposed clinical investigations, preclinical rationale and candidates without interpretable results. Do not copy efficacy claims or classification rules from the reference sites.

## What the audit found

Inspected the working tree based on `8e145b7f5ed589402fe6447790398dfa4b8df9af`, including pre-existing uncommitted work, and the live pages on October 12, 2026. These observations describe that version, not independently verified medical findings.

| Current behavior | Why it fails the condition page |
| --- | --- |
| `components/shared-theme/universal-article.ts` always emits Overview, Options, Mechanisms, Safety and Comparisons; unknown section labels fall into Options. | Heading presence substitutes for a condition-specific editorial plan; irrelevant or empty modules are forced into navigation. |
| Parkinson disease's title is condition-wide, but its description, Options, Safety, Comparisons and Evidence prose mostly describe a metformin pilot. | A narrow drug–condition question has been presented as the condition parent. |
| `lib/mechanisms.ts` prefers one authored condition mechanism record over additional contexts. | The condition inherits one drug's rationale instead of explaining the relevant intervention-specific rationales. |
| The compact evidence table is headed “Outcome and study design”; the drug is a subordinate peer link. Article filters focus on outcomes. | Readers cannot readily scan the condition's investigated drugs and their findings. |
| `candidateLinks` mainly supplies Related reading, which has a three-link cap. | Related links are not the intervention inventory or evidence coverage. |

The current 56 canonical synthesis rows are mapped to their matching condition profiles; the audit found no missing same-condition reverse mapping. The content is narrow even where that join is correct. For example, Parkinson disease has one drug with outcome rows and two candidate links; breast cancer has three and thirteen. These are counts of current records, not counts of all relevant drugs or proof that every candidate is eligible. Four of the 31 condition profiles have no outcome rows. Repairing a lookup or adding sidebar links alone cannot close the research gap.

The pinned One Match Rule Appendix C and the historical 30+30 retrieval briefs already require condition-wide discovery. The failure is carrying that requirement through current coverage, synthesis, parent authoring and acceptance. RRX-INGEST-001 recovery and RRX-GAP-001 integrity repair are useful bounded operations, but neither establishes condition completeness.

## Planned article and sidebar

Use this condition-specific sequence in the shared desktop/mobile navigation, body and citation traversal:

**Overview → Interventions → Safety → Evidence → Research Feed → FAQs → Update History → References.**

| Section | Reader-facing content |
| --- | --- |
| Overview | Explain the condition, relevant subtypes/stages, principal symptoms and outcomes, and concise established-treatment context from permitted sources. Add real subsection links for symptoms, diagnosis, causes or treatment context only when substantive content exists. |
| Interventions | A connected explanation of the repurposing landscape, followed by useful drug-specific subsections. Explain what each intervention is being investigated for, its condition-specific rationale and the principal finding. Put drug mechanisms and appropriate comparisons here, keeping tested, proposed and inferred steps distinct. Do not reproduce a second evidence table or a drug-directory card grid. |
| Safety | The consequential safety issues for the investigated uses and populations, clearly attributed to the relevant drug or regimen. Preserve critical information visibly; link deeper drug-specific contraindication and interaction material where available. One pilot's adverse events cannot stand in for all interventions. |
| Evidence | Brief synthesis and search-scope explanation, relevant filters and coverage notes, ending with the intervention-first evidence table below. |
| Research Feed | One deduplicated condition-relevant catalog of canonical paper summaries and dedicated review links, with actual review/access state. |
| FAQs | Condition-wide reader questions and useful intervention questions, answered inline with exact scope and citations. No quota and no generic filler. |
| Update History | Actual page-specific editorial events, distinguishing presentation changes from scientific reassessment. |
| References | One first-appearance numbered bibliography. |

This proposed composition replaces forced condition-level Options, Mechanism of Action and Comparisons modules. Their supported content must be mapped to the appropriate condition or intervention subsection, not discarded. `#section-options`, `#mechanisms` and `#section-comparisons`, plus existing source/question fragments, retain aliases at their meaningful new destinations. Drug pages retain their own contract. Conditions do not have a single pharmacological mechanism of action.

Keep compact outline icons, active-section behavior, readable prose and the shared responsive shell. Generate navigation from the same typed section plan used by the body; never create empty optional subsection links or silently put unmapped content in Options. Unmapped scientific content must be resolved explicitly during migration. Required missing research remains a completeness failure, not an excuse to fabricate prose or hide a safety gap.

The right rail contains condition scope/subtypes when relevant, a truthful evidence/search snapshot, methods and up to three relevant next-reading links. It must not repeat a single drug's form, trial population or scope as condition-wide facts. The complete intervention set belongs in the article, not in this bounded rail. Preserve the hero author and existing save/account behavior; the on-demand research panel remains a separate surface.

## Condition Evidence table

Plan four compact semantic columns:

| Intervention | Outcome and finding | Evidence certainty | Evidence |
| --- | --- | --- | --- |
| Canonical generic drug or exact regimen, linked to its existing parent | Named outcome and a short supported takeaway; study design and decisive population/use/time context | Existing scoped assessment and access to its explanation | Distinct report/study-family counts opening exact supporting sources |

This condition-only variant supersedes the universal three-column prescription for condition pages. Preserve PepsAnon's typography, row hierarchy, citations, source-count control and right-side panel behavior. Drug tables keep their current presentation. Validate the additional column at narrow widths rather than squeezing or hiding decision-critical information.

Group rows by intervention, then by exact question/outcome. The scientific unit remains **drug or exact regimen + condition/subtype + purpose + population/model + formulation/route + comparator + outcome + timepoint**. Keep multiple outcomes, prevention versus established-disease treatment, symptomatic benefit versus disease modification, adjunctive versus monotherapy, and different populations distinguishable. Never average their grades or create a single “works” score for a drug.

The visible finding must tell the reader what happened. Numerical estimates and uncertainty remain in the canonical records and drawer; show a compact estimate in the row when needed to convey the principal finding. Certainty measures confidence in that finding independently of benefit or harm. Do not infer clinical benefit from a direction arrow or statistical significance.

Separate human clinical findings from preclinical evidence within the table through clearly labeled groups. A candidate with a registry/protocol, context-only support, an unprocessed report or an unresolved eligibility question belongs in a clearly differentiated research/coverage note before the table, not a fabricated graded efficacy row. Retain correction and withdrawal notices. “No eligible evidence found” requires a completed declared search; otherwise say only what the available evidence supports.

Provide intervention-name/alias search and appropriate outcome, population, evidence-basis and finding filters using real records. Default to all reader-eligible findings, including explicitly ungraded findings, with clear grouping and no certainty or favorable-result filter. Keep pending and held records distinguishable in coverage. Use deterministic alphabetical intervention order within groups; optional sorting must not imply superiority. A benefit filter may help locate supportive findings, while stating its scope and retaining access to contrary evidence and safety information. Preserve filter/reset/back/reload behavior through the existing shared exploration contract.

Outcome, certainty and evidence-count controls open the exact scoped row's research panel. An intervention link opens its parent drug page; opening a panel must not unexpectedly navigate away. Preserve source identity, first-appearance citations, original-paper/review links, keyboard containment, dismissal, actual-opener focus restoration and background scroll position. Mobile rendering must retain all four column meanings through an accessible contained table or labeled rows.

## Research and data changes

Use the prospective [RRX-CONDITION-001 ingest addendum](../research/batches/RRX-CONDITION-001/PLAN.md). It extends the research program with condition-first discovery, eligibility and coverage tracking. It does not rewrite historical packets, source restrictions, accepted records or their readiness receipts.

Maintain a condition → candidate intervention → exact question → source/result → synthesis → page map. Candidate eligibility and research status are separate from clinical findings. Reconcile existing `candidateLinks`, target registries, the historical condition requests and owned sources into this map without accepting a link as evidence. Add newly identified drugs through stable canonical identities; do not require a pre-existing drug page for discovery, and do not generate unsupported parent pages merely to create links.

The public condition projection joins accepted syntheses by canonical condition identity and deliberate subtype applicability, grouped by drug/regimen. The drug projection uses the same records in the opposite direction. Neither view authors a separate grade. Broad parent/child condition transfers require documented applicability; an acquisition tag or similar disease name is insufficient. Generation must also report eligible pending sources and candidates so a populated table cannot conceal unfinished research.

Acquire or reuse context for the condition overview, original versus proposed drug uses, mechanisms, harms, interactions, null results and trial status as well as favorable results. Preserve primary/context distinctions, source locators, family deduplication, corrections, exact-scope assessment fingerprints and Q01–Q15 review obligations. Broad discovery and the separate closed-packet recovery stream must not contaminate each other's source authority.

## Implementation sequence and acceptance

1. **Reconcile coverage.** Inventory every condition and known candidate from current registries, candidate links, prior requests and owned evidence. Report separate discovered, screened, acquired, extracted, verified, appraised, synthesized and released counts. Prepare the first condition protocol and current worker-readable inputs under the addendum before acquisition. This planning change does not count that work as executed.
2. **Build one complete condition pilot.** Use C24 Parkinson disease to expose the current single-drug-parent defect. Search beyond existing seeds under the validated protocol, reuse accepted work, and produce a condition-wide candidate/disposition ledger, supported prose and exact-scope synthesis. A successful one-page pilot is a template checkpoint; all condition targets remain in scope.
3. **Implement the shared condition variant.** Update `components/shared-theme/universal-article.ts`, `components/article.tsx`, `components/shared-theme/evidence-table.tsx`, `components/shared-theme/outcome-finder.tsx`, shared types, `lib/content.ts`, `lib/mechanisms.ts` and `lib/citation-plan.ts` together. Reconcile authoring/import paths such as `scripts/apply-reader-outcomes.py` and projected routes through `app/[...path]/page.tsx`. Avoid a new competing condition renderer.
4. **Verify varied pages before scaling.** Exercise C24, a multi-drug oncology condition, a prevention/treatment split and a sparse/preclinical condition. Include a candidate outside the initial portfolio, contrary findings, multiple outcomes for one drug, a combination, overlapping reports, no eligible evidence after search, and pending evidence. Confirm drug-page behavior remains intact.
5. **Scale accepted batches across all conditions.** Update parent titles/descriptions, overview, intervention explanations, safety, table, FAQs, rail, search metadata and generation from the same accepted scope. Preserve unfinished candidates and counts in the handoff. Do not declare an all-pending or single-pilot parent complete.

Acceptance requires a reader to identify the investigated drugs, explain which outcomes show benefit or contrary findings and the principal limits, and reach the supporting source without reconstructing the answer from paper titles. All discovered eligible candidates must have a disposition; all accepted relevant syntheses must appear exactly once in the condition view and agree with their drug view. No fixed drug or paper quota substitutes for the protocol.

Run governance, content, reader, all-profile section, article-navigation, evidence-section, evidence-grading and wiki-link checks, TypeScript/build and public-payload boundary checks after implementation. Extend existing checks to test these scientific/reader invariants rather than only the old fixed label list. Inspect actual desktop/mobile routes at 320, 390, 768 and 1280px, citation order, legacy fragments, filters and all three panel controls (outcome, certainty and evidence count). Repeat generation/import without duplicating or reverting content. Record exact-version technical, scientific, human-review and deployment status separately.

## Reference comparison and current status

Read the references listed in `references/README.md`. Live behavior inspected on October 12, 2026:

- [Microbiome Medicine endometriosis](https://microbiomemedicine.com/conditions/endometriosis) centers its condition content on an Interventions section listing multiple interventions. `WpRender.tsx` distinguishes condition Interventions from intervention Conditions; `ArticleView.tsx` follows actual headings. Reuse the condition/intervention distinction, not its medical classifications. `ConditionsTable.tsx` is a taxon-page component and is not the condition roundup template.
- [Examine endometriosis](https://examine.com/conditions/endometriosis/) has condition-specific overview questions and a database starting with Intervention, followed by Health Outcome, Grade, Effect and Evidence. It establishes the intervention-first reading direction; its proprietary content and combined grading rules are not imported.
- [PepsAnon semaglutide](https://pepsanon.com/peptides/semaglutide) and its `evidence-table.tsx`/`research-panel.tsx` supply the compact table and separate research panel references. Keep its reference tab available. Its live article ordering differs from RemapRx's later adopted tail, which remains authoritative here.
- [RemapRx Parkinson disease](https://remaprx.com/conditions/parkinson-disease) visibly exhibits the single-metformin scope described above. The live review is a product audit, not a clinical evidence appraisal.

Completed in this change: product diagnosis, condition page plan, durable local rule correction and prospective ingest addendum/schema. Pending: executable acquisition readiness, new research, renderer/data migration, rendered acceptance and deployment. This planning change does not edit existing RRX-INGEST-001 plan/schema/history artifacts. A separate concurrent operation changed that batch's live plan, readiness and schema dependencies during inspection; reconcile their current versions before operational GP readiness rather than treating earlier observed hashes as current. Upstream One Match Rule synchronization remains pending through its existing integrator; do not modify the pinned snapshot or frozen pilot baseline in place.

Planning validation on October 12, 2026: `node scripts/check-governance.mjs` passed for 236 preserved rule/history/ingest files and the frozen baseline; targeted `git diff --check` and local document-link checks passed. Independent review of the page plan prompted two corrections: the default table includes all reader-eligible findings, including explicitly ungraded findings, and browser acceptance covers outcome, certainty and evidence-count controls. These are documentation/schema checks and reference observations. No application build, new scientific review or browser acceptance of a changed implementation is claimed.

## October 12 outcome-table supersession

The owner's later Examine screenshots and explicit request adopt Intervention / Outcome / Grade / Effect / Evidence, a single expandable intervention group with compatible studies synthesized by endpoint, A–F benefit assessments and overlap-aware randomized trial/participant counts. Follow [OUTCOME-TABLES.md](OUTCOME-TABLES.md) and the new outcome-benefit method rather than this plan's earlier four-column certainty display. Condition-wide discovery and all source/review requirements remain. Exact clinical rationale and proposed mechanisms belong with each intervention's outcome in the right overlay.

### October 27 selected-source depth continuation

The 07:26 owner order authorizes deeper evidence, mechanisms, human-data and safety explanations for four existing pages: multiple myeloma, ME/CFS, ALS and basal-cell carcinoma. This bounded source expansion does not implement the planned template or claim condition-wide discovery. The 08:12 ruling retains Vitiligo deferral because of CP027-CH25; no exception to the 11 CP027/CP028 book-page hold is inferred. The four-page packet records prospective readiness, actual reading depth, scoped claim grades and remaining review/release gates.

### October 27 deployed/planned comparison

The authorized read-only [structure comparison](CONDITION-STRUCTURE-COMPARISON.md) verifies Sites version46/source2004fbf and the existing condition composition, distinguishes the later five-column table supersession, and records what a future template migration requires. The depth drafts do not implement or ship that template. The untracked D22 publishing framework was consulted without importing or modifying it. Exact metadata, source hashes and remaining gates are in the comparison packet.
