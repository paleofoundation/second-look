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
  const compiledModule = {exports: {}};
  cache.set(file, compiledModule);
  const compiled = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
    fileName: file, compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022,
      jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true},
  }).outputText;
  new Function('require', 'module', 'exports', compiled)(id => {
    if (!id.startsWith('.') && !id.startsWith('@/')) return require(id);
    const base = id.startsWith('@/') ? path.join(root, id.slice(2)) : path.resolve(path.dirname(file), id);
    const target = [base, base + '.ts', base + '.tsx', base + '.json', path.join(base, 'index.ts')]
      .find(candidate => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
    assert(target, 'Cannot resolve ' + id);
    return load(target);
  }, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const {createWikiRegistry, wikiRegistry, wikiTokens, wikiTextRenderer} = load(path.join(root, 'lib/wiki-links.tsx'));
const {content, guideUrl} = load(path.join(root, 'lib/content.ts'));
const {relatedReadingFor} = load(path.join(root, 'lib/related-reading.ts'));
const {Article, CitedProse, ResearchCatalog} = load(path.join(root, 'components/article.tsx'));
const {ThemeProvider} = load(path.join(root, 'components/shared-theme/theme.tsx'));
const {EvidenceTable} = load(path.join(root, 'components/shared-theme/evidence-table.tsx'));
const {MechanismSection} = load(path.join(root, 'components/shared-theme/mechanisms.tsx'));
const html = (Component, props) => renderToStaticMarkup(React.createElement(Component, props));
const links = tokens => tokens.filter(token => token.href).map(token => token.href);
const fixture = createWikiRegistry([
  {title: 'Metformin', href: '/drugs/metformin'},
  {title: 'Type 2 diabetes', href: '/conditions/type-2-diabetes'},
  {title: 'Parkinson disease', href: '/conditions/parkinson-disease'},
  {title: 'Schizophrenia', href: '/conditions/schizophrenia'},
  {title: 'Sarcopenia', href: '/conditions/sarcopenia'},
  {title: 'Long COVID', href: '/conditions/long-covid'},
  {title: 'Sirolimus', href: '/drugs/sirolimus'},
  {title: 'Relative risk', href: '/glossary/relative-risk'},
  {title: 'Cholesterol transport', href: '/glossary/cholesterol-transport'},
  {title: 'Cholesterol transport inhibition', href: '/glossary/cholesterol-transport-inhibition'},
  {title: 'No external target', href: 'https://example.org'},
]);
const tokenize = (text, currentPath = '', seen = new Set()) => wikiTokens(text, currentPath, seen, fixture);
const example = 'Metformin is used for type 2 diabetes; research includes Parkinson’s disease, schizophrenia, sarcopenia and Long COVID.';
const targets = ['/conditions/type-2-diabetes', '/conditions/parkinson-disease', '/conditions/schizophrenia', '/conditions/sarcopenia', '/conditions/long-covid'];
assert.deepEqual(links(tokenize(example, '/drugs/metformin/')), targets, 'Every named condition links without a link-count cap');
assert.equal(tokenize(example).map(token => token.text).join(''), example, 'Text is preserved exactly');
assert.deepEqual(links(tokenize('Cholesterol transport inhibition affects cholesterol transport.')), ['/glossary/cholesterol-transport-inhibition', '/glossary/cholesterol-transport'], 'Longest overlapping term wins');
assert.deepEqual(links(tokenize('Rapamycin and sirolimus are the same medicine.')), ['/drugs/sirolimus'], 'Aliases dedupe by destination');
assert.deepEqual(links(tokenize('Rapamycin and sirolimus.', '/drugs/sirolimus?view=all#research')), [], 'Aliases do not self-link');
assert.deepEqual(links(tokenize('Premetformin metformins xmetformin αmetformin metforminβ.')), [], 'No word-substring links');
assert.deepEqual(links(tokenize('Metformin hydrochloride; metformin.')), ['/drugs/metformin'], 'Longest drug alias is a single link');
assert.equal(tokenize('Metformin hydrochloride')[0].text, 'Metformin hydrochloride');
for (const name of ["Parkinson's disease", 'Parkinson’s disease', 'Parkinson‘s disease', 'PARKINSON DISEASE']) {
  assert.deepEqual(links(tokenize(name)), ['/conditions/parkinson-disease'], 'Possessive/case alias: ' + name);
}
assert.deepEqual(links(tokenize('https://example.org/metformin?condition=schizophrenia www.example.org/metformin metformin@example.org [metformin](https://example.org) `metformin`')), [], 'URLs, emails, authored Markdown links and code remain untouched');
const seen = new Set();
assert.equal(links(tokenize('Metformin.', '', seen)).length, 1);
assert.equal(links(tokenize('Metformin again.', '', seen)).length, 0, 'Citation sentence boundaries preserve paragraph deduplication');
assert.equal(links(tokenize('Metformin.')).length, 1, 'A new paragraph can link the term again');
const ambiguous = createWikiRegistry([{title: 'Drug A', href: '/drugs/a', aliases: ['same']}, {title: 'Drug B', href: '/drugs/b', aliases: ['same']}]);
assert.deepEqual(links(wikiTokens('same', '', new Set(), ambiguous)), [], 'Conflicting aliases never silently choose a target');
assert.deepEqual(links(wikiTokens('ms als nsclc 50 ms')), [], 'Lowercase units and strings do not become acronym links');
assert.deepEqual(links(wikiTokens('MS ALS NSCLC')), ['/conditions/multiple-sclerosis', '/conditions/amyotrophic-lateral-sclerosis', '/conditions/non-small-cell-lung-cancer'], 'Uppercase condition acronyms link');
assert.deepEqual(links(wikiTokens('Ovarian cancer')), [], 'Broad ovarian cancer does not link to a narrower epithelial profile');
const routes = new Set([...content.guides.map(guideUrl), ...content.glossary.map(term => '/glossary/' + term.slug)]);
for (const href of wikiRegistry.aliases.values()) assert(routes.has(href), 'Link target exists: ' + href);

const source = {id: 'fixture-source', title: 'Metformin source title', preview: 'Metformin was compared with placebo.', year: 2026, sourceType: 'primary', url: 'https://example.org/metformin'};
const cited = html(CitedProse, {text: 'Metformin and Long COVID. Metformin again.', sourceIds: [source.id], sources: [source], order: [source.id], currentPath: '/conditions/schizophrenia'});
assert.equal((cited.match(/href="\/drugs\/metformin"/g) || []).length, 1);
assert(cited.includes('href="/conditions/long-covid"'));
assert.equal((cited.match(/class="citation-sup"/g) || []).length, 2, 'Inline links retain every citation');
assert(cited.includes('href="#source-ref-fixture-source"'), 'Citation destinations stay intact');

const config = {mainId: 'main', identity: {name: 'Fixture', homeHref: '/'}};
const renderArticle = guide => renderToStaticMarkup(React.createElement(ThemeProvider, {config},
  React.createElement(Article, {guide, sources: content.sources.filter(s => guide.sourceIds.includes(s.id))})));
const relatedUrls = guide => relatedReadingFor(guide).map(guideUrl);
const renderedRelatedUrls = (guide, rendered = renderArticle(guide)) => {
  const panels = [...rendered.matchAll(/<nav class="related-reading" aria-label="Related reading">([\s\S]*?)<\/nav>/g)];
  assert(panels.length <= 1, 'At most one related-reading navigation: ' + guideUrl(guide));
  return panels.flatMap(panel => [...panel[1].matchAll(/href="([^"]+)"/g)].map(match => match[1]));
};
const metformin = content.guides.find(guide => guide.slug === '/drugs/metformin');
assert(metformin, 'Metformin remains in the guide registry');
const metforminRelated = ['/conditions/parkinson-disease', '/conditions/schizophrenia', '/conditions/sarcopenia'];
assert.deepEqual(relatedUrls(metformin), metforminRelated, 'Metformin keeps authored broad-profile relationship priority');
assert.deepEqual(renderedRelatedUrls(metformin), metforminRelated, 'Sidebar renders Metformin relationships in authored order');
for (const guide of content.guides) {
  const selected = relatedUrls(guide);
  assert(selected.length <= 3, 'Related reading is capped at three: ' + guideUrl(guide));
  assert.equal(selected.length, new Set(selected).size, 'Related destinations are unique: ' + guideUrl(guide));
  for (const href of selected) {
    assert(routes.has(href), 'Related destination exists: ' + href);
    assert.notEqual(href, guideUrl(guide), 'Related reading excludes self: ' + href);
  }
  assert.deepEqual(renderedRelatedUrls(guide), selected, 'Rendered related links match the resolver: ' + guideUrl(guide));
}
for (const [condition, drug] of [
  ['/conditions/long-covid', '/drugs/guanfacine'],
  ['/conditions/epithelial-ovarian-or-fallopian-tube-carcinoma', '/drugs/fenbendazole'],
  ['/conditions/glioblastoma', '/drugs/memantine'],
]) {
  const guide = content.guides.find(candidate => guideUrl(candidate) === condition);
  assert(guide, 'Parent condition remains available: ' + condition);
  const section = guide.sections.find(candidate => candidate.label === 'Options');
  assert(section, 'Parent condition retains Options prose: ' + condition);
  const rendered = renderArticle(guide);
  const options = rendered.match(new RegExp('<section class="article-subsection" id="' + section.id + '">([\\s\\S]*?)<div class="rgbc-faq-block">'))?.[1];
  assert(options?.includes('href="' + drug + '" class="wiki-link"'),
    'Inline Options prose preserves drug access without a Connections section: ' + drug);
  const navigationSentence = section.sentences?.find(sentence => links(wikiTokens(sentence.text, condition)).includes(drug));
  assert(navigationSentence, 'Navigation sentence participates in the exact paragraph map: ' + drug);
  assert.deepEqual(navigationSentence.sources, [], 'Navigation-only text does not borrow an unrelated study citation: ' + drug);
}
const relatedFixture = {
  id: 'fixture-related-reading', entityId: 'fixture-entity', slug: '/fixtures/related-reading', title: 'Fixture', type: 'Drug',
  description: '', topicIds: [], sections: [], faqs: [], sourceIds: [], related: [],
};
const parkinson = content.guides.find(guide => guide.slug === '/conditions/parkinson-disease');
assert(parkinson);
const fallbackFixture = {...relatedFixture,
  related: ['missing-guide', metformin.id, metformin.id],
  description: 'Long COVID and Parkinson disease.',
  candidateLinks: [{id: 'missing', title: 'Missing', url: '/conditions/missing', state: ''}],
};
assert.deepEqual(relatedUrls(fallbackFixture), ['/drugs/metformin', '/conditions/long-covid', '/conditions/parkinson-disease'],
  'Invalid and duplicate curated IDs leave room for relevant canonical fallback');
const selfFixture = {...relatedFixture, id: metformin.id, slug: metformin.slug,
  related: [metformin.id, 'missing-guide', parkinson.id, parkinson.id],
};
assert.deepEqual(relatedUrls(selfFixture), ['/conditions/parkinson-disease'], 'Self and duplicate IDs do not consume sidebar slots');
assert.deepEqual(renderedRelatedUrls(selfFixture), ['/conditions/parkinson-disease'], 'Fewer than three relevant links render without filler');
const legacyOnly = {...relatedFixture,
  sections: [{id: 'old-connections', label: ' Connections ', title: 'Connections', paragraph: 'Metformin and Long COVID.', sources: []}],
  scopedSections: [{id: 'old-scoped-connections', label: 'connections', title: 'Connections', paragraph: 'Parkinson disease.', sources: []}],
};
assert.deepEqual(relatedUrls(legacyOnly), [], 'Removed Connections-only mentions cannot supply sidebar relevance');
assert.deepEqual(renderedRelatedUrls(relatedFixture), [], 'An unrelated page has no empty related-reading panel');
const autophagy = content.glossary.find(term => term.slug === 'autophagy');
assert(autophagy, 'Autophagy glossary page exists for backlink coverage');
const glossaryFixture = {...relatedFixture, id: 'term-autophagy', slug: '/glossary/autophagy', title: autophagy.title,
  type: 'Glossary', sections: [{id: 'meaning', label: 'Meaning', title: 'Meaning', paragraph: autophagy.meaning, sources: autophagy.sources}],
  sourceIds: autophagy.sources,
};
const glossaryRelated = relatedUrls(glossaryFixture);
assert.equal(glossaryRelated.length, 3, 'A widely used glossary term selects three contextual backlinks');
assert.equal(new Set(glossaryRelated).size, 3, 'Glossary backlinks are unique');
assert(!glossaryRelated.includes(glossaryFixture.slug), 'Glossary backlinks exclude self');
assert.deepEqual(renderedRelatedUrls(glossaryFixture), glossaryRelated, 'Glossary rendered backlinks share the three-link cap');
for (const slug of ['/drugs/metformin', '/conditions/long-covid']) {
  const guide = content.guides.find(g => g.slug === slug);
  assert(guide);
  const rendered = renderToStaticMarkup(React.createElement(ThemeProvider, {config},
    React.createElement(Article, {guide, sources: content.sources.filter(s => guide.sourceIds.includes(s.id))})));
  const overview = rendered.match(/data-universal-section="Overview">([\s\S]*?)<\/section><\/section>/)?.[1];
  assert(overview, 'Overview renders: ' + slug);
  assert(overview.includes('<h2>Overview</h2>'));
  assert(!overview.includes('<h3>'), 'No duplicate Overview question heading: ' + slug);
  assert(!overview.includes('href="' + slug + '"'), 'No self-links in Overview');
  if (slug === '/drugs/metformin') {
    for (const target of ['/conditions/parkinson-disease', '/conditions/schizophrenia', '/conditions/long-covid'])
      assert(overview.includes('href="' + target + '"'), 'Metformin Overview links ' + target);
  } else assert(rendered.includes('href="/drugs/metformin" class="wiki-link"'), 'Condition prose links back to drug');
  let depth = 0;
  for (const match of rendered.matchAll(/<\/?a(?=[\s>])[^>]*>/g)) {
    depth += match[0].startsWith('</') ? -1 : 1;
    assert(depth >= 0 && depth <= 1, 'No nested or unbalanced anchors');
  }
  assert.equal(depth, 0);
}
const catalogue = html(ResearchCatalog, {sources: [source]});
assert(catalogue.includes('href="/drugs/metformin"'), 'Source preview prose links entities');
assert(catalogue.includes('<a href="https://example.org/metformin" target="_blank" rel="noreferrer">Metformin source title</a>'), 'Source titles retain their original external link');
const table = html(EvidenceTable, {sources: [], cite: () => null, renderText: wikiTextRenderer('/conditions/schizophrenia'), rows: [{id: 'row', title: 'A result', use: 'Metformin in schizophrenia', population: 'Adults', comparison: 'Placebo', endpoint: 'Score', timepoint: 'Week 4', status: 'reported_result', finding: 'Metformin was studied. Metformin was compared with placebo.', findingSources: [], magnitude: 'Relative risk was reported.', certainty: {label: 'Low', rationale: 'Small study.'}, evidenceBase: 'One trial', limits: [], sourceIds: [], familyIds: [], background: false, pending: []}]});
assert(table.includes('href="/drugs/metformin"') && table.includes('href="/glossary/relative-risk"'), 'Evidence prose uses the shared linker');
assert(!table.includes('href="/conditions/schizophrenia"'), 'Evidence prose excludes the current condition');
const mechanism = html(MechanismSection, {content: {heading: 'Mechanism of Action', detailLabels: {target: 'Target', action: 'Action', model: 'Model'}}, renderText: wikiTextRenderer('/drugs/metformin'), contexts: [{id: 'context', title: 'Context', explanation: 'Finding', evidence: {basis: 'direct_measurement', label: 'Measured', source: null, model: 'Schizophrenia'}, clinicalMeaning: 'Long COVID is a separate question.'}]});
assert(mechanism.includes('href="/conditions/schizophrenia"') && mechanism.includes('href="/conditions/long-covid"'), 'Mechanism context fields and clinical interpretation link entities');

if (process.argv.includes('--require-new-content')) {
  for (const href of [...targets, '/drugs/fluconazole', '/drug-repurposing']) assert(routes.has(href), 'New canonical destination exists: ' + href);
  assert.deepEqual(links(wikiTokens(example, '/drugs/metformin')), targets, 'Actual registry links all five conditions in the requested example');
  const prose = 'Hedgehog pathway inhibition, cholesterol transport inhibition, apoptosis, autophagy, biofilm and hyphal states.';
  assert(links(wikiTokens(prose)).length >= 6, 'Expanded mechanism vocabulary links to glossary definitions');
  const textOnly = value => value.replace(/<[^>]*>/g, '').replace(/\[\d+\]/g, '')
    .replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/\s+/g, ' ').trim();
  const escapeRegex = value => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  for (const slug of ['/drug-repurposing', '/drugs/fluconazole', '/conditions/type-2-diabetes']) {
    const guide = content.guides.find(g => g.slug === slug);
    assert(guide, 'New article is in the canonical guide registry: ' + slug);
    const rendered = renderToStaticMarkup(React.createElement(ThemeProvider, {config},
      React.createElement(Article, {guide, sources: content.sources.filter(s => guide.sourceIds.includes(s.id))})));
    const center = rendered.match(/<article class="research-content__center entry-content">([\s\S]*?)<\/article>/)?.[1];
    assert(center, 'New article content renders: ' + slug);
    const ids = [...rendered.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);
    assert.equal(ids.length, new Set(ids).size, 'Unique rendered IDs: ' + slug);
    for (const match of rendered.matchAll(/href="#([^"]+)"/g))
      assert(ids.includes(match[1]), 'Fragment resolves on ' + slug + ': #' + match[1]);
    for (const match of rendered.matchAll(/href="([^"]+)" class="wiki-link"/g)) {
      assert(routes.has(match[1]), 'Wiki destination exists: ' + match[1]);
      assert.notEqual(match[1], slug, 'New article has no self-link: ' + slug);
    }
    if (slug === '/drug-repurposing') {
      for (const id of ['overview', 'rationale', 'mechanisms', 'evidence', 'status', 'safety', 'reading'])
        assert(guide.sections.some(section => section.id === id), 'Repurposing explainer retains section: ' + id);
      for (const section of guide.sections) {
        const sectionHtml = center.match(new RegExp('<section\\b[^>]*\\bid="' + escapeRegex(section.id) + '"[^>]*>([\\s\\S]*?)<\\/section>'))?.[1];
        assert(sectionHtml, 'Explainer section renders: ' + section.id);
        const heading = sectionHtml.match(/<h2>([\s\S]*?)<\/h2>/)?.[1];
        assert(heading && textOnly(heading).length > 0, 'Explainer section has a visible heading: ' + section.id);
        assert.equal(textOnly(heading), section.title, 'Explainer heading matches authored title: ' + section.id);
        const paragraph = sectionHtml.match(/<p>([\s\S]*?)<\/p>/)?.[1];
        assert(paragraph && textOnly(paragraph).length > 25, 'Explainer section has substantive visible prose: ' + section.id);
        assert.equal(textOnly(paragraph), section.paragraph.replace(/\s+/g, ' ').trim(), 'Explainer paragraph preserves its authored prose: ' + section.id);
      }
    } else {
      const overview = center.match(/data-universal-section="Overview">([\s\S]*?)<\/section><\/section>/)?.[1];
      assert(overview?.includes('<h2>Overview</h2>'), 'New profile has its canonical Overview heading: ' + slug);
      assert(!overview.includes('<h3>'), 'New profile has no duplicate Overview subheading: ' + slug);
      const paragraph = overview.match(/<p>([\s\S]*?)<\/p>/)?.[1];
      assert(paragraph && textOnly(paragraph).length > 25, 'New profile Overview contains visible prose: ' + slug);
      assert.equal(textOnly(paragraph), guide.sections.find(section => section.label === 'Overview').paragraph, 'New profile Overview preserves authored prose: ' + slug);
    }
  }
}
console.log('PASS: canonical wiki routes, aliases, longest whole-word matches, paragraph deduplication, self/URL protection, article SSR, reciprocal condition/drug links, Overview headings, source/citation integrity, evidence and mechanism prose; ordered related reading, canonical fallback, legacy Connections exclusion, and three-link sidebar/backlink cap.');
