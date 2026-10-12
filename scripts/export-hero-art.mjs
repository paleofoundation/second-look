import sharp from 'sharp';
import { mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';

// Technical derivatives only: preserve the master composition and transparency.
const definitions = JSON.parse(await readFile('data/topic-hero-art.json', 'utf8'));
const subjects = definitions.map(item => item.subject);
let previous = {items: []};
try { previous = JSON.parse(await readFile('assets/hero-art/manifest.json', 'utf8')); }
catch (error) { if (error.code !== 'ENOENT') throw error; }
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const forced = process.argv.filter(arg => arg.startsWith('--force=')).map(arg => arg.slice(8));
await mkdir('public/art', { recursive: true });
const manifest = [];
for (const subject of subjects) {
  const master = `assets/hero-art/${subject}-blue-master.png`;
  const info = await sharp(master).metadata();
  if (!info.hasAlpha) throw new Error(`${master} must retain transparency`);
  const outputs = [];
  const masterHash = digest(await readFile(master));
  const prior = previous.items.find(item => item.subject === subject);
  const fresh = async path => {
    if (forced.includes(subject) || prior?.files.find(file => file.path === master)?.sha256 !== masterHash) return false;
    try { return digest(await readFile(path)) === prior.files.find(file => file.path === path)?.sha256; }
    catch (error) { if (error.code === 'ENOENT') return false; throw error; }
  };
  for (const size of [512, 1024]) {
    const path = `public/art/${subject}-blue-hero${size === 512 ? '-512' : ''}.webp`;
    if (!(await fresh(path))) await sharp(master).resize(size, size, { fit: 'contain' }).webp({ quality: 88, alphaQuality: 100, effort: 6 }).toFile(path);
    outputs.push(path);
  }
  const social = `public/art/${subject}-blue-social.png`;
  if (!(await fresh(social))) await sharp(master).resize(1200, 630, { fit: 'contain', background: '#1027B8' }).flatten({ background: '#1027B8' }).png({ compressionLevel: 9 }).toFile(social);
  outputs.push(social);
  const files = [];
  for (const path of [master, ...outputs]) {
    const data = await readFile(path);
    const metadata = await sharp(data).metadata();
    files.push({ path, width: metadata.width, height: metadata.height, bytes: data.length, hasAlpha: metadata.hasAlpha, sha256: digest(data) });
  }
  manifest.push({ subject, files });
}
await writeFile('assets/hero-art/manifest.json', JSON.stringify({ schemaVersion: 'remaprx-hero-art-1.0', created: '2026-10-12', items: manifest }, null, 2) + '\n');
console.log(`Exported and hashed ${manifest.length} topic illustrations.`);
