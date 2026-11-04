import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {
  INDEX_ROBOTS,
  MIN_CITED_SOURCES,
  MIN_DOI_SOURCES,
  MIN_SECTION_CHARS,
  NOINDEX_ROBOTS,
  SITEMAP_PAGE_SIZE,
  canonicalUrl,
  citedSourceIds,
  indexableSitemapEntries,
  indexingJsonLd,
  isIndexableGuide,
  isProductionHost,
  lastmodFor,
  robotsTxtForHost,
  sitemapDocument,
} from '../lib/search-indexing.mjs';

const content = JSON.parse(readFileSync(new URL('../data/public-content.json', import.meta.url), 'utf8'));
const created = JSON.parse(readFileSync(new URL('../data/page-created-dates.json', import.meta.url), 'utf8')).dates;
const updates = JSON.parse(readFileSync(new URL('../data/article-updates.json', import.meta.url), 'utf8')).entries;
const sourcesById = new Map(content.sources.map((source) => [source.id, source]));
const entries = indexableSitemapEntries(content.guides, content.sources, created, updates);

function source(id, doi = `10.1000/${id}`) {
  return {id, title: `Study ${id}`, doi, year: 2024, url: `https://doi.org/${doi}`};
}

function fullGuide(overrides = {}) {
  const ids = Array.from({length: MIN_DOI_SOURCES}, (_, index) => `S${index}`);
  const paragraph = 'A'.repeat(MIN_SECTION_CHARS);
  const section = (id) => ({id, paragraph, sources: [ids[0]]});
  return {
    id: 'fixture',
    slug: '/drugs/fixture',
    title: 'Fixture',
    type: 'Drug',
    description: 'A fixture drug page with enough cited research to clear the index bar.',
    sourceIds: ids,
    faqs: [],
    sections: ['overview', 'benefits', 'safety', 'evidence'].map(section),
    ...overrides,
  };
}

test('robots.txt allows only the public remaprx hosts', () => {
  for (const host of ['remaprx.com', 'www.remaprx.com', 'REMAPRX.com', 'remaprx.com:443', 'www.remaprx.com:8443']) {
    const body = robotsTxtForHost(host);
    assert.equal(body, 'User-agent: *\nAllow: /\n\nSitemap: https://remaprx.com/sitemap.xml\n');
    assert.equal(isProductionHost(host), true);
  }
  for (const host of ['remaprx.workers.dev', 'foo.workers.dev', 'localhost', 'localhost:8787', '127.0.0.1:8788', 'preview.remaprx.com', 'remaprx.com.evil.example', 'www.remaprx.com.evil.example', 'notremaprx.com', '', null, undefined]) {
    const body = robotsTxtForHost(host);
    assert.equal(body, 'User-agent: *\nDisallow: /\n', `host ${host}`);
    assert.equal(body.includes('Sitemap'), false);
    assert.equal(body.includes('Allow'), false);
  }
});

