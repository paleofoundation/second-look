import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import ts from 'typescript';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';

const root = path.resolve(import.meta.dirname, '../../..');
process.chdir(root);
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const ledger = read(path.join(import.meta.dirname, 'source-mappings.json'));
const base = file => execFileSync('git', ['show', `${ledger.baseCommit}:${file}`], {encoding: 'utf8', maxBuffer: 64 * 1024 * 1024});
const accepted = ledger.candidates.filter(row => row.decision === 'wire_existing_source');
assert.equal(execFileSync('git', ['rev-parse', ledger.reviewedReference.preservedBranch], {encoding: 'utf8'}).trim(), ledger.reviewedReference.head);
const allowedFiles = new Set(['data/content.json', 'data/public-content.json', 'data/discovery-pages.json',
  'editorial/parent-guide-scopes.json', 'data/article-updates.json', 'docs/PROJECT-RULES.md', 'docs/RULE-CHANGELOG.md']);
for (const file of execFileSync('git', ['diff', '--name-only', ledger.baseCommit], {encoding: 'utf8'}).trim().split('\n').filter(Boolean)) {
  assert(allowedFiles.has(file) || file.startsWith('research/batches/FILL-REMAPRX-1-STEP1/'), `Unrelated live-source change: ${file}`);
}
for (const file of [...allowedFiles].filter(file => !file.startsWith('docs/'))) {
  assert.equal(fs.readFileSync(file, 'utf8'), execFileSync('git', ['show', `${ledger.reviewedReference.head}:${file}`],
    {encoding: 'utf8', maxBuffer: 64 * 1024 * 1024}), `Reviewed wiring data must be byte-identical: ${file}`);
}
assert.equal(accepted.length, 17);
assert.equal(ledger.candidates.length - accepted.length, 8);
const canonical = read('data/content.json');
for (const row of ledger.candidates) {
  const source = canonical.sources.find(source => source.id === row.sourceId);
  assert(source, `Existing source required: ${row.sourceId}`);
}
execFileSync('python3', ['-c', `import json,hashlib; from pathlib import Path
d=json.loads(Path('data/content.json').read_text());s={x['id']:x for x in d['sources']}
l=json.loads(Path('research/batches/FILL-REMAPRX-1-STEP1/source-mappings.json').read_text())
for r in l['candidates']:
 assert hashlib.sha256(json.dumps(s[r['sourceId']],sort_keys=True,ensure_ascii=False).encode()).hexdigest()==r['existingSourceSha256'],r['sourceId']
`]);

const guideRecords = (file, document) => file.includes('parent-guide-scopes') ? document.parents.map(parent => parent.guide)
  : Array.isArray(document) ? document : document.guides;
for (const file of ['data/content.json', 'data/public-content.json', 'data/discovery-pages.json', 'editorial/parent-guide-scopes.json']) {
  const before = JSON.parse(base(file));
  const expected = structuredClone(before);
  for (const guide of guideRecords(file, expected)) {
    const ids = accepted.filter(row => row.route === guide.slug).map(row => row.sourceId);
    guide.sourceIds = [...new Set([...guide.sourceIds, ...ids])];
  }
  assert.deepEqual(read(file), expected, `Only the explicit source associations may change: ${file}`);
}
for (const file of ['data/reader-evidence.json', 'data/public-reader-evidence.json', 'data/outcome-summaries.json',
  'data/outcome-registry.json', 'data/public-evidence-assessments.json', 'editorial/evidence-assessments.json',
  'data/private-reviews.json', 'data/review-envelopes.json', 'app/robots.ts', 'app/layout.tsx']) {
  assert.equal(fs.readFileSync(file, 'utf8'), base(file), `Preserve scientific/access/indexing state: ${file}`);
}
const priorHistory = JSON.parse(base('data/article-updates.json'));
assert.deepEqual(read('data/article-updates.json'), {...priorHistory, entries: [...ledger.historyEvents, ...priorHistory.entries]});
assert.equal(ledger.historyEvents.length, 7);
assert(ledger.historyEvents.every(event => event.date === '2026-10-26' && event.changeType === 'presentation'
  && event.summary.includes('review status are unchanged')));
