import fs from 'node:fs';
import assert from 'node:assert/strict';
const data=JSON.parse(fs.readFileSync('data/content.json','utf8'));
const reader=JSON.parse(fs.readFileSync('data/reader-evidence.json','utf8'));
const sources=new Map(data.sources.map(s=>[s.id,s]));
const guides=new Map(data.guides.map(g=>[g.id,g]));
const parents=new Map(data.guides.filter(g=>g.entityId).map(g=>[g.entityId,g]));
const rows=new Map(reader.synthesisRows.map(r=>[r.id,r]));
function checkRow(row){
 assert.equal(row.certainty.label,'Not appraised','No formal grade authorized');
 assert.equal(row.coverage.complete,false,'Incomplete body must not claim complete');
 assert.equal(row.publicationState,'private_ai_draft');
 assert(!row.sourceIds.includes('P-REVIVE-2026'),'Quarantined report cannot support efficacy');
 for(const id of row.sourceIds)assert(sources.has(id),'Unknown source');
 if(row.status==='background_only'){assert.equal(row.countsAsPrimaryEvidence,false);assert.equal(row.effects.length,0);assert.equal(row.studyFamilyIds.length,0);assert.equal(row.resultIds.length,0)}
 for(const effect of row.effects){assert(row.sourceIds.includes(effect.sourceId));if(effect.value===null)assert(effect.missingReason||effect.uncertainty.missing_reason||effect.recordedResult,'Missing effect must have a reason')}
 for(const id of [row.drugId,row.conditionId])assert(parents.get(id)?.synthesisIds.includes(row.id),'Parent must reuse exact row');
}
assert.equal([...parents.values()].filter(g=>g.type==='Drug').length,30);assert.equal([...parents.values()].filter(g=>g.type==='Condition').length,30);
for(const g of guides.values()){
 const used=[...g.sections.flatMap(s=>[...s.sources,...(s.sentences||[]).flatMap(v=>v.sources)]),...g.faqs.flatMap(f=>[...f.sources,...(f.sentences||[]).flatMap(v=>v.sources)])];
 for(const rid of g.synthesisIds||[]){const row=rows.get(rid);assert(row);used.push(...row.sourceIds)}
 for(const id of used)assert(g.sourceIds.includes(id)&&sources.has(id),'Unrenderable citation '+g.id+':'+id);
 for(const link of g.candidateLinks||[])assert([...parents.values()].some(p=>p.slug===link.url),'Unknown reciprocal parent');
}
for(const row of rows.values())checkRow(row);
const negative=[];
for(const [name,mutate] of [['invented grade',r=>r.certainty.label='High'],['false completion',r=>r.coverage.complete=true],['quarantined source',r=>r.sourceIds.push('P-REVIVE-2026')],['unknown source',r=>r.sourceIds.push('missing')],['unapproved release',r=>r.publicationState='public']]){const fixture=structuredClone(reader.synthesisRows[1]);mutate(fixture);assert.throws(()=>checkRow(fixture));negative.push(name)}
const bg=structuredClone(reader.synthesisRows.find(r=>r.status==='background_only'));bg.countsAsPrimaryEvidence=true;assert.throws(()=>checkRow(bg));negative.push('background inflated to primary');
assert(data.guides.find(g=>g.entityId==='D07').synthesisIds.length>0);
const report={status:'PASS',drugParents:30,conditionParents:30,sharedRows:rows.size,backgroundRows:reader.synthesisRows.filter(r=>r.status==='background_only').length,reciprocalLinks:[...parents.values()].reduce((n,g)=>n+(g.candidateLinks||[]).length,0),checks:'Reader FK closure, sentence/source closure, same row reused on both parents, exact tier and approval boundaries, all target routes',negativeCasesRejected:negative};
console.log(JSON.stringify(report));