test('sitemap includes only pages that clear the quality bar', () => {
  const metformin = content.guides.find((guide) => guide.slug === '/drugs/metformin');
  const decision = isIndexableGuide(metformin, sourcesById, {live: true});
  assert.equal(decision.indexable, true, decision.reasons.join(','));
  assert.ok(decision.cited >= MIN_CITED_SOURCES);
  assert.ok(decision.dois >= MIN_DOI_SOURCES);
  assert.ok(entries.some((entry) => entry.path === '/drugs/metformin'));

  for (const entry of entries) {
    assert.match(entry.loc, /^https:\/\/remaprx\.com\/(?:drugs|conditions)\//);
    assert.equal(entry.loc, canonicalUrl(entry.path));
    assert.match(entry.lastmod, /^\d{4}-\d{2}-\d{2}$/);
    const guide = content.guides.find((item) => item.slug === entry.path);
    assert.equal(isIndexableGuide(guide, sourcesById, {live: true}).indexable, true);
    assert.ok(guide.type === 'Drug' || guide.type === 'Condition');
  }
  assert.ok(entries.length < content.guides.length, 'thin guides stay out of the sitemap');
  assert.equal(entries.some((entry) => entry.path.startsWith('/research/') || entry.path.startsWith('/glossary/') || entry.path.startsWith('/account')), false);

  const metforminEntry = entries.find((entry) => entry.path === '/drugs/metformin');
  assert.equal(metforminEntry.lastmod, lastmodFor('/drugs/metformin', created, updates));
  assert.ok(metforminEntry.lastmod >= '2026-10-08');

  const document = sitemapDocument(entries);
  assert.equal(document.kind, 'urlset');
  assert.match(document.xml, /<loc>https:\/\/remaprx\.com\/drugs\/metformin<\/loc>/);
  assert.match(document.xml, /<lastmod>\d{4}-\d{2}-\d{2}<\/lastmod>/);
  assert.doesNotMatch(document.xml, /<(?:script|html)/i);
  console.log(`sitemap qualifying pages: ${entries.length}`);
});

test('quality bar rejects thin, incomplete, unresolved, and non-live pages', () => {
  const sources = new Map(Array.from({length: 8}, (_, index) => [`S${index}`, source(`S${index}`)]));
  assert.equal(isIndexableGuide(fullGuide(), sources, {live: true}).indexable, true);

  const shortSafety = fullGuide();
  shortSafety.sections = shortSafety.sections.map((section) => section.id === 'safety' ? {...section, paragraph: 'Too short.'} : section);
  assert.ok(isIndexableGuide(shortSafety, sources, {live: true}).reasons.includes('section:safety'));

  const seven = fullGuide({sourceIds: ['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6']});
  assert.ok(isIndexableGuide(seven, sources, {live: true}).reasons.includes('doi-count'));

  const missing = fullGuide({sourceIds: [...fullGuide().sourceIds, 'missing-source']});
  assert.ok(isIndexableGuide(missing, sources, {live: true}).reasons.includes('unresolved-source'));

  assert.ok(isIndexableGuide(fullGuide(), sources, {live: false}).reasons.includes('not-live'));

  const blocked = new Map(sources);
  for (let index = 0; index < 3; index += 1) blocked.set(`S${index}`, {...source(`S${index}`), status: 'Quarantined'});
  assert.ok(isIndexableGuide(fullGuide(), blocked, {live: true}).reasons.includes('doi-count'));

  const glossary = {id: 'term', slug: '/glossary/example', type: 'Glossary', description: 'A glossary page is not a drug or condition guide.', sections: [], sourceIds: []};
  assert.ok(isIndexableGuide(glossary, sources, {live: true}).reasons.includes('type'));

  const undated = indexableSitemapEntries([fullGuide()], [...sources.values()], {}, []);
  assert.equal(undated[0].lastmod, '2024-01-01');
});

test('sitemap index splits after 5000 URLs', () => {
  const many = Array.from({length: SITEMAP_PAGE_SIZE + 1}, (_, index) => ({
    id: String(index),
    path: `/drugs/example-${index}`,
    loc: `https://remaprx.com/drugs/example-${index}`,
    lastmod: '2026-11-04',
  }));
  const document = sitemapDocument(many);
  assert.equal(document.kind, 'index');
  assert.match(document.xml, /<sitemapindex xmlns="http:\/\/www\.sitemaps\.org\/schemas\/sitemap\/0\.9">/);
  assert.match(document.xml, /<loc>https:\/\/remaprx\.com\/sitemaps\/1\.xml<\/loc>/);
  assert.match(document.xml, /<loc>https:\/\/remaprx\.com\/sitemaps\/2\.xml<\/loc>/);
  assert.equal(document.chunks[0].length, SITEMAP_PAGE_SIZE);
  assert.equal(document.chunks[1].length, 1);
  assert.equal(sitemapDocument(many.slice(0, SITEMAP_PAGE_SIZE)).kind, 'urlset');
});

test('qualifying pages describe research with MedicalWebPage citations', () => {
  const guide = content.guides.find((item) => item.slug === '/drugs/metformin');
  const data = indexingJsonLd(guide, content.sources, '2026-10-12');
  const page = data['@graph'][0];
  assert.equal(page['@type'], 'MedicalWebPage');
  assert.equal(page.url, 'https://remaprx.com/drugs/metformin');
  assert.match(page.usageInfo, /not medical advice/);
  assert.equal(page.usageInfo.includes('—') || page.usageInfo.includes('–'), false);
  assert.ok(page.citation.length >= MIN_DOI_SOURCES);
  assert.ok(page.citation.every((item) => item['@type'] === 'ScholarlyArticle' && item.url.startsWith('https://doi.org/')));
  assert.ok(page.citation.some((item) => item.creativeWorkStatus === 'Retracted'));
  assert.equal(citedSourceIds(guide).length >= MIN_CITED_SOURCES, true);
  assert.equal(INDEX_ROBOTS, 'index,follow');
  assert.equal(NOINDEX_ROBOTS, 'noindex,follow');
});
