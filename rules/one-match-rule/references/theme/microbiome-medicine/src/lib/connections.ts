// "Connections" = up to 3 most-relevant library entities for a page, shown as blue links
// in the right rail above Send feedback. Originally hand-curated (conditions first, then a
// heavily-referenced intervention) — that field wasn't captured in migration, so:
//   1. meta.connections (curated override) wins when present, else
//   2. an auto-default: rank the entities the page links to by mention frequency,
//      conditions first, cap 3.
export type Connection = { label: string; href: string; type: string };

const SEGMENTS = ["conditions", "metals", "interventions", "definition", "microbes", "supplement", "guide", "theory"];
const MAX = 3;

// Auto-default: frequency-rank the page's internal entity links, conditions first, cap N.
export function autoConnections(html: string, selfPath = "", max = MAX): Connection[] {
  if (!html) return [];
  const self = selfPath.replace(/\/+$/, "").toLowerCase();
  const acc = new Map<string, { label: string; type: string; n: number }>();
  const re = new RegExp(
    `<a\\b[^>]*href="(?:https?:)?(?:\\/\\/[^\\/"]+)?(\\/(?:${SEGMENTS.join("|")})\\/[^"#?]+)"[^>]*>([\\s\\S]*?)<\\/a>`,
    "gi"
  );
  let m: RegExpExecArray | null;
  while ((m = re.exec(html))) {
    const href = "/" + m[1].replace(/^\/|\/$/g, "");
    if (href.toLowerCase() === self) continue;
    const label = m[2].replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
    if (!label) continue;
    const cur = acc.get(href);
    if (cur) cur.n++;
    else acc.set(href, { label, type: href.split("/")[1], n: 1 });
  }
  return [...acc.entries()]
    .map(([href, v]) => ({ href, label: v.label, type: v.type, n: v.n }))
    .sort((a, b) => {
      const ac = a.type === "conditions" ? 0 : 1, bc = b.type === "conditions" ? 0 : 1;
      return ac - bc || b.n - a.n || a.label.localeCompare(b.label);
    })
    .slice(0, max)
    .map(({ label, href, type }) => ({ label, href, type }));
}

type Override = { label: string; href: string }[] | undefined | unknown;

// Curated override (meta.connections) wins; otherwise the auto-default.
export function resolveConnections(override: Override, html: string, selfPath = "", max = MAX): Connection[] {
  if (Array.isArray(override) && override.length) {
    return override
      .filter((o): o is { label: string; href: string } => !!o && typeof o.label === "string" && typeof o.href === "string")
      .slice(0, max)
      .map((o) => {
        const href = o.href.replace(/\/+$/, "") || "/";
        return { label: o.label, href, type: href.split("/")[1] || "" };
      });
  }
  return autoConnections(html, selfPath, max);
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

const escRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

// Match terms for a condition title: the base name (case-insensitive) plus any
// parenthetical abbreviation of length >= 3, case-sensitive (e.g. "PCOS", "IBS").
function conditionTerms(title: string): { term: string; ci: boolean }[] {
  const m = title.match(/^(.*?)\s*\(([^)]+)\)\s*$/);
  const base = (m ? m[1] : title).trim();
  const terms: { term: string; ci: boolean }[] = [];
  if (base) terms.push({ term: base, ci: true });
  if (m) { const abbr = m[2].trim(); if (abbr.length >= 3) terms.push({ term: abbr, ci: false }); }
  return terms;
}

