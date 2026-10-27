import assert from 'node:assert/strict';
import test from 'node:test';
import {auditRepository, buildCoverage, citationReferences, classifySource, loadContracts, resolveAlias} from '../scripts/research-review-coverage.mjs';

const actualContracts = loadContracts();
const contracts = {...actualContracts, guideCitationOrder: guide => guide.sourceIds || [], mechanismCitationIds: () => []};
const source = (id, sourceType = 'primary', extra = {}) => ({id, sourceType, title: `Source ${id}`, ...extra});
const guide = ids => ({id: 'G1', slug: '/drugs/test', type: 'Drug', sourceIds: ids, sections: [], faqs: [], synthesisIds: []});
function input(sources, guides = [guide(['P1'])]) {
  return {canonical: {sources, guides, glossary: []}, publicContent: {sources, guides, glossary: []}, reviews: {}, envelopes: {}, aliases: {}, reader: {synthesisRows: []}};
}
function review(id = 'P1', missingness = 'not_reported') {
  return {id, version: 'v1', sourceIds: [id], contentSha256: '', sections: [{id: 'summary', title: 'Summary', paragraph: 'PRIVATE-REVIEW-SENTINEL', sources: [id]}],
    questionAnswers: Array.from({length: 15}, (_, index) => ({id: `Q${String(index + 1).padStart(2, '0')}`, question: 'What did the inspected report provide?', answer: 'PRIVATE-ANSWER-SENTINEL: The inspected methods do not report this item.', status: 'complete', sources: [id], locators: [{sourceId: id, source_url: 'https://example.org/paper', section: 'Methods', basis: 'full_text', missingness}], render: {section: 'summary', fragment: `q${index + 1}`}})),
    openingBlocks: ['what-was-studied', 'who-was-studied', 'important-findings', 'implications'].map(id => ({id, title: 'Opening question', questionIds: ['Q01']}))};
}

test('classification does not use CONTEXT tier to exempt scholarly reviews', () => {
  assert.equal(classifySource(source('R', 'review', {sourceTier: 'CONTEXT'})).kind, 'scholarly_paper');
  assert.equal(classifySource(source('T', 'textbook')).kind, 'scholarly_book_chapter');
  assert.equal(classifySource(source('F', 'context', {design: 'Official US product label'})).kind, 'nonresearch');
  assert.equal(classifySource(source('U', 'context')).kind, 'unclassified');
  assert.equal(classifySource(source('PROTOCOL', 'context', {design: 'Trial protocol'})).kind, 'unclassified');
});

test('canonical obligations unite FAQ, evidence, glossary, review and aliases without counting catalogue-only sources', async () => {
  const sources = [source('P1'), source('P2'), source('P3', 'review'), source('UNUSED'), source('OFFICIAL', 'context', {design: 'Official condition information'})];
  const g = {...guide(['P1', 'P2', 'OFFICIAL']), faqs: [{question: 'A question', sources: ['P2']}], synthesisIds: ['S1']};
  const data = input(sources, [g]);
  data.publicContent.glossary = [{slug: 'term', sources: ['P3']}];
  data.reader.synthesisRows = [{id: 'S1', sourceIds: ['P2'], finding: {sources: ['P2']}}];
  data.aliases = {OLD: 'P1'};
  data.reviews = {OLD: review('OLD'), P1: review('P1')};
  const output = await buildCoverage(data, contracts);
  assert.equal(output.counts.scholarlyPapers, 3);
  assert.equal(output.records.filter(record => record.paperId === 'P1').length, 1);
  assert.deepEqual(output.records.find(record => record.paperId === 'P1').legacyReviewShadows, ['OLD']);
  assert.deepEqual(output.unreferencedSourceIds, ['UNUSED']);
  assert.equal(output.records.find(record => record.paperId === 'P2').publicCited, true);
  assert(!JSON.stringify(output).includes('PRIVATE-ANSWER-SENTINEL'));
  assert(!JSON.stringify(output).includes('PRIVATE-REVIEW-SENTINEL'));
});

test('unresolved types and missing references keep denominator provisional', async () => {
  const data = input([source('P1'), source('UNKNOWN', 'context')], [guide(['P1', 'UNKNOWN', 'ABSENT'])]);
  const output = await buildCoverage(data, contracts);
  assert.equal(output.denominatorStatus, 'provisional_unresolved_classification_or_identity');
  assert.deepEqual(output.unresolvedClassificationIds, ['ABSENT', 'UNKNOWN']);
  assert(output.issues.some(issue => issue.type === 'missing_canonical_source'));
});

test('shared textbook DOI is not a paper merge, but duplicate paper DOI remains unresolved', async () => {
  const data = input([source('A', 'textbook', {doi: '10.1/book'}), source('B', 'textbook', {doi: '10.1/book'}), source('P1', 'primary', {doi: '10.2/report'}), source('P2', 'primary', {doi: 'https://doi.org/10.2/report'})], [guide(['A', 'B', 'P1', 'P2'])]);
  const output = await buildCoverage(data, contracts);
  const duplicates = output.issues.filter(issue => issue.type === 'unreconciled_paper_identity');
  assert.equal(duplicates.length, 1);
  assert.deepEqual(duplicates[0].sourceIds, ['P1', 'P2']);
});

test('known not-reported fields can be structurally complete; unchecked source inputs cannot', async () => {
  const data = input([source('P1')]);
  data.reviews.P1 = review();
  data.reviews.P1.contentSha256 = await actualContracts.protectedReviewSha256(data.reviews.P1);
  data.envelopes.P1 = {preview: {id: 'P1', version: 'v1', sourceIds: ['P1'], reviewState: 'pending'}, release: {state: 'pending', version: 'v1', contentSha256: data.reviews.P1.contentSha256, approvedSha256: null, humanEditorialApproved: false, clinicalSafetyReviewRequired: true, qualifiedClinicalApproval: false}};
  let output = await buildCoverage(data, contracts);
  assert.equal(output.records[0].structurallyComplete, true);
  assert.equal(output.records[0].releasedAndGateEligible, false);
  assert.deepEqual(output.records[0].questionCoverage[0].missingness, ['not_reported']);
  data.reviews.P1.questionAnswers[0].locators[0].missingness = 'not_checked';
  output = await buildCoverage(data, contracts);
  assert.equal(output.records[0].structurallyComplete, false);
  assert.equal(output.records[0].reviewContentHashMatches, false);
  data.reviews.P1.questionAnswers = data.reviews.P1.questionAnswers.slice(1);
  output = await buildCoverage(data, contracts);
  assert.equal(output.records[0].questionCoverage[0].status, 'absent');
});

test('retired section refs are skipped and source-alias cycles fail closed', () => {
  assert.deepEqual(citationReferences({label: 'Connections', sources: ['OLD']}, '', {skipRetired: true}), []);
  assert.throws(() => resolveAlias('A', {A: 'B', B: 'A'}), /cycle/);
});

test('repository audit preserves the established CTX alias and uses the real access contract', async () => {
  const ledger = await auditRepository();
  const alias = ledger.aliasRoutes.find(entry => entry.alias === 'CTX-GUIDE-3');
  assert.equal(alias.canonicalId, 'CTX-off-label-1');
  assert.equal(alias.status, 'redirect_to_canonical_route');
  assert.equal(ledger.records.filter(record => record.paperId === 'CTX-off-label-1').length, 1);
  assert(!ledger.records.some(record => record.paperId === 'CTX-GUIDE-3'));
  assert(ledger.inputHashes['lib/review-access.ts']);
  for (const record of ledger.records) assert.equal(record.questionCoverage.length, 15);
});
