import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const sharp=require('sharp');
const blue='#1736F5', deep='#1027B8', yellow='#FFC709', ink='#17204D', pale='#EFF2FF';
const r='<path fill="COLOR" fill-rule="evenodd" d="M65 78H108C129 78 143 90 143 108C143 123 134 135 120 139L143 167H116L94 140H87V167H65ZM87 97V121H105C116 121 122 117 122 109C122 101 116 97 105 97Z"/>';
const xUp='<path d="M181 119L145 165" fill="none" stroke="COLOR" stroke-width="16" stroke-linecap="round"/>';
const concepts=[
 {id:'a-integrated-wrap',name:'A · Integrated wrap',caption:'The x becomes the arrow and circles the whole Rx.',
  art:r+xUp+'<path d="M149 119L185 162C213 191 193 221 151 230C97 242 44 215 26 168C4 111 35 51 89 29C148 5 215 34 231 93C237 112 236 120 233 128" fill="none" stroke="COLOR" stroke-width="16" stroke-linecap="butt" stroke-linejoin="round"/><circle cx="149" cy="119" r="8" fill="COLOR"/><path d="M221 157L216 120L250 136Z" fill="COLOR"/>'},
 {id:'b-open-orbit',name:'B · Open circular arrow',caption:'A separate return arrow surrounds the bold Rx.',
  art:r+xUp+'<path d="M149 119L185 165" fill="none" stroke="COLOR" stroke-width="16" stroke-linecap="round"/><path d="M184 36A108 108 0 1 0 229 90" fill="none" stroke="COLOR" stroke-width="16" stroke-linecap="round"/><path d="M208 58L245 72L217 101Z" fill="COLOR"/>'}
];
const paint=(art,color=blue)=>art.replaceAll('COLOR',color);
const svg=(body,w=256,h=256,title='RemapRx sketch refinement')=>`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img"><title>${title}</title>${body}</svg>`;
const text=(x,y,t,size=16,color=ink,weight=400)=>`<text x="${x}" y="${y}" font-family="Inter,Arial,sans-serif" font-size="${size}" font-weight="${weight}" fill="${color}">${t}</text>`;
const mark=(c,x,y,size,color=blue)=>`<g transform="translate(${x} ${y}) scale(${size/256})">${paint(c.art,color)}</g>`;
for(const c of concepts){
 for(const [variant,color] of [['blue',blue],['black',ink],['white','#FFFFFF']]) await fs.writeFile(path.join(here,`${c.id}-${variant}.svg`),svg(paint(c.art,color),256,256,c.name));
 await sharp(Buffer.from(svg(paint(c.art)))).resize(640,640).png().toFile(path.join(here,`${c.id}.png`));
 for(const size of [16,32]) await sharp(Buffer.from(svg(paint(c.art)))).resize(size,size).png().toFile(path.join(here,`${c.id}-${size}.png`));
 await fs.writeFile(path.join(here,`${c.id}-wordmark.svg`),svg(mark(c,0,2,70)+text(83,52,'RemapRx',44,blue,700),305,76,c.name+' wordmark'));
}
function card(c,i){const x=48+i*696;return `<g transform="translate(${x} 195)"><rect width="648" height="735" rx="16" fill="white" stroke="#D7DEEF"/>${text(30,44,c.name,24,ink,700)}${text(30,76,c.caption,16,'#5B6175')}<rect x="30" y="106" width="588" height="323" rx="9" fill="${pale}"/>${mark(c,179,128,280)}${text(30,468,'WITH THE WORDMARK',11,'#5B6175',700)}<rect x="30" y="485" width="588" height="86" rx="6" fill="white" stroke="#D7DEEF"/>${mark(c,45,495,64)}${text(123,541,'RemapRx',37,blue,700)}${text(445,535,'Drugs',13,'#5B6175')}${text(505,535,'Conditions',13,'#5B6175')}${text(30,609,'SMALL SIZES',11,'#5B6175',700)}${text(288,609,'MONOCHROME / REVERSED',11,'#5B6175',700)}<rect x="30" y="625" width="228" height="79" rx="6" fill="${pale}"/>${mark(c,55,652,16)}${text(81,666,'16 px',12,'#5B6175')}${mark(c,151,644,32)}${text(194,666,'32 px',12,'#5B6175')}<rect x="286" y="625" width="148" height="79" rx="6" fill="#F5F5F5"/>${mark(c,334,638,53,ink)}<rect x="450" y="625" width="168" height="79" rx="6" fill="${deep}"/>${mark(c,507,638,53,'#FFFFFF')}</g>`;}
const sheet=svg(`<rect width="1440" height="992" fill="#F6F8FD"/><rect width="1440" height="160" fill="${deep}"/>${text(48,42,'REMAPRX / FROM YOUR SKETCHES',12,'#C5D0FF',700)}${text(48,91,'The Rx. The route around it.',37,'white',700)}${text(48,128,'Two interpretations, with the heavier weight of concept #2.',18,'#E2E8FF')}${concepts.map(card).join('')}${text(48,967,'Shape comparison only. The site identity has not been changed.',14,'#5B6175')}`,1440,992,'Two bold RemapRx logo refinements based on the owner’s sketches');
await fs.writeFile(path.join(here,'remaprx-sketch-refinements.svg'),sheet);
await sharp(Buffer.from(sheet)).png().toFile(path.join(here,'remaprx-sketch-refinements.png'));
console.log('Created two sketch-based SVG families and comparison PNG. No production identity changed.');
