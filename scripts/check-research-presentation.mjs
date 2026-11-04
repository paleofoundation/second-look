import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import ts from 'typescript';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';

const root = path.resolve(import.meta.dirname, '..');
const require = createRequire(import.meta.url);
const cache = new Map();
function load(file) {
  if (cache.has(file)) return cache.get(file).exports;
  if (file.endsWith('.css')) return {};
  if (file.endsWith('.json')) return JSON.parse(fs.readFileSync(file, 'utf8'));
  const module = {exports: {}};
  cache.set(file, module);
  const compiled = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
    fileName: file.endsWith('.mjs') ? file.slice(0, -4) + '.js' : file,
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true},
  }).outputText;
  const localRequire = id => {
    if (!id.startsWith('.') && !id.startsWith('@/')) return require(id);
    const base = id.startsWith('@/') ? path.join(root, id.slice(2)) : path.resolve(path.dirname(file), id);
    const target = [base, base + '.ts', base + '.tsx', base + '.json', path.join(base, 'index.ts')]
      .find(candidate => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
    assert(target, 'Cannot resolve ' + id + ' from ' + file);
    return load(target);
  };
  new Function('require', 'module', 'exports', compiled)(localRequire, module, module.exports);
  return module.exports;
}

const {StudyPage} = load(path.join(root, 'components/study-page.tsx'));
const {StudyFacts} = load(path.join(root, 'components/study-source-content.tsx'));
const {Article} = load(path.join(root, 'components/article.tsx'));
const {ThemeProvider} = load(path.join(root, 'components/shared-theme/theme.tsx'));
const {content, isPrimarySource} = load(path.join(root, 'lib/content.ts'));
const {STUDY_QUESTIONS} = load(path.join(root, 'lib/study-presentation.ts'));
const {STUDY_DETAIL_SECTIONS} = load(path.join(root, 'lib/study-review-plan.ts'));
const config = {mainId: 'main', identity: {name: 'RemapRx', homeHref: '/'}};
const render = element => renderToStaticMarkup(React.createElement(ThemeProvider, {config}, element));
const textOf = html => html.replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&#x27;/g, "'")
  .replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/\s+/g, ' ').trim();
const count = (text, part) => text.split(part).length - 1;

const source = content.sources.find(item => item.id === 'P-COVIDOUT-2023');
assert(source, 'Representative current public study exists');
const supporting = content.sources.filter(item => item.id !== source.id).slice(0, 2);
assert.equal(supporting.length, 2, 'Cross-source fixture uses resolvable existing source IDs');
const preview = {
  id: source.id, title: source.title, route: '/research/' + source.id, sourceUrl: source.url,
  preview: source.preview, decisiveLimit: source.decisiveLimit || '', reviewState: 'pending', version: 'fixture', sourceIds: [source.id],
};
const questionIds = Array.from({length: 15}, (_, index) => 'Q' + String(index + 1).padStart(2, '0'));
const review = {
  id: source.id, version: 'fixture-only', contentSha256: 'synthetic-not-a-release',
  sourceIds: [supporting[1].id, supporting[0].id, source.id],
  sections: [{id: 'summary', title: 'Legacy summary', paragraph: 'LEGACY-REVIEW-PARAGRAPH-SENTINEL', sources: [source.id]}],
  openingBlocks: [
    {id: 'what-was-studied', title: STUDY_QUESTIONS[0], questionIds: ['Q01', 'Q03', 'Q04']},
    {id: 'who-was-studied', title: STUDY_QUESTIONS[1], questionIds: ['Q02']},
    {id: 'important-findings', title: STUDY_QUESTIONS[2], questionIds: ['Q05', 'Q06', 'Q08']},
    {id: 'implications', title: STUDY_QUESTIONS[3], questionIds: ['Q09', 'Q10', 'Q14', 'Q15']},
  ],
  questionAnswers: questionIds.map((id, index) => ({
    id, question: 'Fixture question ' + id + '?', answer: 'PRIVATE-ANSWER-' + id + '-SENTINEL.', status: 'complete',
    sources: [supporting[index % supporting.length].id],
    locators: [{sourceId: supporting[index % supporting.length].id, section: 'Fixture Methods', pdf_page: index + 1, basis: 'fixture'}],
    render: {section: 'summary', fragment: 'canonical-' + id.toLowerCase()},
  })),
};
const previewAccess = {kind: 'preview', policy: 'free_authenticated', preview, reason: 'review_pending', review};
const publicHtml = render(React.createElement(StudyPage, {source, access: previewAccess}));
const publicText = textOf(publicHtml);
for (const heading of STUDY_QUESTIONS) assert(publicHtml.includes('<h3>' + heading + '</h3>'), 'Public summary retains opening: ' + heading);
assert(publicText.includes(source.title), 'Publication block preserves the exact source title');
assert(publicHtml.includes('class="study-publication__title"'), 'Exact paper title has a publication location');
assert(publicHtml.includes(source.doi), 'Recorded DOI remains available');
assert(!publicHtml.includes('PRIVATE-ANSWER-') && !publicHtml.includes('data-review-question='), 'Preview does not serialize attached protected answers');
assert(publicText.includes('The complete appraisal has not yet been released.'), 'Pending review is stated');

