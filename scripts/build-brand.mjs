import fs from 'node:fs/promises';
import sharp from 'sharp';

const blue = '#1736F5';
const source = 'assets/brand-concepts/mapping-round-4';
const symbol = (await fs.readFile(`${source}/remaprx-target-logo.svg`, 'utf8')).replace('RemapRx Rx map target concept', 'RemapRx').replace(/[ \t]+$/gm, '');
// Favicon-only optical framing: center the Rx bounds (228.5, 260),
// leaving the lighter target to the right with its outer marks inside the canvas.
const targetScale = 'translate(313 292) scale(.85) translate(-313 -292)';
const favicon = (await fs.readFile(`${source}/remaprx-target-favicon.svg`, 'utf8'))
  .replace('RemapRx blue Rx map target and crosshairs on yellow favicon concept', 'RemapRx')
  .replace('translate(0 10)', 'translate(103.49 76.4) scale(.86)')
  // Scale rings/crosshairs and arrow around the x; leave both letter paths untouched.
  .replace('<g fill="none" stroke=', `<g transform="${targetScale}" fill="none" stroke=`)
  .replace('<path d="M478', `<path transform="${targetScale}" d="M478`)
  .replace(/[ \t]+$/gm, '');
const lettering = JSON.parse(await fs.readFile('assets/brand/remaprx-lettering.json', 'utf8'));
const inside = symbol.slice(symbol.indexOf('</title>') + 8, symbol.lastIndexOf('</svg>'));
await fs.mkdir('public/brand', {recursive:true});
await fs.writeFile('public/brand/remaprx-symbol.svg', symbol);
await fs.writeFile('public/brand/remaprx-symbol-reversed.svg', symbol.replaceAll(blue, '#FFFFFF'));
for (const [name, color] of [['remaprx-wordmark', blue], ['remaprx-wordmark-reversed', '#FFFFFF']]) {
  const wordmark = `<svg xmlns="http://www.w3.org/2000/svg" width="260" height="64" viewBox="0 0 ${lettering.width} 64" role="img" aria-labelledby="title"><title id="title">RemapRx</title><g transform="scale(.11)">${inside.replaceAll(blue, color)}</g><path fill="${color}" d="${lettering.path}"/></svg>`;
  await fs.writeFile(`public/brand/${name}.svg`, wordmark);
}
await fs.writeFile('public/favicon.svg', favicon);
await sharp(Buffer.from(favicon)).resize(180,180).png().toFile('public/apple-touch-icon.png');
const pngs=[];
for (const size of [16,32,48]) pngs.push({size, data:await sharp(Buffer.from(favicon)).resize(size,size).png().toBuffer()});
const header=Buffer.alloc(6+16*pngs.length); header.writeUInt16LE(1,2); header.writeUInt16LE(pngs.length,4);
let offset=header.length;
pngs.forEach(({size,data},i)=>{const p=6+i*16;header[p]=size;header[p+1]=size;header.writeUInt16LE(1,p+4);header.writeUInt16LE(32,p+6);header.writeUInt32LE(data.length,p+8);header.writeUInt32LE(offset,p+12);offset+=data.length;});
await fs.writeFile('public/favicon.ico',Buffer.concat([header,...pngs.map(p=>p.data)]));
// Default social identity; article-specific artwork continues to override this.
const social=`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="${blue}"/><g transform="translate(708 18) scale(.91)">${inside.replaceAll(blue,'#FFC709')}</g><text x="76" y="160" fill="#FFC709" font-size="25" font-family="Arial, sans-serif">THE DRUG REPURPOSING ATLAS</text><text x="70" y="268" fill="white" font-size="74" font-family="Arial, sans-serif">RemapRx</text><text x="76" y="354" fill="white" font-size="43" font-family="Arial, sans-serif"><tspan x="76">Mapping new targets for</tspan><tspan x="76" dy="57">approved medications.</tspan></text><text x="76" y="548" fill="white" font-size="24" font-family="Arial, sans-serif">Map each connection to its sources.</text></svg>`;
await sharp(Buffer.from(social)).png().toFile('public/brand/remaprx-social.png');
console.log('Built approved RemapRx symbols, outlined wordmarks, SVG/ICO favicon, touch icon and social image.');
