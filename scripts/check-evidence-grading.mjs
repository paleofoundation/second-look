import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {compileAssessments,readAssessmentInputs,assessmentFingerprint} from './evidence-assessments.mjs';
import {load} from './check-reader-sections.mjs';

const inputs=readAssessmentInputs();
const projection=compileAssessments(inputs);
assert.deepEqual(projection,JSON.parse(fs.readFileSync('data/public-evidence-assessments.json','utf8')));
const {synthesisRows,content}=load(path.resolve('lib/content.ts'));
const {describeEvidenceConfidence}=load(path.resolve('components/shared-theme/evidence-confidence.ts'));
for(const row of synthesisRows){
 const confidence=describeEvidenceConfidence({...row,background:!row.countsAsPrimaryEvidence,limits:row.limitations.map(l=>({text:l.text,sourceIds:l.sources})),pending:row.coverage.pending},content.sources);
 assert.equal(confidence.category,'assessed',row.id+': completed assessment reaches every renderer');
 assert.equal(confidence.label,row.certainty.label);
 assert(row.certainty.rationale.length>100);
}
const rejected=[];
for(const [name,mutate] of [
 ['missing outcome',i=>i.assessments.records.pop()],
 ['duplicate assessment',i=>i.assessments.records.push(i.assessments.records[0])],
 ['changed source',i=>i.content.sources.find(s=>s.id===i.reader.synthesisRows[0].sourceIds[0]).preview+=' Changed evidence.'],
 ['changed reader finding',i=>i.publicReader.synthesisRows[0].finding.text+=' Changed conclusion.'],
 ['changed outcome scope',i=>i.reader.synthesisRows[0].timepoint='A different follow-up'],
 ['missing outcome scope',i=>{const r=i.reader.synthesisRows[0];r.population='';i.assessments.records.find(a=>a.rowId===r.id).inputSha256=assessmentFingerprint(r,i.content.sources,i.publicReader.synthesisRows[0],i.publicContent.sources)}],
 ['missing rationale',i=>i.assessments.records[0].rationale=''],
 ['missing domain',i=>i.assessments.records[0].domains.pop()],
 ['unrelated citation',i=>i.assessments.records[0].domains[0].sourceIds=['unknown']],
 ['unknown grade',i=>i.assessments.records[0].grade='A+'],
 ['correction upgraded',i=>i.assessments.records.find(a=>a.integrity==='correction_unresolved').grade='High'],
 ['computational upgraded',i=>i.assessments.records.find(a=>a.integrity==='preclinical_only').grade='High'],
 ]){const fixture=structuredClone(inputs);mutate(fixture);assert.throws(()=>compileAssessments(fixture),name);rejected.push(name)}
// Even a fresh fingerprint must not let quarantined reports support a grade.
const quarantine=structuredClone(inputs),row=quarantine.reader.synthesisRows[0];
quarantine.content.sources.find(s=>s.id===row.sourceIds[0]).status='Quarantined';
quarantine.assessments.records.find(a=>a.rowId===row.id).inputSha256=assessmentFingerprint(row,quarantine.content.sources,quarantine.publicReader.synthesisRows[0],quarantine.publicContent.sources);
assert.throws(()=>compileAssessments(quarantine));rejected.push('quarantined source');
assert.deepEqual(compileAssessments(inputs),projection,'Repeat generation is deterministic');
console.log(JSON.stringify({status:'PASS',outcomes:projection.records.length,rejected,repeatGeneration:'PASS'}));
