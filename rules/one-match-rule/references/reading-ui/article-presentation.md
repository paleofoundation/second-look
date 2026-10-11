# Prose, ordered citations and hero actions

This is the reusable correction from the owner's 9 October 2026 screenshots and explicit instructions. It extends master sections 7–8 and gates G4/G4P/G8. Use the real PepsAnon source with the existing Microbiome Medicine base; do not rebuild the article as a dashboard. Read the [PepsAnon code/style packet and adaptation notes](pepsanon-article/README.md), which retains exact source hashes and bounded extracts.

## Narrative section contract

Most explanatory sections are visible, connected prose under descriptive headings. Overview, mechanism explanations, benefits and consequential safety context should be readable without opening controls. Do not render ordinary explanations as repeated metadata cards, fact grids, disconnected label/value rows or unnecessary bullet collections. Use a genuine accessible accordion for bounded questions or optional deeper detail when useful; a heading styled as a button without disclosure behavior is not an accordion. This does not require collapsing every section.

Preserve Microbiome Medicine's page-specific inline FAQ handling: question toggles, concise answer, citations, keyboard/touch operation and fragment reveal. Do not hide decisive findings or safety limits only inside disclosures. The required uses/findings and Evidence tables, canonical study catalogue, bibliography, necessary checklists and author/context metadata retain their semantic structures. The instruction to prefer prose is not permission to delete or convert those tables. Preserve useful approved content, source mappings and review states during a presentation change; do not add filler to satisfy a paragraph count.

For Second Look, the 11 October 2026 owner correction makes the Evidence module
order explicit: explanatory prose and any scoped evidence interpretation come
first; its single three-column **Outcome and study design / Grade / Evidence**
table comes last. Keep outcome and subordinate study design compact, retain the
existing authored Benefits, Results and Evidence prose, and keep full row
findings, magnitude and limits in the matching research panel. Preserve honest
certainty in Grade and both outcome and document-count triggers for that same
right panel. The shared article
plan and citation traversal must enforce this order for generated and imported
routes as well as the initial Drug and Condition examples. The earlier early
findings projection does not apply to this profile; retain its fragment only as
a compatibility alias inside Evidence. See the [table/panel contract](README.md).

## One page-local citation registry

1. Assign display numbers from 1 in first-appearance order in the article's canonical reading sequence, using canonical source identity. Include overview, Mechanisms, later prose, table cells, FAQ answers and source-bearing disclosures in their actual placement, plus any early findings view only when the site's adopted contract includes it. For Second Look, traverse all Evidence prose before its final table and account for the first visible citations in its compact design context; do not let drawer-only detail preempt visible citations. Build this traversal from the rendered content model, not an independently maintained list of fields that can omit a new section. The bibliography itself must not seed numbering.
2. Repeated citations reuse their source's number. A citation group is deduplicated and sorted by display number. For example, a repeat of source 1 after source 4 remains 1; it is not a numbering error and must not be relabeled 5. New first appearances remain sequential. Do not expose internal paper IDs such as CP027 as inline reference labels.
3. Every inline citation is a linked semantic superscript. Put the citation after the supported sentence's final punctuation, including a full stop: `A supported finding.<sup><a href="#ref-1">[1]</a></sup>`. A table phrase without sentence punctuation ends with its superscript; do not invent scientific text or alter numbers merely to add punctuation. Multiple sentences must retain claim-level source support instead of an ambiguous final paragraph-wide citation.
4. The same registry supplies prose, FAQs, tables, overlay context and bibliography labels/targets. Opening a disclosure or research panel, resizing, reordering a display control, or visiting a fragment must not renumber the article. A separately navigated study-review page has its own registry. A source-catalogue link that is not an inline claim citation may retain its descriptive title.
5. Every reference resolves to the right source and dedicated review under the current access policy. Reveal a closed bibliography/study/FAQ target on initial, repeated and back/forward navigation. Keep identity-based destinations and compatibility aliases when displayed numbers change after legitimate content edits. Protected review bodies remain protected; access does not change citation identity.

