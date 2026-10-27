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
const {guideCitationOrder, hasArticleEvidence, articleEvidenceSources} = load(path.join(root, 'lib/citation-plan.ts'));
const {outcomeSummaries, outcomeSummariesFor, evidenceForSummaries} = load(path.join(root, 'lib/outcome-summary.ts'));

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
const proseWithoutCitations = node => hasClass(node, 'citation-sup') ? '' : node.tag === '#text' ? node.text : (node.children || []).map(proseWithoutCitations).join('');
const normalizedText = node => decode(proseWithoutCitations(node)).replace(/\s+/g, ' ').trim();
const proseText = text => text.replace(/\s+/g, ' ').trim();
const ancestor = (node, predicate) => { for (let parent = node.parent; parent; parent = parent.parent) if (predicate(parent)) return parent; return null; };
const flowTags = new Set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'details', 'figure', 'table', 'form', 'button', 'a']);
const flow = node => (node.children || []).flatMap(child => flowTags.has(child.tag) && textOf(child) ? [child] : flow(child));

const visibleGrade = node => textOf(all(node, child => hasClass(child, 'evidence-grade-trigger'))[0]);
const columnHeaders = table => all(table, node => node.tag === 'th' && ancestor(node, parent => parent.tag === 'thead'));
const expectedHeaders = type => [type === 'Condition' ? 'Intervention' : 'Health condition', 'Outcome', 'Grade', 'Effect', 'Evidence'];
const cellsOf = row => row.children.filter(node => node.tag === 'td' || node.tag === 'th');
const summaryViews = new Map();
// Accepted current layout: these drug pages have generic-only Quality copy.
// Keep this explicit so accidentally hiding a substantive Quality section fails.
const genericQualityRoutes = new Set(['fluvoxamine', 'ivermectin', 'mebendazole', 'maraviroc', 'atorvastatin', 'rituximab', 'celecoxib', 'vorinostat', 'clomipramine', 'thalidomide', 'fluconazole'].map(slug => '/drugs/' + slug));
const drugStatusRows = JSON.parse(fs.readFileSync(path.join(root, 'data/drug-status-table.json'), 'utf8')).drugs;

function assertEvidenceCount(node, summaries, label, {participants = true} = {}) {
  // Compute the expected count independently from the displayed aggregate.
  // One family can occur in several outcomes and in several source reports.
  const trials = [...new Map(summaries.flatMap(summary => summary.evidence.trials).map(trial => [trial.id, trial])).values()];
  const controls = all(node, child => hasClass(child, 'evidence-count-link'));
  assert.equal(controls.length, 1, label + ': one evidence control');
  assert.equal(textOf(controls[0]), `${trials.length} ${trials.length === 1 ? 'RCT' : 'RCTs'}`, label + ': independent randomized trial count');
  if (participants) {
    const complete = trials.length > 0 && trials.every(trial => trial.participants !== null);
    const total = complete ? trials.reduce((sum, trial) => sum + trial.participants, 0).toLocaleString('en-US') : 'Not totaled';
    assert.equal(textOf(all(node, child => hasClass(child, 'evidence-participants'))[0]), 'Participants: ' + total,
      label + ': participants counted once per known trial family, with explicit unavailable totals');
  }
  if (!trials.length) assert(textOf(node).includes('View other evidence'), label + ': zero RCTs does not hide other evidence');
}

