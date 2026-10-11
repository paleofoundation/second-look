# Reading UI references — One Match Rule 1.22

This module packet supplements the [whole-site theme contract](../theme/README.md). Start from the active Microbiome Medicine theme; isolated matching modules within a redesigned shell do not satisfy G4T.

Use this packet with master sections 7–8 and G4/G4R/G4P in section 13. These are pinned owner-source **implementation references**, not an installable app, finished destination code or approved research. Port code and styles into shared destination components; do not copy topic content, accounts, author assignments or scientific grades. A newer verified owner revision may supersede these snapshots; record its version and the change.

Read [Prose, ordered citations and hero actions](article-presentation.md) for the owner's current article-presentation correction and its acceptance cases.

The [PepsAnon article source packet](pepsanon-article/README.md) adds exact code/style captures for hero actions, canonical prose and citation ordering, with dependencies, hashes and necessary corrections. It is source material for a port, not a tested destination theme.

## Sources and required reuse

| Module | Reference | Packaged files |
|---|---|---|
| Inline FAQs | `paleofoundation/microbiomemedicine`, commit `28ed85b6d510dfddf1720775b456771c7dc62763`; live [Microbiome Medicine](https://microbiomemedicine.com/) | `microbiome-medicine/faqs.ts`, `faq-source.css`, `DESIGN-SYSTEM-FAQ-excerpt.md`, provenance manifest/audit |
| Compact evidence table | PepsAnon `site-study-records`, commit `e8c88effdf3aad26ebe805c72cbda361c78a4092`; inspected files identical to last recorded successful deployment source `8dfbd38d205b94094b26dada1d477cffc80adb2e` | `pepsanon/evidence-table.tsx`, three reference CSS extracts, `types.reference.ts` |
| Right-side research panel | Same PepsAnon source; [rendered BPC-157 evidence section](https://pepsanon.com/peptides/bpc-157#evidence) | `pepsanon/research-panel.tsx`, `sheet.tsx`, `utils.ts`, `research-details.reference.css` |

Each subdirectory records source files/locators and SHA-256 hashes. Preserve those snapshots. Make changes in the destination implementation and record the adaptation. Root independently observed the live PepsAnon table, opening a count into its right-side modal panel and Escape dismissal preserving the guide URL on 9 October 2026. This was reference inspection, not a Second Look parity test.

## FAQ port

Reuse the `rgbc-faq-block` / `rgbc-faq-item` / `rgbc-faq-icon` / `rgbc-faq-q` / `rgbc-faq-a` structure, native `details`/`summary`, circular plus/minus, serif question styling, indented answer with side rule, and Quick answer label. Native disclosures allow multiple open answers. Map primary, serif-font and answer-rule colors to the destination brand; do not carry Microbiome Medicine's red into every site.

The source helper keeps both plain text and citation-bearing `aHtml`. Preserve authored paragraphs, lists and links through canonical structured rendering or the destination's HTML sanitizer. Its helper is **not a sanitizer**. Do not copy the older ArticleView plain-text fallback that loses citation links. Follow the design-system instruction to preserve an existing authored FAQ block.

Required corrective adaptations: use the actual per-page question map rather than the helper's maximum-three/heading-guess fallback; remove the implicit recommended-dosage framing; enforce one shared duplicate guard in every caller (the historical WpRender path lacked it); add stable canonical question IDs and direct/repeated fragment reveal; keep visible focus and keyboard/touch access; and make any structured data match the full visible answer. Stable question fragments and uniform idempotence are new portable acceptance requirements, **not verified features of the old source**. FAQ answers may be concise; neither generic questions nor arbitrary quotas replace demand coverage.

## Table and panel port

For the Second Look / drug-repurposing profile, the owner's 11 October 2026
instruction is explicit: **Evidence begins with explanatory prose and ends with
the PepsAnon-style evidence table**. Render all section interpretation and scoped
evidence explanations before that final table. Use exactly three semantic columns
in this order: **Outcome and study design / Grade / Evidence**. Keep the outcome
cell compact, with study design beneath the outcome; do not repeat every finding,
numerical estimate and limitation as long paragraphs in the table. Preserve the
existing authored Benefits, Results and Evidence prose, and keep each row's full
finding, magnitude, uncertainty and source details available in its matching
research panel. Grade means evidence certainty and retains its honest unappraised
state; the row's detailed explanation remains available in the panel. Evidence
contains the document-icon count control with
accurate report/study-family/background labels. Keep design context subordinate
to the outcome, and keep both outcome and count controls opening that same row's
right-side research overlay. An extra findings column, a table followed by the
section's remaining prose, or an outcome button that navigates away does not
match this scoped instruction.

Apply this ordering through the shared article/generation contract and every
adopted route adapter, including generated or imported Drug, Condition and
scoped-answer pages. Keep one canonical Evidence synthesis and preserve existing
fragment aliases; do not reintroduce the earlier separate early findings view in
Second Look. The shared citation traversal must follow this actual order and the
table's cells without renumbering when the panel opens. If no synthesis rows are
available, retain the table headers and one truthful empty-state row without
invented grades or source counts; record the unfinished page. This is a requested contract, not
proof that a particular code version is implemented, verified or released.

Preserve semantic table markup, compact rows, primary-colored header, fine cell borders, subordinate cited design context, compact certainty treatment and FileText source-count control. The reference uses 58/18/24 percent columns, a 36rem minimum table width and contained horizontal scrolling; these are useful reference geometry, not reasons to discard required destination fields. Preserve substantive findings and consequential limits in the main guide's prose under its adopted content contract, with row-level details in the panel. Other profiles may require additional visible fields and a documented width/column adaptation; Second Look uses the scoped compact three-column correction above. The table must still look and operate like the reference rather than a generic long-text grid.

Import `table-overflow.reference.css`, `table-base.reference.css`, then `research-details.reference.css` in that order, or preserve the same precedence in the destination style system. Map `--color-primary`, `--color-primary-dark`, surface/border/hover/grade colors and fonts to the brand contract. The excerpts retain literal reference colors for traceability; replace them with destination semantic tokens during the port. Keep accessible contrast and explicit text labels independent of color. Load the destination fonts deliberately rather than relying on accidental fallback.

`ResearchPanel` uses React, Radix Dialog through `radix-ui`, Lucide icons, the Sheet wrapper, and `cn` from clsx/tailwind-merge. Sheet utilities assume the destination's Tailwind and animation setup. Another stack may port the same accessible behavior; never import these files blindly and claim a working component. Source snapshots deliberately omit topic data and private services. Implement destination-native adapters for `CitedText`, `Grade`, source/study identity and synthesis rows; the recorded source types explain the reference API, not a replacement for richer destination schemas.

The reference panel is `min(44rem,100vw)`, sits above the backdrop and header, has a fixed-in-panel header and independently scrolling body, and adapts facts/padding at narrow widths. Both outcome and count controls open the matching row's research. Preserve findings/limits, source identities, study detail disclosures, source/PDF links and locators; metadata belongs once in its source area. Preserve the separate inline Research → Studies/References catalogue.

Required corrective adapters:

- Use typed evidence certainty with neutral Not appraised/held/background/no-eligible-evidence states. **Do not copy `gradeShort`, `gradeLevel` or an otherwise-Low fallback.** Distinguish magnitude, certainty and source status.
- Deduplicate by canonical report/study-family identity, not URL or a source-kind string prefix. Label report, study-family and background counts accurately.
- Never copy the panel's hardcoded access-date fallback or topic-specific hold wording. Use actual dates/reasons and precise unresolved state.
- Track the actual opener explicitly: the two source triggers can otherwise return focus to the wrong button. Verify X/Escape/backdrop close, focus containment/restoration, scroll lock/restoration, touch and reduced motion.
- Preserve correction/quarantine/access state, sentence-level citations, endpoint/population/comparator/timepoint, numerical intervals and all available source locators. The compact reference type must not discard them.

## Evidence to return

For Second Look, assert that each populated Evidence section's first substantive
content is prose and its final substantive content is exactly one table with the
three named columns. Verify both opening paths, exact row/source identity and
actual-opener focus restoration. Include representative Drug, Condition, scoped
answer and comparison routes, an honest missing-synthesis state and regeneration
through the shared contract. A source/SSR assertion supplements, but cannot
replace, the desktop/mobile visual and interaction checks below.

Record reference source/hash → destination file/component → changes and reasons. Include the per-page FAQ coverage map, reference/destination screenshots at comparable desktop/mobile widths, both table-opening paths, panel identity/links and close/focus/scroll checks. Test a second drug and condition page to prove shared inheritance. G4P fails if any required module is absent or replaced with a superficial approximation. Report remaining research work separately; importing UI code does not approve the underlying science.
