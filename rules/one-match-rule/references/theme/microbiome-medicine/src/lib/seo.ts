import type { Metadata } from "next";
import { canonicalPath, canonicalUrl, NOINDEX_PAGE_SLUGS } from "@/lib/seoIndexing";
import { sectionBySegment } from "@/lib/content";

export const SITE_URL = "https://microbiomemedicine.com";
export const SITE_NAME = "Microbiome Medicine";
export const NOINDEX_ROBOTS: Metadata["robots"] = { index: false, follow: false };
// Every image on the site is our own original work. This page states the usage/licensing
// terms and is the target for the ImageObject `license` + `acquireLicensePage` fields, so a
// single edit here remaps the licensing URL across every page's structured data.
export const IMAGE_LICENSE_URL = `${SITE_URL}/image-license`;

export type SeoItem = {
  title: string;
  seo_title?: string | null;
  seo_description?: string | null;
  excerpt_html?: string | null;
  published_at?: string | null;
  modified_at?: string | null;
};

export type SeoOpts = {
  path: string;
  type: string;
  authors?: { name: string; orcid?: string | null }[];
  doi?: string;
  journal?: string;
  image?: string | null;
  imageAlt?: string | null;
  imageCaption?: string | null;
  imageWidth?: number | null;
  imageHeight?: number | null;
  pdfUrl?: string;
};

