import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const here = path.dirname(fileURLToPath(import.meta.url));
const blue = '#1736F5';
const yellow = '#FFC709';
const ink = '#17204D';
const muted = '#5B6175';

// Outlined lettering: no installed-font dependency in the editable masters.
const letters = `
  <path fill-rule="evenodd" d="M44 148H130C186 148 219 175 219 218C219 251 201 275 173 286L229 372H169L122 296H99V372H44ZM99 194V250H128C151 250 165 241 165 222C165 203 151 194 128 194Z"/>
  <path transform="translate(12 0)" d="M235 213H293L329 266L365 213H423L358 292L429 372H369L327 317L285 372H227L298 292Z"/>`;

function mark({ small = false } = {}) {
  const arc = small ? 26 : 17;
  return `<g fill="${blue}">
    <g fill="none" stroke="${blue}" stroke-width="${arc}" stroke-linecap="butt">
      <path d="M181.158 116.534A216 216 0 0 1 ${small ? '446.962 107.252' : '477.968 134.688'}"/>
      <path d="M${small ? '512.457 183.938' : '496.937 158.107'}A216 216 0 0 1 181.158 447.466"/>
    </g>
    ${letters}
    <path d="${small ? 'M495 123L422 163L454 178L465 213Z' : 'M490 132L423 169L454 181L467 213Z'}"/>
  </g>`;
}

function svg(content, { width = 600, height = 560, viewBox = '0 0 600 560', title = 'RemapRx simplified Rx target concept', background = '' } = {}) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="${viewBox}" role="img" aria-labelledby="title"><title id="title">${title}</title>${background ? `<rect width="100%" height="100%" fill="${background}"/>` : ''}${content}</svg>`;
}

const symbol = svg(mark());
const white = svg(mark(), { background: '#FFFFFF' });
// A separately weighted, padded square composition for the browser favicon.
const favicon = svg(`<g transform="translate(12 32) scale(.96)">${mark({ small: true })}</g>`, {
  width: 600, height: 600, viewBox: '0 0 600 600', background: yellow,
  title: 'RemapRx blue Rx and direction arrow on yellow favicon concept',
});

await fs.writeFile(path.join(here, 'remaprx-target-logo.svg'), symbol);
await fs.writeFile(path.join(here, 'remaprx-target-logo-white.svg'), white);
await fs.writeFile(path.join(here, 'remaprx-target-favicon.svg'), favicon);
await sharp(Buffer.from(white)).resize(960, 896).png().toFile(path.join(here, 'remaprx-target-logo-white.png'));
for (const size of [16, 32, 48, 180, 512]) {
  await sharp(Buffer.from(favicon)).resize(size, size).png().toFile(path.join(here, `remaprx-target-favicon-${size}.png`));
}

const text = (x, y, value, size = 18, fill = muted, weight = 400) => `<text x="${x}" y="${y}" font-family="Arial, Helvetica, sans-serif" font-size="${size}" fill="${fill}" font-weight="${weight}">${value}</text>`;
const embed = async (filename, x, y, width, height) => `<image x="${x}" y="${y}" width="${width}" height="${height}" href="data:image/png;base64,${(await fs.readFile(path.join(here, filename))).toString('base64')}"/>`;

const preview = svg(`
  <rect width="1280" height="920" fill="#F6F7FB"/>
  ${text(56, 65, 'RemapRx', 30, ink, 700)}
  ${text(56, 98, 'Simplified Rx + target + direction', 18)}
  ${text(1088, 65, 'PREVIEW', 13, muted, 700)}
  <rect x="40" y="136" width="590" height="552" rx="22" fill="white"/>
  <rect x="650" y="136" width="590" height="552" rx="22" fill="white"/>
  ${text(74, 181, 'BLUE ON WHITE', 14, muted, 700)}
  ${text(684, 181, 'BLUE ON YELLOW · FAVICON', 14, muted, 700)}
  <g transform="translate(92 211) scale(.8)">${mark()}</g>
  ${await embed('remaprx-target-favicon-512.png', 769, 249, 352, 352)}
  ${text(74, 655, 'One outer arc. Flat arrow. Bold Rx.', 17)}
  ${text(684, 655, 'Thicker arc and wider gaps for small sizes.', 17)}
  <rect x="40" y="712" width="590" height="152" rx="18" fill="white"/>
  <rect x="650" y="712" width="590" height="152" rx="18" fill="#17204D"/>
  ${text(74, 747, 'ACTUAL FAVICON SIZES · LIGHT', 12, muted, 700)}
  ${text(684, 747, 'ACTUAL FAVICON SIZES · DARK', 12, '#FFFFFF', 700)}
  ${await embed('remaprx-target-favicon-16.png', 76, 780, 16, 16)}
  ${text(104, 793, 'RemapRx', 16, ink)}
  ${await embed('remaprx-target-favicon-32.png', 320, 772, 32, 32)}
  ${text(366, 793, 'RemapRx', 16, ink)}
  ${text(76, 835, '16 × 16 px', 12)}
  ${text(320, 835, '32 × 32 px', 12)}
  ${await embed('remaprx-target-favicon-16.png', 686, 780, 16, 16)}
  ${text(714, 793, 'RemapRx', 16, '#FFFFFF')}
  ${await embed('remaprx-target-favicon-32.png', 930, 772, 32, 32)}
  ${text(976, 793, 'RemapRx', 16, '#FFFFFF')}
  ${text(686, 835, '16 × 16 px', 12, '#C9D0EF')}
  ${text(930, 835, '32 × 32 px', 12, '#C9D0EF')}
  ${text(56, 899, 'Brand blue #1736F5  /  Brand yellow #FFC709', 13)}
  ${text(911, 899, 'Concept preview · not applied to site', 13)}
`, { width: 1280, height: 920, viewBox: '0 0 1280 920', title: 'RemapRx simplified logo and favicon comparison' });
await fs.writeFile(path.join(here, 'remaprx-target-preview.svg'), preview);
await sharp(Buffer.from(preview)).png().toFile(path.join(here, 'remaprx-target-preview.png'));
console.log('Created editable logo and favicon drafts, five PNG sizes, and comparison preview.');
