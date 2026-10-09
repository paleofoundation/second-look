import fs from 'node:fs';
import crypto from 'node:crypto';

// Conservative release invalidation: any catalogue, shared promise, policy or
// presentation source change requires review of the new marketing hash.
const path = 'data/guide-catalogue.json';
const catalogue = JSON.parse(fs.readFileSync(path, 'utf8'));
const check = process.argv.includes('--check');
let stale = 0;
const shared = ['components/shared-theme/guide-catalogue.tsx', 'lib/guide-catalogue.ts', 'app/[...path]/page.tsx']
  .map(path => ({path, source:fs.readFileSync(path, 'utf8')}));
for (const product of catalogue.products) {
  const {marketingSha256: previous, ...content} = product;
  const computed = crypto.createHash('sha256').update(JSON.stringify({product:content, offer:catalogue.offer, shared})).digest('hex');
  if (computed !== previous) stale++;
  if (!check) product.marketingSha256 = computed;
}
if (check) {
  if (stale) throw new Error(`${stale} guide marketing hashes are stale; regenerate the candidate hashes and obtain new exact-edition approvals before release.`);
  console.log(`Verified ${catalogue.products.length} guide marketing hashes without mutation.`);
} else {
  fs.writeFileSync(path, JSON.stringify(catalogue, null, 2) + '\n');
  console.log(`Recorded marketing hashes for ${catalogue.products.length} products; no release or approval changed.`);
}
