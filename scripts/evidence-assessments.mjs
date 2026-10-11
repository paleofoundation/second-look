import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';

export const METHOD = 'selected-source-editorial-v1';
export const DOMAIN_NAMES = ['Study methods', 'Directness', 'Precision', 'Consistency', 'Source integrity'];
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const canonical = value => Array.isArray(value) ? value.map(canonical) : value && typeof value === 'object'
  ? Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])])) : value;
export const digest = value => crypto.createHash('sha256').update(JSON.stringify(canonical(value))).digest('hex');

// Bind the judgment to both scientific inputs and their reader projection.
// A new result, correction, source, scope or visible finding requires reassessment.
export function assessmentFingerprint(row, sources, publicRow, publicSources) {
  return digest({row, publicRow, sources: row.sourceIds.map(id => sources.find(s => s.id === id)),
    publicSources: row.sourceIds.map(id => publicSources.find(s => s.id === id))});
}

export function compileAssessments({reader, content, publicReader, publicContent, assessments}) {
  assert.equal(assessments.method, METHOD, 'Use the versioned editorial grading method');
  const entries = new Map(assessments.records.map(record => [record.rowId, record]));
  assert.equal(entries.size, assessments.records.length, 'Duplicate outcome assessment');
  assert.equal(entries.size, reader.synthesisRows.length, 'Every outcome needs its own assessment; retire obsolete records explicitly');
  const records = reader.synthesisRows.map(row => {
    for (const field of ['drugId','conditionId','title','use','population','comparison','endpoint','timepoint']) {
      assert(typeof row[field] === 'string' && row[field].trim(), `Missing assessment scope ${field}: ${row.id}`);
    }
    assert(content.guides.some(g=>g.entityId===row.drugId && g.type==='Drug'), 'Unknown drug identity');
    assert(content.guides.some(g=>g.entityId===row.conditionId && g.type==='Condition'), 'Unknown condition identity');
    const a = entries.get(row.id);
    assert(a, `Missing source-backed assessment: ${row.id}`);
    const published = publicReader.synthesisRows.find(record => record.id === row.id);
    assert(published, `Missing reader outcome: ${row.id}`);
    assert.equal(a.inputSha256, assessmentFingerprint(row, content.sources, published, publicContent.sources), `Stale assessment: ${row.id}. Reassess changed evidence; never just refresh its hash.`);
    assert(['High', 'Moderate', 'Low'].includes(a.grade), `Invalid grade: ${row.id}`);
    assert(a.rationale?.trim().length >= 100, `Substantive outcome-specific rationale required: ${row.id}`);
    assert(/^\d{4}-\d{2}-\d{2}$/.test(a.assessedAt), 'Actual assessment date required');
    assert.deepEqual([...new Set(a.sourceIds)].sort(), [...new Set(row.sourceIds)].sort(), `Assessment must account for every selected source: ${row.id}`);
    const sources = a.sourceIds.map(id => content.sources.find(s => s.id === id));
    assert(sources.every(Boolean), 'Unknown assessment source');
    assert(!sources.some(s => /quarantin|retract|withdrawn/i.test(s.status || '')), 'Excluded reports cannot earn an evidence grade');
    assert(['clear','limited_access','correction_unresolved','preclinical_only'].includes(a.integrity), 'Explicit integrity judgment required');
    if (/hold/.test(row.status)) {
      assert.equal(a.integrity, 'correction_unresolved', 'Preserve correction hold');
      assert.equal(a.grade, 'Low', 'An unresolved correction cannot support elevated confidence');
    }
    if (row.status === 'computational_result') {
      assert.equal(a.integrity, 'preclinical_only');
      assert.equal(a.grade, 'Low', 'Computer predictions do not establish clinical benefit');
    }
    if (a.integrity === 'correction_unresolved') assert.equal(a.grade, 'Low', 'Unresolved corrections require limited confidence');
    if (a.grade === 'High') assert.equal(a.integrity, 'clear', 'High requires adequate accessible, intact evidence');
    assert.deepEqual(a.domains.map(d => d.name), DOMAIN_NAMES, 'Assess all five editorial domains in order');
    for (const domain of a.domains) {
      assert(domain.text?.trim().length >= 30, 'Explain each judgment; missing information is not low risk');
      assert(domain.sourceIds?.length && domain.sourceIds.every(id => a.sourceIds.includes(id)), 'Each judgment needs matching sources');
    }
    assert(a.basis?.length && a.sourceIds.every(id => a.basis.some(b => b.sourceId === id && b.locator?.trim())), 'Retain a locator for each supporting source');
    assert(a.basis.every(b => a.sourceIds.includes(b.sourceId)), 'Unknown basis source');
    return {rowId: row.id, label: a.grade, rationale: a.rationale, assessmentStatus: 'assessed',
      assessmentKind: METHOD, method: 'Selected-source editorial assessment · v1',
      scope: [content.guides.find(g=>g.entityId===row.drugId)?.title||row.drugId,
        content.guides.find(g=>g.entityId===row.conditionId)?.title||row.conditionId,
        row.use, row.population, row.route, row.formulation, row.comparison, row.endpoint, row.timepoint].filter(Boolean).join(' · '),
      assessedAt: a.assessedAt, sourceIds: a.sourceIds, domains: a.domains, basis: a.basis, integrity: a.integrity,
      reviewStatus: 'AI-assisted editorial assessment; independent clinical review has not been completed.'};
  });
  return {method: METHOD, records};
}

export function readAssessmentInputs() {
  const read = name => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
  return {reader: read('data/reader-evidence.json'), content: read('data/content.json'),
    publicReader: read('data/public-reader-evidence.json'), publicContent: read('data/public-content.json'),
    assessments: read('editorial/evidence-assessments.json')};
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const projection = compileAssessments(readAssessmentInputs());
  const output = JSON.stringify(projection, null, 2) + '\n';
  const destination = path.join(root, 'data/public-evidence-assessments.json');
  if (process.argv.includes('--write')) fs.writeFileSync(destination, output);
  else assert.equal(fs.readFileSync(destination, 'utf8'), output, 'Grading projection is stale; run node scripts/evidence-assessments.mjs --write after completing assessments');
  console.log(JSON.stringify({status:'PASS', method:METHOD, assessedOutcomes:projection.records.length,
    grades: Object.fromEntries(['High','Moderate','Low'].map(grade => [grade, projection.records.filter(r => r.label === grade).length]))}));
}
