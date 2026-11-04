import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {loadReadinessInputs} from '../scripts/readiness.mjs';
import {
  INDEX_ROBOTS,
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
const loaded = loadReadinessInputs();
const sourcesById = loaded.context.sourcesById;
const entries = indexableSitemapEntries(content.guides, content.sources, created, updates, loaded.context);

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

test('sitemap includes only pages that clear the metformin-grade bar', () => {
  const metformin = content.guides.find((guide) => guide.slug === '/drugs/metformin');
  const decision = isIndexableGuide(metformin, sourcesById, {live: true, context: loaded.context});
  assert.equal(decision.indexable, true, decision.reasons.join(','));
  assert.deepEqual(entries.map((entry) => entry.path), ['/drugs/metformin']);

  for (const slug of ['/drugs/methylene-blue', '/drugs/melphalan']) {
    const guide = content.guides.find((item) => item.slug === slug);
    const thin = isIndexableGuide(guide, sourcesById, {live: true, context: loaded.context});
    assert.equal(thin.indexable, false, slug);
    assert.equal(entries.some((entry) => entry.path === slug), false);
  }

  for (const entry of entries) {
    assert.match(entry.loc, /^https:\/\/remaprx\.com\/(?:drugs|conditions)\//);
    assert.equal(entry.loc, canonicalUrl(entry.path));
    assert.match(entry.lastmod, /^\d{4}-\d{2}-\d{2}$/);
    const guide = content.guides.find((item) => item.slug === entry.path);
    assert.equal(isIndexableGuide(guide, sourcesById, {live: true, context: loaded.context}).indexable, true);
  }
  assert.equal(entries.some((entry) => entry.path.startsWith('/research/') || entry.path.startsWith('/glossary/') || entry.path.startsWith('/account')), false);

  const metforminEntry = entries.find((entry) => entry.path === '/drugs/metformin');
  assert.equal(metforminEntry.lastmod, lastmodFor('/drugs/metformin', created, updates));
  assert.ok(metforminEntry.lastmod >= '2026-10-08');

  const document = sitemapDocument(entries);
  assert.equal(document.kind, 'urlset');
  assert.match(document.xml, /<loc>https:\/\/remaprx\.com\/drugs\/metformin<\/loc>/);
  assert.doesNotMatch(document.xml, /methylene-blue|melphalan/);
  assert.match(document.xml, /<lastmod>\d{4}-\d{2}-\d{2}<\/lastmod>/);
  assert.doesNotMatch(document.xml, /<(?:script|html)/i);

  const undated = indexableSitemapEntries([metformin], content.sources, {}, [], loaded.context);
  assert.match(undated[0].lastmod, /^\d{4}-01-01$/);

  const glossary = {id: 'term', slug: '/glossary/example', type: 'Glossary', description: 'A glossary page is not a drug or condition guide.', sections: [], sourceIds: []};
  assert.ok(isIndexableGuide(glossary, sourcesById, {live: true, context: loaded.context}).reasons.includes('type'));
  assert.ok(isIndexableGuide(metformin, sourcesById, {live: false, context: loaded.context}).reasons.includes('not-live'));
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
  assert.ok(page.citation.length >= 15);
  assert.ok(page.citation.every((item) => item['@type'] === 'ScholarlyArticle' && item.url.startsWith('https://doi.org/')));
  assert.ok(page.citation.some((item) => item.creativeWorkStatus === 'Retracted'));
  assert.ok(citedSourceIds(guide).length >= 15);
  assert.equal(INDEX_ROBOTS, 'index,follow');
  assert.equal(NOINDEX_ROBOTS, 'noindex,follow');
});
