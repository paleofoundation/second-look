# Research Feed and study summary design plan

Date: November 3, 2026. Status: reference audit and proposed implementation plan. Application implementation, scientific-content changes and publication are not part of this planning pass.

## Direction and authority

Owner requirement: Research Feed should follow the research-feed design in the Microbiome Medicine build, use RemapRx brand colors, and provide substantially more robust coverage within each opened feed and study summary page.

The reference design, destination branding and deeper coverage are explicit requirements. The sizes, detailed composition and rollout below are recommendations, not claims of separate owner approval. “Open” includes expanding a feed card and visiting its dedicated page; it does not change the existing free-authenticated full-review policy.

Follow [PROJECT-RULES.md](PROJECT-RULES.md), [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md), [ARTICLE-NAVIGATION.md](ARTICLE-NAVIGATION.md), the [review contract](../rules/one-match-rule/references/research-reviews/README.md), and the [pinned One Match Rule](../rules/one-match-rule/ONE-MATCH-RULE.md). This refines the earlier generic disclosure adaptation. Preserve the separate Evidence table/research drawer, source identities, and Evidence → FAQs → Research Feed → Update History → References order.

## Reference comparison

The [reference inventory](../references/README.md) identifies Microbiome Medicine revision `28ed85b6d510dfddf1720775b456771c7dc62763`. Consulted its `docs/DESIGN-SYSTEM.md`, `src/components/ResearchFeedView.tsx`, `src/lib/researchFeedReveal.ts`, and research-feed styles in `src/styles/theme-wp.css` and `src/app/globals.css`. The specification identifies `_migration/endo-live.html` as the canonical card; its documented header structure agrees with the live DOM.