function inspect(guide, pageSources, {expectScoped = false} = {}) {
  const label = guideUrl(guide);
  const inputBefore = JSON.stringify(guide);
  const html = render(guide, pageSources);
  pageSources = articleEvidenceSources(guide, pageSources);
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
  assert.deepEqual(columnHeaders(table).map(textOf), expectedHeaders(guide.type), label + ': five-column outcome summary hierarchy');
  assert(columnHeaders(table).every(node => node.attrs.scope === 'col'), label + ': semantic column headers');
  for (const header of columnHeaders(table)) {
    const help = all(header, node => node.tag === 'button' && hasClass(node, 'evidence-header-help'));
    assert.equal(help.length, 1, label + ': one explanatory header control for ' + textOf(header));
    assert.equal(decode(help[0].attrs['aria-label']), 'About ' + textOf(header), label + ': labeled header explanation');
  }

  const authoredSections = guide.sections.filter(section => section.label.trim().toLowerCase() === 'evidence');
  if (expectScoped) authoredSections.push(...(guide.scopedSections || []).filter(section => section.label.trim().toLowerCase() !== 'connections'));
  for (const section of authoredSections) {
    if (!section.paragraph?.trim()) continue;
    const sectionNode = all(evidence, node => node.attrs?.id === section.id)[0];
    assert(sectionNode, label + ': authored Evidence/scoped anchor retained: ' + section.id);
    assert(sectionNode.start < table.start, label + ': authored/scoped prose precedes table: ' + section.id);
    assert(normalizedText(sectionNode).includes(proseText(section.paragraph)), label + ': existing scientific prose preserved: ' + section.id);
  }

  const rawRows = (guide.synthesisIds || []).map(id => synthesisRows.find(row => row.id === id)).filter(Boolean);
  const summaries = outcomeSummariesFor(rawRows).toSorted((a, b) => a.label.localeCompare(b.label));
  for (const row of rawRows) assert(summaries.some(summary => summary.synthesisIds.includes(row.id)), label + ': original synthesis remains represented: ' + row.id);
  const expectedGroups = [...Map.groupBy(summaries, summary => guide.type === 'Condition' ? summary.drugId : summary.conditionId)];
  const expectedRows = expectedGroups.flatMap(([, items]) => items);
  const body = all(table, node => node.tag === 'tbody')[0];
  const renderedRows = (body?.children || []).filter(node => node.tag === 'tr');
  if (expectedRows.length) {
    const groupRows = renderedRows.filter(row => hasClass(row, 'evidence-group-row'));
    const outcomeRows = renderedRows.filter(row => row.attrs['data-outcome-summary']);
    assert.equal(renderedRows.length, expectedRows.length + expectedGroups.length, label + ': exactly one group header and one row per outcome summary');
    assert.deepEqual(groupRows.map(row => row.attrs['data-group-id']), expectedGroups.map(([id]) => id), label + ': each condition/intervention occurs once in group order');
    assert.deepEqual(outcomeRows.map(row => row.attrs['data-outcome-summary']), expectedRows.map(row => row.id), label + ': summaries match canonical identity and grouped default order');
    assert.deepEqual(outcomeRows.map(row => row.attrs.id), expectedRows.map(row => row.synthesisIds[0]), label + ': first raw synthesis remains the row fragment');
    const expectedSequence = expectedGroups.flatMap(([id, items]) => ['group:' + id, ...items.map(item => item.id)]);
    assert.deepEqual(renderedRows.map(row => row.attrs['data-outcome-summary'] || 'group:' + row.attrs['data-group-id']), expectedSequence,
      label + ': outcomes remain directly below their own group');
    for (let index = 0; index < expectedGroups.length; index++) {
      const [id, items] = expectedGroups[index];
      const rendered = groupRows[index];
      const peer = content.guides.find(candidate => candidate.entityId === id);
      const groupTitle = peer?.title || id;
      assert.equal(cellsOf(rendered).length, 5, label + ': group spans the five actual columns');
      const heading = cellsOf(rendered)[0];
      assert.equal(heading.tag, 'th', label + ': group uses a semantic row header');
      assert.equal(heading.attrs.scope, 'rowgroup', label + ': group header is distinct from column headers');
      assert.equal(textOf(heading), groupTitle, label + ': condition/intervention label is human-readable');
      if (peer) assert(all(heading, node => node.tag === 'a' && node.attrs.href === guideUrl(peer)).length,
        label + ': group links to the canonical opposite profile');
      const toggles = all(rendered, node => node.tag === 'button' && hasClass(node, 'evidence-group-toggle'));
      assert.equal(toggles.length, 1, label + ': group has one collapse control');
      assert.equal(toggles[0].attrs['aria-expanded'], 'true', label + ': groups are initially expanded');
      assert.equal(decode(toggles[0].attrs['aria-label']), 'Collapse ' + groupTitle + ' outcomes', label + ': collapse control names its group');
      assert.equal(textOf(cellsOf(rendered)[1]), `${items.length} ${items.length === 1 ? 'outcome' : 'outcomes'}`, label + ': group counts summary outcomes');
      assertEvidenceCount(rendered, items, label + ': group ' + id, {participants: false});
      const groupOpeners = all(rendered, node => node.tag === 'button' && node.attrs['aria-haspopup'] === 'dialog');
      assert.equal(groupOpeners.length, 1, label + ': group has one evidence drawer control');
      assert(decode(groupOpeners[0].attrs['aria-label']).includes(groupTitle), label + ': group drawer names its scope');
    }
    for (let index = 0; index < expectedRows.length; index++) {
      const row = expectedRows[index];
      const rendered = outcomeRows[index];
      assert.equal((rendered.children || []).filter(node => node.tag === 'td').length, 5, label + ': five cells for ' + row.id);
      assert(!Object.hasOwn(rendered.attrs, 'hidden'), label + ': initial outcome rows are visible');
      for (const id of row.synthesisIds) assert.equal(all(article, node => node.attrs?.id === id).length, 1,
        label + ': original synthesis fragment exists exactly once: ' + id);
      const controls = all(rendered, node => node.tag === 'button' && node.attrs['aria-haspopup'] === 'dialog');
      assert.equal(controls.length, 3, label + ': outcome, grade and evidence count open the same drawer for ' + row.id);
      assert(controls.some(control => hasClass(control, 'evidence-grade-trigger')), label + ': grade rationale opener');
      assert.equal(visibleGrade(rendered), row.grade.value || '—', label + ': rendered benefit grade matches the separate A–F assessment');
      if (!row.grade.value) assert(textOf(rendered).includes(row.grade.label), label + ': ungraded evidence explains why it has no letter');
      assert(controls.every(control => decode(control.attrs['aria-label'] || '').includes(row.label)), label + ': all three openers identify the same outcome ' + row.id);
      assert(controls.some(control => hasClass(control, 'research-outcome-trigger')), label + ': outcome drawer trigger');
      assert(controls.some(control => hasClass(control, 'evidence-count-link')), label + ': trial-count drawer trigger');
      assert(all(rendered, node => node.tag === 'svg' && hasClass(node, 'lucide-file-text')).length, label + ': evidence count retains document icon');
      assert.equal(textOf(all(rendered, node => hasClass(node, 'evidence-effect-label'))[0]), row.effect.label, label + ': displayed effect matches summary');
      assert.equal(textOf(all(rendered, node => hasClass(node, 'evidence-effect-detail'))[0]), row.effect.detail, label + ': quantitative effect remains visible');
      assertEvidenceCount(rendered, [row], label + ': ' + row.id);
      const rowCitations = all(rendered, node => node.tag === 'sup' && hasClass(node, 'citation-sup'));
      assert.deepEqual(rowCitations.map(citation => citation.attrs['data-source-id']).toSorted(), [...new Set(row.sourceIds)].toSorted(),
        label + ': effect cites the complete merged summary source set exactly once');
      const snapshot = cellsOf(rendered).slice(1).map(normalizedText);
      const views = summaryViews.get(row.id) || [];
      views.push({route: label, type: guide.type, snapshot});
      summaryViews.set(row.id, views);
    }
  } else {
    assert.equal(renderedRows.length, 1, label + ': one honest empty-state row');
    const cells = (renderedRows[0].children || []).filter(node => node.tag === 'td');
    assert.equal(cells.length, 1, label + ': empty state uses one cell');
    assert.equal(cells[0].attrs.colspan, '5', label + ': empty state spans the actual columns');
    assert(/no .*findings|no .*outcomes|no .*evidence/i.test(textOf(cells[0])), label + ': empty state does not invent a finding');
    assert.equal(all(body, node => node.tag === 'button' && node.attrs['aria-haspopup'] === 'dialog').length, 0, label + ': no pretend source opener without evidence');
  }

  // The inline catalogue is retained separately; a table button does not point
  // away to it or replace it with another maintained catalogue.
  assert.equal(all(article, node => node.attrs?.id === 'studies').length, 1, label + ': one canonical inline Studies catalogue');
  assert.equal(all(article, node => node.attrs?.id === 'references').length, 1, label + ': one canonical References catalogue');
  const order = guideCitationOrder(guide, pageSources);
  const citations = all(article, node => node.tag === 'sup' && hasClass(node, 'citation-sup'));
  const first = [...new Set(citations.map(node => node.attrs['data-source-id']))];
  assert.deepEqual(order.slice(0, first.length), first, label + ': actual prose/scoped/effect/table first appearances agree with citation plan');
  for (const citation of citations) assert.equal(textOf(citation), '[' + (order.indexOf(citation.attrs['data-source-id']) + 1) + ']', label + ': stable citation display number');
  for (const section of guide.sections.filter(section => section.label.trim().toLowerCase() !== 'connections')) {
    if (!section.paragraph?.trim()) continue;
    const sectionNode = all(article, node => node.attrs?.id === section.id)[0];
    if (guide.type === 'Drug' && section.label === 'Results') {
      assert(!sectionNode, label + ': redundant Results prose is retired in favor of Evidence');
      continue;
    }
    if (guide.type === 'Drug' && section.label === 'Quality' && genericQualityRoutes.has(guide.slug)) {
      assert(!sectionNode, label + ': generic-only Quality prose stays omitted');
      assert(!all(article, node => node.attrs?.id === 'section-quality').length, label + ': omitted Quality has no empty module');
      continue;
    }
    const statusRows = guide.type === 'Drug' && drugStatusRows[guide.slug];
    if (section.label === 'Status' && statusRows?.length) {
      assert(sectionNode, label + ': Status prose retains its legacy anchor');
      const table = all(article, node => node.tag === 'table' && hasClass(node, 'status-table'))[0];
      assert(table, label + ': Status uses the regulatory table');
      assert.deepEqual(columnHeaders(table).map(textOf), ['Use / indication', 'Regulator', 'Status', 'Year approved', 'Source']);
      const rows = all(table, node => node.tag === 'tr' && ancestor(node, parent => parent.tag === 'tbody'));
      assert.equal(rows.length, statusRows.length, label + ': every regulatory record rendered');
      rows.forEach((row, index) => {
        const record = statusRows[index];
        assert.deepEqual(cellsOf(row).slice(0, 4).map(textOf), [record.use, record.regulator, record.status, String(record.year ?? '—')]);
        assert.deepEqual(all(row, node => node.tag === 'sup').map(node => node.attrs['data-source-id']).sort(), [...record.sourceIds].sort(), label + ': Status source citations');
      });
      continue;
    }
    assert(sectionNode && normalizedText(sectionNode).includes(proseText(section.paragraph)), label + ': existing visible article explanation preserved: ' + section.id);
    if (guide.type === 'Drug' && section.label === 'Benefits') {
      assert(ancestor(sectionNode, node => node.attrs?.['data-universal-section'] === 'Overview'), label + ': Benefits summary belongs to Overview');
      assert(!all(article, node => node.attrs?.id === 'section-benefits').length, label + ': no standalone Benefits module');
    }
  }
  assert.equal(JSON.stringify(guide), inputBefore, label + ': renderer never mutates canonical guide data');
  return {route: label, rows: expectedRows.length, groups: expectedGroups.length, citations: citations.length};
}

