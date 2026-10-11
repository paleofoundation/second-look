import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import ts from 'typescript';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';

// Execute the real TS/TSX modules without adding a test-runner dependency.
const root = path.resolve(import.meta.dirname, '..');
const require = createRequire(import.meta.url);
const cache = new Map();
const publicMechanisms = JSON.parse(fs.readFileSync(path.join(root, 'data/public-mechanisms.json'), 'utf8'));
const mechanismFixture = {
  contexts: [],
  drugs: [{drugId: 'fixture-drug', guideIds: ['fixture-answer'],
    originalAction: {text: 'Original action.', sourceIds: ['original']},
    summary: {text: 'Mechanism summary.', sourceIds: ['summary']},
    questions: [{id: 'mechanism-question', title: 'What is the proposed action?',
      text: 'A source-specific proposed action.', sourceIds: ['mechanism-question'],
      sentences: [{text: 'A source-specific proposed action.', sources: ['mechanism-question', 'original']}]}]}],
};
function load(file) {
  if (cache.has(file)) return cache.get(file).exports;
  if (file.endsWith('.css')) return {};
  if (file.endsWith('/data/public-mechanisms.json')) return {
    ...publicMechanisms, drugs: [...(publicMechanisms.drugs || []), ...mechanismFixture.drugs],
  };
  if (file.endsWith('.json')) return JSON.parse(fs.readFileSync(file, 'utf8'));
  const compiledModule = {exports: {}};
  cache.set(file, compiledModule);
  const source = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
    fileName: file,
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022,
      jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true},
  }).outputText;
  const localRequire = id => {
    if (!id.startsWith('.') && !id.startsWith('@/')) return require(id);
    const base = id.startsWith('@/') ? path.join(root, id.slice(2)) : path.resolve(path.dirname(file), id);
    const target = [base, base + '.ts', base + '.tsx', base + '.json', path.join(base, 'index.ts')]
      .find(candidate => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
    assert(target, 'Cannot resolve ' + id + ' from ' + file);
    return load(target);
  };
  new Function('require', 'module', 'exports', source)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const {Article} = load(path.join(root, 'components/article.tsx'));
const {ThemeProvider} = load(path.join(root, 'components/shared-theme/theme.tsx'));
const {guideCitationOrder} = load(path.join(root, 'lib/citation-plan.ts'));
const {drugMechanismFor} = load(path.join(root, 'lib/mechanisms.ts'));
const sourceIds = ['overview', 'original', 'summary', 'mechanism-question', 'benefits', 'benefit-question', 'faq'];
const sources = sourceIds.map(id => ({id, title: id + ' source', preview: 'Source finding.',
  url: 'https://example.org/' + id, sourceType: 'context', year: 2026}));
const guide = {id: 'fixture-guide', entityId: 'fixture-drug', slug: '/drugs/fixture', title: 'Fixture drug',
  description: 'Fixture description.', type: 'Drug', sourceIds: [...sourceIds].reverse(), topicIds: [], related: [],
  sections: [
    {id: 'overview', label: 'Overview', title: 'Overview findings', paragraph: 'Overview finding.', sources: ['overview']},
    {id: 'benefits', label: 'Benefits', title: '', paragraph: 'Benefits summary stays visible.', sources: ['benefits'],
      questions: [{id: 'benefit-question', question: 'Which outcome changed?', answer: 'The measured outcome.',
        sources: ['benefit-question'], sentences: [{text: 'The measured outcome.', sources: ['benefit-question', 'summary']}]}]},
  ],
  faqs: [{id: 'faq-one', question: 'What else was measured?', answer: 'Another reported outcome.', sources: ['faq']}],
};
const order = guideCitationOrder(guide, sources);
assert.deepEqual(order, sourceIds, 'New sources follow rendered prose and question order, not sourceIds order');
assert.equal(drugMechanismFor({...guide, id: 'fixture-answer', type: 'Drug–condition evidence answer', entityId: undefined})?.drugId, 'fixture-drug');
const config = {mainId: 'main', identity: {name: 'Fixture', homeHref: '/'}};
const render = (value, pageSources = sources) => renderToStaticMarkup(React.createElement(ThemeProvider, {config}, React.createElement(Article, {guide: value, sources: pageSources})));
const html = render(guide);
const article = html.match(/<article class="research-content__center entry-content">([\s\S]*?)<\/article>/)?.[1];
assert(article, 'The canonical article column renders');
const citations = [...article.matchAll(/<sup class="citation-sup" data-source-id="([^"]+)"[^>]*>[\s\S]*?\[(\d+)\]/g)];
assert.deepEqual([...new Set(citations.map(match => match[1]))], sourceIds, 'Rendered first appearances match the registry');
for (const match of citations) assert.equal(Number(match[2]), order.indexOf(match[1]) + 1);
for (const id of ['mechanism-question', 'benefit-question']) {
  assert(article.includes('class="rgbc-faq-item" id="' + id + '"'), 'Question uses canonical native details: ' + id);
  assert(article.includes('id="source-ref-' + (id === 'benefit-question' ? 'benefit-question' : 'mechanism-question') + '"'));
}
assert(article.indexOf('Benefits summary stays visible.') < article.indexOf('<details class="rgbc-faq-item" id="benefit-question"'));
assert(!article.includes('<h3></h3>'), 'Blank section titles do not create headings');
assert.equal((article.match(/id="faqs"/g) || []).length, 1, 'Section questions do not create another FAQ module');
for (const text of ['Laboratory activity, a proposed pathway', 'A mechanism describes how', 'not yet available in this article',
  'Independent review incomplete', 'Scientific review pending', 'Interaction coverage', 'unchecked in this corpus',
  'No completed scientific review date']) assert(!html.includes(text), 'Generic workflow copy is absent: ' + text);
const missing = render({...guide, id: 'unknown', entityId: 'unknown', sections: [], faqs: []});
assert(missing.includes('id="mechanisms"'), 'Canonical mechanism anchor remains without invented answers');
assert(!missing.includes('Original action.'), 'An unrelated guide does not inherit another drug’s mechanism');
assert(!missing.includes('not yet available') && !missing.includes('FAQ coverage is incomplete'));
console.log('PASS: actual article SSR, prose and canonical accordions, mechanism scope, first-appearance citations, blank and missing content, and workflow-copy regression checks.');

// Run the same checks against the actual public Metformin content, not a fixture.
const {content} = load(path.join(root, 'lib/content.ts'));
const metformin = content.guides.find(item => item.slug === '/drugs/metformin');
assert(metformin, 'The public Metformin profile exists');
const metforminSources = content.sources.filter(source => metformin.sourceIds.includes(source.id));
const metforminHtml = render(metformin, metforminSources);
const metforminArticle = metforminHtml.match(/<article class="research-content__center entry-content">([\s\S]*?)<\/article>/)?.[1];
assert(metforminArticle, 'The public Metformin article renders');
const textOf = html => html.replace(/<[^>]*>/g, '').replace(/&#x27;/g, "'").replace(/&quot;/g, '"')
  .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/\[\d+\]/g, '')
  .replace(/\s+/g, ' ').trim();
const mechanismHtml = metforminArticle.slice(metforminArticle.indexOf('<section id="mechanisms"'),
  metforminArticle.indexOf('id="section-benefits"'));
const benefitsHtml = metforminArticle.slice(metforminArticle.indexOf('id="section-benefits"'),
  metforminArticle.indexOf('id="section-safety"'));
const mechanism = drugMechanismFor(metformin);
assert(mechanism?.originalAction?.text, 'Metformin has a sourced original action');
assert(textOf(mechanismHtml).includes(mechanism.originalAction.sentences[0].text));
assert(textOf(mechanismHtml.slice(0, mechanismHtml.indexOf('<details'))).includes(mechanism.summary.text), 'Mechanism summary remains visible before the questions');
assert(mechanism.questions.length >= 10, 'Mechanism questions cover every investigated condition');
for (const question of mechanism.questions) {
  assert(mechanismHtml.includes('<details class="rgbc-faq-item" id="' + question.id + '"'));
  assert(textOf(mechanismHtml).includes(question.title));
  for (const sentence of question.sentences || []) assert(textOf(mechanismHtml).includes(sentence.text), question.id + ' answer sentence is visible in the disclosure');
}
const benefits = metformin.sections.filter(section => section.label === 'Benefits');
assert.equal(benefits.length, 1, 'Benefits has one prose summary');
assert(benefits[0].questions.length >= 12, 'Benefits covers the investigated conditions');
assert.equal((benefitsHtml.match(/class="rgbc-faq-item"/g) || []).length, benefits[0].questions.length);
assert.equal((benefitsHtml.match(/<h2>Benefits<\/h2>/g) || []).length, 1);
assert(!benefitsHtml.includes('<h3>'), 'Benefits has no duplicate summary heading');
for (const sentence of benefits[0].sentences || []) assert(textOf(benefitsHtml).includes(sentence.text));
assert(benefitsHtml.indexOf('<p>') < benefitsHtml.indexOf('<details'), 'The benefits summary is outside and before the accordions');
for (const question of benefits[0].questions) {
  assert(benefitsHtml.includes('<details class="rgbc-faq-item" id="' + question.id + '"'));
  assert(textOf(benefitsHtml).includes(question.question));
  for (const sentence of question.sentences || []) assert(textOf(benefitsHtml).includes(sentence.text), question.id + ' answer sentence is present');
}
const text = textOf(metforminArticle);
for (const finding of ['lactic acidosis', 'vitamin B12', 'eGFR below 30', 'cimetidine', 'retraction and republication']) {
  assert(text.includes(finding), 'Useful safety and source-integrity information remains: ' + finding);
}
for (const rejected of ['A mechanism describes how a drug affects', 'A source-backed explanation of the drug',
  'A reviewed, condition-specific mechanism summary', 'Laboratory activity, a proposed pathway',
  'How to read the evidence across conditions', 'Safety and clinical interpretation remain incomplete',
  'This page does not provide a completed safety assessment', 'absence of a completed assessment is not reassurance']) {
  assert(!text.includes(rejected), 'Rejected copy is absent from the actual Metformin article: ' + rejected);
}
const ids = [...metforminHtml.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);
assert.equal(ids.length, new Set(ids).size, 'All rendered IDs are unique');
for (const href of ['#section-safety', '#faqs', '#section-evidence', '#references', '#mechanisms']) {
  assert(metforminHtml.includes('href="' + href + '"'), 'Navigation/action fragment is present: ' + href);
  assert(ids.includes(href.slice(1)), 'Navigation/action fragment resolves: ' + href);
}
const actualOrder = guideCitationOrder(metformin, metforminSources);
const actualCitations = [...metforminArticle.matchAll(/<sup class="citation-sup" data-source-id="([^"]+)"[^>]*>[\s\S]*?\[(\d+)\]/g)];
const firstAppearances = [...new Set(actualCitations.map(match => match[1]))];
assert.deepEqual(actualOrder.slice(0, firstAppearances.length), firstAppearances, 'Metformin first appearances follow the actual DOM order');
for (const match of actualCitations) {
  assert.equal(Number(match[2]), actualOrder.indexOf(match[1]) + 1);
  assert(ids.includes('source-ref-' + encodeURIComponent(match[1])), 'Every Metformin citation has its bibliography target');
}
assert.equal(metforminSources.length, metformin.sourceIds.length, 'Every declared Metformin source resolves');
console.log('PASS: public Metformin SSR; condition-specific mechanisms; visible benefits summary and accordions; safety and correction facts; unique IDs; action fragments; ' + firstAppearances.length + ' sequential, source-resolved first-appearance citations.');

if (process.argv.includes('--all-profiles')) {
 const profiles=content.guides.filter(g=>g.type==='Drug'||g.type==='Condition');
 assert.equal(profiles.length,62,'All 31 drugs, 30 conditions and one aging goal are included');
 let totalQuestions=0;
 for(const profile of profiles){
  const label=profile.slug;
  const required=profile.type==='Drug'?['Overview','Benefits','Safety','Contraindications','Interactions','Dosing','Results','Quality','Status','Evidence','Connections']:['Overview','Options','Evidence','Safety','Comparisons','Connections'];
  for(const name of required)assert(profile.sections.some(s=>s.label===name&&s.paragraph.trim().length>25),label+': substantive '+name+' prose');
  const opening=profile.sections.find(s=>s.label===(profile.type==='Drug'?'Benefits':'Options'));
  assert(opening.questions?.length,label+': specific benefit/option questions');
  assert(profile.faqs.length,label+': additional reader FAQs');
  const mechanism=drugMechanismFor(profile);
  assert(mechanism?.summary?.text?.length>40,label+': explanatory mechanism summary');
  if(profile.type==='Drug')assert(mechanism.originalAction?.text?.length>30,label+': original pharmacological action');
  assert(mechanism.questions?.length,label+': mechanism questions');
  const pageSources=content.sources.filter(s=>profile.sourceIds.includes(s.id));
  assert.equal(pageSources.length,profile.sourceIds.length,label+': all sources resolve');
  const page=render(profile,pageSources);
  const center=page.match(/<article class="research-content__center entry-content">([\s\S]*?)<\/article>/)?.[1];
  assert(center,label+': article rendered');
  const visible=textOf(center);
  assert(!/not yet available|not yet reviewed|source-backed explanation.*not|assessment remains incomplete|accepted record|in this corpus|full review pending|How to read the evidence across conditions|Laboratory activity, a proposed pathway|Scientific review pending/i.test(visible),label+': production placeholders cannot replace answers');
  const pageIds=[...page.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(pageIds.length,new Set(pageIds).size,label+': unique DOM IDs');
  for(const match of page.matchAll(/href="#([^"]+)"/g))assert(pageIds.includes(match[1]),label+': fragment '+match[1]+' resolves');
  const order=guideCitationOrder(profile,pageSources);
  const citations=[...center.matchAll(/<sup class="citation-sup" data-source-id="([^"]+)"[^>]*>[\s\S]*?\[(\d+)\]/g)];
  const first=[...new Set(citations.map(m=>m[1]))];
  assert.deepEqual(order.slice(0,first.length),first,label+': citation first appearance');
  for(const c of citations){assert.equal(+c[2],order.indexOf(c[1])+1,label+': sequential citation');assert(pageIds.includes('source-ref-'+encodeURIComponent(c[1])),label+': citation target');}
  for(const section of profile.sections){
   if(section.sentences)assert.equal(section.sentences.map(s=>s.text.trim()).join(' '),section.paragraph.trim(),label+': section sentence map');
   for(const q of section.questions||[]){assert(center.includes('class="rgbc-faq-item" id="'+q.id+'"'),label+': canonical question '+q.id);assert(q.answer.length>30&&q.sources.length,label+': sourced question answer');assert(q.sources.every(id=>profile.sourceIds.includes(id)),label+': question source closure');totalQuestions++;}
  }
  for(const p of [mechanism.originalAction,mechanism.summary,...mechanism.questions].filter(Boolean))assert(p.sourceIds.length&&p.sourceIds.every(id=>profile.sourceIds.includes(id)),label+': mechanism source closure');
  totalQuestions+=mechanism.questions.length+profile.faqs.length;
 }
 console.log(JSON.stringify({status:'PASS',profiles:profiles.length,questions:totalQuestions,checks:'Every canonical content section populated; actual SSR; no production placeholders; unique IDs; all fragments; canonical questions; source closure; citation order'}));
}
