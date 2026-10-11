// ASCII-only public slugs. WordPress imported unicode dashes/letters (and
// sometimes already-percent-encoded slugs). Crawlers then 404 because Next
// decodes the URL and the DB lookup misses.

const DASH = /[\u2010-\u2015\u2212\u2043\u00AD\uFE58\uFE63\uFF0D\u2011]/g;

const GREEK: Record<string, string> = {
  α: "alpha",
  β: "beta",
  γ: "gamma",
  δ: "delta",
  ε: "epsilon",
  ζ: "zeta",
  η: "eta",
  θ: "theta",
  ι: "iota",
  κ: "kappa",
  λ: "lambda",
  μ: "mu",
  ν: "nu",
  ξ: "xi",
  ο: "omicron",
  π: "pi",
  ρ: "rho",
  σ: "sigma",
  ς: "sigma",
  τ: "tau",
  υ: "upsilon",
  φ: "phi",
  χ: "chi",
  ψ: "psi",
  ω: "omega",
};

export function decodeSlug(slug: string): string {
  let s = slug;
  for (let i = 0; i < 2; i++) {
    try {
      const next = decodeURIComponent(s);
      if (next === s) break;
      s = next;
    } catch {
      break;
    }
  }
  return s;
}

export function encodeSlug(slug: string): string {
  return encodeURIComponent(decodeSlug(slug)).replace(/%[0-9A-F]{2}/gi, (m) => m.toLowerCase());
}

export function asciiSlug(slug: string): string {
  let s = decodeSlug(slug).normalize("NFKC").toLowerCase();
  s = s.replace(DASH, "-");
  s = s.replace(/[αβγδεζηθικλμνξοπρσςτυφχψω]/g, (ch) => GREEK[ch] || "");
  s = s.replace(/[^a-z0-9]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
  return s;
}

export function isAsciiSlug(slug: string): boolean {
  return /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug);
}

export function slugLookupVariants(slug: string): string[] {
  const decoded = decodeSlug(slug);
  const encoded = encodeSlug(decoded);
  const ascii = asciiSlug(slug);
  const out: string[] = [];
  for (const s of [slug, decoded, encoded, ascii]) {
    if (s && !out.includes(s)) out.push(s);
  }
  return out;
}

export function slugsEquivalent(a: string, b: string): boolean {
  return asciiSlug(a) === asciiSlug(b) && asciiSlug(a).length > 0;
}

/** Longest distinctive ASCII token, for a cheap ilike fallback. */
export function slugSearchToken(slug: string): string | null {
  const stop = new Set([
    "the", "and", "for", "with", "from", "that", "this", "into", "were", "was",
    "its", "via", "in", "of", "to", "on", "by", "as", "an", "or", "at",
  ]);
  const tokens = asciiSlug(slug)
    .split("-")
    .filter((t) => t.length >= 6 && !stop.has(t))
    .sort((a, b) => b.length - a.length);
  return tokens[0] || null;
}
