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
  if (file.endsWith('.json')) return JSON.parse(fs.readFileSync(file, 'utf8'));
  const compiledModule = {exports: {}};
  cache.set(file, compiledModule);
  const compiled = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
    fileName: file.endsWith('.mjs') ? file.slice(0, -4) + '.js' : file,
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022,
      jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true},
  }).outputText;
  const localRequire = id => {
    if (!id.startsWith('.') && !id.startsWith('@/')) return require(id);
    const base = id.startsWith('@/') ? path.join(root, id.slice(2)) : path.resolve(path.dirname(file), id);
    const target = [base, base + '.ts', base + '.tsx', base + '.json']
      .find(candidate => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
    assert(target, 'Cannot resolve ' + id + ' from ' + file);
    return load(target);
  };
  new Function('require', 'module', 'exports', compiled)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const {content, synthesisRows} = load(path.join(root, 'lib/content.ts'));
const {evidenceMechanismsFor, evidenceMechanismSourceIds, mechanismEvidenceHref, mechanismCitationIds, drugMechanismFor} = load(path.join(root, 'lib/mechanisms.ts'));
const {articleEvidenceSources, guideCitationOrder} = load(path.join(root, 'lib/citation-plan.ts'));
const {MechanismSection} = load(path.join(root, 'components/shared-theme/mechanisms.tsx'));
const {outcomeSummariesFor} = load(path.join(root, 'lib/outcome-summary.ts'));
const metformin = content.guides.find(guide => guide.id === 'G-METFORMIN');
assert(metformin);

const covid = evidenceMechanismsFor('D01', 'C01');
assert.equal(covid.length, 1, 'One authored Long COVID rationale is shared by its outcomes');
assert.equal(covid[0].id, 'metformin-mechanism-1');
assert.match(covid[0].limits.text, /Prevention and treatment trials address different questions/);
assert.deepEqual(covid[0].rationale.sentences[0].sources, ['MF-COVID-VIRAL-2024']);
assert.deepEqual(evidenceMechanismsFor('D01', 'C02'), covid, 'The explicitly combined acute/Long COVID rationale is shared without rewriting its limits');
assert.deepEqual(evidenceMechanismsFor('D01', 'C19'), [], 'Metformin does not inherit itraconazole’s basal-cell mechanism');
assert.deepEqual(evidenceMechanismsFor('unknown', 'C01'), [], 'Condition overviews are never assigned to an unrelated drug');
assert.equal(evidenceMechanismsFor('D17', 'C10')[0].id, 'doxycycline-periodontal-background', 'Explicit context drug/condition keys support fallback');
assert.match(evidenceMechanismsFor('D17', 'C10')[0].locator, /Chapter 23/);
assert.deepEqual(evidenceMechanismsFor('D17', 'C01'), [], 'Shared textbook citations do not establish a condition relationship');

const covidRows = synthesisRows.filter(row => row.drugId === 'D01' && row.conditionId === 'C01');
assert.equal(evidenceMechanismSourceIds([...covidRows, ...covidRows]).length, 3, 'Companion outcomes do not duplicate mechanism sources');
const href = mechanismEvidenceHref(metformin, covid[0].id);
assert.match(href, /^#SYN-D01-C01-/);
assert.equal(mechanismEvidenceHref(metformin, 'metformin-myeloma-mechanism'), undefined, 'A mechanism without an evidence row remains in the article');

const original = drugMechanismFor(metformin);
const rows = original.rationales.map(row => ({...row, evidenceHref: mechanismEvidenceHref(metformin, row.id),
  rationale: row.rationale.text, tested: row.tested.text, limits: row.limits.text}));
const markup = renderToStaticMarkup(React.createElement(MechanismSection, {
  content: {heading: 'Mechanism of Action', detailLabels: {target: 'Target', action: 'Action', model: 'Model'}},
  rationalePlacement: 'evidence', originalAction: 'Original action stays here.', rationales: rows,
}));
assert(markup.includes('Original action stays here.'));
assert(!markup.includes(covid[0].rationale.text), 'Moved rationale is no longer duplicated in the main table');
assert(markup.includes('href="' + href + '"'), 'Legacy mechanism fragment links to the matching evidence row');
assert(markup.includes(rows.find(row => row.id === 'metformin-myeloma-mechanism').rationale), 'Unmatched preclinical rationale is preserved');
for (const row of rows) assert.equal(markup.split('id="' + row.id + '"').length - 1, 1, 'Each legacy mechanism anchor remains unique');
assert(mechanismCitationIds(metformin, 'evidence').includes(original.rationales.find(row => row.id === 'metformin-myeloma-mechanism').rationale.sourceIds[0]));

const condition = content.guides.find(guide => guide.id === 'G-LONGCOVID');
const baseline = condition.sourceIds.map(id => content.sources.find(source => source.id === id)).filter(Boolean);
const withMechanisms = articleEvidenceSources(condition, baseline);
for (const id of covid[0].sourceIds) assert(withMechanisms.some(source => source.id === id), 'Opposite guide resolves source ' + id);
assert.deepEqual(articleEvidenceSources(condition, withMechanisms), withMechanisms, 'Source augmentation is idempotent');
assert.equal(new Set(withMechanisms.map(source => source.id)).size, withMechanisms.length);

// A mechanism-only citation must not take a number ahead of later article prose.
// Use context-source fixtures so the Research Feed cannot reference it first.
const summaries = outcomeSummariesFor(covidRows);
assert(summaries.length, 'Canonical outcome summaries must be available');
const visible = new Set(summaries.flatMap(summary => summary.sourceIds));
const mechanismOnly = covid[0].sourceIds.find(id => !visible.has(id));
assert(mechanismOnly, 'Fixture has a separate mechanistic report');
const fixture = {...condition, id: 'fixture-citation-order', entityId: 'fixture-condition',
  synthesisIds: covidRows.map(row => row.id), sourceIds: ['last-visible'], sections: [], scopedSections: [],
  faqs: [{question: 'Visible final answer?', answer: 'Visible answer.', sources: ['last-visible']}]};
const fixtureSources = [...articleEvidenceSources(fixture, []), {id: 'last-visible', title: 'Final visible source', preview: '', url: '#'}]
  .map(source => ({...source, sourceType: 'context'}));
const order = guideCitationOrder(fixture, fixtureSources);
assert(order.indexOf(mechanismOnly) > order.indexOf('last-visible'), 'Drawer-only sources follow all visible body citations');
assert.deepEqual(guideCitationOrder(fixture, fixtureSources), order, 'Opening the same source registry does not renumber it');
console.log('PASS: exact mechanism scope, opposite-guide source closure, legacy anchors, retained preclinical rationale and deferred drawer citations.');
