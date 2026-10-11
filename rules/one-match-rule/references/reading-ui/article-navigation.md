# Article navigation, study summaries and Update History

Adopted 11 October 2026 from the owner's Examine sidebar screenshots and explicit Drug Repurposing request. This is a reusable contract under master sections 7–8, 12 and G4/G4P/G8/G9, not a claim that all existing sites are already migrated or deployed.

## Navigation and page order

Give every top-level article section a small outline icon before its text label, with consistent approximately 18–20px geometry, stroke weight, alignment and spacing. The provided screenshots demonstrate the desired restrained treatment: clipboard for Overview, chart for Evidence, feed/radio waves for Research Feed, question bubble for FAQs, history/clock for Update History and book/document for References. Use existing licensed icons or an equivalent source-derived implementation; preserve the site's identity. Other scientific modules retain meaningful configured icons. Icons are decorative when text supplies the accessible name (`aria-hidden` for SVG or empty alt for images); do not introduce duplicate spoken labels or extra focus stops.

Keep scientific modules such as Mechanisms, Benefits, Safety, Contraindications, Interactions and Dosing. The screenshots are not authority to delete these modules or to collapse every article into only six sections. Use concise labels and a shared typed section-ID/icon registry. **Research Feed** and **Update History** are deliberate exceptions to the older single-word-label rule. Expansion indicators remain distinct from section icons. Where an existing section has children, preserve accessible manual collapse/expand, active state and functional links; do not invent children solely to imitate a screenshot.

For applicable guides the terminal sequence is **Evidence → Research Feed → FAQs → Update History → References**, with the remaining adopted substantive modules before it. The body, left rail, mobile contents and canonical citation traversal derive from one ordered plan. FAQs must follow Evidence in both the sidebar and page content. Preserve scientific/source content and existing anchors when moving sections. Use compatibility aliases for old Research, Studies, update and reference fragments; direct, repeated, reload and back/forward navigation must reveal a target hidden inside a disclosure.

Post types that do not have this full module set retain their explicit typed contract; do not invent irrelevant FAQs or a study feed on a login screen. A page must not silently drop an applicable required module because its array is empty.

## Research Feed is the study-summary destination

Reuse the site's canonical paper/review catalogue: one item per canonical report, with explicit study-family relationships, rather than an independently maintained second feed. Research Feed must expose the available study summaries, their findings and decisive limitations, relevant population/design/year when known, and the matching dedicated review and original-source links. It cannot be a renamed bibliography, list of titles alone, duplicate evidence table, or unrelated news feed.

Every cited research paper still requires the dedicated source-traceable Q01–Q15 review in the [review contract](../research-reviews/README.md). The feed uses a concise safe projection of those same records. Unreviewed or unavailable inputs remain accurately marked; missing appraisals cannot be completed by changing the feed label or adding empty questions. Full review delivery still obeys server-enforced login, intake and release rules. Reference identities, source corrections and review routes remain shared with citations, the evidence panel and source library.

References is the one numbered bibliography, placed after Update History and collapsed by default under the established contract. It is a separate navigation destination, not another study-summary catalogue. This replaces the former forced Research → Studies/References sidebar grouping while preserving the canonical data and anti-duplication rules.

## Source mapping for Update History and icons

Use `paleofoundation/microbiomemedicine` at inspected commit `28ed85b6d510dfddf1720775b456771c7dc62763`:

| Behavior | Portable source |
|---|---|
| Heading-derived navigation groups with compact icon images and manual expansion | [SectionNav.tsx](../theme/microbiome-medicine/src/components/SectionNav.tsx), [ArticleView.tsx](../theme/microbiome-medicine/src/components/ArticleView.tsx), `SECTION_ICONS` and `buildNavGroups` |
| Design specification: short labels, heading emission order, material-change history | [DESIGN-SYSTEM reference](../theme/microbiome-medicine/docs/DESIGN-SYSTEM.md.reference.txt), Section sidebar and Update History entries |
| Timeline line/dot, date, title/type, content and responsive styles | [theme-wp.css](../theme/microbiome-medicine/src/styles/theme-wp.css), `.mbio-update-history` and `.mbio-card*` selectors |
| Exact existing history markup shape | [history-structure.reference.html](microbiome-medicine/history-structure.reference.html), extracted from source `src/data/taxon-demo.json`; original text/date/title replaced with explicit placeholders |

The complete pinned stylesheet and components are reference source, not a drop-in destination app. Record source-to-destination component/style adaptations. Port the `.mbio-update-history` → `.mbio-update-history__content` → `.mbio-card` hierarchy with `.mbio-card__border`, date, title/type and content into the existing shared renderer. Use semantic `<time datetime>` in the destination and brand tokens for the timeline rather than copying source red. Do not copy historical topic text, dates or people as new page events. Source inspection verified the markup/styles; it does not establish destination parity or that the reference's older section order supersedes the current request.

The source's icon grouping is useful guidance; add the destination's required accessible disclosure labels/expanded state and preserve proper link behavior. Keep the PepsAnon research overlay and current scientific modules separate. The owner request is authoritative over historical source-generation shortcuts.

## Editorial event contract

Update History is real page content after FAQs and before References, with a working sidebar target. Render page-specific versioned editorial events newest first: stable event ID, actual date/version, material change title/type and concise explanation; link affected outcomes/answers and source/review changes where applicable. Maintain source provenance privately. Explain whether a conclusion, certainty judgment, substantive summary or consequential safety statement changed. An honest initial recorded edition can be listed when supported; do not infer original publication or appraisal dates from a file's modification time, current build or deployment.

Separate evidence-search cutoff, substantive editorial review and actual event dates. A newly acquired paper or recently written summary is awaiting synthesis integration until that integration occurs; it is not evidence that the guide was reappraised. Preserve correction and retraction notices. A UI-only change must not imply new scientific review. Keep owner requests, task IDs, worker instructions, internal build commentary and private prioritization out of the reader-facing event body.

If no documented events exist, render a concise truthful empty state while retaining the section and navigation. Do not make up change entries, reviewer approval, source counts or a “last reviewed today” date merely to populate the timeline. The requirement adds a shared editorial-data projection, not a recurring automation or a new literature acquisition job.

## Acceptance

Inspect representative entity, second entity and condition guides and every affected imported/projected renderer branch at desktop and phone widths, plus repeat generation. Confirm compact outline icons align with labels, do not crowd long labels, inherit useful active/focus state, and remain secondary to text. Exercise keyboard/touch and existing expand/collapse behavior.

Read the actual DOM and screen from Evidence to References: Evidence content precedes the one Research Feed, then FAQs, then Update History, then the bibliography, matching navigation order. Confirm substantive earlier modules remain. Open a feed item and reach its exact source/review without leaking a protected body. Test reference and old study/Research fragments on first load, repeated clicks and back/forward. Check citation numbers against the final reading order, including initially closed summaries and FAQs.

Compare the history structure/styles with Microbiome source. Exercise multiple truthful events, a single event and no-history state; distinguish scientific updates from presentation-only events and source corrections. No invented dates, generic site-wide events masquerading as page-specific updates or duplicate summary catalogues. Capture exact route/code/data versions. Rule/source/package PASS is separate from rendered destination verification, scientific approval and release.
