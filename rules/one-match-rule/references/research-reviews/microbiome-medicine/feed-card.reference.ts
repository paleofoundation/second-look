
// Build the signed-in card body (excerpt + accordion content + footer) for one study.
function cardBody(row: FeedRow): string {
  const url = `/research-feeds/${row.slug}`;
  const feed = row.meta?.feed;
  const paper = feed?.paper_url || url;
  const excerpt = (row.excerpt_html || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  // Summary sections: convert the study's <h3 …> headings to clean <h4> (matches the
  // generator's cards; dropping the ids avoids duplicate ids across many cards).
  // Card body = the study's 4-section summary as h4. The card title is a non-link <div>; the
  // header toggles the accordion to reveal this body inline, and the footer "Open" is the only
  // link to the summary page. Empty summary renders nothing here.
  const summary = (row.content_html || "")
    .replace(/<h3\b[^>]*>/g, `<h4 class="wp-block-heading">`)
    .replace(/<\/h3>/g, "</h4>");
  const mailto = `mailto:?subject=${encodeURIComponent(row.title || "")}&body=${encodeURIComponent(paper)}`;
  return (
    `<div class="research-feed__excerpt">${excerpt}</div>` +
    `<div class="research-feed__content accordion__content">${rfGraphs(feed)}${summary}</div>` +
    `<div class="research-feed__footer"><div>` +
    `<a class="btn" href="${url}">${SVG_DOC}Open</a>` +
    `<a class="btn" href="${paper}" target="_blank" rel="noreferrer">${SVG_LINK}Link</a>` +
    `<a class="btn" href="${mailto}">${SVG_MAIL}Email</a>` +
    `</div></div>`
  );
}

// norm(title) -> canonical slug for every research-feed item (loaded once per request).
