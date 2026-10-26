import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import ts from 'typescript';
const root=path.resolve(import.meta.dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
function load(file){
 const module={exports:{}};
 const source=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,esModuleInterop:true}}).outputText;
 new Function('require','module','exports',source)(id=>{assert.equal(id,'@/data/outcome-summaries.json');return read('data/outcome-summaries.json');},module,module.exports);
 return module.exports;
}
const stable=x=>Array.isArray(x)?x.map(stable):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,stable(x[k])])):x;
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(stable(x))).digest('hex');
const raw=read('data/reader-evidence.json').synthesisRows;
const projected=read('data/public-reader-evidence.json').synthesisRows;
const sources=read('data/public-content.json').sources;
const prior=read('editorial/evidence-assessments.json').records;
const data=read('data/outcome-summaries.json');
const provenance=read('editorial/outcome-summary/assessments.json').records;
const authored=read('editorial/outcome-summary/authored.json');
const identities=read('editorial/outcome-summary/trial-identities.json').trials;
const index=(values,key)=>new Map(values.map(v=>[v[key],v]));
const rows=index(raw,'id'),publicRows=index(projected,'id'),sourceIndex=index(sources,'id'),priorIndex=index(prior,'rowId'),proof=index(provenance,'id'),authorIndex=index(authored,'id'),trialIndex=index(identities,'id');
const inputsFor=record=>{const member=record.synthesisIds.map(id=>rows.get(id));const sourceIds=[...new Set(member.flatMap(r=>r.sourceIds))];return {rows:member,publicRows:record.synthesisIds.map(id=>publicRows.get(id)),priorAssessments:record.synthesisIds.map(id=>priorIndex.get(id)),sources:sourceIds.map(id=>sourceIndex.get(id))};};
function validate(record){
 assert(record.id&&record.label&&record.aggregationNote,'Missing summary identity/meaning');
 assert(record.synthesisIds.length>0&&new Set(record.synthesisIds).size===record.synthesisIds.length,'Duplicate or missing members');
 const member=record.synthesisIds.map(id=>{assert(rows.has(id),'Unknown synthesis');return rows.get(id);});
 assert(member.every(r=>r.drugId===record.drugId&&r.conditionId===record.conditionId),'Cannot merge distinct drugs or conditions');
 assert.deepEqual(record.sourceIds,[...new Set(member.flatMap(r=>r.sourceIds))],'Summary support must exactly preserve member sources');
 assert.deepEqual(record.grade.sourceIds,record.sourceIds,'Grade citations match all assessed sources');
 assert(['A','B','C','D','E','F',null].includes(record.grade.value),'Unsupported letter');
 assert(record.grade.rationale.length>70&&record.effect.rationale.length>50,'Missing substantive assessment');
 assert(record.effect.label&&record.effect.detail&&['benefit','harm','mixed','uncertain','not_applicable'].includes(record.effect.direction),'Missing separate effect interpretation');
 if(member.some(r=>r.status==='provisional_correction_hold'||r.status==='held'||r.status==='computational_result')||member.some(r=>priorIndex.get(r.id)?.integrity==='unresolved_correction'))assert.equal(record.grade.value,null,'A source hold or computational result cannot become an efficacy letter');
 if(record.grade.value==='F')assert(record.evidence.rctCount>0,'Missing research cannot become F');
 assert.equal(record.evidence.rctCount,record.evidence.trials.length,'RCT count is unique families');
 assert.equal(new Set(record.evidence.trialFamilyIds).size,record.evidence.rctCount,'Duplicate trial family');
 assert.deepEqual(record.evidence.trialFamilyIds,record.evidence.trials.map(t=>t.id),'Family count mapping');
 for(const trial of record.evidence.trials){
  const canonical=trialIndex.get(trial.id);assert(canonical,'Unknown trial identity');
  const denominator=trial.comparisonId?canonical.comparisons?.[trial.comparisonId]:canonical;
  assert(denominator,'Unknown trial comparison');
  if(trial.comparisonId){
   assert.equal(denominator.drugId,record.drugId,'Trial comparison belongs to another drug');
   assert(record.synthesisIds.every(id=>denominator.synthesisIds.includes(id)),'Trial comparison scope mismatch');
  }
  assert.equal(trial.participants,denominator.participants,'Unreviewed participant denominator');
  assert.equal(trial.participantBasis,denominator.participantBasis,'Unreviewed denominator basis');
  assert(trial.participants===null||Number.isInteger(trial.participants)&&trial.participants>0,'Unknown count is null, never zero');
  assert(trial.sourceIds.length&&trial.sourceIds.every(id=>record.sourceIds.includes(id)&&canonical.sourceIds.includes(id)&&denominator.sourceIds.includes(id)),'Trial support escapes this outcome');
 }
 const complete=record.evidence.trials.length>0&&record.evidence.trials.every(t=>t.participants!==null);
 assert.equal(record.evidence.participants,complete?record.evidence.trials.reduce((n,t)=>n+t.participants,0):null,'Unknown or repeated denominator');
 assert.deepEqual(record.evidence.sourceIds,[...new Set(record.evidence.trials.flatMap(t=>t.sourceIds))],'Evidence source mismatch');
 const p=proof.get(record.id),a=authorIndex.get(record.id);assert(p&&a,'Missing authored provenance');
 assert.equal(hash(inputsFor(record)),p.inputsSha256,'Changed evidence requires actual reassessment');
 assert.equal(a.assessedInputSha256,p.inputsSha256,'Compiler must not refresh a stale evidence fingerprint');
 assert.equal(hash(record),p.publicRecordSha256,'Public projection differs from assessed record');
 assert(p.sourceLocators.length&&record.sourceIds.every(id=>p.sourceLocators.some(b=>b.sourceId===id&&b.locator)),'Every source needs a real retained locator');
 assert.equal(p.humanApproval,'not recorded','No invented human approval');
 if(a.assessedOn){assert.equal(p.assessedOn,a.assessedOn);assert.equal(record.assessedOn,a.assessedOn,'New assessment date must not inherit a historical date');}
}
assert.equal(data.method,'selected-source-benefit-v1');
assert.equal(new Set(data.records.map(r=>r.id)).size,data.records.length);
for(const record of data.records)validate(record);
const mapped=data.records.flatMap(r=>r.synthesisIds);
assert.equal(new Set(mapped).size,mapped.length,'An original synthesis is represented once');
assert.deepEqual([...mapped].sort(),raw.map(r=>r.id).sort(),'Every original synthesis is preserved');
assert.deepEqual(provenance.map(r=>r.id),data.records.map(r=>r.id));
const {outcomeSummariesFor,outcomeSummaryFor,evidenceForSummaries}=load(path.join(root,'lib/outcome-summary.ts'));
assert.equal(outcomeSummariesFor(raw).length,data.records.length);
for(const row of raw)assert(outcomeSummaryFor(row.id)?.synthesisIds.includes(row.id));
const longCovid=outcomeSummariesFor(raw.filter(r=>r.drugId==='D01'&&r.conditionId==='C01'));
assert.equal(longCovid.length,3,'Diagnosis, symptoms and established-treatment recovery stay separate');
assert.equal(evidenceForSummaries(longCovid).rctCount,3,'ACTIV-6 repeated endpoints do not count twice');
assert.equal(evidenceForSummaries(longCovid).participants,1431+3214+264,'Reconciled trial populations count once');
assert.equal(evidenceForSummaries(outcomeSummariesFor(raw.filter(r=>r.drugId==='D03'&&r.conditionId==='C01'))).participants,155+964);
const lung=outcomeSummaryFor('SYN-D07-C14-COND-C14-ITRA-2013');
assert.equal(lung.synthesisIds.length,2);assert.equal(lung.evidence.rctCount,1);assert.equal(lung.evidence.participants,23);
const ms=outcomeSummaryFor('SYN-D16-C27-COND-C27-MINOCIS-2017');assert.equal(ms.synthesisIds.length,2);assert.equal(ms.evidence.participants,142);
const duplicate=structuredClone(lung);duplicate.evidence.trials[0].sourceIds=duplicate.evidence.trials[0].sourceIds.slice(0,1);
assert.equal(evidenceForSummaries([lung,duplicate]).rctCount,1);
assert.equal(evidenceForSummaries([lung,duplicate]).participants,23);
const conflicting=structuredClone(lung);conflicting.evidence.trials[0].participants=24;
assert.equal(evidenceForSummaries([lung,conflicting]).participants,null,'Conflicting denominator cannot use last value');
assert.deepEqual(evidenceForSummaries([lung,conflicting]),evidenceForSummaries([conflicting,lung]),'Conflicting count is order independent');
assert.deepEqual(evidenceForSummaries([lung]),lung.evidence,'Singleton retains exact denominator explanation');
assert.equal(evidenceForSummaries([]).participants,null,'No trial is not zero participants');
const held=structuredClone(data.records[0]);held.grade.value='F';assert.throws(()=>validate(held),/hold|computational/);
const stale=structuredClone(data.records[1]);stale.effect.detail='invented effect';assert.throws(()=>validate(stale),/projection differs/);
const missing=structuredClone(lung);missing.sourceIds=[];assert.throws(()=>validate(missing),/support/);
const wrongCount=structuredClone(lung);wrongCount.evidence.participants=46;assert.throws(()=>validate(wrongCount),/denominator/);
// Exact new comparison bases stay within the shared factorial family.
const fluvox=outcomeSummaryFor('SYN-FILL2-D02-COVIDOUT-COMPOSITE');
const ivermectin=outcomeSummaryFor('SYN-FILL2-D08-COVIDOUT-COMPOSITE');
assert.equal(fluvox.evidence.participants,661);assert.equal(ivermectin.evidence.participants,808);
assert.equal(fluvox.evidence.trials[0].id,ivermectin.evidence.trials[0].id);
assert.equal(evidenceForSummaries([fluvox,ivermectin]).rctCount,1);
assert.equal(evidenceForSummaries([fluvox,ivermectin]).participants,null,'Overlapping distinct comparison sets are not additive');
const pearl=['SYN-FILL2-D06-AGING-VAT','SYN-FILL2-D06-AGING-LEAN'].map(outcomeSummaryFor);
assert.equal(evidenceForSummaries(pearl).rctCount,1);assert.equal(evidenceForSummaries(pearl).participants,125);
for(const summary of [...pearl,fluvox,ivermectin])assert.equal(summary.assessedOn,'2026-10-26');
for(const mutate of [
 r=>r.evidence.trials[0].comparisonId='unknown',
 r=>{r.evidence.trials[0].comparisonId='D08';r.evidence.trials[0].participants=808;},
 r=>r.evidence.trials[0].participants=1431,
 r=>r.evidence.trials[0].participantBasis='Invented same-trial population',
 r=>r.assessedOn='2026-10-12',
]){const fixture=structuredClone(fluvox);mutate(fixture);assert.throws(()=>validate(fixture),'Reject wrong comparison, denominator or backdate');}
console.log(JSON.stringify({status:'PASS',syntheses:raw.length,summaries:data.records.length,uniqueRCTs:identities.length,missingRCTParticipantCounts:identities.filter(t=>t.participants===null).length,letters:Object.fromEntries(['A','B','C','D','E','F','ungraded'].map(g=>[g,data.records.filter(r=>(r.grade.value??'ungraded')===g).length])),longCovidMetformin:evidenceForSummaries(longCovid),checks:['source and row closure','explicit source-located assessments','stale input and projection rejection','held/computational grade rejection','overlap-aware trial and participant totals','conflicting denominator rejection','unknown is null','single-summary explanation preserved']},null,2));