// Strip unfinished citation markers ("x" / "[x]") so they never leak into meta
// descriptions, Scholar citation_abstract, or JSON-LD (which crawlers read). Mirrors
// the render rule in textRules.ts, but for the plain-text fields built here.
function stripUnfinishedCites(s: string): string {
  return s
    .replace(/<a\b[^>]*(?:rgbc-reference|js-rgbc-scroll-link)[^>]*>\s*\[?\s*x\s*\]?\s*<\/a>/gi, "")
    .replace(/\[\s*x\s*\]/gi, " ");
}
function stripTags(s?: string | null): string | undefined {
  if (!s) return undefined;
  const t = stripUnfinishedCites(s)
    .replace(/<[^>]+>/g, " ")
    // Migration artifact: "Overview" heading glued to the start of the excerpt
    // ("OverviewGraves' Disease ..."). Only matches when glued to a Capital letter.
    .replace(/\bOverview(?=[A-Z])/g, "")
    .replace(/\[\s*x\s*\]/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
  return t || undefined;
}
function abs(u?: string | null): string | undefined {
  if (!u) return undefined;
  if (/^https?:\/\//.test(u)) return u;
  return SITE_URL + (u.startsWith("/") ? u : "/" + u);
}

// Metadata: title/description + canonical + OpenGraph + Twitter + Google Scholar citation_* tags.
export function buildMetadata(item: SeoItem, o: SeoOpts): Metadata {
  const rawTitle = item.seo_title || item.title;
  const title = rawTitle.replace(/\s+[-–—|]\s+Microbiome Medicine\s*$/i, "").trim() || rawTitle;
  const description = item.seo_description || stripTags(item.excerpt_html);
  const image = abs(o.image);
  // Google Scholar prefers slash-separated dates (YYYY/MM/DD).
  const date = (item.published_at || item.modified_at || "").slice(0, 10).replace(/-/g, "/");
  const path = canonicalPath(o.path);
  const canonical = canonicalUrl(path);
  const noindex = path !== "/" && NOINDEX_PAGE_SLUGS.has(path.slice(1));
  // Authorless pages are authored by Karen (site rule), so Scholar always gets an author.
  const authors = o.authors?.length ? o.authors : [{ name: "Karen Pendergrass" }];
  const citationAbstract = stripTags(item.seo_description) || stripTags(item.excerpt_html);

  // Highwire Press citation_* tags — the bibliographic metadata Google Scholar indexes on.
  const other: Record<string, string | string[]> = {
    citation_title: item.title,
    citation_journal_title: o.journal || SITE_NAME,
    citation_publisher: SITE_NAME,
    citation_author: authors.map((a) => a.name),
    citation_fulltext_world_readable: "true",
    citation_language: "en",
    citation_abstract_html_url: canonical,
    citation_fulltext_html_url: canonical,
  };
  if (date) { other.citation_publication_date = date; other.citation_online_date = date; }
  if (citationAbstract) other.citation_abstract = citationAbstract.slice(0, 5000);
  if (o.doi) other.citation_doi = o.doi;
  const pdf = abs(o.pdfUrl);
  if (pdf) other.citation_pdf_url = pdf;

  return {
    title,
    description,
    alternates: { canonical },
    robots: noindex ? NOINDEX_ROBOTS : undefined,
    openGraph: {
      title,
      description: description || undefined,
      url: canonical,
      siteName: SITE_NAME,
      type: "article",
      publishedTime: item.published_at || undefined,
      modifiedTime: item.modified_at || undefined,
      authors: authors.map((a) => a.name),
      images: image ? [{ url: image, alt: o.imageAlt || title }] : undefined,
    },
    twitter: { card: "summary_large_image", title, description: description || undefined, images: image ? [{ url: image, alt: o.imageAlt || title }] : undefined },
    other,
  };
}

// JSON-LD graph: MedicalWebPage/ScholarlyArticle/Article + optional FAQPage + BreadcrumbList.
export function buildJsonLd(
  item: SeoItem,
  o: SeoOpts & { faqs?: { q: string; a: string }[]; breadcrumbs?: { name: string; url: string }[] }
): Record<string, unknown>[] {
  const url = canonicalUrl(o.path);
  const date = item.published_at || item.modified_at || undefined;
  const scholarly = ["research-feed", "theory"].includes(o.type);
  const medical = ["condition", "microbe", "metal", "definition", "intervention", "supplement"].includes(o.type);
  const main: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": scholarly ? "ScholarlyArticle" : medical ? "MedicalWebPage" : "Article",
    headline: item.title,
    name: item.title,
    description: stripTags(item.seo_description || item.excerpt_html),
    url,
    mainEntityOfPage: url,
    datePublished: date,
    dateModified: item.modified_at || date,
    inLanguage: "en-US",
    isAccessibleForFree: true,
    publisher: { "@type": "Organization", name: SITE_NAME, url: SITE_URL },
    author: (o.authors?.length ? o.authors : [{ name: "Karen Pendergrass", orcid: "https://orcid.org/0000-0002-2348-7259" }])
      .map((a) => ({ "@type": "Person", name: a.name, ...(a.orcid ? { identifier: a.orcid, sameAs: a.orcid } : {}) })),
  };
  if (o.doi) main.sameAs = `https://doi.org/${o.doi}`;
  // ImageObject for the page's representative image (hero/featured) so Google Images +
  // LLMs get a captioned, attributed, page-representative image. Caption is the same
  // AI-generated text shown in figcaptions; omitted cleanly when there is no hero.
  const imgAbs = abs(o.image);
  if (imgAbs) {
    // Every image on the site is our own original work, so the hero ImageObject carries full
    // ownership + licensing metadata. creditText/copyrightNotice/license/acquireLicensePage are
    // Google's image-license fields — supplying them clears the "missing field" notices in the
    // Search Console image reports and makes the images eligible for the licensable badge.
    const copyrightYear = date ? Number(String(date).slice(0, 4)) || undefined : undefined;
    main.image = {
      "@type": "ImageObject",
      contentUrl: imgAbs,
      url: imgAbs,
      ...(o.imageCaption ? { caption: stripTags(o.imageCaption) } : {}),
      ...(o.imageWidth ? { width: o.imageWidth } : {}),
      ...(o.imageHeight ? { height: o.imageHeight } : {}),
      representativeOfPage: true,
      creator: { "@type": "Organization", name: SITE_NAME, url: SITE_URL },
      creditText: SITE_NAME,
      copyrightHolder: { "@type": "Organization", name: SITE_NAME, url: SITE_URL },
      copyrightNotice: copyrightYear ? `© ${copyrightYear} ${SITE_NAME}` : `© ${SITE_NAME}`,
      ...(copyrightYear ? { copyrightYear } : {}),
      license: IMAGE_LICENSE_URL,
      acquireLicensePage: IMAGE_LICENSE_URL,
    };
  }
  const out: Record<string, unknown>[] = [main];

  if (o.faqs?.length) {
    out.push({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      mainEntity: o.faqs.map((f) => ({
        "@type": "Question",
        name: stripUnfinishedCites(f.q),
        acceptedAnswer: { "@type": "Answer", text: stripUnfinishedCites(f.a) },
      })),
    });
  }
  if (o.breadcrumbs?.length) {
    out.push({
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: o.breadcrumbs.map((b, i) => ({ "@type": "ListItem", position: i + 1, name: b.name, item: canonicalUrl(b.url) })),
    });
  }
  return out;
}

export function buildArchiveMetadata(segment: string, titleOverride?: string): Metadata {
  const s = sectionBySegment(segment);
  return {
    title: titleOverride || s?.label || segment,
    description: s?.blurb,
    alternates: { canonical: canonicalUrl(`/${segment}`) },
  };
}
