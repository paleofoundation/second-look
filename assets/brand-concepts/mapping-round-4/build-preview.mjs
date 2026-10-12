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
  <path fill-rule="evenodd" d="M44 148H130C186 148 219 175 219 218C219 251 201 275 173 286L211 372H153L119 296H99V372H44ZM99 194V250H128C151 250 165 241 165 222C165 203 151 194 128 194Z"/>
  <path d="M227 213H279L315 266L352 213H407L343 292L413 372H357L313 317L273 372H217L282 292Z"/>`;

const polar = (radius, degrees) => {
  const a = degrees * Math.PI / 180;
  return `${(313 + radius * Math.cos(a)).toFixed(3)} ${(292 + radius * Math.sin(a)).toFixed(3)}`;
};
const arc = (radius, start, end, large = 0) => `M${polar(radius, start)}A${radius} ${radius} 0 ${large} 1 ${polar(radius, end)}`;

function mark({ small = false } = {}) {
  return `<g fill="${blue}">
    <g fill="none" stroke="${blue}" stroke-linecap="round">
      <path stroke-width="${small ? 19 : 16}" stroke-linecap="butt" d="${arc(215, -133, -47)} ${arc(215, -30, 135)}"/>
      <path stroke-width="${small ? 10 : 8}" stroke-linecap="butt" d="${arc(170, -124, -53)} ${arc(170, -28, 132)}"/>
      <path stroke-width="${small ? 12 : 10}" d="M313 46V145M462 292H556M313 440V538"/>
      <path stroke-width="${small ? 8 : 6}" stroke-linecap="butt" d="M${polar(170, 45)}L${polar(215, 45)}M${polar(170, 134)}L${polar(215, 134)}"/>
      <g stroke-width="${small ? 8 : 6}" opacity="${small ? '1' : '.38'}">
        <path d="M313 169V196M313 397V425M221 292H251M433 292H458"/>
        <path stroke-width="4" d="M304 187H322M235 286V298M448 286V298M304 409H322"/>
      </g>
    </g>
    ${letters}
    <path d="M478 141L407 176L440 188L452 220Z"/>
  </g>`;
}

function svg(content, { width = 600, height = 580, viewBox = '0 0 600 580', title = 'RemapRx Rx map target concept', background = '' } = {}) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="${viewBox}" role="img" aria-labelledby="title"><title id="title">${title}</title>${background ? `<rect width="100%" height="100%" fill="${background}"/>` : ''}${content}</svg>`;
}

const symbol = svg(mark());
const white = svg(mark(), { background: '#FFFFFF' });
// Preserve every mapping detail at small sizes; strengthen strokes only.
const favicon = svg(`<g transform="translate(0 10)">${mark({ small: true })}</g>`, {
  width: 600, height: 600, viewBox: '0 0 600 600', background: yellow,
  title: 'RemapRx blue Rx map target and crosshairs on yellow favicon concept',
});

await fs.writeFile(path.join(here, 'remaprx-target-logo.svg'), symbol);
await fs.writeFile(path.join(here, 'remaprx-target-logo-white.svg'), white);
await fs.writeFile(path.join(here, 'remaprx-target-favicon.svg'), favicon);
await sharp(Buffer.from(white)).resize(960, 928).png().toFile(path.join(here, 'remaprx-target-logo-white.png'));
for (const size of [16, 32, 48, 180, 512]) {
  await sharp(Buffer.from(favicon)).resize(size, size).png().toFile(path.join(here, `remaprx-target-favicon-${size}.png`));
}

const text = (x, y, value, size = 18, fill = muted, weight = 400) => `<text x="${x}" y="${y}" font-family="Arial, Helvetica, sans-serif" font-size="${size}" fill="${fill}" font-weight="${weight}">${value}</text>`;
const embed = async (filename, x, y, width, height) => `<image x="${x}" y="${y}" width="${width}" height="${height}" href="data:image/png;base64,${(await fs.readFile(path.join(here, filename))).toString('base64')}"/>`;

const preview = svg(`
  <rect width="1280" height="920" fill="#F6F7FB"/>
  ${text(56, 65, 'RemapRx', 30, ink, 700)}
  ${text(56, 98, 'Mapping detail restored · tighter Rx', 18)}
  ${text(1088, 65, 'PREVIEW', 13, muted, 700)}
  <rect x="40" y="136" width="590" height="552" rx="22" fill="white"/>
  <rect x="650" y="136" width="590" height="552" rx="22" fill="white"/>
  ${text(74, 181, 'BLUE ON WHITE', 14, muted, 700)}
  ${text(684, 181, 'BLUE ON YELLOW · FAVICON', 14, muted, 700)}
  <g transform="translate(95 193) scale(.78)">${mark()}</g>
  ${await embed('remaprx-target-favicon-512.png', 769, 249, 352, 352)}
  ${text(74, 655, 'The x sits at the center of the map target.', 17)}
  ${text(684, 655, 'Mapping details retained in the favicon.', 17)}
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
`, { width: 1280, height: 920, viewBox: '0 0 1280 920', title: 'RemapRx mapping logo and favicon comparison' });
await fs.writeFile(path.join(here, 'remaprx-target-preview.svg'), preview);
await sharp(Buffer.from(preview)).png().toFile(path.join(here, 'remaprx-target-preview.png'));
console.log('Created editable logo and favicon drafts, five PNG sizes, and comparison preview.');
