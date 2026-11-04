/**
 * Search indexing for remaprx.com.
 *
 * Production hosts (remaprx.com and www.remaprx.com) may be crawled.
 * Every other host, including workers.dev and previews, stays disallowed.
 * Only LIVE drug and condition pages that pass the metformin-grade bar in
 * scripts/readiness.mjs are listed in the sitemap and rendered without
 * noindex. Other public pages use noindex,follow so a crawler can still
 * reach a page that later qualifies. docs/READY.md describes the bar.
 *
 * scripts/check-citation-gate.mjs still blocks a new or changed guide whose
 * DOIs are missing from research/deposits or research/corpus, do not resolve
 * on Crossref, or carry a retraction notice. This module does not repeat
 * that live Crossref call.
 */
import {assessGuide, readinessContext} from './readiness.mjs';

export const CANONICAL_ORIGIN = 'https://remaprx.com';
export const SITEMAP_URL = 'https://remaprx.com/sitemap.xml';
export const SITEMAP_PAGE_SIZE = 5000;
export const INDEX_ROBOTS = 'index,follow';
export const NOINDEX_ROBOTS = 'noindex,follow';

const PROCESS_PATTERN = /illustration|palette|image|icon|navigation|sidebar|reading order|layout|theme|design|reorganiz|easier to|ingest|pipeline|checkpoint|validat|render|handoff|internal review|rule version|build|deploy/i;
const MATERIAL_PRESENTATION = /^(expanded|added|new section|safety|correction)/i;

/** Keep in sync with the reader-facing Update History filter. */
export function isMaterialUpdate(entry) {
  if (!entry) return false;
  if (entry.changeType !== 'presentation') return !PROCESS_PATTERN.test(entry.title || '');
  return MATERIAL_PRESENTATION.test(entry.title || '') && !PROCESS_PATTERN.test(entry.title || '');
}

export function hostnameFromHostHeader(host) {
  if (!host) return '';
  const value = String(host).split(',')[0].trim().toLowerCase();
  if (value.startsWith('[')) {
    const end = value.indexOf(']');
    return end === -1 ? '' : value.slice(1, end);
  }
  return value.replace(/:\d+$/, '');
}

export function isProductionHost(host) {
  const name = hostnameFromHostHeader(host);
  return name === 'remaprx.com' || name === 'www.remaprx.com';
}

export function robotsTxtForHost(host) {
  if (!isProductionHost(host)) return 'User-agent: *\nDisallow: /\n';
  return `User-agent: *\nAllow: /\n\nSitemap: ${SITEMAP_URL}\n`;
}

