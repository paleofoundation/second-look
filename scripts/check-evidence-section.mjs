import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import ts from 'typescript';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {load, render} from './check-reader-sections.mjs';

const root = path.resolve(import.meta.dirname, '..');
const {content, synthesisRows, guideUrl} = load(path.join(root, 'lib/content.ts'));
const {guideCitationOrder, hasArticleEvidence} = load(path.join(root, 'lib/citation-plan.ts'));
const {studyDesignsFor} = load(path.join(root, 'lib/evidence-presentation.ts'));

// A small structural reader for the controlled React SSR output. It follows
// balanced tags rather than treating a nested </section> as the Evidence end.
const voidTags = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr']);
function parse(html) {
  const document = {tag: '#document', attrs: {}, children: [], start: 0, end: html.length};
  const stack = [document];
  for (const token of html.matchAll(/<!--[\s\S]*?-->|<![^>]*>|<\/?[a-zA-Z][^>]*>|[^<]+/g)) {
    const value = token[0];
    if (value.startsWith('<!')) continue;
    if (value.startsWith('</')) {
      const tag = value.match(/^<\/([^\s>]+)/)[1].toLowerCase();
      const index = stack.findLastIndex(node => node.tag === tag);
      assert(index > 0, 'Unexpected closing SSR tag: ' + tag);
      for (const node of stack.splice(index)) node.end = token.index + value.length;
      continue;
    }
    const parent = stack.at(-1);
    if (!value.startsWith('<')) {
      parent.children.push({tag: '#text', text: value, start: token.index, end: token.index + value.length, parent});
      continue;
    }
    const tag = value.match(/^<([^\s/>]+)/)[1].toLowerCase();
    const attrs = Object.fromEntries([...value.matchAll(/\s([^\s=/>]+)(?:="([^"]*)")?/g)].map(match => [match[1].toLowerCase(), match[2] ?? '']));
    const node = {tag, attrs, children: [], start: token.index, end: token.index + value.length, parent};
    parent.children.push(node);
    if (!voidTags.has(tag) && !value.endsWith('/>')) stack.push(node);
  }
  assert.equal(stack.length, 1, 'SSR markup closes every non-void element');
  return document;
}
const descendants = node => (node.children || []).flatMap(child => [child, ...descendants(child)]);
const all = (node, predicate) => descendants(node).filter(predicate);
const hasClass = (node, name) => (node.attrs?.class || '').split(/\s+/).includes(name);
const decode = text => text.replace(/&#x([\da-f]+);/gi, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
  .replace(/&#(\d+);/g, (_, number) => String.fromCodePoint(Number(number)))
  .replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
const rawText = node => node.tag === '#text' ? node.text : (node.children || []).map(rawText).join('');
const textOf = node => decode(rawText(node)).replace(/\s+/g, ' ').trim();
const normalizedText = node => textOf(node).replace(/\[\d+\]/g, '').replace(/\s+/g, ' ').trim();
const proseText = text => text.replace(/\s+/g, ' ').trim();
const ancestor = (node, predicate) => { for (let parent = node.parent; parent; parent = parent.parent) if (predicate(parent)) return parent; return null; };
const flowTags = new Set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'details', 'figure', 'table', 'form', 'button', 'a']);
const flow = node => (node.children || []).flatMap(child => flowTags.has(child.tag) && textOf(child) ? [child] : flow(child));

const visibleGrade = node => textOf(all(node, child => hasClass(child, 'evidence-grade-trigger'))[0]);

function inspect(guide, pageSources, {expectScoped = false} = {}) {
  const label = guideUrl(guide);
  const inputBefore = JSON.stringify(guide);
  const html = render(guide, pageSources);
  const document = parse(html);
  const article = all(document, node => node.tag === 'article' && hasClass(node, 'research-content__center'))[0];
  assert(article, label + ': actual Article center rendered');
  const evidenceSections = all(article, node => node.attrs?.id === 'section-evidence');
  assert.equal(evidenceSections.length, 1, label + ': one canonical Evidence section');
  const evidence = evidenceSections[0];
  const readingFlow = flow(evidence);
  assert.equal(readingFlow[0]?.tag, 'h2', label + ': Evidence starts with its canonical heading');
  assert.equal(textOf(readingFlow[0]), 'Evidence', label + ': canonical Evidence heading text');
  assert.equal(readingFlow[1]?.tag, 'p', label + ': prose immediately follows the heading (no repeated subheading, table or filter first)');
  assert(normalizedText(readingFlow[1]).length > 25, label + ': opening Evidence prose is substantive');

  const tables = all(evidence, node => node.tag === 'table');
  assert.equal(tables.length, 1, label + ': exactly one Evidence table, including empty coverage');
  const table = tables[0];
  const finalBlock = readingFlow.at(-1);
  assert(finalBlock === table || (finalBlock?.tag === 'figure' && descendants(finalBlock).includes(table)), label + ': table is the final Evidence content');
  assert.equal(all(article, node => node.tag === 'table' && ancestor(node, parent => hasClass(parent, 'evidence-table'))).length, 1,
    label + ': no duplicated early evidence table');
  assert.deepEqual(all(table, node => node.tag === 'th').map(textOf), ['Outcome and study design', 'Grade', 'Evidence'], label + ': PepsAnon three-column hierarchy');
  assert(all(table, node => node.tag === 'th').every(node => node.attrs.scope === 'col'), label + ': semantic column headers');

  const authoredSections = guide.sections.filter(section => section.label.trim().toLowerCase() === 'evidence');
  if (expectScoped) authoredSections.push(...(guide.scopedSections || []).filter(section => section.label.trim().toLowerCase() !== 'connections'));
  for (const section of authoredSections) {
    if (!section.paragraph?.trim()) continue;
    const sectionNode = all(evidence, node => node.attrs?.id === section.id)[0];
    assert(sectionNode, label + ': authored Evidence/scoped anchor retained: ' + section.id);
    assert(sectionNode.start < table.start, label + ': authored/scoped prose precedes table: ' + section.id);
    assert(normalizedText(sectionNode).includes(proseText(section.paragraph)), label + ': existing scientific prose preserved: ' + section.id);
  }

  const expectedRows = (guide.synthesisIds || []).map(id => synthesisRows.find(row => row.id === id)).filter(Boolean)
    .sort((a, b) => a.title.localeCompare(b.title));
  const body = all(table, node => node.tag === 'tbody')[0];
  const renderedRows = (body?.children || []).filter(node => node.tag === 'tr');
  if (expectedRows.length) {
    assert.deepEqual(renderedRows.map(row => row.attrs.id), expectedRows.map(row => row.id), label + ': rows match canonical identity and default order');
    for (let index = 0; index < expectedRows.length; index++) {
      const row = expectedRows[index];
      const rendered = renderedRows[index];
      assert.equal((rendered.children || []).filter(node => node.tag === 'td').length, 3, label + ': three cells for ' + row.id);
      const controls = all(rendered, node => node.tag === 'button' && node.attrs['aria-haspopup'] === 'dialog');
      assert.equal(controls.length, 3, label + ': outcome, grade and evidence count open the same drawer for ' + row.id);
      assert(controls.some(control => hasClass(control, 'evidence-grade-trigger')), label + ': grade rationale opener');
      assert(visibleGrade(rendered) === row.certainty.label, label + ': rendered grade matches canonical assessment');
      assert(controls.every(control => decode(control.attrs['aria-label'] || '').includes(row.title)), label + ': both openers identify the same outcome ' + row.id);
      assert(controls.some(control => hasClass(control, 'research-outcome-trigger')), label + ': outcome drawer trigger');
      assert(controls.some(control => hasClass(control, 'evidence-count-link')), label + ': document-count drawer trigger');
      assert(all(rendered, node => node.tag === 'svg' && hasClass(node, 'lucide-file-text')).length, label + ': evidence count retains document icon');
      const visible = normalizedText(rendered);
      const designs = studyDesignsFor(row, pageSources);
      for (const design of designs) assert(visible.includes(proseText(design.text)), label + ': cited source-backed design is visible for ' + row.id);
      const designSourceIds = new Set(designs.flatMap(design => design.sourceIds));
      const rowCitations = all(rendered, node => node.tag === 'sup' && hasClass(node, 'citation-sup'));
      assert(rowCitations.every(citation => designSourceIds.has(citation.attrs['data-source-id'])), label + ': compact design citations use that outcome\'s sources');
    }
  } else {
    assert.equal(renderedRows.length, 1, label + ': one honest empty-state row');
    const cells = (renderedRows[0].children || []).filter(node => node.tag === 'td');
    assert.equal(cells.length, 1, label + ': empty state uses one cell');
    assert.equal(cells[0].attrs.colspan, '3', label + ': empty state spans the actual columns');
    assert(/no .*findings|no .*outcomes|no .*evidence/i.test(textOf(cells[0])), label + ': empty state does not invent a finding');
    assert.equal(all(table, node => node.tag === 'button' && node.attrs['aria-haspopup'] === 'dialog').length, 0, label + ': no pretend source opener without evidence');
  }

  // The inline catalogue is retained separately; a table button does not point
  // away to it or replace it with another maintained catalogue.
  assert.equal(all(article, node => node.attrs?.id === 'studies').length, 1, label + ': one canonical inline Studies catalogue');
  assert.equal(all(article, node => node.attrs?.id === 'references').length, 1, label + ': one canonical References catalogue');
  const order = guideCitationOrder(guide, pageSources);
  const citations = all(article, node => node.tag === 'sup' && hasClass(node, 'citation-sup'));
  const first = [...new Set(citations.map(node => node.attrs['data-source-id']))];
  assert.deepEqual(order.slice(0, first.length), first, label + ': actual prose/scoped/design/table first appearances agree with citation plan');
  for (const citation of citations) assert.equal(textOf(citation), '[' + (order.indexOf(citation.attrs['data-source-id']) + 1) + ']', label + ': stable citation display number');
  for (const section of guide.sections.filter(section => section.label.trim().toLowerCase() !== 'connections')) {
    if (!section.paragraph?.trim()) continue;
    const sectionNode = all(article, node => node.attrs?.id === section.id)[0];
    assert(sectionNode && normalizedText(sectionNode).includes(proseText(section.paragraph)), label + ': existing visible article explanation preserved: ' + section.id);
  }
  assert.equal(JSON.stringify(guide), inputBefore, label + ': renderer never mutates canonical guide data');
  return {route: label, rows: expectedRows.length, citations: citations.length};
}

const profiles = content.guides.filter(guide => guide.type === 'Drug' || guide.type === 'Condition');
assert(profiles.length && profiles.some(guide => guide.type === 'Drug') && profiles.some(guide => guide.type === 'Condition'));
const additional = content.guides.filter(guide => !profiles.includes(guide) && hasArticleEvidence(guide));
const results = [...profiles, ...additional].map(guide => inspect(guide, content.sources.filter(source => guide.sourceIds.includes(source.id))));

// A configuration-only second topic tests the same shared renderer. It adds no
// source data to the site and makes the scoped-only citation precede the table.
const base = profiles.find(guide => guide.synthesisIds?.length);
const row = synthesisRows.find(row => row.id === base.synthesisIds[0]);
const fixtureSources = ['fixture-opening', 'fixture-evidence', 'fixture-scoped'].map(id => ({id, title: id, url: 'https://example.org/' + id,
  preview: 'Synthetic implementation fixture.', sourceType: 'context'}));
for (const type of ['Drug', 'Condition']) {
  const fixture = {...base, id: 'fixture-' + type.toLowerCase(), entityId: 'fixture-entity', type,
    title: 'Synthetic topic', slug: '/fixture/' + type.toLowerCase(), synthesisIds: [row.id], faqs: [], related: [],
    sections: [
      {id: 'fixture-overview', label: 'Overview', title: 'Overview', paragraph: 'This synthetic topic exercises the shared article renderer.', sources: ['fixture-opening']},
      {id: 'fixture-evidence-intro', label: 'Evidence', title: 'Legacy authored Evidence title', paragraph: 'This existing evidence explanation must appear before the table.', sources: ['fixture-evidence']},
    ],
    scopedSections: [{id: 'fixture-scoped-detail', label: 'Details', title: 'Scoped research detail', paragraph: 'This source supports a scoped explanation that must precede the table.', sources: ['fixture-scoped']}],
    sourceIds: [...row.sourceIds, ...fixtureSources.map(source => source.id)].reverse(),
  };
  const pageSources = [...content.sources.filter(source => row.sourceIds.includes(source.id)), ...fixtureSources];
  inspect(fixture, pageSources, {expectScoped: true});
  const order = guideCitationOrder(fixture, pageSources);
  assert.deepEqual(order.slice(0, 3), fixtureSources.map(source => source.id), type + ': scoped prose citations precede any table-only source');
  assert.equal(render(fixture, pageSources), render(fixture, pageSources), type + ': repeat generation preserves the same composition');
}

// Exercise the actual filter renderer with a browser query snapshot. Only the
// external-store snapshot is supplied by this fixture; the React component and
// empty EvidenceTable are the production implementations, with no DOM edits.
const require = createRequire(import.meta.url);
const finderPath = path.join(root, 'components/shared-theme/outcome-finder.tsx');
const finderModule = {exports: {}};
const querySnapshot = '?outcome_q=unmatched-fixture-term';
const finderCode = ts.transpileModule(fs.readFileSync(finderPath, 'utf8'), {
  fileName: finderPath,
  compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022,
    jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true},
}).outputText;
new Function('require', 'module', 'exports', finderCode)(id => id === 'react'
  ? {...React, useSyncExternalStore: () => querySnapshot} : require(id), finderModule, finderModule.exports);
const {EvidenceTable} = load(path.join(root, 'components/shared-theme/evidence-table.tsx'));
const filteredSelections = [];
const filteredHtml = renderToStaticMarkup(React.createElement(finderModule.exports.OutcomeFinder, {
  compact: true,
  records: [{id: 'fixture-outcome', title: 'Fixture outcome', definition: 'A synthetic renderer fixture.', aliases: [],
    entity: {id: 'fixture-entity', label: 'Fixture entity'}, condition: {id: 'fixture-condition', label: 'Fixture condition'},
    population: 'Fixture population', design: 'Fixture design', assessment: 'Not appraised', timepoint: '', comparator: '',
    endpointRole: null, clinicalMeaning: null}],
  renderRows: ids => {
    filteredSelections.push(ids);
    return React.createElement(EvidenceTable, {rows: [], sources: [], cite: () => null,
      emptyMessage: 'No recorded outcome matches these filters.'});
  },
}));
assert.deepEqual(filteredSelections, [[]], 'Zero filter matches still call the canonical table renderer with an empty selection');
const filteredDocument = parse(filteredHtml);
const filteredFinder = all(filteredDocument, node => hasClass(node, 'outcome-finder'))[0];
const filteredTable = all(filteredFinder, node => node.tag === 'table')[0];
const filterReset = all(filteredFinder, node => node.tag === 'button' && textOf(node) === 'Show all recorded outcomes')[0];
assert(filteredTable && filterReset && filterReset.start < filteredTable.start, 'The no-match reset control precedes the final table');
assert.equal(flow(filteredFinder).at(-1)?.tag, 'figure', 'A zero-match filtered Evidence section still ends in its table');
assert.deepEqual(all(filteredTable, node => node.tag === 'th').map(textOf), ['Outcome and study design', 'Grade', 'Evidence']);
assert(all(filteredFinder, node => node.attrs?.role === 'status').some(node => textOf(node).startsWith('0 of 1 recorded outcomes.')),
  'Filtered-empty state reports zero matches, not zero total coverage');
assert(textOf(filteredTable).includes('No recorded outcome matches these filters.'), 'Filter mismatch has a distinct truthful table message');
console.log(JSON.stringify({status: 'PASS', profiles: profiles.length, additionalEvidenceGuides: additional.length,
  populatedTables: results.filter(result => result.rows).length, emptyTables: results.filter(result => !result.rows).length,
  rows: results.reduce((sum, result) => sum + result.rows, 0), syntheticScopedFixtures: 2, filteredEmptyFixture: 'PASS',
  checks: 'Actual Article SSR; prose-first Evidence; authored and scoped text before final three-column table; canonical rows, cited study designs and both labelled openers; preserved narrative; stable citations; one inline catalogue; repeat generation',
  limits: 'SSR checks do not establish drawer findings/magnitude content, interaction, focus, scroll, visual parity or deployment. Verify those in the browser. This is not whole G4R or scientific-completeness acceptance.'}));