// Internally link the FIRST mention of each existing condition in a page's body (rule:
// research-feed pages must link the conditions they discuss). Returns the linked HTML plus
// the conditions actually linked, in order of appearance, for the Connections sidebar.
// Skips text inside existing <a>…</a> and headings; links at most one condition per text run.
export function autolinkConditions(html: string, conditions: { title: string; href: string }[]): { html: string; linked: Connection[] } {
  if (!html || !conditions.length) return { html, linked: [] };
  const conds = [...conditions]
    .sort((a, b) => b.title.length - a.title.length)
    .map((c) => ({ c, terms: conditionTerms(c.title) }))
    .filter((x) => x.terms.length);
  const done = new Set<string>();
  const linked = new Map<string, Connection>();
  const parts = html.split(/(<[^>]+>)/);
  let aDepth = 0, hDepth = 0;
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    if (p.startsWith("<")) {
      if (/^<a\b/i.test(p)) aDepth++;
      else if (/^<\/a>/i.test(p)) aDepth = Math.max(0, aDepth - 1);
      else if (/^<h[1-6][\s/>]/i.test(p)) hDepth++;
      else if (/^<\/h[1-6]>/i.test(p)) hDepth = Math.max(0, hDepth - 1);
      continue;
    }
    if (aDepth > 0 || hDepth > 0 || !p.trim()) continue;
    let best: { idx: number; len: number; matched: string; href: string; label: string } | null = null;
    for (const { c, terms } of conds) {
      if (done.has(c.href)) continue;
      for (const t of terms) {
        // Treat any apostrophe variant interchangeably (title "Crohn’s" vs body "Crohn's").
        const pat = escRe(t.term).replace(/['‘’ʼ]/g, "['‘’ʼ]");
        const m = new RegExp(`\\b${pat}\\b`, t.ci ? "i" : "").exec(p);
        if (m && (!best || m.index < best.idx)) {
          best = { idx: m.index, len: m[0].length, matched: m[0], href: c.href, label: c.title.replace(/\s*\([^)]*\)\s*$/, "").trim() };
        }
      }
    }
    if (best) {
      parts[i] = p.slice(0, best.idx) + `<a href="${best.href}">${best.matched}</a>` + p.slice(best.idx + best.len);
      done.add(best.href);
      if (!linked.has(best.href)) linked.set(best.href, { label: best.label, href: best.href, type: "conditions" });
    }
  }
  return { html: parts.join(""), linked: [...linked.values()] };
}

// Ambiguous common words to NOT autolink even though they name an entity (Karen: "lead"
// is a problem word, "zinc"/"iron"/etc. are fine in this metals/microbiome context).
const LINK_DENY = new Set(["lead"]);

// Match terms for any concept entity: the base name (minus a trailing "(ABBR)") plus that
// parenthetical abbreviation. Acronym bases (all-caps, e.g. STOPs, EDTA) and abbreviations
// match case-sensitively; ordinary names case-insensitively. Bases shorter than 4 chars or
// on the denylist are dropped to limit noise.
export function entityTerms(title: string): { term: string; ci: boolean }[] {
  const paren = title.match(/^(.*?)\s*\(([^)]+)\)\s*$/);
  const base = (paren ? paren[1] : title).trim();
  const terms: { term: string; ci: boolean }[] = [];
  if (base.length >= 4 && !LINK_DENY.has(base.toLowerCase())) {
    const core = base.replace(/s$/, "");
    const acronym = core === core.toUpperCase() && /[A-Z]/.test(core) && /^[A-Z0-9][A-Z0-9.\- ]*$/.test(core);
    terms.push({ term: base, ci: !acronym });
    if (acronym && /s$/.test(base)) terms.push({ term: core, ci: false }); // "STOPs" -> also "STOP"
  }
  if (paren) {
    const abbr = paren[2].trim();
    if (abbr.length >= 3 && !LINK_DENY.has(abbr.toLowerCase())) terms.push({ term: abbr, ci: false });
  }
  return terms;
}