const before = JSON.stringify(review);
const fullHtml = render(React.createElement(StudyPage, {source, access: {kind: 'full', policy: 'free_authenticated', preview: {...preview, reviewState: 'released'}, review}}));
for (const id of questionIds) {
  assert.equal(count(fullHtml, 'data-review-question="' + id + '"'), 1, id + ' has exactly one detailed answer');
  assert.equal(count(fullHtml, 'PRIVATE-ANSWER-' + id + '-SENTINEL'), 1, id + ' answer prose renders exactly once');
  assert.equal(count(fullHtml, 'id="canonical-' + id.toLowerCase() + '"'), 1, id + ' keeps its canonical fragment');
}
for (const section of STUDY_DETAIL_SECTIONS) assert(fullHtml.includes('id="' + section.id + '"'), 'Detailed section exists: ' + section.id);
assert(!fullHtml.includes('Full appraisal questions'), 'Legacy raw appraisal wrapper is absent');
assert(!fullHtml.includes('LEGACY-REVIEW-PARAGRAPH-SENTINEL'), 'Legacy summary is not duplicated beside the mapped answers');
assert.equal(JSON.stringify(review), before, 'Rendering preserves the source review and hash');
const ids = [...fullHtml.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);
assert.equal(new Set(ids).size, ids.length, 'Study page fragment IDs are unique');
const citationPairs = [...fullHtml.matchAll(/<sup class="citation-sup" data-source-id="([^"]+)"[^>]*>[\s\S]*?class="citation-trigger"[^>]*>\[(\d+)\]<\/a>/g)]
  .map(match => ({id: match[1], n: Number(match[2])}));
assert(citationPairs.length > 15, 'Public summary and all detailed answers retain citations');
const citationOrder = [...new Set(citationPairs.map(pair => pair.id))];
for (const pair of citationPairs) assert.equal(pair.n, citationOrder.indexOf(pair.id) + 1, 'Citation number follows actual first appearance: ' + pair.id);
assert.deepEqual(citationOrder, [source.id, supporting[0].id, supporting[1].id], 'Cross-source first appearances follow the rendered detail order');

const states = [
  ['signed_out', 'Sign in for free access to the complete review.', true],
  ['intake_required', 'Complete your reader profile to access the complete review.', true],
  ['review_withdrawn', 'The review has been withdrawn.', false],
  ['content_unavailable', 'The complete review is temporarily unavailable.', false],
  ['review_incomplete', 'The complete appraisal is still being completed.', false],
  ['approval_missing', 'The complete appraisal has not yet been released.', false],
];
for (const [reason, expected, hasAction] of states) {
  const html = render(React.createElement(StudyPage, {source, access: {...previewAccess, reason}}));
  const status = html.match(/<section[^>]*id="review-status"[\s\S]*?<\/section>/)?.[0];
  assert(status && textOf(status).includes(expected), 'Visible access state: ' + reason);
  assert.equal(status.includes('<a '), hasAction, 'Only actionable access states offer an unlock action: ' + reason);
  assert(!html.includes('PRIVATE-ANSWER-'), 'No protected answer in ' + reason);
}
const unavailable = render(React.createElement(StudyPage, {source, access: {kind: 'unavailable', preview, message: 'fixture failure', review}}));
assert(textOf(unavailable).includes('Review availability could not be checked.'), 'Account/storage failure has an honest retry message');
assert(!unavailable.includes('PRIVATE-ANSWER-'), 'Unavailable state does not serialize protected answers');

