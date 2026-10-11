// Universal content rules (Karen): NO em-dashes and NO visible ampersands, anywhere.
// Applied at render to every page body so the 575+ migrated rows are covered without
// hand-editing each one. Self-protecting against URLs / entities / attributes:
//   - em-dash (— or &mdash;) never appears in URLs or attributes; a numeric range becomes
//     "to", any other em-dash becomes ", " (a comma).
//   - an ampersand is only rewritten to "and" when it is SPACE-flanked prose ("X & Y" or
//     "X &amp; Y"). URL params (?s=96&d=mm), HTML entities (&amp; &nbsp; &mdash;), and the
//     JS && operator have no surrounding space, so they are left untouched by construction.
import { ORCID_SVG } from "@/components/OrcidIcon";
import { normSrc, classify, type ImageMeta } from "@/lib/imageClassify";
import { unslashInternalHrefs } from "@/lib/seoIndexing";

// Inline citation rule (Karen, locked in): every inline citation must render as a
// superscripted, bracketed, linked number — <sup><a class="rgbc-reference ...">[N]</a></sup>.
// You must NEVER see a literal "[x]" (filled or not) and never a non-superscript bracketed
// number. Two passes:
//   1) NORMALIZE numbered citations: migration damaged the markup (lost <sup> wrappers,
//      broken bracket nesting, junk like "[4][x]"). We repair the markup while PRESERVING
//      each citation's authored number — it never renumbers (numbers were assigned at
//      authoring by reference-list position and are not safely recomputable from markup,
//      since a source cited N times legitimately shows N different numbers).
//   2) STRIP unfinished citations: any marker still showing "x"/"[x]" had no recoverable
//      number (no reference-list entry, a list with non-unique ids, or a direct-URL
//      citation) and is removed entirely, along with bare "[x]" placeholders left in prose
//      or tables. Pages whose numbers ARE cleanly recoverable get them repaired at the
//      source (wp_render) so the citation survives as a real number rather than being cut.
const CITE = "";
function normalizeCitations(html: string): string {
  if (!html) return html;
  const hasRef = html.indexOf("rgbc-reference") !== -1;
  const hasX = /\[\s*x\s*\]/i.test(html);
  if (!hasRef && !hasX) return html;
  let out = html;

  if (hasRef) {
    const cites: { a: string; n: string }[] = [];
    out = out.replace(/<a\b([^>]*\bid="[^"]*-back"[^>]*)>([\s\S]*?)<\/a>/g, (m, attrs, inner) => {
      if (!/rgbc-reference/.test(attrs) || !/js-rgbc-scroll-link/.test(attrs)) return m;
      const d = (inner.match(/\d+/) || [])[0];
      if (!d) return m; // no recoverable number — removed by the strip pass below
      cites.push({ a: attrs, n: d });
      return CITE + (cites.length - 1) + CITE;
    });
    if (cites.length) {
      const s = CITE + "\\d+" + CITE;
      out = out
        .replace(new RegExp("\\[\\s*(" + s + ")", "g"), "$1")
        .replace(new RegExp("(" + s + ")\\s*\\]", "g"), "$1")
        .replace(new RegExp("<sup>\\s*((?:" + s + "[\\s\\[\\]]*)+)</sup>", "g"), "$1")
        .replace(new RegExp("<sup>\\s*(" + s + ")", "g"), "$1")
        .replace(new RegExp("(" + s + ")\\s*</sup>", "g"), "$1")
        .replace(new RegExp(CITE + "(\\d+)" + CITE, "g"), (_m, i) => `<sup><a${cites[+i].a}>[${cites[+i].n}]</a></sup>`);
    }
  }

  // Strip every UNNUMBERED citation marker and bare "[x]" so a literal "[x]" (or a stray
  // "x" citation) can never render. Real numbered citations are already <sup>[N]</sup> above.
  return out
    .replace(/<sup>\s*\[?\s*<a\b[^>]*>\s*\[?\s*x\s*\]?\s*<\/a>\s*\]?\s*<\/sup>/gi, "")
    .replace(/<a\b[^>]*(?:rgbc-reference|js-rgbc-scroll-link)[^>]*>\s*\[?\s*x\s*\]?\s*<\/a>/gi, "")
    .replace(/<sup>\s*(?:\[\s*x\s*\]\s*)+<\/sup>/gi, "")
    .replace(/\[\s*x\s*\]/gi, "")
    .replace(/<sup>\s*<a\b[^>]*>\s*<\/a>\s*<\/sup>/gi, "")
    .replace(/<sup>\s*<\/sup>/gi, "");
}