const profiles = content.guides.filter(guide => guide.type === 'Drug' || guide.type === 'Condition');
assert(profiles.length && profiles.some(guide => guide.type === 'Drug') && profiles.some(guide => guide.type === 'Condition'));
const additional = content.guides.filter(guide => !profiles.includes(guide) && hasArticleEvidence(guide));
const results = [...profiles, ...additional].map(guide => inspect(guide, content.sources.filter(source => guide.sourceIds.includes(source.id))));

// These are two views of the same authored assessment, not separately authored
// grades or counts. Compare rendered cells after removing page-specific citation
// numbers; their source identities were checked independently above.
let pairedSummaries = 0;
for (const summary of outcomeSummaries) {
  const views = summaryViews.get(summary.id) || [];
  const drug = views.find(view => view.type === 'Drug');
  const condition = views.find(view => view.type === 'Condition');
  assert(drug, summary.id + ': summary is visible from its drug profile');
  assert(condition, summary.id + ': summary is visible from its condition profile');
  assert.deepEqual(drug.snapshot, condition.snapshot, summary.id + ': drug and condition show the same outcome, grade, effect and RCT evidence');
  for (const view of views) assert.deepEqual(view.snapshot, drug.snapshot, summary.id + ': answer/comparison views preserve the same assessment at ' + view.route);
  pairedSummaries++;
}
assert(pairedSummaries > 0, 'Production data supplies paired drug/condition summaries');
assert(outcomeSummaries.some(summary => summary.synthesisIds.length > 1), 'Compatible original findings are actually merged into outcome summaries');