const sparse = {...source, id: 'fixture-sparse-source', n: undefined, randomizedN: undefined, sampleDescription: undefined, population: undefined, design: undefined, intervention: undefined, comparator: undefined};
const sparseFacts = render(React.createElement(StudyFacts, {source: sparse}));
assert.equal(sparseFacts, '', 'Sparse source does not fabricate sample counts or study facts');
const missingUrl = {...sparse, url: '', doi: undefined, pmid: undefined};
const missingUrlHtml = render(React.createElement(StudyPage, {source: missingUrl, access: {kind: 'not_found'}}));

const metformin = content.guides.find(guide => guide.slug === '/drugs/metformin');
assert(metformin, 'Representative current parent article exists');
const feedHtml = render(React.createElement(Article, {guide: metformin, sources: content.sources.filter(item => metformin.sourceIds.includes(item.id))}));
const cardMarker = '<div class="research-feed__item study-summary-card" data-study-id="' + source.id + '">';
const cardStart = feedHtml.indexOf(cardMarker);
assert(cardStart >= 0, 'Current public study is included in the shared feed');
const nextCard = feedHtml.indexOf('<div class="research-feed__item study-summary-card"', cardStart + cardMarker.length);
const card = feedHtml.slice(cardStart, nextCard < 0 ? undefined : nextCard);
const header = card.match(/<summary class="research-feed__header-wrap">([\s\S]*?)<\/summary>/)?.[1];
assert(header && textOf(header).includes(source.title), 'Card header retains the exact study title');
assert(!header.includes('<a '), 'Card header toggles rather than linking away');
assert(card.includes('class="research-feed__toggle-icon"'), 'Card has its separate plus/minus control');
assert(card.includes('class="research-feed__excerpt"'), 'Closed card includes the finding excerpt');
const footer = card.match(/<div class="research-feed__footer">([\s\S]*?)<\/div><\/div>/)?.[1];
assert(footer, 'Card footer exists');
assert.equal((footer.match(/<a /g) || []).length, 3, 'Card footer contains Open, Link and Email');
assert(footer.includes('href="/research/' + source.id + '"') && footer.includes('>Open</a>'), 'Open targets the canonical study page');
assert(footer.includes('>Link</a>') && footer.includes('>Email</a>') && footer.includes('mailto:'), 'Original-paper and draft-email actions remain distinct');
for (const heading of STUDY_QUESTIONS) assert(card.includes('<h4>' + heading + '</h4>'), 'Expanded card contains opening: ' + heading);

let sweptStudyPages = 0, sweptBackgroundPages = 0;
for (const currentSource of content.sources) {
  const html = render(React.createElement(StudyPage, {source: currentSource, access: {kind: 'not_found'}}));
  const sourceIds = [...html.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);
  assert.equal(new Set(sourceIds).size, sourceIds.length, currentSource.id + ': every fragment ID is unique');
  const publicationTitle = html.match(/<p class="study-publication__title">([\s\S]*?)<\/p>/)?.[1];
  assert(publicationTitle, currentSource.id + ': exact publication title block exists');
  assert.equal(textOf(publicationTitle), currentSource.title.replace(/\s+/g, ' ').trim(), currentSource.id + ': publication title retained');
  for (const match of html.matchAll(/\shref="#([^"]*)"/g)) {
    const target = decodeURIComponent(match[1]);
    assert(sourceIds.includes(target), currentSource.id + ': local fragment resolves: #' + target);
  }
  assert(!html.includes('data-review-question=') && !html.includes('PRIVATE-ANSWER-'), currentSource.id + ': no protected answer payload');
  const isStudy = isPrimarySource(currentSource) || currentSource.sourceType === 'review';
  for (const heading of STUDY_QUESTIONS) {
    const present = html.includes('<h3>' + heading + '</h3>');
    assert.equal(present, isStudy, currentSource.id + ': research questions match source type');
  }
  if (isStudy) sweptStudyPages++; else sweptBackgroundPages++;
}
console.log(`PASS: all ${content.sources.length} current source pages render (${sweptStudyPages} research, ${sweptBackgroundPages} background), with unique IDs, exact publication titles, valid local fragments, and no protected answers.`);
assert(!missingUrlHtml.includes('Read the original paper'), 'Absent source URL does not produce an original-paper action');
assert(!missingUrlHtml.includes('href=""'), 'Absent source URL does not produce a self-navigation link');

console.log('PASS: study pages preserve public identity and four openings, render each authorized Q01–Q15 answer once with stable fragments/citations, expose honest access states, and omit invented sparse facts.');
console.log('PASS: current feed cards retain nonlinked expansion headers, finding excerpts, canonical Open/original Link/draft Email actions and four-question summaries.');
