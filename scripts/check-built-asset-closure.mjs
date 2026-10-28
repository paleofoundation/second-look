import {readFile, stat} from 'node:fs/promises';
import path from 'node:path';

// RSC preload hints can outlive CSS-only chunks removed by the bundler.
// Check the emitted manifest against actual deployed files after every build.
const clientRoot = path.resolve('dist/client');
const manifest = await readFile('dist/server/__vite_rsc_assets_manifest.js', 'utf8');
const urls = [...new Set(manifest.match(/\/_next\/static\/[^"\\\s]+/g) ?? [])];
if (!urls.length) throw new Error('No RSC asset dependencies found; build first.');
const missing = [];
for (const url of urls) {
  const asset = path.resolve(clientRoot, url.slice(1));
  if (!asset.startsWith(clientRoot + path.sep)) throw new Error('Asset escapes client output: ' + url);
  try { if (!(await stat(asset)).isFile()) missing.push(url); }
  catch (error) { if (error.code !== 'ENOENT') throw error; missing.push(url); }
}
if (missing.length) throw new Error('RSC manifest references missing assets:\n' + missing.join('\n'));
console.log(`Built asset closure passed: ${urls.length} unique RSC JavaScript/CSS dependencies exist.`);
