#!/usr/bin/env node
// Precomputes "Page created" dates for Update History from git history (never file mtimes).
// A page's date is the author date of the first commit in data/ that introduced its
// quoted slug (or, for /research/<id>, its quoted source id). Rerun: node scripts/build-page-created-dates.mjs
import {execFileSync} from 'node:child_process';
import {readFileSync, writeFileSync} from 'node:fs';
const updates = JSON.parse(readFileSync('data/article-updates.json', 'utf8')).entries;
const content = JSON.parse(readFileSync('data/public-content.json', 'utf8'));
const discovery = JSON.parse(readFileSync('data/discovery-pages.json', 'utf8'));
const pages = new Set([...updates.flatMap(entry => entry.pagePaths), ...content.guides.map(g => g.slug), ...discovery.map(g => g.slug)].filter(Boolean));
const dates = {}; const missing = [];
for (const page of [...pages].sort()) {
  const needle = page.startsWith('/research/') ? `"${page.slice('/research/'.length)}"` : `"${page}"`;
  const out = execFileSync('git', ['log', '-S' + needle, '--reverse', '--format=%as', '--', 'data'], {encoding: 'utf8'}).trim().split('\n')[0];
  if (/^\d{4}-\d{2}-\d{2}$/.test(out)) dates[page] = out; else missing.push(page);
}
writeFileSync('data/page-created-dates.json', JSON.stringify({source: 'git log -S first commit in data/ introducing the page slug or source id', dates}, null, 1) + '\n');
console.log(`dated ${Object.keys(dates).length}, missing ${missing.length}`); if (missing.length) console.log(missing.join('\n'));
