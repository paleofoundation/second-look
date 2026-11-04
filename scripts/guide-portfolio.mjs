import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {load} from './check-reader-sections.mjs';

const root=path.resolve(import.meta.dirname,'..');
const {content,guideUrl}=load(path.join(root,'lib/content.ts'));
const {guideProducts,guideOffer}=load(path.join(root,'lib/guide-catalogue.ts'));
const {topicGuideMappings}=load(path.join(root,'lib/topic-guides.ts'));
const registry=JSON.parse(fs.readFileSync(path.join(root,'research/batches/RRX-GUIDE-PORTFOLIO-20261104/deliverables.json'),'utf8'));
assert.equal(registry.schemaVersion,1);
const manuscripts=new Map();
for(const item of registry.manuscripts){
  assert(!manuscripts.has(item.productId),'Duplicate manuscript registration');
  const target=path.resolve(root,item.manifestPath);
  assert(target.startsWith(root+path.sep)&&!path.isAbsolute(item.manifestPath),'Repository-relative manifest required');
  const manifest=JSON.parse(fs.readFileSync(target,'utf8'));
  assert.equal(manifest.productId,item.productId);
  assert(guideProducts.some(p=>p.id===item.productId),'Manuscript must belong to a known product');
  assert(manifest.assets.length>=3,'Register actual edition assets, not only an outline');
  for(const asset of manifest.assets)assert(/^[a-f0-9]{64}$/.test(asset.sha256));
  manuscripts.set(item.productId,{...item,manifest});
}
const topics=content.guides.filter(g=>g.type==='Drug'||g.type==='Condition');
const rows=topics.map(topic=>{
  const mappings=topicGuideMappings.filter(m=>m.kind===topic.type.toLowerCase()&&m.slug===topic.slug.split('/').at(-1));
  assert.equal(mappings.length,1,'Every topic requires exactly one own-topic guide: '+topic.slug);
  const mapping=mappings[0];
  const product=guideProducts.find(p=>p.id===mapping.productId);
  assert(product,'Missing product for '+topic.slug);
  assert.equal(mapping.articleUrl,guideUrl(topic));
  assert.equal(product.relatedHref,guideUrl(topic));
  assert.equal(product.priceMinor,4900);
  assert.equal(product.currency,'USD');
  return {topic,product,manuscript:manuscripts.get(product.id)};
});
assert.equal(new Set(rows.map(r=>r.product.id)).size,rows.length,'One drug guide cannot substitute for a condition guide');
const priority=id=>{const index=guideOffer.launchProductIds.indexOf(id);return index<0?guideOffer.launchProductIds.length:index;};
rows.sort((a,b)=>priority(a.product.id)-priority(b.product.id)||a.topic.type.localeCompare(b.topic.type)||a.topic.title.localeCompare(b.topic.title,'en'));
const released=rows.filter(r=>r.product.releaseState==='released').length;
const cell=text=>String(text).replaceAll('|','\\|').replaceAll('\n',' ');
const report=[
  '# Guide portfolio', '',
  'Generated from the current application topic registry, product mappings and private-deliverable manifests with `node scripts/guide-portfolio.mjs --write`. Do not edit the inventory by hand.', '',
  `Required: **${rows.length} own-topic guides** (${rows.filter(r=>r.topic.type==='Drug').length} drugs and ${rows.filter(r=>r.topic.type==='Condition').length} conditions). Registered manuscript candidates: **${manuscripts.size}**. Catalog releases: **${released}**.`, '',
  'The owner requires every current and future drug and condition page to have a substantive guide available for purchase. Each costs $49 USD once, with future approved editions included. Membership is $59/month after the first three guides are released. Metformin, Long COVID and itraconazole are first in sequence; all other topics remain required.', '',
  'A mapping or outline is not a completed guide. “Not registered” means this inventory has no actual manuscript manifest; it is not an exhaustive search of every external file. A registered candidate is not automatically reviewed, released or purchasable. The table records catalog state, not proof of live checkout.', '',
  '## Work to completion', '',
  'For each unregistered topic: reconcile its actual source set under the research-ingest contract, complete source assessments and integrity checks, then author its substantive web/PDF guide, sample and summary. Reuse assessed sources where the exact scope applies, not prose or efficacy conclusions from a different topic. Condition guides require condition-wide intervention coverage. No fixed reference-count ceiling applies.', '',
  'For each candidate: finish its named source/access limitations and edition review work, record real exact-asset approvals, upload the protected assets and release its own product. Verify signed-in checkout, payment reconciliation, permanent topic entitlement and web/PDF delivery on the deployed version. Preserve public safety information and free articles/reviews.', '',
  'Seller selected by the owner: Microbiome Signatures LLC. Live-capable code and synthetic payment fixtures do not establish a deployed payment service. Merchant configuration, the isolated provider sandbox acceptance and actual production activation are tracked in [GUIDE-COMMERCE.md](GUIDE-COMMERCE.md).', '',
  '## Required guides', '',
  '| Topic | Page type | Product | Manuscript | Catalog state |',
  '| --- | --- | --- | --- | --- |',
  ...rows.map(({topic,product,manuscript})=>`| ${cell(topic.title)} | ${topic.type} | [${cell(product.id)}](https://remaprx.com/guides/products/${product.slug}) | ${manuscript?`[${cell(manuscript.manifest.version)}](../${manuscript.manifestPath})`: 'Not registered'} | ${product.releaseState} |`), '',
  '## Checks and limits', '',
  '`node scripts/check-topic-guides.mjs` verifies every real page and its own offer, plus pending/released/withdrawn presentation. `node scripts/guide-portfolio.mjs --check` rejects a stale inventory. `--require-released` additionally fails until every required product is released in the catalog; even a pass is not proof of production payment acceptance.', '',
  'The guide manifests point to private files outside Git. Those files must be transferred through the private asset workflow; the portfolio does not copy paid prose into the application, public downloads or this document.', '',
].join('\n');
const output=path.join(root,'docs/GUIDE-PORTFOLIO.md');
if(process.argv.includes('--write'))fs.writeFileSync(output,report);
if(process.argv.includes('--check'))assert.equal(fs.readFileSync(output,'utf8'),report,'Guide inventory is stale; regenerate after reconciling topic and manuscript changes');
console.log(`Guide coverage: ${rows.length} mapped topics; ${manuscripts.size} registered manuscript candidates; ${released} catalog releases. Live purchasability is not inferred.`);
if(process.argv.includes('--require-released')&&released!==rows.length){
  console.error(`Incomplete: ${rows.length-released} required guides are not released.`);
  process.exitCode=1;
}
