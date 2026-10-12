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
assert.deepEqual(definitions.map(item => item.canonicalPath).sort(), topics.map(guideUrl).sort(), 'Every existing drug and condition route has exactly one image mapping');
assert.equal(new Set(definitions.map(item => item.subject)).size, topics.length, 'Every topic has an individual asset');
assert.equal(manifest.items.length, topics.length);
const masterHashes = new Set();
for (const page of topics) {
  const canonicalPath = guideUrl(page);
  const art = getTopicHeroArt(canonicalPath);
  assert(art && art.alt && art.title && art.caption && art.description && art.socialImage.alt, canonicalPath + ': complete descriptive fields');
  const subject = canonicalPath.split('/').at(-1);
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
      assert.equal(info.width, info.height, file.path + ': square');
      const stats = await sharp(bytes).stats();
      assert(stats.channels[3].min === 0 && stats.channels[3].max === 255, file.path + ': transparent surroundings and visible subject');
      if (file.path.endsWith('-master.png')) {
        assert(!masterHashes.has(hash), file.path + ': unique original'); masterHashes.add(hash);
      } else assert.equal(info.width, file.path.endsWith('-512.webp') ? 512 : 1024);
    }
  }
  const html = render(page, content.sources.filter(source => page.sourceIds.includes(source.id)));
  assert(html.includes(`src="${art.src}"`), canonicalPath + ': article renders assigned image');
  assert(html.includes('research-hero--topic-art'), canonicalPath + ': responsive topic layout');
  assert(html.includes('srcSet=') || html.includes('srcset='), canonicalPath + ': responsive source set');
}
assert.equal(getTopicHeroArt('/research/example'), undefined, 'Unrelated routes retain their existing artwork');
console.log(`Verified ${topics.length} topic mappings, rendered heroes, alpha, dimensions and ${topics.length * 4} file hashes.`);
