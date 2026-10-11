import { parseCsvObjects } from "./csv.mjs";

// WP sanitize_title: lowercase, strip accents, non-alphanumerics -> single hyphen,
// collapse/trim. "Stage 3/4 …: A Study" -> "stage-3-4-a-study".
export function slugify(s) {
  return (s || "")
    .toString()
    .toLowerCase()
    .normalize("NFKD").replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "");
}

const esc = (s) => (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const firstSentence = (s) => {
  const t = (s || "").replace(/\s+/g, " ").trim();
  const m = t.match(/^.*?[.!?](\s|$)/);
  return (m ? m[0] : t).trim().slice(0, 280);
};

// Split a structured abstract (OBJECTIVE:/RESULTS:/CONCLUSION: …) into the four
// canonical research-feed sections. Mechanical seed; LLM refinement is a future step.
export function abstractToSections(abstract) {
  const text = (abstract || "").trim();
  if (!text) return null;
  const re = /([A-Z][A-Z0-9 ,/()'-]{2,}?):\s+/g;
  const parts = [];
  let m, lastLabel = null, lastIdx = 0;
  while ((m = re.exec(text))) {
    if (lastLabel !== null) parts.push([lastLabel, text.slice(lastIdx, m.index).trim()]);
    lastLabel = m[1].trim();
    lastIdx = re.lastIndex;
  }
  if (lastLabel !== null) parts.push([lastLabel, text.slice(lastIdx).trim()]);

  const bucket = { studied: [], who: [], findings: [], implications: [] };
  const classify = (label) => {
    if (/OBJECTIVE|BACKGROUND|QUESTION|\bAIM|PURPOSE|PROBLEM|KNOWN ALREADY/i.test(label)) return "studied";
    if (/DESIGN|PARTICIPANT|PATIENT|METHOD|MATERIAL|SETTING|POPULATION/i.test(label)) return "who";
    if (/RESULT|FINDING|ROLE OF CHANCE/i.test(label)) return "findings";
    if (/CONCLUSION|IMPLICATION|INTERPRETATION|SIGNIFICANCE/i.test(label)) return "implications";
    return null;
  };
  if (parts.length >= 2) for (const [label, body] of parts) {
    const b = classify(label);
    if (b && body) bucket[b].push(body);
  }
  const out = [];
  if (bucket.studied.length) out.push(["What was studied?", bucket.studied.join(" ")]);
  if (bucket.who.length) out.push(["Who was studied?", bucket.who.join(" ")]);
  if (bucket.findings.length) out.push(["What were the most important findings?", bucket.findings.join(" ")]);
  if (bucket.implications.length) out.push(["What are the greatest implications of this study?", bucket.implications.join(" ")]);
  // Unstructured abstract: keep the whole thing under the first heading.
  if (!out.length) out.push(["What was studied?", text]);
  return out;
}

export function sectionsToHtml(sections) {
  // Canonical research-feed page format: h3 section headings + paragraphs (matches the
  // migrated WordPress research-feed pages rendered by ResearchFeedView).
  return sections.map(([h, t]) => `<h3 class="wp-block-heading">${esc(h)}</h3>\n<p class="wp-block-paragraph">${esc(t)}</p>`).join("\n");
}

// Build research-feed rows (one per study) + a title->internal-url map for the
// condition's signature Studies list. Reuses existing pages (does not duplicate):
// if slugify(title) already exists in content_items, link to it and skip creation.
export function buildResearchFeeds({ studiesCsv, experimentsCsv, conditionLabel, conditionSlug, author, existingSlugs, existingByTitle }) {
  const studies = parseCsvObjects(studiesCsv);
  const experiments = parseCsvObjects(experimentsCsv);
  const split = (v) => (v || "").split(",").map((x) => x.trim()).filter(Boolean);
  const uniq = (a) => [...new Set(a)];

  const byStudy = new Map();
  for (const e of experiments) {
    const key = (e["Study"] || "").trim();
    if (!key) continue;
    (byStudy.get(key) || byStudy.set(key, []).get(key)).push(e);
  }

  const existing = new Set(existingSlugs || []);
  const liveByTitle = existingByTitle || new Map(); // exact study Title -> existing slug
  const usedNew = new Set();
  const rows = [];
  const urlByTitle = new Map();

  for (const s of studies) {
    const title = (s["Title"] || "").trim();
    if (!title) continue;
    const key = (s["PMID"] || "").trim() || (s["Study page name"] || "").trim();

    // Reuse an existing research-feed page by exact title (robust to WP slug quirks
    // like percent-encoded Greek letters). Only create when no live page exists.
    const liveSlug = liveByTitle.get(title);
    if (liveSlug) { urlByTitle.set(title, `/research-feeds/${liveSlug}`); continue; }

    let slug = slugify(title);
    {
      let base = slug, n = 1;
      while (usedNew.has(slug) || existing.has(slug)) { n++; slug = `${base}-${n}`; }
      usedNew.add(slug);
      const exps = byStudy.get(key) || byStudy.get((s["Study page name"] || "").trim()) || [];
      const feed = {
        location: uniq(exps.flatMap((e) => split(e["Location of subjects"]))),
        sample_site: uniq(exps.flatMap((e) => split(e["Body site"]))),
        species: uniq(exps.flatMap((e) => split(e["Host species"]))),
        paper_url: (s["URL"] || "").trim() || (s["DOI"] ? `https://doi.org/${s["DOI"].trim()}` : ""),
        conditions: conditionLabel ? [{ label: conditionLabel, href: `/conditions/${conditionSlug}/` }] : [],
      };
      rows.push({
        type: "research-feed",
        slug,
        title,
        status: "publish",
        excerpt_html: firstSentence(s["Abstract"]) || title,
        content_html: sectionsToHtml(abstractToSections(s["Abstract"]) || [["What was studied?", title]]),
        published_at: s["Year"] ? `${s["Year"].trim()}-01-01` : null,
        meta: { feed, authors: author ? [author] : [] },
      });
    }
    urlByTitle.set(title, `/research-feeds/${slug}`);
  }
  return { rows, urlByTitle };
}
