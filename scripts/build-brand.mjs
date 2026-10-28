import fs from 'node:fs/promises';
import sharp from 'sharp';

const blue = '#1736F5';
const lightBlue = '#EFF2FF';
const symbol = (await fs.readFile('assets/brand/remaprx-enclosing-symbol.svg', 'utf8')).replace(/[ \t]+$/gm, '');
const lettering = JSON.parse(await fs.readFile('assets/brand/remaprx-lettering.json', 'utf8'));
const inside = symbol.slice(symbol.indexOf('</title>') + 8, symbol.lastIndexOf('</svg>'));
// Both rings surround the complete Rx. The square icon adds equal vertical padding.
const iconInside = inside.replace('stroke-width="16"', 'stroke-width="19"')
  .replace('stroke-width="8"', 'stroke-width="10"')
  .replace('stroke-width="10" d="M300', 'stroke-width="12" d="M300');
const squareIcon = (background) => `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600" role="img" aria-labelledby="title"><title id="title">RemapRx</title><rect width="600" height="600" fill="${background}"/><g transform="translate(0 10)">${iconInside}</g></svg>`;
const favicon = squareIcon('#FFC709');
const appIcon = squareIcon('#FFFFFF');
await fs.mkdir('public/brand', {recursive:true});
await fs.writeFile('public/brand/remaprx-symbol.svg', symbol);
await fs.writeFile('public/brand/remaprx-symbol-reversed.svg', symbol.replaceAll(blue, '#FFFFFF'));
for (const [name, color] of [['remaprx-wordmark', blue], ['remaprx-wordmark-reversed', '#FFFFFF']]) {
  const wordmark = `<svg xmlns="http://www.w3.org/2000/svg" width="260" height="64" viewBox="0 0 ${lettering.width} 64" role="img" aria-labelledby="title"><title id="title">RemapRx</title><g transform="scale(.11)">${inside.replaceAll(blue, color)}</g><path fill="${color}" d="${lettering.path}"/></svg>`;
  await fs.writeFile(`public/brand/${name}.svg`, wordmark);
}
await fs.writeFile('public/favicon.svg', favicon);
await fs.writeFile('public/brand/remaprx-app-icon.svg', appIcon);
await sharp(Buffer.from(appIcon)).resize(180,180).png().toFile('public/apple-touch-icon.png');
for (const size of [192, 512]) await sharp(Buffer.from(appIcon)).resize(size,size).png().toFile(`public/brand/remaprx-icon-${size}.png`);
const pngs=[];
for (const size of [16,32,48]) pngs.push({size, data:await sharp(Buffer.from(favicon)).resize(size,size).png().toBuffer()});
const header=Buffer.alloc(6+16*pngs.length); header.writeUInt16LE(1,2); header.writeUInt16LE(pngs.length,4);
let offset=header.length;
pngs.forEach(({size,data},i)=>{const p=6+i*16;header[p]=size;header[p+1]=size;header.writeUInt16LE(1,p+4);header.writeUInt16LE(32,p+6);header.writeUInt32LE(data.length,p+8);header.writeUInt32LE(offset,p+12);offset+=data.length;});
await fs.writeFile('public/favicon.ico',Buffer.concat([header,...pngs.map(p=>p.data)]));
// Default social identity; article-specific artwork continues to override this.
const social=`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="${blue}"/><g transform="translate(688 71) scale(.84)">${inside.replaceAll(blue,lightBlue)}</g><text x="76" y="160" fill="#FFC709" font-size="25" font-family="Arial, sans-serif">THE DRUG REPURPOSING ATLAS</text><text x="70" y="268" fill="white" font-size="74" font-family="Arial, sans-serif">RemapRx</text><text x="76" y="354" fill="white" font-size="43" font-family="Arial, sans-serif"><tspan x="76">Mapping new targets for</tspan><tspan x="76" dy="57">approved medications.</tspan></text><text x="76" y="548" fill="white" font-size="24" font-family="Arial, sans-serif">Map each connection to its sources.</text></svg>`;
await sharp(Buffer.from(social)).png().toFile('public/brand/remaprx-social.png');
console.log('Built enclosing-Rx symbols, wordmarks, blue/yellow website favicon, blue/white app and touch icons, and social image.');
