import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {compileAssessments,readAssessmentInputs,assessmentFingerprint} from '../../../scripts/evidence-assessments.mjs';

const root = path.resolve(import.meta.dirname, '../../..');
process.chdir(root);
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const inventory = read(path.join(import.meta.dirname, 'inventory.json'));
const canonical = read('data/content.json');
const discovery = read('data/discovery-pages.json');
const rows = read('data/reader-evidence.json').synthesisRows;
const profiles = [...canonical.guides, ...discovery].filter(guide => ['Drug','Condition'].includes(guide.type) && !guide.synthesisIds?.length);
assert.equal(profiles.length, 16);
assert.equal(inventory.records.length, 93);
assert.equal(new Set(inventory.records.map(record => record.sourceId)).size, 86);
assert.deepEqual(inventory.profiles.map(profile => profile.route), profiles.map(profile => profile.slug));
for (const guide of profiles) {
  assert.deepEqual(inventory.records.filter(record => record.route === guide.slug).map(record => record.sourceId), guide.sourceIds);
  assert.equal(rows.filter(row => (guide.type === 'Drug' ? row.drugId : row.conditionId) === guide.entityId).length, 0);
}
execFileSync('git', ['diff','--exit-code',inventory.baseCommit,'--','app','components','data','editorial','lib','public','scripts','styles','build','.openai']);
const before = fs.readFileSync(path.join(import.meta.dirname, 'inventory.json'));
execFileSync('python3', ['research/batches/FILL-REMAPRX-1-STEP2/inventory.py']);
assert.deepEqual(fs.readFileSync(path.join(import.meta.dirname, 'inventory.json')), before, 'Repeat inventory must not change bytes');
execFileSync('python3', ['-c', `import hashlib,json;from pathlib import Path
d=json.loads(Path('data/content.json').read_text());s={x['id']:x for x in d['sources']}
i=json.loads(Path('research/batches/FILL-REMAPRX-1-STEP2/inventory.json').read_text())
for r in i['records']:
 assert hashlib.sha256(json.dumps(s[r['sourceId']],ensure_ascii=False,sort_keys=True).encode()).hexdigest()==r['sourceRecordSha256'],r['sourceId']
 assert r['locators']==s[r['sourceId']].get('locators',[]),r['sourceId']
`]);

// Demonstrate the actual model boundary using an explicitly synthetic,
// in-memory fixture; never create a scientific row or projection on disk.
const original = readAssessmentInputs();
assert.equal(compileAssessments(original).records.length, 62);
const fixture = structuredClone(original);
const pending = {...structuredClone(rows[0]), id:'SYNTHETIC-STEP2-PENDING-EXCLUDED', drugId:'D02', conditionId:'C02',
  title:'Synthetic fixture, excluded from production', use:'Synthetic fixture use', population:'Synthetic fixture population',
  comparison:'Synthetic fixture comparator', endpoint:'Synthetic fixture endpoint', timepoint:'Synthetic fixture timepoint',
  status:'reported_result', sourceIds:['P-D02-ACTIV6-2023'], finding:{text:'Synthetic fixture text, excluded from production.',sources:['P-D02-ACTIV6-2023']}};
fixture.reader.synthesisRows.push(pending);
fixture.publicReader.synthesisRows.push(structuredClone(pending));
assert.throws(() => compileAssessments(fixture), /Every outcome needs its own assessment/);
fixture.assessments.records.push({rowId:pending.id, grade:'Not appraised', assessmentStatus:'not_appraised', assessedAt:null,
  inputSha256:assessmentFingerprint(pending,fixture.content.sources,pending,fixture.publicContent.sources)});
assert.throws(() => compileAssessments(fixture), /Invalid grade/);
assert.deepEqual(readAssessmentInputs(), original, 'Synthetic gate fixtures must not mutate production inputs');

// Render the real inherited Article for every empty profile.
const require = createRequire(import.meta.url), ts = require('typescript'), React = require('react');
const {renderToStaticMarkup} = require('react-dom/server');
const cache = new Map();
function load(file) {
  if (cache.has(file)) return cache.get(file).exports;
  if (file.endsWith('.css')) return {};
  if (file.endsWith('.json')) return read(file);
  const module = {exports:{}}; cache.set(file,module);
  const code = ts.transpileModule(fs.readFileSync(file,'utf8'), {fileName:file,compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true}}).outputText;
  const localRequire = id => {
    if (!id.startsWith('.') && !id.startsWith('@/')) return require(id);
    const base = id.startsWith('@/') ? path.join(root,id.slice(2)) : path.resolve(path.dirname(file),id);
    const target = [base,base+'.ts',base+'.tsx',base+'.json',path.join(base,'index.ts')].find(candidate => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
    assert(target, `Cannot resolve ${id}`); return load(target);
  };
  new Function('require','module','exports',code)(localRequire,module,module.exports); return module.exports;
}
const {Article} = load(path.join(root,'components/article.tsx'));
const {ThemeProvider} = load(path.join(root,'components/shared-theme/theme.tsx'));
const {content} = load(path.join(root,'lib/content.ts'));
for (const profile of inventory.profiles) {
  const guide = content.guides.find(guide => guide.slug === profile.route);
  const sources = content.sources.filter(source => guide.sourceIds.includes(source.id));
  const html = renderToStaticMarkup(React.createElement(ThemeProvider,{config:{mainId:'main',identity:{name:'RemapRx',homeHref:'/'}}},React.createElement(Article,{guide,sources})));
  assert(html.includes('No outcome findings are available in this table.'), profile.route+': truthful table-empty state');
  for (const id of profile.sourceIds) assert(html.includes(`id="source-ref-${id}"`), profile.route+': retained source reference '+id);
}
console.log(JSON.stringify({status:'PASS',step2State:'GATE_NOT_OUTCOME_FILL_PASS',profiles:16,sourceAssociations:93,distinctSources:86,
  exactReusableOutcomeRows:0,newOutcomes:0,appAndScientificFilesChanged:0,actualProfileSSR:16,repeatInventoryChanges:0,
  gateFixturesRejected:['missing assessment','unappraised assessment cannot be compiled as assessed']},null,2));
