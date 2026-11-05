import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import ts from 'typescript';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {execFileSync} from 'node:child_process';
import {load,render} from './check-reader-sections.mjs';
const root=path.resolve(import.meta.dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const {content,isPrimarySource}=load(path.join(root,'lib/content.ts'));
const {articleEvidenceSources}=load(path.join(root,'lib/citation-plan.ts'));
const config=read('data/canonical-drug-pages.json');
const summaries=read('data/drug-study-summaries.json');
const expected=content.guides.filter(g=>g.type==='Drug'&&g.slug!=='/drugs/metformin').map(g=>g.slug).sort();
assert.deepEqual([...config.pages].sort(),expected,'Every non-Metformin live drug route is included exactly once');
assert.equal(expected.length,33);
const feedIds=new Set();
for(const route of expected){
 const guide=content.guides.find(g=>g.slug===route);
 const sources=articleEvidenceSources(guide,content.sources.filter(s=>guide.sourceIds.includes(s.id)));
 const html=render(guide,sources);
 const article=html.match(/<article class="research-content__center entry-content">([\s\S]*?)<\/article>/)[1];
 const ids=['section-overview','mechanisms','section-safety','section-contraindications','section-interactions','section-dosing','section-status','section-evidence','faqs','research-feed','update-history','references'];
 let position=-1;
 for(const id of ids){const next=article.indexOf(`id="${id}"`);assert(next>position,route+': canonical order '+id);position=next;}
 const mechanisms=article.slice(article.indexOf('id="mechanisms"'),article.indexOf('id="section-safety"'));
 assert(!mechanisms.includes('<details'),route+': main mechanism explanations are visible');
 assert(mechanisms.includes('<p>'),route+': mechanism prose is present');
 const overview=article.slice(article.indexOf('id="section-overview"'),article.indexOf('id="mechanisms"'));
 assert(!overview.includes('<details'),route+': overview visible');
 assert(!article.slice(0,article.indexOf('id="references"')).includes('<ul'),route+': no narrative bullet lists');
 const feed=article.slice(article.indexOf('id="research-feed"'),article.indexOf('id="update-history"'));
 assert(!/not yet been summarized|detailed appraisal.*not yet available/.test(feed),route+': no avoidable feed placeholders');
 for(const source of sources.filter(isPrimarySource)){
  feedIds.add(source.id);
  assert(Array.isArray(summaries[source.id])&&summaries[source.id].length===4,route+': four source-bound answers for '+source.id);
  assert(summaries[source.id].every(a=>a.trim().length>0),route+': nonempty summaries');
  assert(!summaries[source.id].some(a=>/\bpartner(ship)?s?\b|[\u2013\u2014]/i.test(a)),route+': authored language constraints');
 }
 const prose=[...guide.sections.map(s=>s.paragraph),...guide.faqs.map(q=>q.answer)].join(' ');
 if(/cancer|tumor|leukemia|lymphoma|myeloma|glioblastoma|carcinoma|melanoma|sarcoma/i.test(guide.sections.map(s=>s.paragraph).join(' '))) assert(article.includes('Cancer research needs clinical context'),route+': cancer context notice');
 assert(!/\bpartner(ship)?s?\b|[\u2013\u2014]/i.test(prose),route+': page language constraints');
 assert(article.includes('data-update-id="canonical-'),route+': dated substantive update is visible');
}
// Exact scientific records must survive a presentation pass without a new grade/count.
const base='c63f817efc74afd0c7bcbef8b23dcd1d2a039c59';
for(const file of ['data/reader-evidence.json','data/public-reader-evidence.json','editorial/evidence-assessments.json','data/public-evidence-assessments.json','editorial/outcome-summary/assessments.json','editorial/outcome-summary/authored.json']){
 assert.equal(fs.readFileSync(path.join(root,file),'utf8'),execFileSync('git',['show',base+':'+file],{cwd:root,encoding:'utf8',maxBuffer:20e6}),file+': evidence, grade and trial identities unchanged');
}
for(const [file,key,idKey,id] of [['data/content.json','guides','id','G-METFORMIN'],['data/public-content.json','guides','id','G-METFORMIN'],['data/public-mechanisms.json','drugs','drugId','D01'],['editorial/parent-guide-scopes.json','parents','guideId','G-METFORMIN']]){
 const prior=JSON.parse(execFileSync('git',['show',base+':'+file],{cwd:root,encoding:'utf8',maxBuffer:20e6}));
 assert.deepEqual(read(file)[key].find(x=>x[idKey]===id),prior[key].find(x=>x[idKey]===id),file+': Metformin unchanged');
}
console.log(JSON.stringify({status:'PASS',drugPages:expected.length,sourceSummaries:feedIds.size,answers:feedIds.size*4,evidenceAndTrialRecords:'byte-identical',metformin:'unchanged'}));

// Compare actual Metformin markup with the pre-change rendering implementation.
// Current canonical records were checked above. Other pages cannot affect this fixture.
const require=createRequire(import.meta.url);
const baselineFiles=new Set(['components/article.tsx','components/shared-theme/mechanisms.tsx','components/study-source-content.tsx','lib/citation-plan.ts']);
const cache=new Map();
function baselineLoad(file){
 if(cache.has(file))return cache.get(file).exports;
 if(file.endsWith('.css'))return {};
 if(file.endsWith('.json'))return JSON.parse(fs.readFileSync(file,'utf8'));
 const record={exports:{}};cache.set(file,record);
 const rel=path.relative(root,file);
 const source=baselineFiles.has(rel)?execFileSync('git',['show',base+':'+rel],{cwd:root,encoding:'utf8',maxBuffer:20e6}):fs.readFileSync(file,'utf8');
 const compiled=ts.transpileModule(source,{fileName:file.endsWith('.mjs')?file.slice(0,-4)+'.js':file,compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true}}).outputText;
 const localRequire=id=>{
  if(!id.startsWith('.')&&!id.startsWith('@/'))return require(id);
  const start=id.startsWith('@/')?path.join(root,id.slice(2)):path.resolve(path.dirname(file),id);
  const target=[start,start+'.ts',start+'.tsx',start+'.json',path.join(start,'index.ts')].find(p=>fs.existsSync(p)&&fs.statSync(p).isFile());
  assert(target,'Resolve '+id);return baselineLoad(target);
 };
 new Function('require','module','exports',compiled)(localRequire,record,record.exports);return record.exports;
}
const metformin=content.guides.find(g=>g.slug==='/drugs/metformin');
const metforminSources=content.sources.filter(s=>metformin.sourceIds.includes(s.id));
const {Article:BaselineArticle}=baselineLoad(path.join(root,'components/article.tsx'));
const {ThemeProvider}=baselineLoad(path.join(root,'components/shared-theme/theme.tsx'));
const baselineMarkup=renderToStaticMarkup(React.createElement(ThemeProvider,{config:{mainId: "main",identity:{name:"Fixture",homeHref:"/"}}},React.createElement(BaselineArticle,{guide:metformin,sources:metforminSources})));
assert.equal(render(metformin,metforminSources),baselineMarkup,'Metformin full SSR markup is byte-identical to the original renderer');
console.log('PASS: Metformin full rendered markup is byte-identical to the original rendering implementation.');