Do not repair numbering with a CSS-only superscript, a regex over already-rendered text, manual per-page numbering, source-ID sorting, or appending uncited records ahead of the article's cited sources. Handle structured content before rendering and validate actual final DOM order. Preserve all original source IDs, locators, corrections and quarantine states.

## Shared hero action row

Applicable entity/intervention guides render the PepsAnon-style action row inside the hero beneath its title/intro area: **Save [entity]**, **Safety**, **FAQs**, **Evidence**, **References**, with the corresponding bookmark, shield, discussion, chart and book icons. Topic naming is configuration: use Save drug for a drug site, not Save peptide. Preserve the reference's compact button hierarchy, spacing, borders and responsive wrapping through shared code/styles. The right-side hero author block, linked green ORCID and accessible biography remain present.

Other authored post types define their applicable action set in the same typed contract; do not invent irrelevant sections to display every button. An action appears only with a real destination or supported operation. If a required guide section is missing, complete it or record an unfinished guide state; silently hiding all its actions does not pass. A body-sidebar Save control or navigation rail does not substitute for this hero row.

- **Save** uses the existing supported account/private-library adapter, reflects actual saved state, persists across reload, handles failures honestly and returns an anonymous reader through login to the same item. Do not replace it with a browser-only bookmark or decorative button. Keep duplicate controls synchronized if retained elsewhere.
- **Safety**, **FAQs** and **Evidence** navigate to their correct page sections with usable sticky-header offsets and focus behavior. Evidence reaches the synthesis, not just a paper list.
- **References** reaches and opens the canonical bibliography. Direct and repeated clicks must work even when the hash has not changed. No duplicate reference list or second Research catalogue is created.

Pass this action set into the actual article hero in every route adapter. Having an unused `actions` prop in a library component is not implementation. Ensure projected parent/question routes and generated pages use the same contract. Reuse source appearance without carrying over PepsAnon authors, medical claims, scientific grades or obsolete service bindings.

## Required acceptance

For PepsAnon peptide and stack detail routes, the owner’s 9 October 2026 correction removes Connections and its desktop/mobile section-navigation entry. Apply this in shared contracts/renderers and ensure new pages inherit it; do not substitute a renamed relationship panel. Verify absence on both page families while preserving neighboring sections, inline/component/context links, canonical relation data and the research overlay. This exclusion is scoped to those pages, not a global prohibition on related content or other sites’ adopted modules.

Inspect Metformin-equivalent, second-entity and condition routes at approximately 320, 390, 768 and 1280px, plus a configuration-only synthetic topic through the same theme. Record actual rendered evidence and the source-to-destination map. Check the main explanations are predominantly visible prose; any accordions genuinely open/close and support direct fragments; tables and source limits remain visible; the complete applicable hero row is inside the hero, wraps without overflow and does not collide with the author.

Test citations when a Mechanisms source appears before a previously cited findings source; when a source repeats; when a group contains duplicate and reversed IDs; when a FAQ is initially closed; and when the research panel opens. Assert first new labels are 1, 2, 3 in canonical reading order, repeated identities keep their labels, groups are ascending without duplicates, superscripts follow punctuation, and bibliography/overlay/review targets agree. Catch an omitted rendering branch or newly added section rather than only testing a manually enumerated list. Preserve identity after a legitimate edit/reingest and check both initial and repeated reference clicks.

Exercise all hero actions with keyboard and touch, References disclosure reveal, and actual Save/login/persistence/error behavior using authorized test state and cleanup. A DOM element count alone cannot pass visual or functional parity. Missing buttons, dead hashes, cards replacing narrative, plain or before-period citations, per-section numbering resets, interaction-dependent renumbering, wrong-source targets or deleted evidence tables fail this scope. Technical/visual PASS does not establish scientific appraisal, full review, public release or guide-commerce readiness.
