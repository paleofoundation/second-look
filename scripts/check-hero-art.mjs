import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import sharp from 'sharp';
import {load, render} from './check-reader-sections.mjs';

const {content, guideUrl} = load(path.resolve('lib/content.ts'));
const {getTopicHeroArt} = load(path.resolve('lib/hero-art.ts'));
const definitions = JSON.parse(await readFile('data/topic-hero-art.json', 'utf8'));
const manifest = JSON.parse(await readFile('assets/hero-art/manifest.json', 'utf8'));
const topics = content.guides.filter(page => /^\/(drugs|conditions)\//.test(guideUrl(page)));
// Every current drug, condition and glossary entry requires an explicit illustration.
const glossary = content.glossary.map(term => ({
  id: 'term-' + term.slug, slug: '/glossary/' + term.slug, title: term.title, type: 'Glossary',
  description: 'A scientific term, with its context intact.', topicIds: [],
  sections: [
    {id: 'meaning', label: 'Meaning', title: 'Meaning', paragraph: term.meaning, sources: term.sources, sentences: term.sentenceMaps?.meaning},
    {id: 'context', label: 'Context', title: 'Why the distinction matters', paragraph: term.context, sources: term.sources, sentences: term.sentenceMaps?.context},
    {id: 'examples', label: 'Examples', title: 'Read it in context', paragraph: term.examples, sources: term.sources, sentences: term.sentenceMaps?.examples},
  ],
  faqs: [], sourceIds: term.sources, related: [],
}));
const knownPages = new Map([...topics, ...glossary].map(page => [guideUrl(page), page]));
const assignedPaths = new Set(definitions.map(item => item.canonicalPath));
assert.equal(assignedPaths.size, definitions.length, 'Each canonical path has at most one image mapping');
for (const page of [...topics, ...glossary]) assert(assignedPaths.has(guideUrl(page)), guideUrl(page) + ': required topic/glossary artwork');
for (const item of definitions) assert(knownPages.has(item.canonicalPath), item.canonicalPath + ': known drug, condition or glossary page');
assert.equal(new Set(definitions.map(item => item.subject)).size, definitions.length, 'Every illustrated page has an individual asset');
assert.deepEqual(manifest.items.map(item => item.subject).sort(), definitions.map(item => item.subject).sort(), 'The manifest contains exactly the assigned illustrations');
const masterHashes = new Set();
for (const definition of definitions) {
  const canonicalPath = definition.canonicalPath;
  const page = knownPages.get(canonicalPath);
  const art = getTopicHeroArt(canonicalPath);
  assert(art && art.alt && art.title && art.caption && art.description && art.socialImage.alt, canonicalPath + ': complete descriptive fields');
  const subject = canonicalPath.split('/').at(-1);
  assert.equal(definition.subject, subject, canonicalPath + ': canonical asset name');
  assert.equal(art.src, `/art/${subject}-blue-hero.webp`);
  assert.equal(art.socialImage.src, `/art/${subject}-blue-social.png`);
  const record = manifest.items.find(item => item.subject === subject);
  assert(record && record.files.length === 4, canonicalPath + ': master and three derivatives');
  for (const file of record.files) {
    const bytes = await readFile(file.path);
    const info = await sharp(bytes).metadata();
    const hash = createHash('sha256').update(bytes).digest('hex');
    assert.equal(hash, file.sha256, file.path + ': recorded hash');
    assert.equal(bytes.length, file.bytes);
    assert.equal(info.width, file.width);
    assert.equal(info.height, file.height);
    if (file.path.endsWith('-social.png')) {
      assert.equal(info.width, 1200); assert.equal(info.height, 630); assert(!info.hasAlpha);
    } else {
      assert(info.hasAlpha, file.path + ': alpha channel');
      const stats = await sharp(bytes).stats();
      assert(stats.channels[3].min === 0 && stats.channels[3].max >= 254, file.path + ': transparent surroundings and visible subject (8-bit alpha tolerance)');
      if (file.path.endsWith('-master.png')) {
        assert(!masterHashes.has(hash), file.path + ': unique original'); masterHashes.add(hash);
      } else {
        assert.equal(info.width, info.height, file.path + ': square responsive export');
        assert.equal(info.width, file.path.endsWith('-512.webp') ? 512 : 1024);
        for (const [left, top] of [[0, 0], [info.width - 1, 0], [0, info.height - 1], [info.width - 1, info.height - 1]]) {
          const corner = await sharp(bytes).extract({left, top, width: 1, height: 1}).raw().toBuffer();
          assert(corner[3] <= 2, file.path + ': transparent contain padding (8-bit edge tolerance)');
        }
      }
    }
  }
  const html = render(page, content.sources.filter(source => page.sourceIds.includes(source.id)));
  assert(html.includes(`src="${art.src}"`), canonicalPath + ': article renders assigned image');
  assert(html.includes('research-hero--topic-art'), canonicalPath + ': responsive topic layout');
  assert(html.includes('srcSet=') || html.includes('srcset='), canonicalPath + ': responsive source set');
}
assert.equal(getTopicHeroArt('/research/example'), undefined, 'Unrelated routes retain their existing artwork');
console.log(`Verified ${definitions.length} image mappings (${topics.length} drug/condition topics and ${glossary.length} glossary entries), rendered heroes, alpha, dimensions and ${definitions.length * 4} file hashes.`);