const trialA = {id: 'fixture-trial-a', sourceIds: ['fixture-report-a'], participants: 30, participantBasis: 'Thirty randomized participants.'};
const trialB = {id: 'fixture-trial-b', sourceIds: ['fixture-report-b'], participants: 20, participantBasis: 'Twenty randomized participants.'};
const withTrials = trials => ({evidence: {
  trials, sourceIds: trials.flatMap(trial => trial.sourceIds), rctCount: trials.length,
  trialFamilyIds: trials.map(trial => trial.id), participantBasis: 'Synthetic trial populations.',
  participants: trials.length && trials.every(trial => trial.participants !== null) ? trials.reduce((sum, trial) => sum + trial.participants, 0) : null,
}});
const overlap = evidenceForSummaries([withTrials([trialA, trialB]), withTrials([trialA])]);
assert.equal(overlap.rctCount, 2, 'Repeated outcomes from a trial do not create extra RCTs');
assert.equal(overlap.participants, 50, 'Repeated outcomes do not duplicate participants');
assert.deepEqual(overlap.trialFamilyIds.toSorted(), ['fixture-trial-a', 'fixture-trial-b'], 'Group aggregate retains independent trial identities');
assert.deepEqual(overlap.sourceIds.toSorted(), ['fixture-report-a', 'fixture-report-b'], 'Group aggregate retains the union of report identities');
assert.equal(evidenceForSummaries([withTrials([trialA]), withTrials([{...trialB, participants: null}])]).participants, null,
  'An unknown trial denominator cannot become a deceptively complete participant total');
