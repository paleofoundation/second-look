import {readFile, writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';

const read = async path => JSON.parse(await readFile(path, 'utf8'));
const canonical = (await read('data/public-content.json')).guides;
const discovery = await read('data/discovery-pages.json');
const topics = [...canonical, ...discovery.filter(page => !canonical.some(guide => guide.id === page.id || guide.slug === page.slug))]
  .filter(page => /^\/(drugs|conditions)\//.test(page.slug));
const initial = await read('assets/hero-art/initial-metadata.json');
const definitions = new Map(initial.map(item => [item.canonicalPath, item]));
const generationFiles = ['drug-generation.json', 'root-drug-generation.json', 'condition-a-generation.json', 'condition-b-generation.json'];
for (const file of generationFiles) {
  let records;
  try { records = await read(`assets/hero-art/${file}`); }
  catch (error) { if (process.argv.includes('--partial') && error.code === 'ENOENT') continue; throw error; }
  for (const item of records) {
    if (process.argv.includes('--partial') && (!item.alt?.trim() || !item.prompt?.trim())) continue;
    const page = topics.find(page => page.slug === item.canonicalPath);
    assert(page, `Unknown topic ${item.canonicalPath}`);
    assert(!definitions.has(item.canonicalPath), `Duplicate artwork assignment ${item.canonicalPath}`);
    assert.equal(item.slug, item.canonicalPath.split('/').at(-1));
    assert(item.alt?.trim() && item.prompt?.trim(), `Missing visible description or provenance for ${item.slug}`);
    await readFile(`assets/hero-art/${item.slug}-blue-master.png`);
    definitions.set(item.canonicalPath, {
      canonicalPath: item.canonicalPath,
      subject: item.slug,
      alt: item.alt,
      title: `${page.title} guide — blue topic illustration`,
      caption: `Blue editorial illustration for the ${page.title} research guide.`,
      description: `${item.alt} This editorial illustration accompanies the ${page.title} research guide. ${page.slug.startsWith('/drugs/') ? 'The generic imagery does not identify a commercial product, dose, or treatment benefit.' : 'It does not depict diagnostic findings or treatment effects.'}`,
      socialAlt: `${item.alt} Illustration for the ${page.title} research guide.`,
    });
  }
}
const missing = topics.filter(page => !definitions.has(page.slug));
if (!process.argv.includes('--partial')) assert.equal(missing.length, 0, `Missing artwork: ${missing.map(page => page.slug).join(', ')}`);
await writeFile('data/topic-hero-art.json', JSON.stringify([...definitions.values()].sort((a, b) => a.canonicalPath.localeCompare(b.canonicalPath)), null, 2) + '\n');
console.log(`Mapped ${definitions.size}/${topics.length} topics; ${missing.length} remain.`);
