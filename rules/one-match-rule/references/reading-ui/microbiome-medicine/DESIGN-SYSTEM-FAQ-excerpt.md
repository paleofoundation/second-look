- **FAQs:** heading "FAQs"; `.rgbc-faq-block` › `.rgbc-faq-item` `<details>` with the chevron icon
  and "Quick answer:". **FAQs are page-specific**, written around the questions people actually
  search for that entity (e.g. "Is X good or bad?", "What causes high X?", "How do you lower X?").
  They are NOT a template repeated across pages. Answers may carry inline `cite()` citations
  (proper `<sup><a class="rgbc-reference">` superscript links), so the answer is emitted as HTML,
  not `esc()`'d. `ArticleView` auto-builds FAQs ONLY for pages with no `.rgbc-faq-block` (older
  migrated pages); it must never rebuild over a real block (that duplicated it and re-escaped
  `&ldquo;`→`&amp;ldquo;` and stripped `[n]` citation links to plain text).
- **No raw HTML typographic entities in generated content.** Use real Unicode characters (" " · →
  – ₂), never `&ldquo;`/`&rdquo;`/`&rarr;`/`&middot;`/`&ndash;`/`&#8322;`. Entities render fine as
  content but reappear as literal text the moment any feature extracts and re-escapes them.
