import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';

const file = path.resolve(import.meta.dirname, '../lib/study-review-plan.ts');
const compiled = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
  compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022},
}).outputText;
const module = {exports: {}};
// This pure presentation module has type-only imports and needs no app runtime.
new Function('module', 'exports', compiled)(module, module.exports);
const {STUDY_OPENING_QUESTIONS, STUDY_DETAIL_SECTIONS, buildStudyReviewPlan} = module.exports;

const questionIds = Array.from({length: 15}, (_, index) => `Q${String(index + 1).padStart(2, '0')}`);
assert.deepEqual(STUDY_DETAIL_SECTIONS.flatMap(section => section.questionIds).toSorted(), questionIds,
  'Each Q01–Q15 has exactly one detailed destination');
assert.deepEqual(STUDY_OPENING_QUESTIONS.map(block => block.id),
  ['what-was-studied', 'who-was-studied', 'important-findings', 'implications']);

const review = {
  id: 'fixture-review', version: 'fixture-v1', contentSha256: 'unchanged-approved-hash',
  sourceIds: ['paper-b', 'paper-a', 'paper-c'],
  sections: [],
  questionAnswers: questionIds.map((id, index) => ({
    id, question: `Existing question ${id}`, answer: `Existing answer ${id}.`, status: 'complete',
    sources: [index % 2 ? 'paper-a' : 'paper-b', 'paper-c'], locators: [{sourceId: 'paper-b', section: 'Results'}],
    render: {section: 'summary', fragment: `existing-${id.toLowerCase()}`},
  })),
  openingBlocks: [
    {id: 'what-was-studied', title: 'Authored opening question', questionIds: ['Q02', 'Q01']},
    {id: 'who-was-studied', title: 'Authored population question', questionIds: ['Q02', 'Q07']},
    {id: 'important-findings', title: 'Authored findings question', questionIds: ['Q05', 'Q06', 'Q08']},
    {id: 'implications', title: 'Authored implications question', questionIds: ['Q09', 'Q10', 'Q14', 'Q15']},
  ],
};
const before = JSON.stringify(review);
const plan = buildStudyReviewPlan(review);
assert.equal(plan.openings[0].title, 'Authored opening question');
assert.deepEqual(plan.openings[0].answers.map(answer => answer.id), ['Q02', 'Q01']);
assert.deepEqual(plan.openings[1].answers.map(answer => answer.id), ['Q02', 'Q07']);
assert.deepEqual(plan.sections.flatMap(section => section.answers.map(answer => answer.id)).toSorted(), questionIds);
const renderedCitations = [...new Set([...plan.openings, ...plan.sections]
  .flatMap(block => block.answers.flatMap(answer => answer.sources)))];
assert.deepEqual(plan.citations, renderedCitations, 'Citations follow the returned rendering plan');
assert.deepEqual(plan.citations, ['paper-a', 'paper-c', 'paper-b'], 'Authored opening order controls first appearances');
assert.equal(plan.sections[0].answers[0], review.questionAnswers[0], 'Answers keep canonical object identity');
assert.equal(plan.sections[0].answers[0].render.fragment, 'existing-q01', 'Existing question fragment is preserved');
assert.equal(JSON.stringify(review), before, 'Building a presentation cannot alter the review or its hash');

const sparseReview = {...review, questionAnswers: [review.questionAnswers[5]], openingBlocks: undefined};
const sparseBefore = JSON.stringify(sparseReview);
const sparse = buildStudyReviewPlan(sparseReview);
assert.equal(sparse.openings.length, 4, 'The four reader questions remain available as labels');
assert.equal(sparse.openings[2].answers[0], review.questionAnswers[5], 'Fallback resolves an existing Q06 answer');
assert.deepEqual(sparse.sections.flatMap(section => section.answers.map(answer => answer.id)), ['Q06']);
assert.equal(JSON.stringify(sparseReview), sparseBefore);
const empty = buildStudyReviewPlan({...review, questionAnswers: undefined, openingBlocks: undefined});
assert(empty.openings.every(block => block.answers.length === 0));
assert(empty.sections.every(block => block.answers.length === 0));
assert.deepEqual(empty.citations, [], 'Missing evidence does not create invented citations');

console.log('PASS: study presentation maps every Q01–Q15 once in detail, preserves authored openings and fragments, follows rendered citation order, and leaves sparse/approved source records unchanged.');