Browser inspection on November 3 covered [Microbiome Medicine's endometriosis feed](https://microbiomemedicine.com/conditions/endometriosis#rgbc-research-feed), [RemapRx's Metformin feed](https://remaprx.com/drugs/metformin#research-feed), and its [COVID-OUT source page](https://remaprx.com/research/P-COVIDOUT-2023). The PepsAnon reference tab was retained; its `guide-research.tsx`, `research-catalog.tsx` and `docs/canonical-research.md` were read for canonical reuse and fragment behavior.

| Surface | Observed gap | Planned response |
| --- | --- | --- |
| Closed RemapRx feed | Plain disclosure triangle, dense title/population/design lines, no visible finding | Reference-style bordered card, circular plus/minus, separate metadata and finding-led excerpt |
| Opened RemapRx feed | Inspected public card shows a preview, repeated limitation/correction text, nested facts and two links | Four coherent questions, visible essential facts and one clear integrity notice |
| Dedicated RemapRx page | Long published title dominates the hero; preview repeats in the body; inspected signed-out page has Summary/Limits | Research-specific hierarchy, concise heading, publication identity, deeper sections and explicit availability |
| Reference access | Live signed-out Microbiome page displays account walls | Full four-question content was inspected in source/specification, not in an authenticated browser session; do not import placeholder text, quotas or cosmetic protection |
| Source/release alignment | Live Metformin still places Research Feed before FAQs; local contract/renderer specify FAQs first | Reconcile current hosted source before implementation and verify intended order at release |

These are bounded UI observations, not a corpus-wide scientific audit. A public preview does not establish whether a private full review exists or is complete.

## 1. Research Feed cards

### Closed card

Use the Microbiome structure: white surface, fine light-gray border, approximately 6px corner radius, 24px internal spacing and 24–32px separation. Reduce padding to 16px on phones. Avoid heavy shadows and promotional graphics.

The header contains a circular plus and complete study title in dark ink. The whole header toggles expansion; the title does not navigate. Use native disclosure semantics or an equivalent keyboard-operable control while matching the reference appearance. Category/source links sit outside the toggle.

Below the title, show the real publication date and assigned drug/condition categories. A year-only record displays a year, without an invented month/day. Do not substitute the journal for a category. Add a short actual study-type label, such as randomized trial, observational study, animal study or systematic review. Move paragraph-length eligibility information into the body.

Show one finding-led sentence with its most consequential qualification. The feed must be informative before a click. Material correction/retraction status remains visible when closed; a missing authored finding gets an honest limited-preview state.

Retain quiet footer pills: **Open**, **Link**, **Email**. Open visits the canonical RemapRx study page; Link visits the exact original paper; Email prepares a draft with the canonical review link and source identity. It does not send mail. Give each action a specific accessible name. Omit Link if no verified external URL exists rather than substituting an internal destination.

### Open card

The plus changes to minus; the header becomes RemapRx blue. Hide the excerpt when the fuller content opens to avoid duplication. Keep essential facts visible without another nested disclosure.

Adapt the reference's metadata block to show design, population/model, study size with denominator type, intervention/comparator, treatment duration and outcome follow-up. Include setting when useful. Omit irrelevant fields and label material missing information accurately. Do not copy the microbiome-only Location / Sample Site / Species fields unchanged.

Keep the four exact opening questions as blue headings:

| Question | Required substance |
| --- | --- |
| What was studied? | Exact drug–condition question; prevention versus treatment; formulation/route, comparator and main endpoint |
| Who was studied? | People or model, eligibility, setting, randomized versus analyzed counts, and exclusions affecting applicability |
| What were the most important findings? | Primary result first, relevant arm values and uncertainty, major secondary findings and important harms, including null or unfavorable findings |
| What are the greatest implications of this study? | What the study adds, what it cannot establish, decisive limitations and relevance to the wider evidence |

Use substantive connected prose with sentence-level citations. Add a compact results table under findings when useful. Place a correction notice above affected results once rather than repeating it in several callouts. Keep footer navigation visually distinct from expansion.

Approximately 300–600 words is a useful design test for a typical clinical study's expanded summary, not a minimum quota or completion criterion. Complexity and inspected evidence determine length. Content must respect the reader's access state.

## 2. Dedicated study page

Preserve `/research/{canonical-source-id}` and aliases. Use a study-specific composition on the shared article shell rather than forcing a research report into the drug-guide template.

### Header and layout

Use a compact blue hero with a short, accurate editorial heading and bounded one- or two-sentence takeaway. Directly below, a publication block preserves the exact paper title, paper authors, journal, publication date, DOI/PMID and original-paper link. A shorter editorial heading does not replace bibliographic identity or justify stronger causal wording.

Retain the verified review-author/bio/ORCID treatment in the hero, distinct from the paper's authors. Show only real author/reviewer assignments. Separate publication date, review-update date and integrity-check date; do not inherit a hard-coded site-wide edition date. Communicate review/release status truthfully.

Desktop: slim sticky contents rail, comfortable central reading column of roughly 680–760px when space permits, restrained existing sharing/related rail. Related links remain at most three. Do not force a drug illustration or repeated one-study metric into the reading space. Mobile: stack hero and metadata, keep the author visible, and use a compact contents control.

### Recommended page sequence

| Section / contents label | Coverage |
| --- | --- |
| Summary | Four familiar questions, essential study facts and decisive takeaway; same review represented in the feed |
| Methods | Design, setting, eligibility, allocation/concealment, blinding, arms, formulation/route/exposure, co-interventions, endpoint hierarchy, analysis population, attrition and adherence |
| Results | Source-backed outcome table, primary/secondary/exploratory labels, arm denominators, timepoints, units, estimates, uncertainty and interpretation |
| Safety | Harms sought, ascertainment, severity/serious events, discontinuations, exposed denominators and detection limits |
| Limitations | Design-appropriate bias, confounding, missingness, multiplicity, precision, selective reporting, protocol deviations and internal inconsistencies; explain their consequences |
| Applicability | Who/what results cover, prevention versus treatment, exclusions, formulation/route/exposure mismatch and surrogate versus patient-important outcomes |
| Context | Independent replication versus companion reports, agreement/conflict with other reviewed evidence, exact drug/condition/outcome links and what this paper changes |
| Disclosures | Funding, supplied products, author conflicts, registration/protocol, source access and integrity; separate review authorship and status |
| Update History | Specific dated changes and correction consequences, with affected claims; never just a build date |
| References | Numbered sources, original/companion/supplement/correction links and useful page/table/figure locators |

Core findings, methods, safety and limitations remain visible. Reserve secondary disclosures for long secondary-outcome tables, detailed bias reasoning and source locations. Avoid repeating full answers under the four openings, generic sections and a raw Q01–Q15 dump. The opening is a synthesis; deeper sections substantiate it. A typical clinical review might occupy 1,200–2,500 words, but coverage and source quality govern, not length.

### Results table

Recommended columns: **Outcome and timepoint / Intervention / Comparator / Effect and uncertainty / Interpretation**. Distinguish randomized N, analyzed N, safety N and event counts. Preserve separate arms/timepoints and label primary, secondary and exploratory analyses.

Binary outcomes use n/N and absolute risks when supported, alongside the reported relative measure and confidence interval. Continuous outcomes name the scale, direction, units and between-group estimate. Never substitute within-group improvement for a treatment effect or interpret a hazard ratio as an absolute risk difference. P values supplement effect size and uncertainty. Derived numbers require a recorded method and valid inputs.

Distinguish not reported, not yet extracted, not accessible and not applicable. Missing harms reporting is not zero harms; non-significance does not establish equivalence. Conflicting or corrected values stay withheld or qualified until reconciled.

Do not assign an automatic study-wide A–F benefit badge. The existing benefit assessment belongs to an exact outcome synthesis and is separate from certainty and study bias. Context can link to that scoped assessment without inventing a paper-level grade.

## 3. Q01–Q15 coverage without a bureaucratic reading experience

Keep canonical question IDs in the versioned data and map each answer to its visible destination. The reader need not see internal Q numbers. One canonical record supplies the concise feed projection and fuller page, subject to authorization.

| Question | Detailed destination |
| --- | --- |
| Q01: question actually tested | Summary; Methods objective/prespecification |
| Q02: who or what was studied | Summary facts; Methods population/model/counts |
| Q03: what exactly was used | Methods formulation, route, exposure and co-interventions |
| Q04: comparator | Methods control, allocation and blinding |
| Q05: what was measured and why it matters | Methods endpoint hierarchy; Results interpretation |
| Q06: size of result | Results arm data, estimates and uncertainty |
| Q07: other observations | Methods/Results attrition, exclusions, adherence, missingness and experimental units |
| Q08: harms | Safety |
| Q09: misleading design/analysis | Limitations |
| Q10: applicability | Applicability |
| Q11: independence | Context study-family relationships and replication scope |
| Q12: investigators/support | Publication block; Disclosures funding/products/conflicts |
| Q13: current/intact source | Disclosures version/access/integrity; Update History |
| Q14: supported/contradicted claims | Context exact outcome/claim relationships |
| Q15: change in understanding | Summary implications; Context conclusion and remaining questions |

Require exactly one canonical answer/status per question, even when it informs more than one projection. Justified non-applicability is allowed; unperformed work cannot become “not reported.” A complete layout is not a completed appraisal.

Adapt to design. Systematic reviews need search dates, eligibility, included-study overlap, synthesis methods, heterogeneity and bias. Observational studies need ascertainment, adjustment, confounding and selection issues. Animal/cell work needs experimental units, biological versus technical replication, exposure relevance and translation limits. Protocols show planned methods and the absence of results. Nonresearch background sources retain an appropriate source page without fabricated trial facts. Every cited scholarly paper, including secondary research, retains its dedicated review obligation.

## 4. Access and availability

| State | Presentation |
| --- | --- |
| Public preview | Source identity, genuine concise finding/limit, original link, integrity notice and accurate availability; free sign-in invitation for an actually released full review |
| Signed in, intake complete, review released | Authorized four-question expanded summary and complete review, without subscription or sample quota |
| Review pending / required inputs missing | Available public information plus a clear statement that the full review is not yet available; no promise that login reveals unfinished work |
| Withdrawn/retracted | Prominent source-backed notice, affected conclusions and notice/context links; identity/history preserved and invalidated efficacy claims excluded |
| Request failure | Retry state, distinct from a scientific or release decision |

Authorize server-side before loading or serializing protected bodies, including HTML, hydration, APIs, search, exports and the Evidence panel. Do not copy the reference's blurred wall or transmit hidden full text. Preserve supported login, persisted intake and return to the exact review/card fragment. Richer anonymous summaries beyond the existing public-preview contract would require a deliberate content-policy decision; this plan retains the current boundary.

## 5. Brand and behavior

| Role | RemapRx treatment |
| --- | --- |
| Active header, question headings, internal links and plus/minus | Brand blue `#1736F5` |
| Hero and author panel | Existing blue/deep-blue roles, including `#1027B8` |
| Reading surface and text | White; ink `#17204D`; readable secondary ink `#5B6175` |
| Borders and occasional facts tint | Light gray `#DEDEDE`; pale blue `#EFF2FF` |
| High-emphasis actions / focus on dark surfaces | Yellow `#FFC709`, never a signal of favorable results |
| Typography | Existing Lora headings and Inter body, normal weights and generous spacing |

Use shared tokens. Starting sizes to test: 22px card title, 20–22px question headings, 16–18px body and 14px metadata; compact page hero around 36–44px desktop and 28–32px mobile. Keep full titles untruncated. Footer pills remain muted at rest and blue on interaction. Preserve visible focus, approximately 44px effective touch targets, decorative icons, text status labels and the site's no-underline internal links.

Multiple cards can remain open. Deep links reveal and focus the exact card and preserve aliases. Expansion cannot renumber citations. Retain the current single-source inline rule unless every additional citation is covered by a separately validated page citation plan. Cross-source context remains on the dedicated page; do not discard citations to force an inline rendering.

Keep one card per canonical paper/report. Associate companion reports with study families without collapsing distinct report identities or counting their participants twice. Do not add a second study table/catalog. Feed scope follows the actual drug/condition relationships, not simply keyword matches or possession of a PDF.

## 6. Implementation sequence

1. **Reconcile and inventory.** Start from current hosted source in an isolated checkout, reconcile later local contracts/concurrent edits, and inventory facts, review availability, authorship and question coverage. Separate missing content from missing presentation. Do not run historical corpus generators.
2. **Create one inspectable page pair.** Use the existing Metformin feed and existing study routes to demonstrate closed/open cards and the dedicated page at desktop/mobile widths. Reuse source-backed content and leave unresolved values explicit. If no released full review is available, use clearly synthetic fixtures solely to test that state; never change real release flags for a demo.
3. **Implement shared components and typed projections.** Refactor `StudySummary`, `StudyFacts` and `InlineStudyReview` in `components/article.tsx`; add study-specific composition in the `research/` branch of `app/[...path]/page.tsx`; replace repetitive `components/review-answers.tsx` output with mapped sections. Version the restricted section types/projection checks in `lib/review-access.ts` as needed. Reuse the server review repository and authorization path.
4. **Complete research gaps through the existing workflow.** Before substantive extraction/appraisal, read [RESEARCH-INGEST.md](RESEARCH-INGEST.md), the full pinned rule and a matching plan/schema; record operational readiness. Preserve bounded candidates and separate apply/review/release gates. This design request does not automatically resume the research queue.
5. **Verify and extend.** After evaluating the page pair, reuse the accepted shared presentation across drug/condition feeds and study pages, then in `/research` where appropriate. Drug/condition/design/year directory filters are a later enhancement. Do not restore removed Evidence quick-search controls or imply literature completeness from feed counts.

The first implementation deliverable is an actual inspectable feed-and-study-page pair, comparison screenshots and a specific content-gap list. A process diagram, schema or successful build alone does not satisfy it.

## 7. Acceptance and handoff

Visual checks: reference card hierarchy, plus/minus, blue open state, four headings and quiet actions; desktop, 390px and 320px widths; long titles, multiple open cards, 200% zoom, keyboard/focus, reduced motion and table overflow. Only a wide table may scroll horizontally; the page must not.

Behavior checks: expansion versus Open navigation, original/email destinations, repeated same-fragment links, aliases, login return, matching body/contents order and frozen bracketed superscript citations. Verify the separate Evidence drawer remains functional.

Content checks: RCT, observational, systematic review, preclinical, protocol/no-results, correction/retraction, sparse preview and cross-source examples. Require every Q01–Q15, real source locators or justified states, major results and harms, limitations, funding, independence and applicability. No invented facts, grades, authorship, review status or dates.

Access checks: anonymous, expired-session, intake-incomplete, authorized released, pending, withdrawn and load-error states. Inspect actual response payloads; a visual gate is insufficient. Synthetic fixture success does not certify authenticated production access.

For implementation, run relevant existing governance, article navigation, reader sections, evidence, citations, review access and public-boundary checks, TypeScript and build. Record exact version/results, screenshots, unresolved scientific gaps and deployment separately. For this documentation-only pass, run governance and document link/preservation/whitespace checks; do not claim application tests or scientific verification.

## Planning status

Completed: bounded reference/source inspection, signed-out live comparison, coverage mapping, recommended composition, staged plan and durable contract links. Reference projects were read only. Application implementation, authenticated full-review comparison, new research, scientific acceptance and publication remain future work. No pinned-rule, upstream or installed-skill synchronization is claimed.
