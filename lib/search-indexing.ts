import publicContent from '@/data/public-content.json';
import createdDates from '@/data/page-created-dates.json';
import updatesFile from '@/data/article-updates.json';
import mechanisms from '@/data/public-mechanisms.json';
import suitability from '@/data/treatment-suitability.json';
import readerEvidence from '@/data/public-reader-evidence.json';
import outcomeSummariesFile from '@/data/outcome-summaries.json';
import drugStatus from '@/data/drug-status-table.json';
import {readinessContext} from './readiness.mjs';
import {
  INDEX_ROBOTS,
  NOINDEX_ROBOTS,
  SITEMAP_URL,
  STATIC_PAGE_COPY,
  canonicalUrl,
  indexableSitemapEntries,
  indexingJsonLd,
  isIndexableGuide,
  isProductionHost,
  lastmodFor,
  renderUrlSet,
  robotsTxtForHost,
  sitemapDocument,
  uniqueDescription,
} from './search-indexing.mjs';

type PublicGuide = {
  id: string;
  slug: string;
  title: string;
  type: string;
  description: string;
  sections?: unknown[];
  faqs?: unknown[];
  scopedSections?: unknown[];
  sourceIds?: string[];
};
type PublicSource = {id: string; title: string; doi?: string | null; year?: number; status?: string; correction?: string; url?: string};
type UpdateEntry = {date: string; title: string; changeType: string; pagePaths: string[]};

const content = publicContent as unknown as {guides: PublicGuide[]; sources: PublicSource[]};
const created = (createdDates as {dates: Record<string, string>}).dates;
const updates = (updatesFile as {entries: UpdateEntry[]}).entries;
const sourcesById = new Map(content.sources.map(source => [source.id, source]));
const library = readinessContext({
  sources: content.sources,
  mechanisms,
  suitability,
  synthesisRows: readerEvidence,
  outcomeSummaries: outcomeSummariesFile,
  status: drugStatus,
});

export {
  INDEX_ROBOTS,
  NOINDEX_ROBOTS,
  SITEMAP_URL,
  STATIC_PAGE_COPY,
  canonicalUrl,
  isProductionHost,
  robotsTxtForHost,
  uniqueDescription,
};

export function isPublicGuideIndexable(id: string) {
  const guide = content.guides.find(item => item.id === id);
  if (!guide) return false;
  return isIndexableGuide(guide, sourcesById, {live: true, context: library}).indexable;
}

export function publicSitemapEntries() {
  return indexableSitemapEntries(content.guides, content.sources, created, updates, library);
}

export function publicSitemapXml() {
  return sitemapDocument(publicSitemapEntries()).xml;
}

/** Chunk routes exist for a sitemap index. A single urlset lives at /sitemap.xml. */
export function publicSitemapPartXml(part: number) {
  const entries = publicSitemapEntries();
  const document = sitemapDocument(entries);
  if (!Number.isInteger(part) || part < 1 || document.kind === 'urlset' || !document.chunks[part - 1]) return null;
  return renderUrlSet(document.chunks[part - 1]);
}

export function indexingJsonLdForGuide(id: string) {
  const guide = content.guides.find(item => item.id === id);
  if (!guide || !isPublicGuideIndexable(id)) return null;
  return indexingJsonLd(guide, content.sources, lastmodFor(guide.slug, created, updates));
}
