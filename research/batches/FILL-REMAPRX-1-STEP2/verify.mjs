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
const candidates=read(path.join(import.meta.dirname,'appraisal/candidates.json'));
const accounting=read(path.join(import.meta.dirname,'appraisal/profile-accounting.json'));
const dispositions=read(path.join(import.meta.dirname,'appraisal/source-dispositions.json'));
const fromBase=file=>JSON.parse(execFileSync('git',['show',inventory.baseCommit+':'+file],{encoding:'utf8',maxBuffer:8*1024*1024}));
const baselineProfiles=[...fromBase('data/content.json').guides,...fromBase('data/discovery-pages.json')]
 .filter(guide=>['Drug','Condition'].includes(guide.type)&&!guide.synthesisIds?.length);
assert.equal(baselineProfiles.length,16);
assert.equal(inventory.records.length,93);
assert.equal(new Set(inventory.records.map(r=>r.sourceId)).size,86);
assert.deepEqual(inventory.profiles.map(p=>p.route),baselineProfiles.map(p=>p.slug));
assert.equal(candidates.length,8);
assert.equal(accounting.filledProfiles,5);assert.equal(accounting.emptyProfiles,11);
assert.equal(accounting.queueLines,76);assert.equal(accounting.queueDistinctSourceIds,72);assert.equal(accounting.queueSent,false);
assert.equal(dispositions.records.length,93);
assert.deepEqual(dispositions.records.map(r=>[r.route,r.sourceId]),inventory.records.map(r=>[r.route,r.sourceId]));
assert(dispositions.records.every(r=>r.disposition&&r.reason&&r.humanReview&&r.release==='not authorized'));
for(const [file,key,id] of [
 ['data/reader-evidence.json','synthesisRows','id'],['data/public-reader-evidence.json','synthesisRows','id'],
 ['editorial/evidence-assessments.json','records','rowId'],['data/public-evidence-assessments.json','records','rowId'],
 ['data/outcome-summaries.json','records','id'],['editorial/outcome-summary/assessments.json','records','id']]){
 const current=new Map(read(file)[key].map(r=>[r[id],r]));
 for(const old of fromBase(file)[key])assert.deepEqual(current.get(old[id]),old,'Preserve prior accepted record '+old[id]);
}
for(const file of ['editorial/EVIDENCE-GRADING.md','scripts/evidence-assessments.mjs'])
 assert.equal(fs.readFileSync(file,'utf8'),execFileSync('git',['show',inventory.baseCommit+':'+file],{encoding:'utf8'}),'Unchanged grading contract/compiler');
const dosing=canonical.guides.find(g=>g.entityId==='D02').sections.find(s=>s.id==='dosing');
assert(dosing.paragraph.includes('50 mg twice daily on day 1, followed by 100 mg twice daily for 12 additional days'));
assert.deepEqual(dosing.sources,['P-D02-ACTIV6-2023']);
const baselineSources=fromBase('data/content.json').sources;
for(const source of canonical.sources){
 const old=baselineSources.find(s=>s.id===source.id);assert(old,'No new source identities');
 if(source.id==='P-D08-HCC-2022'){
  assert.equal(source.status,'Quarantined');assert(source.correction.includes('10.1002/prp2.70222'));
  for(const key of Object.keys(old).filter(k=>!['preview','status','correction','decisiveLimit'].includes(k)))assert.deepEqual(source[key],old[key]);
 }else assert.deepEqual(source,old,'Preserve unrelated source '+source.id);
}
const before=fs.readFileSync(path.join(import.meta.dirname,'inventory.json'));
execFileSync('python3',['research/batches/FILL-REMAPRX-1-STEP2/inventory.py']);
assert.deepEqual(fs.readFileSync(path.join(import.meta.dirname,'inventory.json')),before,'Frozen initial audit repeat is unchanged');
const assessmentInputs=readAssessmentInputs();
const summaryRecords=read('data/outcome-summaries.json').records;
for(const c of candidates){
 const r=rows.find(r=>r.id===c.row.id);assert.deepEqual(r,c.row);
 const a=assessmentInputs.assessments.records.find(a=>a.rowId===r.id);assert(a);assert.equal(a.domains.length,5);assert.equal(a.assessedAt,'2026-10-26');
 assert.equal(a.inputSha256,assessmentFingerprint(r,canonical.sources,c.publicRow,assessmentInputs.publicContent.sources));
 assert.equal(r.publicationState,'private_ai_draft');assert.equal(r.humanApproval,'pending');assert.equal(r.certainty.label,'Not appraised');
 const summary=summaryRecords.find(s=>s.synthesisIds.includes(r.id));assert(summary);assert.equal(summary.assessedOn,'2026-10-26');
 if(a.integrity==='preclinical_only'){assert.equal(a.grade,'Low');assert.equal(summary.grade.value,null);assert.equal(summary.evidence.rctCount,0);assert.equal(summary.evidence.participants,null);}
 for(const binding of c.sourceBindings){
  const bytes=fs.readFileSync(binding.path);const {createHash}=await import('node:crypto');assert.equal(createHash('sha256').update(bytes).digest('hex'),binding.expectedSha256,'Exact original hash');
 }
}
assert(!rows.some(r=>r.sourceIds.includes('P-D08-HCC-2022')),'Retracted source cannot support a canonical outcome');
const repeatFiles=execFileSync('git',['ls-files','data','editorial'],{encoding:'utf8'}).trim().split('\n');
repeatFiles.push(...fs.readdirSync(path.join(import.meta.dirname,'appraisal')).filter(f=>f.endsWith('.json')||f.endsWith('.csv')).map(f=>path.join(import.meta.dirname,'appraisal',f)));
const bytesBefore=new Map(repeatFiles.map(file=>[file,fs.readFileSync(file)]));
for(const [command,args] of [['python3',['research/batches/FILL-REMAPRX-1-STEP2/appraisal/project.py']],['node',['scripts/evidence-assessments.mjs','--write']],['python3',['editorial/outcome-summary/build.py']],['python3',['research/batches/FILL-REMAPRX-1-STEP2/appraisal/account.py']]])execFileSync(command,args);
for(const [file,bytes] of bytesBefore)assert.deepEqual(fs.readFileSync(file),bytes,'Repeat projection changes '+file);

// Demonstrate the actual model boundary using an explicitly synthetic,
// in-memory fixture; never create a scientific row or projection on disk.
const original = readAssessmentInputs();
assert.equal(compileAssessments(original).records.length, 70);
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
  const scoped=rows.filter(row=>(guide.type==='Drug'?row.drugId:row.conditionId)===guide.entityId);
  assert.equal(html.includes('No outcome findings are available in this table.'),scoped.length===0,profile.route+': exact filled/empty state');
  for(const row of scoped)assert(html.includes(`id="${row.id}"`),profile.route+': canonical row fragment '+row.id);
  for (const id of profile.sourceIds) assert(html.includes(`id="source-ref-${id}"`), profile.route+': retained source reference '+id);
}
console.log(JSON.stringify({status:'PASS',step2State:'EXISTING_SOURCE_APPRAISAL_DRAFT_CANDIDATE',profiles:16,filled:5,empty:11,sourceAssociations:93,distinctSources:86,
 newOutcomes:8,newAssessments:8,domainJudgments:40,queueLines:76,queueSent:false,actualProfileSSR:16,repeatProjectionChanges:0,
 preservedPriorRows:62,preservedPriorSummaries:60,independentAcceptances:0,humanApprovals:0,releasedRows:0,
 negativeFixturesRejected:['missing assessment','unappraised canonical assessment']},null,2));
