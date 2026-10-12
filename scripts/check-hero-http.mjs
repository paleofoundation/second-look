import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import sharp from 'sharp';

// End-to-end verification of served metadata and public image delivery.
const origin = process.argv.find(arg => arg.startsWith('--origin='))?.slice(9) || 'http://127.0.0.1:5174';
const definitions = JSON.parse(await readFile('data/topic-hero-art.json', 'utf8'));
const decode = value => value.replace(/&quot;/g, '"').replace(/&#x27;|&#39;|&apos;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
const attributes = tag => Object.fromEntries([...tag.matchAll(/([\w:-]+)="([^"]*)"/g)].map(match => [match[1], decode(match[2])]));
const errors = [];
let verified = 0;
const pending = [...definitions];
await Promise.all(Array.from({length: 4}, async () => {
  while (pending.length) {
    const art = pending.shift();
    try {
      const response = await fetch(origin + art.canonicalPath);
      assert.equal(response.status, 200, 'page HTTP status');
      const html = await response.text();
      const tags = [...html.matchAll(/<(?:meta|link|img)\b[^>]*>/g)].map(match => attributes(match[0]));
      const meta = name => tags.find(tag => tag.property === name || tag.name === name)?.content;
      const canonical = 'https://remaprx.com' + art.canonicalPath;
      const imagePath = `/art/${art.subject}-blue-hero.webp`;
      const socialPath = `/art/${art.subject}-blue-social.png`;
      assert(tags.some(tag => tag.rel === 'canonical' && tag.href === canonical), 'canonical URL');
      assert.equal(meta('og:image'), 'https://remaprx.com' + socialPath);
      assert.equal(meta('og:image:alt'), art.socialAlt);
      assert.equal(meta('twitter:image'), 'https://remaprx.com' + socialPath);
      assert.equal(meta('twitter:card'), 'summary_large_image');
      assert(meta('robots')?.includes('noindex') && meta('robots')?.includes('nofollow'), 'existing indexing hold');
      assert(tags.some(tag => tag.src === imagePath && tag.alt === art.alt && tag.srcSet?.includes('512w')), 'visible responsive hero');
      const jsonld = [...html.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)].flatMap(match => JSON.parse(match[1])['@graph'] || []);
      const image = jsonld.find(item => item['@type'] === 'ImageObject');
      const page = jsonld.find(item => item['@type'] === 'WebPage');
      assert.equal(image?.contentUrl, 'https://remaprx.com' + imagePath);
      assert.equal(image?.description, art.description);
      assert.equal(page?.primaryImageOfPage?.['@id'], image?.['@id']);
      for (const [imageURL, width, height, format] of [[imagePath, 1024, 1024, 'webp'], [socialPath, 1200, 630, 'png']]) {
        const asset = await fetch(origin + imageURL);
        assert.equal(asset.status, 200, imageURL + ' HTTP status');
        const info = await sharp(Buffer.from(await asset.arrayBuffer())).metadata();
        assert.equal(info.width, width); assert.equal(info.height, height); assert.equal(info.format, format);
      }
      verified++;
    } catch (error) { errors.push(`${art.canonicalPath}: ${error.message}`); }
  }
}));
assert.equal(errors.length, 0, errors.join('\n'));
console.log(`Verified ${verified} served topic pages, canonical/OG/Twitter/ImageObject metadata, indexing hold and ${verified * 2} delivered images at ${origin}.`);
