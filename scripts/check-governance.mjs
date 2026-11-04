import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, resolve, relative, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const json = path => JSON.parse(readFileSync(resolve(root, path), 'utf8'));
const required = [
  'AGENTS.md', 'README.md', 'CONTRIBUTING.md', 'docs/PROJECT-RULES.md',
  'docs/RULE-CHANGELOG.md', 'docs/RESEARCH-INGEST.md', 'docs/COLLABORATOR-HANDOFF.md',
  'references/README.md', 'research/README.md', 'research/INGEST-HANDOFF-TEMPLATE.md',
  'editorial/mechanism-expansion/ingestion-plan.json',
  'editorial/mechanism-expansion/mechanism-extraction-schema.json',
  'editorial/mechanism-expansion/review-question-input-map.json',
];
for (const path of required) if (!existsSync(resolve(root, path))) failures.push(`Missing ${path}`);

let verified = 0;
for (const path of [
  'rules/one-match-rule/snapshot-manifest.json',
  'docs/rule-history/import-manifest.json',
  'research/prior-pilot/import-manifest.json',
]) {
  const manifest = json(path);
  const base = resolve(root, dirname(path));
  const seen = new Set();
  if (!Array.isArray(manifest.files) || !manifest.files.length) failures.push(`Empty manifest: ${path}`);
  for (const entry of manifest.files ?? []) {
    const target = resolve(base, entry.path);
    const rel = relative(base, target);
    if (isAbsolute(entry.path) || rel.startsWith('..') || seen.has(entry.path)) {
      failures.push(`Unsafe or duplicate path in ${path}: ${entry.path}`);
      continue;
    }
    seen.add(entry.path);
    if (!existsSync(target)) { failures.push(`Missing snapshot file: ${rel}`); continue; }
    const bytes = readFileSync(target);
    if (hash(bytes) !== entry.sha256 || bytes.length !== entry.bytes) failures.push(`Changed snapshot: ${target}`);
    verified++;
  }
  if (path.startsWith('rules/')) {
    const master = readFileSync(resolve(base, 'ONE-MATCH-RULE.md'));
    if (hash(master) !== manifest.masterSha256) failures.push('Master hash disagrees with snapshot metadata');
    if (!master.toString().includes(`Version ${manifest.ruleVersion} `)) failures.push('Master version disagrees with snapshot metadata');
    const walk = dir => readdirSync(dir, { withFileTypes: true }).flatMap(item =>
      item.isDirectory() ? walk(resolve(dir, item.name)) : [relative(base, resolve(dir, item.name))]);
    for (const item of walk(base)) if (item !== 'snapshot-manifest.json' && !seen.has(item)) failures.push(`Unmanifested rule file: ${item}`);
  }
}

// This starting rule is an experiment baseline: it must never be refreshed in place.
const frozen = '01896e3c254f37483c226da52da0ef239b03eb7c762e5171675ae6dc302150d2';
if (hash(readFileSync(resolve(root, 'docs/one-match-rule-baseline.md'))) !== frozen) failures.push('Frozen v1.1 baseline changed');
if (json('docs/baseline-record.json').sha256 !== frozen) failures.push('Frozen baseline metadata changed');

for (const path of ['AGENTS.md', 'README.md', 'CONTRIBUTING.md']) {
  if (!readFileSync(resolve(root, path), 'utf8').includes('docs/RESEARCH-INGEST.md')) failures.push(`${path} must route researchers to ingestion instructions`);
}
// Citation gate (2026-11-04): new or changed guides must cite on-file, Crossref-valid, unretracted DOIs.
{
  const { spawnSync } = await import('node:child_process');
  const gate = spawnSync(process.execPath, [resolve(root, 'scripts/check-citation-gate.mjs')], { stdio: 'inherit', cwd: root });
  if (gate.status !== 0) failures.push('Citation gate failed (scripts/check-citation-gate.mjs)');
}
if (failures.length) {
  console.error(failures.join('\n'));
  process.exitCode = 1;
} else {
  console.log(`PASS: ${verified} preserved rule/history/ingest files, frozen baseline and collaborator entry points. This is repository integrity, not scientific acceptance.`);
}
