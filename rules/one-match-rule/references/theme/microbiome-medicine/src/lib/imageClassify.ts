// Image classification + src normalization — PURE functions, no imports, shared by the
// render transform (src/lib/textRules.ts normalizeImages) and the AI-vision generation
// batch so the two ALWAYS agree on what an image is. No Supabase/runtime deps here so it
// is safe to import from any module (server or client) without bundling the DB client.

export type ImageKind = "content" | "hero" | "decorative" | "unknown";
export type ImageMeta = {
  kind: Exclude<ImageKind, "unknown">;
  alt: string | null;
  caption: string | null;
  width: number | null;
  height: number | null;
};

// Stable key for an <img> src: decode entity ampersands, make our own origin
// root-relative, and drop the query/hash (gravatar size params, cache-busts) so the
// same image keys identically wherever it appears.
export function normSrc(src: string): string {
  if (!src) return "";
  return src
    .trim()
    .replace(/&amp;/gi, "&")
    .replace(/^https?:\/\/(www\.)?microbiomemedicine\.com/i, "")
    .replace(/[?#].*$/, "");
}

// Classify by normalized src. DECORATIVE = avatars + theme/plugin chrome (never
// captioned, never schema/sitemap). CONTENT = real uploads (diagrams, heroes, art).
// UNKNOWN = anything else (treated like content for lazy/decoding, but never captioned
// and never given an injected alt). A metaMap row's kind always overrides this.
export function classify(normalizedSrc: string): ImageKind {
  const s = normalizedSrc;
  if (!s || /^data:/i.test(s)) return "unknown";
  if (/(^|\.)gravatar\.com/i.test(s) || /\/avatar\//i.test(s)) return "decorative";
  if (/\/static_media\//i.test(s)) return "decorative";
  if (/\/wp-content\/themes\//i.test(s) || /\/wp-includes\//i.test(s)) return "decorative";
  // Some /uploads/ files are generic section icons or logos, not content art.
  if (/\/wp-content\/uploads\//i.test(s)) return /(?:^|[-_/])(?:icon|logo)(?:[-_.]|$)/i.test(s) ? "decorative" : "content";
  return "unknown";
}