// Image rule (Karen, locked in): every image renders indexable + LLM-legible without
// touching the file itself. This idempotent pass, run on the same body HTML as the text
// rules, for each <img>: (1) classifies it decorative (avatar/UI chrome) vs content
// (real upload) vs unknown; (2) adds loading=lazy + decoding=async to non-hero images
// (CWV) and fetchpriority=high to the hero; (3) injects the AI-generated alt + intrinsic
// width/height from image_meta when present; (4) wraps CONTENT figures that have a
// caption in <figure class="rgbc-figure"> + a subtle <figcaption> (content only — hero
// and decorative stay uncaptioned; the caption still flows to ImageObject/alt elsewhere).
// It only ADDS attributes/wrappers, never reorders captured markup, so wp_render stays
// pixel-exact, and applyImages(applyImages(x)) === applyImages(x).
const hasAttr = (tag: string, name: string): boolean => new RegExp(`\\b${name}\\s*=`, "i").test(tag);
const getAttr = (tag: string, name: string): string | null => {
  const m = tag.match(new RegExp(`\\b${name}\\s*=\\s*"([^"]*)"|\\b${name}\\s*=\\s*'([^']*)'`, "i"));
  return m ? (m[1] ?? m[2] ?? "") : null;
};
const escAttr = (s: string): string =>
  s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const escText = (s: string): string =>
  s.replace(/&(?!(?:[a-z0-9]+|#\d+);)/gi, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
function addAttr(tag: string, name: string, value: string): string {
  if (hasAttr(tag, name)) return tag;
  return tag.replace(/(\s*\/?>)\s*$/, ` ${name}="${escAttr(value)}"$1`);
}
function setAttr(tag: string, name: string, value: string): string {
  if (hasAttr(tag, name))
    return tag.replace(new RegExp(`(\\b${name}\\s*=\\s*)("[^"]*"|'[^']*')`, "i"), `$1"${escAttr(value)}"`);
  return tag.replace(/(\s*\/?>)\s*$/, ` ${name}="${escAttr(value)}"$1`);
}

function normalizeImages(html: string, metaMap?: Map<string, ImageMeta>): string {
  if (!html || html.indexOf("<img") === -1) return html;
  const map = metaMap ?? new Map<string, ImageMeta>();
  return html.replace(
    /(<figure\b[^>]*>\s*)?(<img\b[^>]*>)((?:\s*<figcaption\b[\s\S]*?<\/figcaption>)?\s*<\/figure>)?/gi,
    (_whole, figOpen: string | undefined, imgTag: string, figTail: string | undefined) => {
      const key = normSrc(getAttr(imgTag, "src") || "");
      const meta = map.get(key);
      const kind = meta?.kind || classify(key);
      const isHero = /research-hero__left-image/.test(imgTag) || kind === "hero";

      let img = imgTag;
      if (meta?.width && !hasAttr(img, "width")) img = addAttr(img, "width", String(meta.width));
      if (meta?.height && !hasAttr(img, "height")) img = addAttr(img, "height", String(meta.height));
      img = addAttr(img, "decoding", "async");
      if (isHero) img = addAttr(img, "fetchpriority", "high");
      else img = addAttr(img, "loading", "lazy");
      if (meta?.alt && (isHero || kind === "content")) img = setAttr(img, "alt", meta.alt);

      const open = figOpen || "";
      const tail = figTail || "";
      const wantCaption = !isHero && kind === "content" && !!meta?.caption;
      if (!wantCaption) return open + img + tail;

      const cap = `<figcaption class="rgbc-figcaption">${escText(meta!.caption!)}</figcaption>`;
      if (open || tail) {
        // already inside a <figure>: add our caption only if none exists (idempotent)
        if (/<figcaption/i.test(tail)) return open + img + tail;
        return open + img + tail.replace(/<\/figure>\s*$/i, `${cap}</figure>`);
      }
      // bare content image with a caption: wrap it
      return `<figure class="rgbc-figure">${img}${cap}</figure>`;
    }
  );
}

export function applyTextRules(html: string, opts?: { images?: Map<string, ImageMeta> }): string {
  if (!html) return html;
  const out = normalizeCitations(unslashInternalHrefs(html))
    // Migration artifact: the first section heading "Overview" was glued onto the start of
    // the auto-generated hero excerpt ("OverviewGraves' Disease ..."). It only ever appears
    // glued directly to a Capital letter — the real <h2>Overview</h2> heading is followed by
    // "<", so this never touches a legitimate heading.
    .replace(/\bOverview(?=[A-Z])/g, "")
    .replace(/(\d)\s*(?:—|&mdash;|—)\s*(\d)/g, "$1 to $2")
    .replace(/\s*(?:—|&mdash;|—)\s*/g, ", ")
    .replace(/([A-Za-z0-9)\]])\s(?:&amp;|&)\s([A-Za-z0-9(\[])/g, "$1 and $2")
    // Author ORCID links captured from WP render their text as "ID"; swap in the real ORCID iD logo.
    .replace(/(<a\b[^>]*\borchid-id\b[^>]*>)\s*ID\s*(<\/a>)/gi, `$1${ORCID_SVG}$2`);
  return normalizeImages(out, opts?.images);
}
