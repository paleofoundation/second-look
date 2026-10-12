import assert from 'node:assert/strict';
import path from 'node:path';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {load, render} from './check-reader-sections.mjs';

const root = path.resolve(import.meta.dirname, '..');
const {content, guideUrl, isPrimarySource} = load(path.join(root, 'lib/content.ts'));
const {articleUpdates, articleUpdatesForPath, articleUpdateDate} = load(path.join(root, 'lib/update-history.ts'));
const tail = [
  ['section-evidence', 'Evidence'], ['research-feed', 'Research Feed'],
  ['faqs', 'FAQs'], ['update-history', 'Update History'], ['references', 'References'],
];
const profiles = content.guides.filter(guide => ['Drug', 'Condition', 'Evidence comparison'].includes(guide.type) || guide.type.includes('evidence answer'));
for (const guide of profiles) {
  const pageSources = content.sources.filter(source => guide.sourceIds.includes(source.id));
  const html = render(guide, pageSources);
  const nav = html.match(/<nav[^>]*aria-label="On this page"[^>]*>([\s\S]*?)<\/nav>/)?.[1];
  const article = html.match(/<article class="research-content__center entry-content">([\s\S]*?)<\/article>/)?.[1];
  assert(nav && article, guide.slug + ': article and contents both render');
  let navPosition = -1, bodyPosition = -1;
  for (const [id, label] of tail) {
    const nextNav = nav.indexOf('href="#' + id + '"');
    const nextBody = article.indexOf('id="' + id + '"');
    assert(nextNav > navPosition, guide.slug + ': sidebar order at ' + label);
    assert(nextBody > bodyPosition, guide.slug + ': body order at ' + label);
    navPosition = nextNav; bodyPosition = nextBody;
  }
  const navLinks = [...nav.matchAll(/<a\b[^>]*class="post-content__link[^>]*>[\s\S]*?<\/a>/g)];
  for (const [link] of navLinks) {
    assert(link.includes('class="omr-toc-icon" aria-hidden="true"'), guide.slug + ': decorative icon accompanies every top-level label');
    assert(/<svg[^>]*aria-hidden="true"/.test(link), guide.slug + ': icon has no duplicated accessible name');
    assert(/<span>[^<]+<\/span>/.test(link), guide.slug + ': visible link text retained');
  }
  const feed = article.slice(article.indexOf('id="research-feed"'), article.indexOf('id="faqs"'));
  assert(!feed.includes('id="references"'), guide.slug + ': bibliography is separate from Research Feed');
  const studyIds = [...feed.matchAll(/data-study-id="([^"]+)"/g)].map(match => match[1]);
  assert.deepEqual(studyIds, pageSources.filter(isPrimarySource).map(source => source.id), guide.slug + ': one canonical summary per primary source');
  for (const id of studyIds) {
    assert(feed.includes('id="study-' + id + '"'), guide.slug + ': stable disclosure target');
    assert(feed.includes('href="/research/' + id + '"'), guide.slug + ': dedicated summary destination');
  }
  for (const alias of ['research', 'studies', 'edition']) assert(article.includes('id="' + alias + '"'), guide.slug + ': legacy fragment ' + alias);
  assert(articleUpdatesForPath(guideUrl(guide)).length, guide.slug + ': dated history is scoped to existing article');
  assert(article.includes('dateTime="2026-10-11"'), guide.slug + ': persistent date rendered rather than a live build date');
}

const updateIds = new Set();
for (const update of articleUpdates) {
  assert(!updateIds.has(update.id), 'Update identifiers are unique'); updateIds.add(update.id);
  assert(/^\d{4}-\d{2}-\d{2}$/.test(update.date), 'History date is explicit');
  assert(update.title && update.summary && update.changeType, 'Meaningful history fields are present');
  assert.equal(new Set(update.pagePaths).size, update.pagePaths.length, 'History scope does not duplicate routes');
}
assert.equal(articleUpdateDate('2026-10-11'), 'October 11, 2026', 'Dates are timezone-stable');
assert.deepEqual(articleUpdatesForPath('/drugs/a-future-article'), [], 'New pages do not inherit old changes');
assert.deepEqual(articleUpdatesForPath('/drugs/metformin/?view=reader#edition'), articleUpdatesForPath('/drugs/metformin'), 'History scope tolerates query and fragment URLs');

// Approved-body rendering is tested with synthetic inputs; no live draft is released.
const {canRenderStudyReviewInline, InlineStudyReview} = load(path.join(root, 'components/article.tsx'));
const openingIds = ['what-was-studied', 'who-was-studied', 'important-findings', 'implications'];
const reviewFixture = id => ({
  id, sourceIds: [id], sections: [{id: 'summary', title: 'Summary', paragraph: 'An authored summary.', sources: [id], sentences: [{text: 'An authored summary.', sources: [id]}]}],
  openingBlocks: openingIds.map((blockId, index) => ({id: blockId, title: blockId, questionIds: ['Q0' + (index + 1)]})),
  questionAnswers: openingIds.map((_, index) => ({id: 'Q0' + (index + 1), answer: 'An authored answer.', sources: [id], locators: [{section: 'Results', pdf_page: 3}]})),
});
const fixtureSources = ['fixture-one', 'fixture-two'].map(id => ({id, title: id, preview: 'A public preview.', url: 'https://example.org/' + id}));
const frozenOrder = fixtureSources.map(source => source.id);
let combined = '';
for (const source of fixtureSources) {
  const review = reviewFixture(source.id);
  assert(canRenderStudyReviewInline(review, source.id, fixtureSources, frozenOrder), 'Self-contained authorized review retains the page citation registry');
  const body = renderToStaticMarkup(React.createElement(InlineStudyReview, {review, sources: fixtureSources, order: frozenOrder, currentPath: '/fixture'}));
  for (const id of openingIds) assert(body.includes('id="study-' + source.id + '-opening-' + id + '"'), 'Every canonical opening is present and scoped to its study');
  assert(body.includes('Results · PDF page 3'), 'Source locator remains visible');
  const citations = [...body.matchAll(/data-source-id="([^"]+)"[\s\S]*?\[(\d+)\]/g)];
  assert(citations.length >= 5 && citations.every(match => match[1] === source.id && +match[2] === frozenOrder.indexOf(source.id) + 1), 'Opening answers and sections retain frozen citations');
  combined += body;
  assert(!canRenderStudyReviewInline({...review, sourceIds: ['unknown']}, source.id, fixtureSources, frozenOrder), 'Unknown citations stay on the dedicated review page');
  assert(!canRenderStudyReviewInline({...review, sourceIds: frozenOrder}, source.id, fixtureSources, frozenOrder), 'Cross-source reviews cannot change first appearances on expansion');
  assert(!canRenderStudyReviewInline({...review, questionAnswers: []}, source.id, fixtureSources, frozenOrder), 'Missing opening answers cannot be silently dropped');
}
const inlineIds = [...combined.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);
assert.equal(new Set(inlineIds).size, inlineIds.length, 'Two expanded reviews have no duplicate fragment IDs');
console.log(`PASS: ${profiles.length} articles have ordered icon navigation, matching body sections, canonical study summaries, legacy fragments and scoped durable history.`);
console.log('PASS: authorized summary fixtures preserve four opening blocks, source locators, frozen citations and unique IDs; unresolved/cross-source bodies remain on their dedicated pages.');