export function canonicalUrl(path) {
  if (!path || path === '/') return `${CANONICAL_ORIGIN}/`;
  const clean = (String(path).startsWith('/') ? String(path) : `/${path}`).split(/[?#]/, 1)[0].replace(/\/+$/, '');
  return `${CANONICAL_ORIGIN}${clean || '/'}`;
}

export function uniqueDescription(title, description) {
  const text = String(description || '').replace(/\s+/g, ' ').trim();
  if (text.length >= 40) return text;
  const name = String(title || 'This page').replace(/\s+/g, ' ').trim() || 'This page';
  return `${name}. Research record in the RemapRx library.`;
}

export const STATIC_PAGE_COPY = {
  search: {
    title: 'Search the evidence library',
    description: 'Search drugs, conditions, studies, and glossary terms in the RemapRx library.',
  },
  research: {
    title: 'Research library',
    description: 'Browse original studies and supporting sources by drug, condition, and research question.',
  },
  questions: {
    title: 'Questions worth asking',
    description: 'Questions the library is tracking, with the evidence currently available for each.',
  },
  drugs: {
    title: 'Drugs',
    description: 'Drug pages in the repurposing atlas, including how each medicine works and what studies report.',
  },
  conditions: {
    title: 'Conditions and goals',
    description: 'Condition pages in the repurposing atlas, including the drugs studied and what the studies found.',
  },
  comparisons: {
    title: 'Compare the questions',
    description: 'Side by side questions that keep prevention, treatment, and other research scopes distinct.',
  },
  glossary: {
    title: 'A language for reading evidence',
    description: 'Short definitions for terms used in the evidence pages, with their study context attached.',
  },
  guides: {
    title: 'Guides and research companions',
    description: 'Educational guides that explain the research. They do not diagnose, prescribe, or replace professional care.',
  },
  'guides/membership': {
    title: 'Guide membership',
    description: 'Membership for future released guides. No charges or preorders are available yet.',
  },
  methods: {
    title: 'How we read the evidence',
    description: 'How RemapRx reads studies, grades outcome benefit, and keeps limitations visible.',
  },
  editorial: {
    title: 'Editorial standards',
    description: 'Editorial standards, corrections, and the limits of authorship on RemapRx.',
  },
  about: {
    title: 'About RemapRx',
    description: 'RemapRx is the drug repurposing atlas. It maps medications, investigated uses, and source-linked findings.',
  },
  privacy: {
    title: 'Privacy',
    description: 'How RemapRx handles saved research, reader profiles, and private notes.',
  },
  terms: {
    title: 'Terms of use',
    description: 'Terms for using this educational research site. It is not a treatment service.',
  },
  disclaimer: {
    title: 'Educational disclaimer',
    description: 'RemapRx explains research. It is not medical advice and does not replace professional care.',
  },
  corrections: {
    title: 'Corrections & contact',
    description: 'How to report a source or interpretation error. This channel is not urgent medical support.',
  },
  outcomes: {
    title: 'Explore research outcomes',
    description: 'Recorded research outcomes with the population, comparison, timepoint, and sources.',
  },
  account: {
    title: 'Saved research',
    description: 'Saved research for a signed-in reader. Private notes stay off public pages.',
  },
  'guides/library': {
    title: 'My guides',
    description: 'Guides linked to a signed-in account. This preview does not enable purchases.',
  },
};

export function normalizeDoi(value) {
  return String(value || '').trim().toLowerCase().replace(/^https?:\/\/(dx\.)?doi\.org\//, '');
}

export function isBlockedSource(source) {
  if (!source) return false;
  const status = String(source.status || '');
  const correction = typeof source.correction === 'string' ? source.correction : '';
  return /quarantine|retract|withdraw|remov/i.test(`${status} ${correction}`);
}

export function citedSourceIds(guide) {
  const ids = new Set(guide?.sourceIds || []);
  const visit = (value) => {
    if (Array.isArray(value)) {
      value.forEach(visit);
      return;
    }
    if (!value || typeof value !== 'object') return;
    if (Array.isArray(value.sources)) {
      for (const source of value.sources) ids.add(typeof source === 'string' ? source : source?.id);
    }
    Object.values(value).forEach(visit);
  };
  visit(guide?.sections);
  visit(guide?.faqs);
  visit(guide?.scopedSections);
  ids.delete(undefined);
  ids.delete(null);
  ids.delete('');
  return [...ids];
}

/**
 * @param {object} guide
 * @param {Map<string, object>} sourcesById
 * @param {{live?: boolean, context?: object}} [options]
 */
export function isIndexableGuide(guide, sourcesById, options = {}) {
  const base = options.context
    ? {...options.context, sourcesById: options.context.sourcesById || sourcesById, live: options.live !== false && options.context.live !== false}
    : readinessContext({sources: [...(sourcesById?.values?.() || [])], live: options.live !== false});
  const result = assessGuide(guide, base);
  return {indexable: result.pass, reasons: result.failing, cited: result.cited, dois: result.distinctDois, words: result.words};
}

function newestSourceYear(guide, sourcesById) {
  let max = 0;
  for (const id of citedSourceIds(guide)) {
    const year = sourcesById.get(id)?.year;
    if (Number.isInteger(year) && year > max && year < 10000) max = year;
  }
  return max ? `${max}-01-01` : undefined;
}

export function lastmodFor(path, createdDates, updateEntries) {
  const normalized = String(path || '/').split(/[?#]/, 1)[0].replace(/\/+$/, '') || '/';
  const dates = [];
  const created = createdDates?.[normalized];
  if (/^\d{4}-\d{2}-\d{2}$/.test(created || '')) dates.push(created);
  for (const entry of updateEntries || []) {
    if (!entry?.pagePaths?.includes(normalized) || !isMaterialUpdate(entry)) continue;
    if (/^\d{4}-\d{2}-\d{2}$/.test(entry.date || '')) dates.push(entry.date);
  }
  if (!dates.length) return undefined;
  return dates.sort().at(-1);
}

/** @param {object} [library] Readiness context from scripts/readiness.mjs. */
export function indexableSitemapEntries(guides, sources, createdDates, updateEntries, library) {
  const sourcesById = library?.sourcesById || (sources instanceof Map ? sources : new Map(sources.map((source) => [source.id, source])));
  const entries = [];
  for (const guide of guides) {
    if (!isIndexableGuide(guide, sourcesById, {live: true, context: library}).indexable) continue;
    const path = guide.slug?.startsWith('/') ? guide.slug : `/${guide.slug}`;
    entries.push({
      id: guide.id,
      path,
      loc: canonicalUrl(path),
      lastmod: lastmodFor(path, createdDates, updateEntries) || newestSourceYear(guide, sourcesById),
    });
  }
  entries.sort((a, b) => a.loc.localeCompare(b.loc));
  return entries;
}

function xmlEscape(value) {
  return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export function renderUrlSet(entries) {
  const body = entries.map((entry) => {
    const lastmod = entry.lastmod ? `<lastmod>${xmlEscape(entry.lastmod)}</lastmod>` : '';
    return `  <url><loc>${xmlEscape(entry.loc)}</loc>${lastmod}</url>`;
  }).join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}${body ? '\n' : ''}</urlset>\n`;
}

export function renderSitemapIndex(parts) {
  const body = parts.map((part) => {
    const lastmod = part.lastmod ? `<lastmod>${xmlEscape(part.lastmod)}</lastmod>` : '';
    return `  <sitemap><loc>${xmlEscape(part.loc)}</loc>${lastmod}</sitemap>`;
  }).join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</sitemapindex>\n`;
}

export function partitionSitemap(entries) {
  if (entries.length <= SITEMAP_PAGE_SIZE) return [entries];
  const chunks = [];
  for (let index = 0; index < entries.length; index += SITEMAP_PAGE_SIZE) {
    chunks.push(entries.slice(index, index + SITEMAP_PAGE_SIZE));
  }
  return chunks;
}

export function sitemapDocument(entries) {
  const chunks = partitionSitemap(entries);
  if (chunks.length === 1) return {kind: 'urlset', xml: renderUrlSet(chunks[0] || []), chunks};
  const parts = chunks.map((chunk, index) => ({
    loc: `${CANONICAL_ORIGIN}/sitemaps/${index + 1}.xml`,
    lastmod: chunk.map((entry) => entry.lastmod).filter(Boolean).sort().at(-1),
  }));
  return {kind: 'index', xml: renderSitemapIndex(parts), chunks};
}

export function indexingJsonLd(guide, sources, lastmod) {
  const sourcesById = sources instanceof Map ? sources : new Map(sources.map((source) => [source.id, source]));
  const citation = [];
  for (const id of citedSourceIds(guide)) {
    const source = sourcesById.get(id);
    const doi = normalizeDoi(source?.doi);
    if (!source || !doi) continue;
    const article = {
      '@type': 'ScholarlyArticle',
      headline: source.title,
      name: source.title,
      url: `https://doi.org/${doi}`,
      identifier: doi,
    };
    if (source.year) article.datePublished = String(source.year);
    if (isBlockedSource(source)) article.creativeWorkStatus = 'Retracted';
    citation.push(article);
  }
  const url = canonicalUrl(guide.slug);
  const page = {
    '@type': 'MedicalWebPage',
    '@id': `${url}#webpage`,
    url,
    name: guide.title,
    description: guide.description,
    inLanguage: 'en-US',
    isPartOf: {'@type': 'WebSite', name: 'RemapRx', url: `${CANONICAL_ORIGIN}/`},
    citation,
    usageInfo: 'This page explains research. It is not medical advice and does not diagnose, prescribe, or replace care from a qualified professional.',
  };
  if (lastmod) page.dateModified = lastmod;
  return {'@context': 'https://schema.org', '@graph': [page]};
}
