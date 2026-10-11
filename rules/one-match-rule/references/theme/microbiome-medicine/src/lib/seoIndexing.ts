// Canonical host, path, and indexability rules for crawlers.
// Apex https://microbiomemedicine.com, no trailing slash (except `/`).

export const CANONICAL_HOST = "microbiomemedicine.com";
export const SITE_ORIGIN = `https://${CANONICAL_HOST}`;

export const PRODUCTION_ALIAS_HOSTS = new Set([
  "www.microbiomemedicine.com",
  "microbiomemedicine.vercel.app",
  "microbiomemedicine-karen-pendergrass-projects.vercel.app",
  "microbiomemedicine-karen-1166-karen-pendergrass-projects.vercel.app",
]);

/** Root WP/utility slugs that 200 but must not be indexed or listed in the sitemap. */
export const NOINDEX_PAGE_SLUGS = new Set([
  "auth",
  "checkout",
  "login",
  "membership",
  "membership-2",
  "microbiome-signatures-home-new",
  "tables-test",
]);

/** Path prefixes that are private, preview-only, or search/thin. */
export const NOINDEX_PATH_PREFIXES = [
  "/search",
  "/login",
  "/dashboard",
  "/auth/",
  "/research-feed-demo",
  "/signature-demo",
  "/taxon-demo",
  "/taxa",
] as const;

export function hostnameOf(hostHeader: string): string {
  return hostHeader.split(":")[0].toLowerCase();
}

export function isLocalHost(host: string): boolean {
  const h = hostnameOf(host);
  return h === "localhost" || h === "127.0.0.1" || h === "[::1]" || h.endsWith(".local");
}

/** Unique preview deployment hosts (not the production vercel.app aliases). */
export function isPreviewHost(host: string): boolean {
  const h = hostnameOf(host);
  return h.endsWith(".vercel.app") && !PRODUCTION_ALIAS_HOSTS.has(h);
}

export function shouldForceApex(host: string): boolean {
  const h = hostnameOf(host);
  if (!h || isLocalHost(h) || isPreviewHost(h)) return false;
  return h !== CANONICAL_HOST;
}

export function stripTrailingSlash(pathname: string): string {
  if (!pathname || pathname === "/") return "/";
  const next = pathname.replace(/\/+$/, "");
  return next || "/";
}

export function canonicalPath(pathname: string): string {
  const p = pathname.startsWith("/") ? pathname : `/${pathname}`;
  return stripTrailingSlash(p);
}

export function canonicalUrl(pathname: string): string {
  const p = canonicalPath(pathname);
  // Next.js emits the homepage canonical without a trailing slash; match that so
  // sitemap + <link rel=canonical> stay identical.
  return p === "/" ? SITE_ORIGIN : `${SITE_ORIGIN}${p}`;
}

export function pathHasExtraSlash(pathname: string): boolean {
  return pathname.length > 1 && pathname.endsWith("/");
}

/** Rewrite captured WP href/action values to the no-slash canonical path. */
export function unslashInternalHrefs(html: string): string {
  return html.replace(/\b(href|action)=(["'])([^"']*)\2/gi, (full, attr: string, q: string, url: string) => {
    if (!url || /^(#|mailto:|javascript:|tel:)/i.test(url)) return full;
    try {
      const abs = /^https?:\/\//i.test(url);
      const base = abs ? url : `${SITE_ORIGIN}${url.startsWith("/") ? url : `/${url}`}`;
      const u = new URL(base);
      const host = u.hostname.replace(/^www\./, "");
      if (host !== CANONICAL_HOST) return full;
      const path = stripTrailingSlash(u.pathname);
      const next = `${path}${u.search}${u.hash}`;
      return `${attr}=${q}${next}${q}`;
    } catch {
      return full;
    }
  });
}

export function isNoindexPath(pathname: string): boolean {
  const p = canonicalPath(pathname);
  if (p !== "/" && NOINDEX_PAGE_SLUGS.has(p.slice(1))) return true;
  return NOINDEX_PATH_PREFIXES.some((prefix) => {
    const c = canonicalPath(prefix);
    return p === c || p.startsWith(`${c}/`);
  });
}

export type CanonicalDecision =
  | { redirect: string; status: 301 | 308 }
  | { redirect: null };

/**
 * One-hop canonicalization: apex host + no trailing slash + WordPress `/?s=` → `/search?q=`.
 * `origin` is used for same-host redirects (localhost / preview).
 */
export function decideCanonical(
  host: string,
  pathname: string,
  search: string,
  origin: string
): CanonicalDecision {
  const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  const forceApex = shouldForceApex(host);
  const base = forceApex ? SITE_ORIGIN : origin.replace(/\/$/, "");

  const path = canonicalPath(pathname);
  if (path === "/" && params.has("s")) {
    const dest = new URL("/search", `${base}/`);
    const q = (params.get("s") || "").trim();
    if (q) dest.searchParams.set("q", q);
    return { redirect: dest.toString(), status: 301 };
  }

  if (/^\/10\.\d+/.test(path)) {
    const dest = new URL("/search", `${base}/`);
    dest.searchParams.set("q", path.slice(1));
    return { redirect: dest.toString(), status: 301 };
  }

  const slashWrong = pathHasExtraSlash(pathname);
  if (!forceApex && !slashWrong) return { redirect: null };

  const dest = new URL(`${base}${path === "/" ? "/" : path}`);
  // Keep non-search query strings (utm, page, …) on the canonical URL.
  params.forEach((value, key) => dest.searchParams.append(key, value));
  return { redirect: dest.toString(), status: 308 };
}
