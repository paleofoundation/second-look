/** One private versioned source -> schema-validated web JSON + three reusable-renderer PDFs. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { pathToFileURL, fileURLToPath } from 'node:url';
import ts from 'typescript';
import { z } from 'zod';
const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(directory, '../..');
const require = createRequire(import.meta.url);
const schemaSource = fs.readFileSync(path.join(root, 'lib/guide-manuscript.ts'), 'utf8');
const schemaModule = { exports: {} };
new Function('require', 'module', 'exports', ts.transpileModule(schemaSource, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText)(require, schemaModule, schemaModule.exports);
const { guideManuscriptSchema } = schemaModule.exports;
const selection = z.object({ chapterId: z.string(), blockIndexes: z.array(z.number().int().nonnegative()).min(1) }).strict();
const sourceSchema = z.object({
  schemaVersion: z.literal('remaprx-guide-source-1'),
  slug: z.string().regex(/^[a-z0-9-]+$/),
  synthetic: z.boolean(),
  audience: z.string().min(1),
  manuscript: guideManuscriptSchema,
  previewSelections: z.array(selection).min(1),
  summarySelections: z.array(selection).min(1),
  sharedLimitSelections: z.array(selection).min(1),
}).strict();
const digest = value => crypto.createHash('sha256').update(value).digest('hex');
const serialized = value => JSON.stringify(value, null, 2) + '\n';
const escape = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');

function selected(source, selections) {
  const picks = new Map();
  for (const pick of selections) {
    const chapter = source.manuscript.chapters.find(item => item.id === pick.chapterId);
    if (!chapter || pick.blockIndexes.some(index => !chapter.blocks[index])) throw new Error('Selection does not resolve to a manuscript block.');
    if (new Set(pick.blockIndexes).size !== pick.blockIndexes.length) throw new Error('Duplicate selection index.');
    const indices = picks.get(pick.chapterId) ?? new Set();
    for (const index of pick.blockIndexes) indices.add(index);
    picks.set(pick.chapterId, indices);
  }
  return source.manuscript.chapters.flatMap(chapter => picks.has(chapter.id) ? [{ ...chapter, blocks: chapter.blocks.filter((_, index) => picks.get(chapter.id).has(index)) }] : []);
}
function scopedManuscript(source, selections) {
  const chapters = selected(source, selections);
  const references = new Set(chapters.flatMap(chapter => chapter.blocks.flatMap(block => block.sourceIds)));
  return guideManuscriptSchema.parse({ ...source.manuscript, chapters, references: source.manuscript.references.filter(reference => references.has(reference.id)) });
}
const blockPlainText = block => block.type === 'table' ? [block.caption, block.columns.join(' | '), ...block.rows.map(row => row.join(' | '))].join('\n') : block.type === 'list' || block.type === 'questions' ? [block.title, ...block.items].filter(Boolean).join('\n') : [block.title, block.text].filter(Boolean).join(': ');
function nativeManuscript(source, manuscript, variant) {
  const full = source.manuscript;
  const referenceIndex = new Map(full.references.map((reference, index) => [reference.id, { ...reference, label: String(index + 1) }]));
  const cited = block => block.sourceIds.map(id => { const ref = referenceIndex.get(id); return `<super><link href="${escape(ref.url)}">[${ref.label}]</link></super>`; }).join(' ');
  const blocks = block => {
    const cite = cited(block);
    if (block.type === 'paragraph') return [{ type: 'paragraph', text: escape(block.text) + (cite ? ' ' + cite : '') }];
    if (block.type === 'callout') return [{ type: 'entry', title: escape(block.title), blocks: [{ type: 'callout', text: escape(block.text) + (cite ? ' ' + cite : '') }] }];
    if (block.type === 'list') return [...block.items.map(item => ({ type: 'paragraph', text: '- ' + escape(item) })), ...(cite ? [{ type: 'source', text: cite }] : [])];
    if (block.type === 'questions') return [{ type: 'worksheet', title: escape(block.title), prompts: block.items }, ...(cite ? [{ type: 'source', text: cite }] : [])];
    return [{ type: 'heading', text: escape(block.caption) }, { type: 'table', headers: block.columns, rows: block.rows }, ...(cite ? [{ type: 'source', text: cite }] : [])];
  };
  const orientationId = 'remaprx-guide-orientation';
  const referenceId = 'remaprx-guide-references';
  if (full.chapters.some(chapter => [orientationId, referenceId].includes(chapter.id))) throw new Error('Reserved renderer chapter identifier.');
  const converted = (variant === 'summary' ? selected(source, source.summarySelections) : manuscript.chapters).map(chapter => ({ ...chapter, blocks: chapter.blocks.flatMap(blocks) }));
  const contents = [{ chapterId: orientationId, title: 'Orientation' }, ...converted.map(chapter => ({ chapterId: chapter.id, title: chapter.title })), { chapterId: referenceId, title: 'Sources, contributors and updates' }];
  const orientation = { id: orientationId, title: full.title, blocks: [
    { type: 'kicker', text: escape(`Edition ${full.version} | Evidence cutoff ${full.evidenceCutoff}`) },
    { type: 'paragraph', text: escape(full.description) },
    { type: 'notice', text: escape(full.medicalNotice) },
    { type: 'heading', text: 'In this ' + (variant === 'preview' ? 'sample' : 'guide') },
    { type: 'toc', items: contents },
  ] };
  const references = { id: referenceId, title: 'Sources, contributors and updates', blocks: [
    { type: 'bibliography' }, { type: 'heading', text: 'Contributors' }, { type: 'contributors' },
    { type: 'heading', text: 'What changed' }, { type: 'paragraph', text: escape(full.changeSummary) },
    { type: 'source', text: '<link href="https://remaprx.com/corrections">Suggest a correction</link> | <link href="https://remaprx.com/disclaimer">Educational-use policy</link>' },
  ] };
  const chapters = [orientation, ...converted, references];
  // Preview selection is independently scoped to exact blocks; its excluded
  // synthetic placeholder satisfies the upstream proper-subset invariant.
  const excluded = { id: 'remaprx-guide-private-excluded', title: 'Unselected private content', blocks: [] };
  const summaryBlocks = [...converted.flatMap(chapter => [{ type: 'heading', text: escape(chapter.title) }, ...chapter.blocks]), { type: 'bibliography' }];
  return {
    schemaVersion: 'consumer-guide-manuscript-1.0', productId: full.productId, slug: source.slug, title: full.title,
    audience: source.audience, scope: full.description,
    edition: { id: full.editionId, version: full.version, updated: full.updatedAt.slice(0, 10), evidenceCutoff: full.evidenceCutoff },
    notice: escape(full.medicalNotice),
    decisiveLimits: selected(source, source.sharedLimitSelections).flatMap(chapter => chapter.blocks.map(block => escape(blockPlainText(block)) + (cited(block) ? ' ' + cited(block) : ''))),
    release: { status: 'draft', humanEditorial: 'PENDING', qualifiedIndependent: 'PENDING', legal: 'PENDING', accessibility: 'HOLD', readerTest: 'PENDING', commercial: false, public: false },
    contributors: full.contributors.map(person => ({ name: person.name, role: person.role, status: [person.qualifications, 'Conflicts: ' + person.conflicts].filter(Boolean).join('. '), ...(person.orcid ? { orcid: person.orcid } : {}) })),
    sources: manuscript.references.map(reference => ({ ...reference, label: referenceIndex.get(reference.id).label, locator: reference.note ?? 'Linked source', role: source.synthetic ? 'Synthetic fixture reference; not medical evidence' : 'Source cited in this edition' })),
    chapters: variant === 'full' ? chapters : [...chapters, excluded], previewChapterIds: (variant === 'full' ? chapters.slice(0, -1) : chapters).map(chapter => chapter.id),
    summary: { title: full.title + ': printable summary', blocks: summaryBlocks },
    correctionRoute: 'https://remaprx.com/corrections', policyRoute: 'https://remaprx.com/disclaimer', synthetic: source.synthetic,
    provenance: { adapter: 'remaprx-guide-source-1', selectedVariant: variant, noReleaseApprovalCreated: true },
  };
}
export function prepareSource(input) {
  const source = sourceSchema.parse(input);
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$/.test(source.manuscript.version)) throw new Error('Edition version must be safe for an asset filename.');
  for (const group of [source.previewSelections, source.summarySelections, source.sharedLimitSelections]) selected(source, group);
  if (selected(source, source.sharedLimitSelections).some(chapter => chapter.blocks.some(block => !['paragraph', 'callout'].includes(block.type)))) throw new Error('Shared limits must be plain paragraphs or callouts, preserving their readable meaning in every format.');
  const limits = new Set(source.sharedLimitSelections.flatMap(pick => pick.blockIndexes.map(index => `${pick.chapterId}:${index}`)));
  if (source.summarySelections.some(pick => pick.blockIndexes.some(index => limits.has(`${pick.chapterId}:${index}`)))) throw new Error('Summary selections must not duplicate mandatory shared limits. They are included automatically.');
  const preview = scopedManuscript(source, [...source.previewSelections, ...source.sharedLimitSelections]);
  const summary = scopedManuscript(source, [...source.summarySelections, ...source.sharedLimitSelections]);
  const total = source.manuscript.chapters.reduce((count, chapter) => count + chapter.blocks.length, 0);
  if (preview.chapters.reduce((count, chapter) => count + chapter.blocks.length, 0) >= total) throw new Error('Preview must omit at least one full-guide block.');
  if (summary.chapters.reduce((count, chapter) => count + chapter.blocks.length, 0) >= total) throw new Error('Summary must omit at least one full-guide block.');
  // The native renderer adds decisive limits automatically to summary; omit
  // duplicated safety blocks from the explicitly selected summary body.
  return { source, web: source.manuscript, preview, summary, native: { full: nativeManuscript(source, source.manuscript, 'full'), preview: nativeManuscript(source, preview, 'preview'), summary: nativeManuscript(source, summary, 'summary') } };
}
export function buildGuide({ sourceFile, output, python = process.env.REMAPRX_PYTHON ?? 'python3' }) {
  const out = path.resolve(output);
  if (out === root || out.startsWith(root + path.sep)) throw new Error('Choose a private output directory outside the application checkout.');
  fs.mkdirSync(out, { recursive: true, mode: 0o700 });
  const actualOut = fs.realpathSync(out);
  // Paid manuscripts and generated files must never enter the deployment tree.
  if (actualOut === root || actualOut.startsWith(root + path.sep)) throw new Error('Choose a private output directory outside the application checkout.');
  const prepared = prepareSource(JSON.parse(fs.readFileSync(sourceFile, 'utf8')));
  const work = path.join(out, 'private-intermediate'); fs.mkdirSync(work, { recursive: true, mode: 0o700 });
  const write = (name, data, directory = out) => { fs.writeFileSync(path.join(directory, name), serialized(data), { mode: 0o600 }); };
  write('web-manuscript.json', prepared.web); write('sample-candidate.json', prepared.preview); write('summary-candidate.json', prepared.summary);
  for (const [variant, native] of Object.entries(prepared.native)) write(variant + '.native.json', native, work);
  const rendered = spawnSync(python, [path.join(directory, 'render-variants.py'), '--work', work, '--out', out], { encoding: 'utf8' });
  if (rendered.status !== 0) throw new Error('Reusable PDF renderer failed: ' + rendered.stderr);
  const pdf = JSON.parse(fs.readFileSync(path.join(out, 'pdf-manifest.json'), 'utf8'));
  for (const entry of Object.values(pdf.assets)) fs.chmodSync(path.join(out, entry.file), 0o600);
  const files = ['web-manuscript.json', 'sample-candidate.json', 'summary-candidate.json', ...Object.values(pdf.assets).map(asset => asset.file)];
  const manifest = { schemaVersion: 'remaprx-guide-build-1', productId: prepared.web.productId, editionId: prepared.web.editionId, version: prepared.web.version, evidenceCutoff: prepared.web.evidenceCutoff, updatedAt: prepared.web.updatedAt, synthetic: prepared.source.synthetic, releaseState: 'private_draft', sampleApproval: 'pending', sourceSha256: digest(fs.readFileSync(sourceFile)), adapterSha256: digest(fs.readFileSync(new URL(import.meta.url))), webSchemaSha256: digest(schemaSource), assets: Object.fromEntries(files.map(file => [file, { sha256: digest(fs.readFileSync(path.join(out, file))), bytes: fs.statSync(path.join(out, file)).size }])), pdf };
  write('build-manifest.json', manifest);
  return manifest;
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const args = Object.fromEntries(Array.from({ length: (process.argv.length - 2) / 2 }, (_, index) => [process.argv[2 + index * 2], process.argv[3 + index * 2]]));
  if (!args['--source'] || !args['--out']) throw new Error('Usage: node scripts/guide-renderer/build.mjs --source PRIVATE_SOURCE.json --out PRIVATE_DIRECTORY [--python PYTHON]');
  const result = buildGuide({ sourceFile: args['--source'], output: args['--out'], python: args['--python'] });
  console.log(JSON.stringify({ productId: result.productId, editionId: result.editionId, state: result.releaseState, assets: Object.keys(result.assets) }));
}