// Generalized autolinker: link the FIRST mention of every concept entity in a page body
// (all types, not just conditions). Whole-word, body-only (skips existing <a>, headings,
// and <style>/<script>/<svg>), first-mention-only per entity, multiple entities per run.
// Entities already linked anywhere in the html are pre-marked done, so we never double-link
// or override a manual/curated link.
export function autolinkEntities(
  html: string,
  targets: { title: string; href: string; type: string }[],
  selfHref = ""
): { html: string; linked: Connection[] } {
  if (!html || !targets.length) return { html, linked: [] };
  const self = selfHref.replace(/\/+$/, "").toLowerCase();
  const apo = (s: string) => escRe(s).replace(/['‘’ʼ]/g, "['‘’ʼ]");
  const items = targets
    .filter((t) => t.href.replace(/\/+$/, "").toLowerCase() !== self)
    .map((t) => ({ t, terms: entityTerms(t.title).map((x) => ({ ...x, re: new RegExp(`\\b${apo(x.term)}\\b`, x.ci ? "i" : "") })) }))
    .filter((x) => x.terms.length)
    .sort((a, b) => Math.max(...b.terms.map((x) => x.term.length)) - Math.max(...a.terms.map((x) => x.term.length)));
  const done = new Set<string>();
  // Pre-seed: any entity already linked in the html (manual/curated) is left alone.
  for (const { t } of items) {
    const h = t.href.replace(/\/+$/, "");
    if (new RegExp(`href="(?:https?:)?(?://[^/"]+)?${escRe(h)}/?"`, "i").test(html)) done.add(t.href);
  }
  const linked = new Map<string, Connection>();
  const parts = html.split(/(<[^>]+>)/);
  let aDepth = 0, hDepth = 0, sDepth = 0;
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    if (p.startsWith("<")) {
      if (/^<a\b/i.test(p)) aDepth++;
      else if (/^<\/a>/i.test(p)) aDepth = Math.max(0, aDepth - 1);
      else if (/^<h[1-6][\s/>]/i.test(p)) hDepth++;
      else if (/^<\/h[1-6]>/i.test(p)) hDepth = Math.max(0, hDepth - 1);
      else if (/^<(style|script|svg|noscript|textarea|code|pre)[\s/>]/i.test(p)) sDepth++;
      else if (/^<\/(style|script|svg|noscript|textarea|code|pre)>/i.test(p)) sDepth = Math.max(0, sDepth - 1);
      continue;
    }
    if (aDepth > 0 || hDepth > 0 || sDepth > 0 || !p.trim()) continue;
    const hits: { idx: number; len: number; matched: string; href: string; label: string; type: string }[] = [];
    for (const { t, terms } of items) {
      if (done.has(t.href)) continue;
      for (const term of terms) {
        const m = term.re.exec(p);
        if (m) { hits.push({ idx: m.index, len: m[0].length, matched: m[0], href: t.href, label: t.title.replace(/\s*\([^)]*\)\s*$/, "").trim(), type: t.type }); break; }
      }
    }
    if (!hits.length) continue;
    hits.sort((a, b) => a.idx - b.idx || b.len - a.len);
    let out = "", pos = 0;
    for (const h of hits) {
      if (done.has(h.href) || h.idx < pos) continue;
      out += p.slice(pos, h.idx) + `<a href="${h.href}">${h.matched}</a>`;
      pos = h.idx + h.len;
      done.add(h.href);
      if (!linked.has(h.href)) linked.set(h.href, { label: h.label, href: h.href, type: h.type });
    }
    out += p.slice(pos);
    parts[i] = out;
  }
  return { html: parts.join(""), linked: [...linked.values()] };
}

// Build the Connections list for a research-feed: a curated meta.connections override
// wins; otherwise the feed's tagged conditions first, then any other condition linked in
// the body. Conditions-first, deduped by href, capped at 3.
export function buildConnections(
  override: Override,
  feedConditions: { label: string; href: string }[],
  linked: Connection[],
  max = MAX
): Connection[] {
  if (Array.isArray(override) && override.length) return resolveConnections(override, "", "", max);
  const seen = new Set<string>();
  const out: Connection[] = [];
  for (const c of [...feedConditions.map((c) => ({ label: c.label, href: c.href, type: "conditions" })), ...linked]) {
    const key = (c.href || "").replace(/\/+$/, "").toLowerCase();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(c);
    if (out.length >= max) break;
  }
  return out;
}

// HTML-string version for injection into verbatim WP markup.
export function connectionsBlockHtml(html: string, selfPath = "", override?: Override): string {
  const cons = resolveConnections(override, html, selfPath);
  if (!cons.length) return "";
  const items = cons.map((c) => `<li><a href="${esc(c.href)}">${esc(c.label)}</a></li>`).join("");
  return `<div class="research-content__connections"><ul class="research-content__connections-list">${items}</ul></div>`;
}
