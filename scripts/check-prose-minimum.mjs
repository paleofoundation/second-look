import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {createProseSSRLoader} from './prose-ssr-loader.mjs';

const root = path.resolve(import.meta.dirname, '..');
const load = createProseSSRLoader(root);
const {Article} = load(path.join(root, 'components/article.tsx'));
const {ThemeProvider} = load(path.join(root, 'components/shared-theme/theme.tsx'));
const {content, guideUrl} = load(path.join(root, 'lib/content.ts'));
const guides = content.guides.filter(guide => ['Drug', 'Condition'].includes(guide.type));
const pages = guides.map(guide => ({
  guideId: guide.id, slug: guideUrl(guide), type: guide.type,
  sections: guide.sections.filter(section => section.paragraph && section.label !== 'Connections')
    .map(section => ({id: section.id, label: section.label, required: false})),
  hasMechanismProse: true,
  html: renderToStaticMarkup(React.createElement(ThemeProvider,
    {config: {mainId: 'main', identity: {name: 'RemapRx', homeHref: '/'}}},
    React.createElement(Article, {guide, sources: guide.sourceIds.map(id => content.sources.find(source => source.id === id)).filter(Boolean)}))),
}));
for (const page of pages) {
  // Also catch visibly empty narrative modules, rather than silently passing a
  // page merely because the underlying authored paragraph is absent.
  const narrative = ['Overview', 'Options', 'Safety', 'Contraindications', 'Interactions', 'Dosing', 'Quality', 'Comparisons', 'Evidence'];
  const moduleTags = [...page.html.matchAll(/<section\b[^>]*\bid="([^"]+)"[^>]*\bdata-universal-section="([^"]+)"[^>]*>/g)];
  for (const [, id, label] of moduleTags) {
    if (narrative.includes(label) && !page.sections.some(section => section.label === label)) {
      page.sections.push({id, label, required: true});
    }
  }
}
const result = spawnSync('python3', [path.join(root, 'scripts/prose-minimum-html.py')], {
  input: JSON.stringify(pages), encoding: 'utf8', maxBuffer: 32 * 1024 * 1024,
});
if (result.status !== 0) throw new Error(result.stderr || 'Prose HTML audit failed');
const report = JSON.parse(result.stdout);
const outIndex = process.argv.indexOf('--report');
if (outIndex !== -1) fs.writeFileSync(path.resolve(root, process.argv[outIndex + 1]), JSON.stringify(report, null, 2) + '\n');
console.log(`${report.failures.length ? 'FAIL' : 'PASS'}: ${report.pageCount} pages, ${report.sectionCount} rendered prose sections; ${report.failures.length} below 113 words / 845 characters.`);
for (const failure of report.failures) console.log(`${failure.slug} #${failure.sectionId}: ${failure.words} words / ${failure.characters} characters`);
if (report.failures.length && !process.argv.includes('--inventory')) process.exitCode = 1;
