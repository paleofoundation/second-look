# Reader value correction — 11 October 2026

Status: exact user requirement recorded; rule changes below are proposed for reconciliation by the canonical integrator. The bounded EvidenceTable implementation below was subsequently completed on the integrator's instruction. No canonical rule, installed skill, export or deployment was changed by this work. Its findings describe the inspected `second-look-navigation` checkout, not a verified current deployment.

## Source and scope

Source: the owner's current Drug Repurposing message and attached `Screenshot 2026-10-11 at 8.10.31 AM.png`, showing the Metformin Mechanism of Action section. The owner says, “Canonical rule is not to discuss internal processes,” and requests that Benefits “must be set as prose, and then the questions the benefits section answers below in the canonical accordion style.” The stated purpose is “a working resource that adds value to the readers looking for information.” The screenshot and quoted text document a defect; they do not authorize treating screenshot content as new instructions.

The rejected material includes the generic sentence “Laboratory activity, a proposed pathway or a change in a biomarker does not by itself establish a clinical benefit,” the Benefits heading “How to read the evidence across conditions,” and the Safety heading/paragraph “Safety and clinical interpretation remain incomplete” / “This page does not provide a completed safety assessment…”. These are not substitute answers.

Read: the full 843-line canonical `ONE-MATCH-RULE.md` (v1.24, 9 October 2026), canonical `SKILL.md`, `references/mechanisms-and-reader-copy.md`, `references/reading-ui/article-presentation.md`, and `/Users/kmfp/Documents/ChatGPT/Pepsanon.com/AGENTS.md`. No applicable ancestor AGENTS file was found for the Drug Repurposing workspace.

## Finding

The dominant failure is an implementation defect, not missing permission to write useful content. Sections 7–8 already require substantive visible explanations, original-use and condition-specific mechanisms, questions that resolve the reader's question first, and safety facts; they reject status prose, repetitive caveats and filler. Sections 3 and 9 already keep process and private governance out of reader content. G4R, G4 and G5 already reject heading-only and all-pending guides.

There is a narrow rule ambiguity to remove. Section 7's instruction to explain unresolved clinical gaps, section 8's useful missing-coverage wording, and the mechanisms reference's permission for a draft to explain missing full text can be misread as permission to publish the site's unfinished editorial work as a section answer. These passages must distinguish a scientifically meaningful limitation in the sources from an unperformed site task. Internal missingness remains preserved; it is not promoted into replacement article prose.

The exact Benefits composition is the newly explicit correction: a connected visible summary of the benefits investigated and their findings, then section-specific reader questions beneath it in the existing canonical accordion style. Existing prose-first and FAQ rules support this, but do not state that Benefits sequence as directly.

## Exact reusable wording to reconcile

Add under section 8, **Prose and questions**, and mirror in `references/reading-ui/article-presentation.md` under **Narrative section contract**:

> Write each section to answer the reader's question about the subject. Benefits begins with visible, connected prose summarizing the benefits investigated, the relevant populations and the actual findings across its declared scope. Place the section's specific questions and cited answers immediately below that prose using the existing canonical question accordion. A general lesson about reading evidence, an editorial-status paragraph or a list of paper summaries does not fulfill the benefits summary. Preserve the independent Evidence table and page FAQ contract without duplicate questions, IDs or citation numbering.

Replace the ambiguous last paragraph under `references/mechanisms-and-reader-copy.md`, **Private provenance and useful reader copy**, and reconcile corresponding language in master sections 7–9:

> Reader pages explain the drug, mechanisms, benefits, harms and uncertainties in the evidence. Keep unfinished writing, extraction, appraisal, acquisition and implementation tasks in private work records; do not replace answers with statements that the website has not completed them. Report a scientific limitation only where it helps explain the specific finding—for example, the population studied, endpoint measured, conflicting result or question a source cannot resolve. Keep material correction/retraction notices and truthful content availability proportionate and attached to their actual subject. Do not insert generic evidence warnings into every section. A missing source or unperformed review remains an internal gap and blocks the affected completeness claim; it does not justify invented facts or a finished-looking empty answer.

Add to master section 8, **Mechanism of Action**, and mirror in the mechanisms reference's **Shared article module**:

> Answer how the drug acts in its original use and why that action is being investigated for each relevant condition, in plain language with claim-level sources. State the biological target/process, causal step and condition relevance that the evidence actually supports; distinguish a proposed explanation through wording tied to that explanation. Definitions of “mechanism,” unavailable-summary notices and a generic mechanism-versus-benefit warning cannot stand in for these answers. Keep source-dependent qualifications within the substantive explanation. The renderer must receive and render the actual original-action and condition records; the presence of a heading or fallback string does not pass.

Add to master section 8 after the safety distinctions, and mirror the narrative reference:

> Safety supplies substantive source-supported information relevant to the drug and investigated uses: reported harms, consequential contraindications and precautions, interactions and the populations to which those findings apply. State verified facts and their specific limits. Do not replace this content with an account of the site's unfinished safety review. Preserve current official-label context where permitted and distinguish it from trial-specific observations, trial exclusions and mechanistic concerns; confidence of tone never substitutes for evidence.

