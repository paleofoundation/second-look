import {readFile, writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';

const read = async path => JSON.parse(await readFile(path, 'utf8'));
const content = await read('data/public-content.json');
const canonical = content.guides;
const discovery = await read('data/discovery-pages.json');
const topics = [...canonical, ...discovery.filter(page => !canonical.some(guide => guide.id === page.id || guide.slug === page.slug))]
  .filter(page => /^\/(drugs|conditions)\//.test(page.slug));
const glossary = content.glossary.map(term => ({...term, slug: `/glossary/${term.slug}`}));
const knownPages = new Map([...topics, ...glossary].map(page => [page.slug, page]));
const initial = await read('assets/hero-art/initial-metadata.json');
const definitions = new Map();
for (const item of initial) {
  assert(knownPages.has(item.canonicalPath), `Unknown topic ${item.canonicalPath}`);
  assert(!definitions.has(item.canonicalPath), `Duplicate artwork assignment ${item.canonicalPath}`);
  definitions.set(item.canonicalPath, item);
}
const generationFiles = ['drug-generation.json', 'root-drug-generation.json', 'condition-a-generation.json', 'condition-b-generation.json', 'glossary-generation.json'];
for (const file of generationFiles) {
  let records;
  try { records = await read(`assets/hero-art/${file}`); }
  catch (error) {
    if (error.code === 'ENOENT' && process.argv.includes('--partial')) continue;
    throw error;
  }
  for (const item of records) {
    if (process.argv.includes('--partial') && (!item.alt?.trim() || !item.prompt?.trim())) continue;
    const page = knownPages.get(item.canonicalPath);
    assert(page, `Unknown topic ${item.canonicalPath}`);
    const isGlossary = page.slug.startsWith('/glossary/');
    assert.equal(isGlossary, file === 'glossary-generation.json', `Artwork provenance category mismatch for ${item.canonicalPath}`);
    assert(!definitions.has(item.canonicalPath), `Duplicate artwork assignment ${item.canonicalPath}`);
    assert.equal(item.slug, item.canonicalPath.split('/').at(-1));
    assert(item.alt?.trim() && item.prompt?.trim(), `Missing visible description or provenance for ${item.slug}`);
    await readFile(`assets/hero-art/${item.slug}-blue-master.png`);
    const pageLabel = `${page.title} ${isGlossary ? 'glossary entry' : 'research guide'}`;
    definitions.set(item.canonicalPath, {
      canonicalPath: item.canonicalPath,
      subject: item.slug,
      alt: item.alt,
      title: `${page.title} ${isGlossary ? 'glossary entry' : 'guide'} — blue topic illustration`,
      caption: `Blue editorial illustration for the ${pageLabel}.`,
      description: `${item.alt} This editorial illustration accompanies the ${pageLabel}. ${isGlossary ? 'It is a simplified conceptual illustration, not a complete scientific diagram.' : page.slug.startsWith('/drugs/') ? 'The generic imagery does not identify a commercial product, dose, or treatment benefit.' : 'It does not depict diagnostic findings or treatment effects.'}`,
      socialAlt: `${item.alt} Illustration for the ${pageLabel}.`,
    });
  }
}
const requiredPages = [...topics, ...glossary];
const missing = requiredPages.filter(page => !definitions.has(page.slug));
if (!process.argv.includes('--partial')) assert.equal(missing.length, 0, `Missing artwork: ${missing.map(page => page.slug).join(', ')}`);
assert.equal(new Set([...definitions.values()].map(item => item.subject)).size, definitions.size, 'Every illustrated page has an individual asset');
await writeFile('data/topic-hero-art.json', JSON.stringify([...definitions.values()].sort((a, b) => a.canonicalPath.localeCompare(b.canonicalPath)), null, 2) + '\n');
const glossaryCount = [...definitions.keys()].filter(canonicalPath => canonicalPath.startsWith('/glossary/')).length;
console.log(`Mapped ${definitions.size}/${requiredPages.length} required pages, including ${glossaryCount}/${glossary.length} glossary illustrations; ${missing.length} pages remain.`);
