import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import ts from 'typescript';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';

// Execute the real TS/TSX modules without adding a test-runner dependency.
const root = path.resolve(import.meta.dirname, '..');
const require = createRequire(import.meta.url);
const cache = new Map();
const publicMechanisms = JSON.parse(fs.readFileSync(path.join(root, 'data/public-mechanisms.json'), 'utf8'));
const mechanismFixture = {
  contexts: [],
  drugs: [{drugId: 'fixture-drug', guideIds: ['fixture-answer'],
    originalAction: {text: 'Original action.', sourceIds: ['original']},
    summary: {text: 'Mechanism summary.', sourceIds: ['summary']},
    questions: [{id: 'mechanism-question', title: 'What is the proposed action?',
      text: 'A source-specific proposed action.', sourceIds: ['mechanism-question'],
      sentences: [{text: 'A source-specific proposed action.', sources: ['mechanism-question', 'original']}]}]}],
};
function load(file) {
  if (cache.has(file)) return cache.get(file).exports;
  if (file.endsWith('.css')) return {};
  if (file.endsWith('/data/public-mechanisms.json')) return {
    ...publicMechanisms, drugs: [...(publicMechanisms.drugs || []), ...mechanismFixture.drugs],
  };
  if (file.endsWith('.json')) return JSON.parse(fs.readFileSync(file, 'utf8'));
  const compiledModule = {exports: {}};
  cache.set(file, compiledModule);
  const source = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
    fileName: file,
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022,
      jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true},
  }).outputText;
  const localRequire = id => {
    if (!id.startsWith('.') && !id.startsWith('@/')) return require(id);
    const base = id.startsWith('@/') ? path.join(root, id.slice(2)) : path.resolve(path.dirname(file), id);
    const target = [base, base + '.ts', base + '.tsx', base + '.json', path.join(base, 'index.ts')]
      .find(candidate => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
    assert(target, 'Cannot resolve ' + id + ' from ' + file);
    return load(target);
  };
  new Function('require', 'module', 'exports', source)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const {Article} = load(path.join(root, 'components/article.tsx'));
const {ThemeProvider} = load(path.join(root, 'components/shared-theme/theme.tsx'));
const {guideCitationOrder,articleSectionGroups,articleEvidenceSources,benefitQuestionPlan} = load(path.join(root, 'lib/citation-plan.ts'));
const {buildUniversalArticlePlan,universalArticlePlanErrors,isRetiredArticleSection} = load(path.join(root, 'components/shared-theme/universal-article.ts'));
const {drugMechanismFor,evidenceMechanismsFor,mechanismEvidenceHref} = load(path.join(root, 'lib/mechanisms.ts'));
const sourceIds = ['overview', 'original', 'summary', 'mechanism-question', 'benefits', 'benefit-question', 'faq'];
const sources = sourceIds.map(id => ({id, title: id + ' source', preview: 'Source finding.',
  url: 'https://example.org/' + id, sourceType: 'context', year: 2026}));
const guide = {id: 'fixture-guide', entityId: 'fixture-drug', slug: '/drugs/fixture', title: 'Fixture drug',
  description: 'Fixture description.', type: 'Drug', sourceIds: [...sourceIds].reverse(), topicIds: [], related: [],
  sections: [
    {id: 'overview', label: 'Overview', title: 'Overview findings', paragraph: 'Overview finding.', sources: ['overview']},
    {id: 'benefits', label: 'Benefits', title: '', paragraph: 'Benefits summary stays visible.', sources: ['benefits'],
      questions: [{id: 'benefit-question', question: 'Which outcome changed?', answer: 'The measured outcome.',
        sources: ['benefit-question'], sentences: [{text: 'The measured outcome.', sources: ['benefit-question', 'summary']}]}]},
  ],
  faqs: [{id: 'faq-one', question: 'What else was measured?', answer: 'Another reported outcome.', sources: ['faq']}],
};
const order = guideCitationOrder(guide, sources);
// Drug Benefits renders in Overview; uncovered Benefits questions render in FAQs.
const renderedOrder = ['overview', 'benefits', 'original', 'summary', 'mechanism-question', 'faq', 'benefit-question'];
assert.deepEqual(order, renderedOrder, 'New sources follow rendered prose and question order, not sourceIds order');
assert.equal(drugMechanismFor({...guide, id: 'fixture-answer', type: 'Drug–condition evidence answer', entityId: undefined})?.drugId, 'fixture-drug');
const config = {mainId: 'main', identity: {name: 'Fixture', homeHref: '/'}};
const render = (value, pageSources = sources) => renderToStaticMarkup(React.createElement(ThemeProvider, {config}, React.createElement(Article, {guide: value, sources: pageSources})));
const html = render(guide);
const article = html.match(/<article class="research-content__center entry-content">([\s\S]*?)<\/article>/)?.[1];
assert(article, 'The canonical article column renders');
const citations = [...article.matchAll(/<sup class="citation-sup" data-source-id="([^"]+)"[^>]*>[\s\S]*?\[(\d+)\]/g)];
assert.deepEqual([...new Set(citations.map(match => match[1]))], renderedOrder, 'Rendered first appearances match the registry');
for (const match of citations) assert.equal(Number(match[2]), order.indexOf(match[1]) + 1);
for (const id of ['mechanism-question', 'benefit-question']) {
  assert(article.includes('class="rgbc-faq-item" id="' + id + '"'), 'Question uses canonical native details: ' + id);
  assert(article.includes('id="source-ref-' + (id === 'benefit-question' ? 'benefit-question' : 'mechanism-question') + '"'));
}
assert(article.indexOf('Benefits summary stays visible.') < article.indexOf('<details class="rgbc-faq-item" id="benefit-question"'));
assert(!article.includes('<h3></h3>'), 'Blank section titles do not create headings');
assert.equal((article.match(/id="faqs"/g) || []).length, 1, 'Section questions do not create another FAQ module');
for (const text of ['Laboratory activity, a proposed pathway', 'A mechanism describes how', 'not yet available in this article',
  'Independent review incomplete', 'Scientific review pending', 'Interaction coverage', 'unchecked in this corpus',
  'No completed scientific review date']) assert(!html.includes(text), 'Generic workflow copy is absent: ' + text);
const missing = render({...guide, id: 'unknown', entityId: 'unknown', sections: [], faqs: []});
assert(missing.includes('id="mechanisms"'), 'Canonical mechanism anchor remains without invented answers');
assert(!missing.includes('Original action.'), 'An unrelated guide does not inherit another drug’s mechanism');
assert(!missing.includes('not yet available') && !missing.includes('FAQ coverage is incomplete'));
console.log('PASS: actual article SSR, prose and canonical accordions, mechanism scope, first-appearance citations, blank and missing content, and workflow-copy regression checks.');

// Relationship data is retained, but its retired article module must never be
// reassigned to Benefits/Options or enter the body/citation reading sequence.
const retiredSection = {id:'retired-connections',label:'Connections',title:'Connections',
 paragraph:'Retired relationship prose sentinel.',sources:['retired-only'],
 questions:[{id:'retired-question',question:'Retired relationship question?',answer:'Retired relationship answer sentinel.',sources:['retired-only']}]};
const retiredScoped = {...retiredSection,id:'retired-scoped-connections',label:' connections ',questions:[]};
const activeScoped = {id:'active-scoped',label:'Details',title:'Scoped evidence',paragraph:'Active scoped evidence sentinel.',sources:['scoped']};
const retirementSources = [...sources,...['retired-only','scoped'].map(id=>({id,title:id+' source',preview:'Source finding.',url:'https://example.org/'+id,sourceType:'context'}))];
for(const type of ['Drug','Condition','Explainer','Drug–condition evidence answer','Evidence comparison','Glossary','Study','Background source']){
 const fixture={...guide,type,sourceIds:[...guide.sourceIds,'scoped'],
  sections:[retiredSection,...guide.sections],scopedSections:[retiredScoped,activeScoped]};
 const snapshot=JSON.stringify(fixture);
 const groups=articleSectionGroups(fixture);
 assert(!Object.values(groups).flat().some(isRetiredArticleSection),type+': retired main/scoped sections excluded from render groups');
 const order=guideCitationOrder(fixture,retirementSources);
 assert(!order.includes('retired-only'),type+': retired section citations excluded from traversal');
 assert(order.includes('scoped'),type+': active scoped citation retained');
 if(type==='Drug'||type==='Condition'){
  const plan=buildUniversalArticlePlan(fixture);
  assert.deepEqual(universalArticlePlanErrors(fixture,plan),[],type+': retirement preserves active-section invariants');
  assert(!plan.modules.some(module=>module.label==='Connections'),type+': no Connections module');
  assert(!plan.navigation.some(item=>item.label==='Connections'),type+': no Connections navigation');
  assert(!plan.modules.flatMap(module=>[...module.sections,...(module.scoped?.sections||[])]).some(isRetiredArticleSection),type+': no fallback destination for retired sections');
  const retiredOnlyPlan=buildUniversalArticlePlan({...fixture,scopedSections:[retiredScoped]});
  assert(!retiredOnlyPlan.modules.some(module=>module.scoped),type+': no empty scoped wrapper after retirement');
 }
 const retiredHtml=render(fixture,retirementSources);
 assert(!retiredHtml.includes('Retired relationship prose sentinel.')&&!retiredHtml.includes('Retired relationship answer sentinel.'),type+': retired prose and questions absent from body');
 assert(!retiredHtml.includes('href="#retired-connections"')&&!retiredHtml.includes('href="#section-connections"'),type+': no retired navigation targets');
 assert(!retiredHtml.includes('data-universal-section="Connections"'),type+': no retired body module');
 assert(retiredHtml.includes('Active scoped evidence sentinel.'),type+': active scoped body remains');
 assert.equal(JSON.stringify(fixture),snapshot,type+': original relationship data remains intact');
}
console.log('PASS: Connections retired from all guide render groups, universal modules/navigation and main/scoped citation traversal; active content and legacy data preserved.');

// Run the same checks against the actual public Metformin content, not a fixture.
const {content,synthesisRows} = load(path.join(root, 'lib/content.ts'));
const metformin = content.guides.find(item => item.slug === '/drugs/metformin');
assert(metformin, 'The public Metformin profile exists');
const metforminSources = content.sources.filter(source => metformin.sourceIds.includes(source.id));
const metforminHtml = render(metformin, metforminSources);
const metforminArticle = metforminHtml.match(/<article class="research-content__center entry-content">([\s\S]*?)<\/article>/)?.[1];
assert(metforminArticle, 'The public Metformin article renders');
const textOf = html => html.replace(/<[^>]*>/g, '').replace(/&#x27;/g, "'").replace(/&quot;/g, '"')
  .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/\[\d+\]/g, '')
  .replace(/\s+/g, ' ').trim();
function assertMechanismLocations(profile, record, mechanismSection, page, pageSources) {
 const removedBlock=profile.id==='G-METFORMIN';
 if(removedBlock){
  for(const text of ['Rationale by condition','mechanism-evidence-links','mechanism-rationale-table','For treatment outcomes'])assert(!mechanismSection.includes(text),'Metformin removed rationale block: '+text);
 }
 const resolvedSources=articleEvidenceSources(profile,pageSources);
 const order=guideCitationOrder(profile,pageSources);
 for(const rationale of record.rationales||[]){
  const label=profile.slug+': '+rationale.id;
  assert(mechanismSection.includes('id="'+rationale.id+'"'),label+': legacy mechanism anchor remains usable');
  const evidenceHref=mechanismEvidenceHref(profile,rationale.id);
  let selected=rationale;
  if(evidenceHref){
   if(!removedBlock)assert(mechanismSection.includes('<span id="'+rationale.id+'"><a href="'+evidenceHref+'">'),label+': legacy anchor links to the matching evidence row');
   assert(page.includes('id="'+evidenceHref.slice(1)+'"'),label+': evidence destination renders');
   assert(!mechanismSection.includes('<tr role="row" id="'+rationale.id+'"'),label+': moved rationale does not remain in the main table');
   const row=synthesisRows.find(row=>row.id===evidenceHref.slice(1));
   assert(row,label+': destination is a canonical synthesis row');
   selected=evidenceMechanismsFor(row.drugId,row.conditionId).find(item=>item.id===rationale.id);
   assert(selected,label+': exact drug/condition drawer receives this rationale');
  }
  for(const field of ['rationale','tested','limits']){
   assert.deepEqual(selected[field],rationale[field],label+': '+field+' retains exact prose and sentence citations');
   for(const sentence of rationale[field].sentences||[]){
    if(!evidenceHref&&!removedBlock)assert(textOf(mechanismSection).includes(sentence.text),label+': unmapped rationale remains visible');
    for(const id of sentence.sources){
     assert(resolvedSources.some(source=>source.id===id),label+': mechanism source resolves '+id);
     assert(order.includes(id),label+': source retains a page citation number '+id);
     assert(page.includes('id="source-ref-'+encodeURIComponent(id)+'"'),label+': citation has a bibliography target '+id);
     if(!evidenceHref&&!removedBlock)assert(mechanismSection.includes('data-source-id="'+id+'"'),label+': retained rationale has rendered citations');
    }
   }
  }
 }
}
const mechanismHtml = metforminArticle.slice(metforminArticle.indexOf('<section id="mechanisms"'),
  metforminArticle.indexOf('id="section-safety"'));
const overviewHtml = metforminArticle.slice(metforminArticle.indexOf('id="section-overview"'), metforminArticle.indexOf('<section id="mechanisms"'));
const faqHtml = metforminArticle.slice(metforminArticle.indexOf('id="faqs"'), metforminArticle.indexOf('id="update-history"'));
const mechanism = drugMechanismFor(metformin);
assert(mechanism?.originalAction?.text, 'Metformin has a sourced original action');
assert(textOf(mechanismHtml).includes(mechanism.originalAction.sentences[0].text));
assert.equal((mechanismHtml.match(/<details\b/g) || []).length, 3, 'Metformin has three pathway disclosures');
assert(!/<details\b[^>]*\bopen(?:\s|=|>)/.test(mechanismHtml), 'Pathway disclosures start collapsed');
assert.equal(mechanism.pathways.length, 3, 'Metformin explains its three principal mechanism themes');
assert.equal(mechanism.rationales.length, 10, 'Metformin distinguishes mechanisms, measurements and limits across conditions');
assert.equal((mechanismHtml.split('class="rgbc-faq-block mechanism-pathway-disclosures"')[0].match(/<p(?:\s|>)/g) || []).length, 1, 'Mechanism introduction is one cohesive paragraph');
for (const pathway of mechanism.pathways) {
  assert(mechanismHtml.includes('id="' + pathway.id + '"'));
  assert(mechanismHtml.includes('<h3 class="rgbc-faq-q">' + pathway.title + '</h3>'), 'Pathway disclosure retains its declarative heading');
  for (const sentence of pathway.sentences || []) assert(textOf(mechanismHtml).includes(sentence.text));
}
assertMechanismLocations(metformin,mechanism,mechanismHtml,metforminHtml,metforminSources);
const benefits = metformin.sections.filter(section => section.label === 'Benefits');
assert.equal(benefits.length, 1, 'Benefits has one prose summary');
assert(!metforminArticle.includes('id="section-benefits"'), 'Benefits no longer renders as its own section');
for (const sentence of benefits[0].sentences || []) assert(textOf(overviewHtml).includes(sentence.text), 'Benefits summary renders inside Overview');
const benefitPlan = benefitQuestionPlan(metformin, (metformin.synthesisIds || []).map(id => synthesisRows.find(row => row.id === id)).filter(Boolean));
assert.equal(benefitPlan.moved.length + benefitPlan.dropped.length, benefits[0].questions.length);
for (const question of benefitPlan.moved) {
  assert(faqHtml.includes('id="' + question.id + '"'), question.id + ' moved into FAQs');
  for (const sentence of question.sentences || []) assert(textOf(faqHtml).includes(sentence.text), question.id + ' answer sentence is present');
}
for (const question of benefitPlan.dropped) assert(!metforminArticle.includes('id="' + question.id + '"'), question.id + ' covered elsewhere and not duplicated');
const text = textOf(metforminArticle);
for (const finding of ['lactic acidosis', 'vitamin B12', 'eGFR below 30', 'cimetidine', 'retraction and republication']) {
  assert(text.includes(finding), 'Useful safety and source-integrity information remains: ' + finding);
}
for (const rejected of ['A mechanism describes how a drug affects', 'A source-backed explanation of the drug',
  'A reviewed, condition-specific mechanism summary', 'Laboratory activity, a proposed pathway',
  'How to read the evidence across conditions', 'Safety and clinical interpretation remain incomplete',
  'This page does not provide a completed safety assessment', 'absence of a completed assessment is not reassurance']) {
  assert(!text.includes(rejected), 'Rejected copy is absent from the actual Metformin article: ' + rejected);
}
const ids = [...metforminHtml.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);
assert.equal(ids.length, new Set(ids).size, 'All rendered IDs are unique');
for (const href of ['#section-safety', '#faqs', '#section-evidence', '#references', '#mechanisms']) {
  assert(metforminHtml.includes('href="' + href + '"'), 'Navigation/action fragment is present: ' + href);
  assert(ids.includes(href.slice(1)), 'Navigation/action fragment resolves: ' + href);
}
const actualOrder = guideCitationOrder(metformin, metforminSources);
const actualCitations = [...metforminArticle.matchAll(/<sup class="citation-sup" data-source-id="([^"]+)"[^>]*>[\s\S]*?\[(\d+)\]/g)];
const firstAppearances = [...new Set(actualCitations.map(match => match[1]))];
assert.deepEqual(actualOrder.slice(0, firstAppearances.length), firstAppearances, 'Metformin first appearances follow the actual DOM order');
for (const match of actualCitations) {
  assert.equal(Number(match[2]), actualOrder.indexOf(match[1]) + 1);
  assert(ids.includes('source-ref-' + encodeURIComponent(match[1])), 'Every Metformin citation has its bibliography target');
}
assert.equal(metforminSources.length, metformin.sourceIds.length, 'Every declared Metformin source resolves');
console.log('PASS: public Metformin SSR; condition-specific mechanisms; visible benefits summary and accordions; safety and correction facts; unique IDs; action fragments; ' + firstAppearances.length + ' sequential, source-resolved first-appearance citations.');

if (process.argv.includes('--all-profiles')) {
 const profiles=content.guides.filter(g=>g.type==='Drug'||g.type==='Condition');
 const expectedProfiles=content.guides.filter(g=>g.slug.startsWith('/drugs/')||g.slug.startsWith('/conditions/'));
 assert.deepEqual(new Set(profiles.map(g=>g.slug)),new Set(expectedProfiles.map(g=>g.slug)),'Every drug/condition route participates in profile checks');
 assert(profiles.some(g=>g.slug==='/drugs/metformin')&&profiles.some(g=>g.slug==='/conditions/long-covid'),'Core drug and condition coverage remains present');
 let totalQuestions=0;
 for(const profile of profiles){
  const label=profile.slug;
  const required=profile.type==='Drug'?['Overview','Benefits','Safety','Contraindications','Interactions','Dosing','Results','Quality','Status','Evidence']:['Overview','Options','Evidence','Safety','Comparisons'];
  for(const name of required)assert(profile.sections.some(s=>s.label===name&&s.paragraph.trim().length>25),label+': substantive '+name+' prose');
  const opening=profile.sections.find(s=>s.label===(profile.type==='Drug'?'Benefits':'Options'));
  assert(opening.questions?.length,label+': specific benefit/option questions');
  assert(profile.faqs.length,label+': additional reader FAQs');
  const mechanism=drugMechanismFor(profile);
  assert((mechanism?.summary?.text || mechanism?.originalAction?.text)?.length>40,label+': explanatory mechanism prose');
  if(profile.type==='Drug')assert(mechanism.originalAction?.text?.length>30,label+': original pharmacological action');
  assert(mechanism.questions?.length || (mechanism.pathways?.length && mechanism.rationales?.length),label+': mechanism explanations');
  const pageSources=content.sources.filter(s=>profile.sourceIds.includes(s.id));
  assert.equal(pageSources.length,profile.sourceIds.length,label+': all sources resolve');
  const page=render(profile,pageSources);
  const center=page.match(/<article class="research-content__center entry-content">([\s\S]*?)<\/article>/)?.[1];
  assert(center,label+': article rendered');
  const plan=buildUniversalArticlePlan(profile);
  assert.deepEqual(universalArticlePlanErrors(profile,plan),[],label+': active section invariants');
  assert(!plan.modules.some(module=>module.label==='Connections')&&!plan.navigation.some(item=>item.label==='Connections'),label+': Connections module and navigation absent');
  assert(!center.includes('data-universal-section="Connections"')&&!page.includes('href="#section-connections"'),label+': Connections absent from rendered body and navigation');
  const overview=center.match(/data-universal-section="Overview">([\s\S]*?)<\/section><\/section>/)?.[1];
  assert(overview&&overview.includes('<h2>Overview</h2>'),label+': canonical Overview heading');
  assert(!overview.includes('<h3>'),label+': Overview has no duplicate authored question heading');
  const visible=textOf(center);
  assert(!/not yet available|not yet reviewed|source-backed explanation.*not|assessment remains incomplete|accepted record|in this corpus|full review pending|How to read the evidence across conditions|Laboratory activity, a proposed pathway|Scientific review pending/i.test(visible),label+': production placeholders cannot replace answers');
  const pageIds=[...page.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(pageIds.length,new Set(pageIds).size,label+': unique DOM IDs');
  for(const match of page.matchAll(/href="#([^"]+)"/g))assert(pageIds.includes(match[1]),label+': fragment '+match[1]+' resolves');
  const order=guideCitationOrder(profile,pageSources);
  const citations=[...center.matchAll(/<sup class="citation-sup" data-source-id="([^"]+)"[^>]*>[\s\S]*?\[(\d+)\]/g)];
  const first=[...new Set(citations.map(m=>m[1]))];
  assert.deepEqual(order.slice(0,first.length),first,label+': citation first appearance');
  for(const c of citations){assert.equal(+c[2],order.indexOf(c[1])+1,label+': sequential citation');assert(pageIds.includes('source-ref-'+encodeURIComponent(c[1])),label+': citation target');}
  const benefitPlan=benefitQuestionPlan(profile,synthesisRows.filter(row=>(profile.synthesisIds||[]).includes(row.id)));
  for(const section of profile.sections){
   if(section.sentences)assert.equal(section.sentences.map(s=>s.text.trim()).join(' '),section.paragraph.trim(),label+': section sentence map');
   for(const q of section.questions||[]){
    if(!isRetiredArticleSection(section)){
     const benefit=profile.type==='Drug'&&section.label==='Benefits';
     const covered=benefit&&benefitPlan.dropped.some(question=>question.id===q.id);
     if(!covered){
      assert(center.includes('class="rgbc-faq-item" id="'+q.id+'"'),label+': canonical question '+q.id);
      if(benefit)assert(center.indexOf('id="'+q.id+'"')>center.indexOf('id="faqs"'),label+': uncovered benefit question moved to FAQs');
      totalQuestions++;
     }
    }
    assert(q.answer.length>30&&q.sources.length,label+': sourced question answer');
    assert(q.sources.every(id=>profile.sourceIds.includes(id)),label+': question source closure');
   }
  }
  for(const p of [mechanism.originalAction,mechanism.summary,...(mechanism.questions||[]),...(mechanism.pathways||[]),...(mechanism.rationales||[]).flatMap(row=>[row.rationale,row.tested,row.limits])].filter(Boolean))assert(p.sourceIds.length&&p.sourceIds.every(id=>profile.sourceIds.includes(id)),label+': mechanism source closure');
  totalQuestions+=(mechanism.questions||[]).length+profile.faqs.length;
 }
 console.log(JSON.stringify({status:'PASS',profiles:profiles.length,questions:totalQuestions,checks:'Every canonical content section populated; actual SSR; no production placeholders; unique IDs; all fragments; canonical questions; source closure; citation order'}));
}

// Itraconazole retains its pathways and unmapped rationale in the article; moved
// condition explanations preserve exact sentence/source records in the drawer.
const pilot = content.guides.find(g=>g.slug==='/drugs/itraconazole');
const pilotRecord = drugMechanismFor(pilot);
const pilotSources = content.sources.filter(s=>pilot.sourceIds.includes(s.id));
const pilotHtml = render(pilot, pilotSources);
const pilotSection = pilotHtml.match(/<section id="mechanisms"[\s\S]*?<\/section>/)[0];
assert(!pilotSection.includes('<details'), 'Pilot mechanisms are visible without opening disclosures');
assert.equal((pilotSection.match(/role="rowheader"/g)||[]).length,pilotRecord.rationales.filter(row=>!mechanismEvidenceHref(pilot,row.id)).length,'Only rationales without evidence rows remain in the article table');
assert.equal((pilotSection.match(/class="mechanism-pathway"/g)||[]).length,2,'Two shared pathway explanations');
assert(pilotSection.indexOf('hedgehog-cellular')<pilotSection.indexOf('condition-rationales'),'Shared pathways precede condition table');
for(const id of ['ovarian','prostate','lung','colorectal','pancreatic','melanoma','bcc','aml','myeloma','hedgehog-cellular','cholesterol-transport']) assert(pilotSection.includes('id="'+id+'"'),'Legacy mechanism fragment survives: '+id);
assertMechanismLocations(pilot,pilotRecord,pilotSection,pilotHtml,pilotSources);
for(const prose of [pilotRecord.originalAction,...pilotRecord.pathways,...pilotRecord.rationales.flatMap(row=>[row.rationale,row.tested,row.limits])]) {
 assert.equal(prose.sentences.map(sentence=>sentence.text).join(' '),prose.text,'Pilot sentence mapping');
 assert.deepEqual(new Set(prose.sentences.flatMap(sentence=>sentence.sources)),new Set(prose.sourceIds),'Pilot citation mapping');
}
assert.deepEqual(publicMechanisms.drugs.filter(record=>record.presentation==='pathway-table-pilot').map(record=>record.drugId).sort(),['D01','D07'],'Mechanism tables are limited to the two user-authorized pilots');
console.log('PASS: itraconazole pathways, mapped drawer rationale, retained preclinical rows, eleven legacy fragments and source closure.');

// Reuse the real-module loader and SSR host in the Evidence composition checks.
// No test-only renderer or scientific data projection should stand in for Article.
export {load, render};