assert.equal(evidenceForSummaries([]).participants, null, 'Absence of randomized evidence is not a zero-participant clinical result');

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
assert.deepEqual(columnHeaders(filteredTable).map(textOf), expectedHeaders('Drug'));
assert(all(filteredFinder, node => node.attrs?.role === 'status').some(node => textOf(node).startsWith('0 of 1 recorded outcomes.')),
  'Filtered-empty state reports zero matches, not zero total coverage');
assert(textOf(filteredTable).includes('No recorded outcome matches these filters.'), 'Filter mismatch has a distinct truthful table message');
console.log(JSON.stringify({status: 'PASS', profiles: profiles.length, additionalEvidenceGuides: additional.length,
  populatedTables: results.filter(result => result.rows).length, emptyTables: results.filter(result => !result.rows).length,
  rows: results.reduce((sum, result) => sum + result.rows, 0), groups: results.reduce((sum, result) => sum + result.groups, 0),
  pairedSummaries, mergedSummaries: outcomeSummaries.filter(summary => summary.synthesisIds.length > 1).length,
  syntheticScopedFixtures: 2, filteredEmptyFixture: 'PASS', trialOverlapFixtures: 'PASS',
  checks: 'Actual Article SSR; prose-first Evidence; authored and scoped text before final five-column table; unique condition/intervention groups; shared outcome identity and A–F assessment in both directions; effect source closure; independent trial/participant counts; labeled openers and initially expanded groups; legacy synthesis aliases; preserved narrative; stable citations; one inline catalogue; repeat generation',
  limits: 'SSR checks do not establish drawer findings/magnitude content, interaction, focus, scroll, visual parity or deployment. Verify those in the browser. This is not whole G4R or scientific-completeness acceptance.'}));
