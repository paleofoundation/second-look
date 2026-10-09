import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
const {products} = JSON.parse(fs.readFileSync('data/guide-catalogue.json', 'utf8'));
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
for (const product of products) {
  if (!product.edition) continue;
  if (!product.previewHref?.startsWith('/downloads/')) throw new Error('A guide preview must name a local, explicit preview asset.');
  const file = path.resolve('public', '.' + product.previewHref);
  if (!file.startsWith(path.resolve('public/downloads') + path.sep)) throw new Error('Invalid guide preview path.');
  const hash = sha(fs.readFileSync(file));
  if (hash !== product.edition.previewSha256) throw new Error(`Preview mismatch for ${product.id}/${product.edition.version}`);
  if (hash === product.edition.fullSha256) throw new Error('The protected guide cannot be used as its preview.');
  for (const name of fs.readdirSync('public/downloads')) {
    const candidate = path.join('public/downloads',name);
    if (fs.statSync(candidate).isFile() && sha(fs.readFileSync(candidate)) === product.edition.fullSha256) throw new Error('Protected full guide found in public downloads.');
  }
}
console.log('Guide edition/preview hashes match; no full guide is present in public downloads.');