assert.equal(fs.readFileSync('app/robots.ts', 'utf8').includes("disallow:'/'"), true);
assert.match(fs.readFileSync('app/layout.tsx', 'utf8'), /index: false, follow: false/);

// Load the real article and adapters, as in the repository's SSR checks.
const require = createRequire(import.meta.url), cache = new Map();
function load(file) {
  if (cache.has(file)) return cache.get(file).exports;
  if (file.endsWith('.css')) return {};
  if (file.endsWith('.json')) return read(file);
  const module = {exports: {}};
  cache.set(file, module);
  const compiled = ts.transpileModule(fs.readFileSync(file, 'utf8'), {fileName: file,
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true}}).outputText;
  const localRequire = id => {
    if (!id.startsWith('.') && !id.startsWith('@/')) return require(id);
    const resolved = id.startsWith('@/') ? path.join(root, id.slice(2)) : path.resolve(path.dirname(file), id);
    const target = [resolved, resolved + '.ts', resolved + '.tsx', resolved + '.json', path.join(resolved, 'index.ts')]
      .find(candidate => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
    assert(target, `Cannot resolve ${id}`);
    return load(target);
  };
  new Function('require', 'module', 'exports', compiled)(localRequire, module, module.exports);
  return module.exports;
}
const {Article} = load(path.join(root, 'components/article.tsx'));
const {ThemeProvider} = load(path.join(root, 'components/shared-theme/theme.tsx'));
const {content, isPrimarySource} = load(path.join(root, 'lib/content.ts'));
const renderResults = [];
for (const route of [...new Set(ledger.candidates.map(row => row.route))]) {
  const guide = content.guides.find(guide => guide.slug === route);
  assert(guide, `Destination exists: ${route}`);
  const sources = guide.sourceIds.map(id => content.sources.find(source => source.id === id));
  assert(sources.every(Boolean));
  const html = renderToStaticMarkup(React.createElement(ThemeProvider, {config: {mainId: 'main', identity: {name: 'RemapRx', homeHref: '/'}}},
    React.createElement(Article, {guide, sources})));
  for (const row of accepted.filter(row => row.route === route)) {
    assert(html.includes(`id="source-ref-${row.sourceId}"`), `${route}: reference missing ${row.sourceId}`);
    const source = sources.find(source => source.id === row.sourceId);
    if (isPrimarySource(source)) assert(html.includes(`id="study-${row.sourceId}"`), `${route}: feed missing ${row.sourceId}`);
    else assert(!html.includes(`id="study-${row.sourceId}"`), `${route}: context must not become a primary study`);
    assert(html.includes(source.url.replaceAll('&', '&amp;')), `${route}: original source link missing`);
  }
  assert.equal((html.match(/id="research-feed"/g) || []).length, 1, 'One canonical feed');
  renderResults.push({route, addedSourceAssociations: accepted.filter(row => row.route === route).length,
    retainedSynthesisRows: guide.synthesisIds.length});
}
// Repeating the bounded operation cannot duplicate citations or change bytes.
const tracked = execFileSync('git', ['diff', '--binary'], {encoding: 'utf8'});
execFileSync('python3', ['research/batches/FILL-REMAPRX-1-STEP1/apply.py']);
assert.equal(execFileSync('git', ['diff', '--binary'], {encoding: 'utf8'}), tracked);
console.log(JSON.stringify({status: 'PASS', candidates: 25, wired: 17, rejected: 8, renderResults,
  sourceRecordsChanged: 0, outcomeRowsChanged: 0, scientificOrReleaseStatesChanged: 0, repeatChanges: 0}, null, 2));
