import fs from 'node:fs';
import path from 'node:path';

const projections = ['public-content','topics','author-profiles','guide-catalogue','navigation-interest','public-mechanisms'];
const privateKeys = new Set(['provenance','sourceLinks','demandTopicIds','contractException']);
const privateCopy = /owner[-_ ](?:requested|required|priorit)|mandatory owner|coordinating task|observed_reddit_question|saved discussions|next acquisition packet|Keep required acquisition|acquisition backlog|non-preface accepted CP28/i;
let fields = 0;
function inspect(value, location) {
  if (typeof value === 'string') {
    fields++;
    if (privateCopy.test(value)) throw new Error(`Private production copy in ${location}`);
  } else if (Array.isArray(value)) value.forEach((v,i)=>inspect(v,`${location}/${i}`));
  else if (value && typeof value === 'object') for (const [key,v] of Object.entries(value)) {
    if (privateKeys.has(key)) throw new Error(`Private provenance field in ${location}/${key}`);
    inspect(v,`${location}/${key}`);
  }
}
for (const projection of projections) inspect(JSON.parse(fs.readFileSync(`data/${projection}.json`,'utf8')),projection);
const content = JSON.parse(fs.readFileSync('data/public-content.json','utf8'));
const mechanisms = JSON.parse(fs.readFileSync('data/public-mechanisms.json','utf8'));
for (const record of mechanisms.contexts) {
  if (!record.sourceIds.length || !record.locator) throw new Error('A displayed mechanism needs sources and a locator.');
  for (const id of record.sourceIds) if (!content.sources.some(source=>source.id===id && source.status!=='Quarantined')) throw new Error('Mechanism source missing or quarantined.');
}
function files(root) { return fs.readdirSync(root,{withFileTypes:true}).flatMap(item=>item.isDirectory()?files(path.join(root,item.name)):[path.join(root,item.name)]); }
let payloads = 0;
if (!process.argv.includes('--source-only')) {
  if (!fs.existsSync('dist/client')) throw new Error('Build client output before verifying payloads.');
  for (const file of files('dist/client').filter(file=>/\.(js|json|html|map)$/.test(file))) {
    payloads++;
    const text=fs.readFileSync(file,'utf8');
    if (privateCopy.test(text) || /observed_reddit_question|"demandTopicIds"|"sourceLinks"/.test(text)) throw new Error(`Private provenance in built payload: ${file}`);
  }
}
console.log(JSON.stringify({status:'PASS',projections:projections.length,fields,payloads,mechanismContexts:mechanisms.contexts.length}));
