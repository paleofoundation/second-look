import { cache } from "react";
import { supabase } from "./supabase";

// The condition/microbe/metal-page "Research Feed" is a WordPress accordion of study cards.
// Each card has a header (toggle + title) + sub-header (date / category) and then, for
// LOGGED-OUT visitors, a `<div class="wall">` teaser ("Create a free account to unlock").
// For SIGNED-IN readers we swap that wall for the study's real card body — matching the
// canonical generator format (_generator/pages/*/build.mjs): an italic excerpt, an
// accordion content block (Location/Sample Site/Species graphs + the summary as <h4>
// sections), and a footer with Open / Link / Email. Logged-out readers keep the wall.

const SVG_DOC = `<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:4px"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`;
const SVG_LINK = `<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:4px"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>`;
const SVG_MAIL = `<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:4px"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>`;

type FeedMeta = { location?: string[]; sample_site?: string[]; species?: string[]; paper_url?: string };
type FeedRow = { slug: string; title: string | null; excerpt_html: string | null; content_html: string | null; meta: { feed?: FeedMeta } | null };

function norm(s: string): string {
  return s.replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/&#0?39;|&rsquo;|&#8217;|&#x27;/g, "'").replace(/\s+/g, " ").trim().toLowerCase();
}

// End index of the balanced <div…> block starting at `start`.
function blockEnd(html: string, start: number): number {
  const re = /<div\b|<\/div>/g;
  re.lastIndex = start;
  let depth = 0, m: RegExpExecArray | null;
  while ((m = re.exec(html))) {
    depth += m[0] === "</div>" ? -1 : 1;
    if (depth === 0) return re.lastIndex;
  }
  return -1;
}

// Location / Sample Site / Species mini-graphs (generator's rfGraphs, verbatim shape).
function rfGraphs(f: FeedMeta | undefined): string {
  if (!f) return "";
  const fields: [string, string[]][] = [["Location", f.location || []], ["Sample Site", f.sample_site || []], ["Species", f.species || []]];
  const present = fields.filter(([, v]) => Array.isArray(v) && v.length);
  if (!present.length) return "";
  return `<div class="research-feed__graphs">` + present.map(([t, items]) =>
    `<div class="research-feed__graph"><div class="research-feed__graph-title">${t}</div><div class="research-feed__graph-items">` +
    items.map((i) => `<div class="research-feed__graph-item">${i}</div>`).join("") + `</div></div>`).join("") + `</div>`;
}

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
// Paginated (there are >1000 items, past Supabase's default cap) and dedup-aware: many
// studies exist twice (a clean generator item + an older WP-migrated `-N` copy with a
// truncated auto-excerpt), so on a title collision prefer the clean excerpt, then the
// base slug.
const getFeedTitleIndex = cache(async (): Promise<Map<string, string>> => {
  type Row = { slug: string; title: string | null; excerpt_html: string | null };
  const all: Row[] = [];
  const PAGE = 1000;
  for (let from = 0; from < 20000; from += PAGE) {
    const { data, error } = await supabase
      .from("content_items")
      .select("slug,title,excerpt_html")
      .eq("type", "research-feed")
      .range(from, from + PAGE - 1);
    if (error || !data?.length) break;
    all.push(...(data as Row[]));
    if (data.length < PAGE) break;
  }
  const truncated = (e: string | null) => /\[&hellip;\]|\[…\]/.test(e || "");
  const best = new Map<string, { slug: string; score: number }>();
  for (const d of all) {
    if (!d.title || !d.slug) continue;
    const key = norm(d.title);
    const score = (truncated(d.excerpt_html) ? 0 : 2) + (/-\d+$/.test(d.slug) ? 0 : 1);
    const prev = best.get(key);
    if (!prev || score > prev.score) best.set(key, { slug: d.slug, score });
  }
  const m = new Map<string, string>();
  for (const [k, v] of best) m.set(k, v.slug);
  return m;
});

// Signed-in only: replace each Research Feed teaser `.wall` with the real study card body.
export async function revealResearchFeedWalls(html: string): Promise<string> {
  if (!html || !html.includes('class="wall"')) return html;
  const titles = [...html.matchAll(/research-feed__title[^>]*>([\s\S]*?)<\/(?:a|div|h[1-6])>/g)].map((m) => ({
    idx: m.index as number,
    key: norm(m[1]),
  }));
  if (!titles.length) return html;
  // Each wall belongs to the nearest research-feed card title before it (within the card).
  const walls: { start: number; end: number; key: string }[] = [];
  for (const m of html.matchAll(/<div class="wall">/g)) {
    const start = m.index as number;
    const end = blockEnd(html, start);
    if (end < 0) continue;
    const t = titles.filter((x) => x.idx < start && start - x.idx < 5000).pop();
    if (t?.key) walls.push({ start, end, key: t.key });
  }
  if (!walls.length) return html;
  const index = await getFeedTitleIndex();
  const slugs = [...new Set(walls.map((w) => index.get(w.key)).filter(Boolean) as string[])];
  if (!slugs.length) return html;
  const { data } = await supabase
    .from("content_items")
    .select("slug,title,excerpt_html,content_html,meta")
    .in("slug", slugs);
  const bySlug = new Map((data || []).map((d) => [d.slug, d as FeedRow]));
  // Replace from the last wall to the first so earlier offsets stay valid.
  for (let i = walls.length - 1; i >= 0; i--) {
    const slug = index.get(walls[i].key);
    const row = slug ? bySlug.get(slug) : undefined;
    if (row) html = html.slice(0, walls[i].start) + cardBody(row) + html.slice(walls[i].end);
  }
  return html;
}