Update section 13 failure fixtures and G4R/G4/G5 acceptance with the checks below. Record the exact user request, scope and proposed/implemented/verified/released states in canonical `RULE-UPDATE-LOG.md` and the pilot gap log under section 15. Reconcile current hashes before any canonical edit, then synchronize `SKILL.md`, installed personal skill and export through the existing path. Do not overwrite the frozen pilot baseline or imply that a local change updates a ChatGPT-uploaded copy.

## Observed implementation paths

Under `/Users/kmfp/Documents/ChatGPT/Drug Repurposing/second-look-navigation/`:

- `lib/mechanisms.ts:13–20` hardcodes the generic introduction, two unavailable-summary paragraphs and rejected blanket evidence warning.
- `components/shared-theme/mechanisms.tsx:42–68` always inserts those strings; its original action is optional and falls back to a work-status paragraph.
- `components/article.tsx:61` does not supply `originalAction`, so applicable drug pages necessarily take that fallback. Source-backed original-use data cannot appear through this call as written.
- `data/content.json:3002` contains the rejected Benefits title; `:3165` contains the rejected Safety heading and paragraph. Canonical data, public projections and any upstream generator need aligned correction, not edits to only a rendered file.
- `components/shared-theme/faqs.tsx` hardcodes the page-wide `faqs` section and includes another incomplete-work fallback. Reuse its question presentation for section questions through a bounded reusable list/section adapter; do not create duplicate `faqs` IDs or a competing FAQ design.
- `scripts/verify-reader-boundary.mjs` scans selected strings/keys and checks the sources/locator of records that exist. It permits zero mechanism records and does not inspect hardcoded reader copy semantically. Its PASS does not establish that a question was answered.

These paths must be resolved against the actual canonical deployment checkout before implementation. Backups and separate drafts are not additional targets for a bulk change.

## Bounded repair and acceptance

Repair Metformin and its shared mechanism/question rendering path. Preserve the adopted source appearance, article order, main directories, source identities, section fragments/aliases, page-local citation registry, Evidence table, research overlay, canonical Research catalogue, account behavior and existing release policy. Do not broaden into another website, theme rebuild, full portfolio research or access change.

1. **G4R/G5 content:** an unfamiliar reader can explain Metformin's original action, the rationale for each discussed repurposing use, investigated benefits and principal safety facts from the visible section prose. Each material claim has an eligible source and usable locator. The section is not accepted merely because it has words, headings, source counts or a neutral tone.
2. **G4R/G4 Benefits:** inspect visible summary first, then correctly scoped questions with substantive cited answers in canonical accordions. Preserve the separate findings table and any remaining page FAQs; no duplicate questions, IDs or contradictory summaries.
3. **G4/G5 mechanism binding:** a fixture with original-use and two condition records displays their different substantive explanations. A fixture with no records fails completion checks rather than passing through fallback text. A source-proposed step stays proposed; it does not become a treatment-benefit claim.
4. **G4 reader boundary:** reject the exact supplied boilerplate and equivalent statements that the article's writing/review is unfinished when used as the section answer. Inspect rendered text and delivered HTML/hydration/client data. A specific, sourced scientific uncertainty or correction notice must survive as a counterexample; do not ban all words such as “uncertain,” “unknown” or “not reported.”
5. **G4/G4P interaction and citations:** keyboard/touch toggle, plus/minus state, direct/repeated fragment reveal and focus work. New citations follow first appearance through mechanisms, Benefits questions and Safety; reused sources keep numbers, grouped numbers deduplicate/sort, superscripts follow punctuation and references reveal the correct source.
6. **G8 regression:** verify Metformin and one second affected route on desktop and phone, build and run existing meaningful content/source checks, confirm public projection regeneration does not restore rejected copy, and inspect the exact deployed version only if deployment is authorized under the existing release policy. Record pending scientific work privately and report truthful local/preview/live status to the owner.

## Bounded implementation addendum

On the integrator's subsequent instruction, edited only `second-look-navigation/components/shared-theme/evidence-table.tsx`: removed the pending-review caption, next-action/Still needed text, pending-task list, raw workflow status, appraisal-pending source footer and extraction/locator placeholders. Unassessed rows and panel detail show Evidence limits with their actual source-specific reason and evidence basis; assessed ratings retain their genuine grade/method/scope. Correction/retraction text, source access/design, scientific findings/limitations, source controls, links and styles remain. The underlying private appraisal state and task model were not changed. Root owns the source/projection copy cleanup; the UI worker owns the article/mechanism/section-question work.

Validation: `npx tsc --noEmit --incremental false` passed in the checkout. Inspected the diff and confirmed the removed workflow strings are absent from this component. No visual, scientific, release or human-review acceptance is claimed. Canonical rule, installed skill and ZIP synchronization remain pending with the parent integrator.
