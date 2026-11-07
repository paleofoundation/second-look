import test from 'node:test';
import assert from 'node:assert/strict';
import {
  DOI_DEEPENING_TARGET,
  MIN_BODY_WORDS,
  MIN_DISTINCT_DOIS,
  MIN_DOSING_WORDS,
  MIN_STUDY_SUMMARIES,
  assessGuide,
  assessLibrary,
  deepenQueue,
  formatReadinessReport,
  loadReadinessInputs,
  readinessContext,
  wordCount,
} from '../scripts/readiness.mjs';

function filler(count, stem) {
  return Array.from({length: count}, (_, index) => `${stem}${index}`).join(' ');
}

function source(id, extras = {}) {
  return {
    id,
    title: `Study ${id}`,
    doi: `10.1000/${id.toLowerCase()}`,
    year: 2024,
    url: `https://doi.org/10.1000/${id.toLowerCase()}`,
    sourceType: 'primary',
    preview: filler(40, 'finding'),
    design: 'Randomized trial',
    population: 'Adults in the reported trial',
    ...extras,
  };
}

function readyLibrary(doiCount = MIN_DISTINCT_DOIS) {
  const sources = Array.from({length: doiCount}, (_, index) => source(`S${index}`, index < MIN_STUDY_SUMMARIES ? {} : {sourceType: 'context', preview: 'Background.'}));
  for (const item of sources.slice(0, MIN_STUDY_SUMMARIES)) item.preview = filler(160, 'finding');
  const guideSources = sources.map(item => item.id);
  const dosing = `The phase 2 trial tested 500 mg twice daily for 14 days. ${filler(MIN_DOSING_WORDS, 'schedule')}`;
  const guide = {
    id: 'G-FIXTURE',
    slug: '/drugs/fixture',
    title: 'Fixture',
    type: 'Drug',
    entityId: 'FIX',
    description: 'A fixture drug page used to test the metformin-grade bar.',
    sourceIds: guideSources,
    synthesisIds: ['row-a', 'row-b'],
    faqs: [{id: 'faq-1', question: 'What is still uncertain?', answer: filler(30, 'limit'), sources: ['S0']}],
    sections: [
      {id: 'overview', label: 'Overview', title: 'What is it?', paragraph: filler(MIN_BODY_WORDS, 'body'), sources: ['S0']},
      {id: 'benefits', label: 'Benefits', paragraph: filler(40, 'benefit'), sources: ['S0'], questions: []},
      {id: 'safety', label: 'Safety', paragraph: 'In adults, diarrhea, nausea, and abdominal discomfort are common, and lactic acidosis is the serious risk when kidney function is poor.', sources: ['S0']},
      {id: 'contraindications', label: 'Contraindications', paragraph: 'Do not start this drug when kidney filtration is below the labeled cutoff or metabolic acidosis is present.', sources: ['S0']},
      {id: 'interactions', label: 'Interactions', paragraph: 'Insulin and alcohol raise the risk of hypoglycemia or lactic acidosis and need a medication review.', sources: ['S0']},
      {id: 'dosing', label: 'Dosing', paragraph: dosing, sources: ['S0']},
      {id: 'quality', label: 'Quality', paragraph: 'Immediate-release and extended-release formulations differ, and the trials used the immediate-release tablet.', sources: ['S0']},
      {id: 'evidence', label: 'Evidence', paragraph: filler(40, 'evidence'), sources: ['S0']},
    ],
  };
  const context = readinessContext({
    sources,
    mechanisms: [{
      drugId: 'FIX',
      originalAction: {text: filler(30, 'action'), sourceIds: ['S0']},
      pathways: [
        {id: 'p1', title: 'Insulin and growth signaling', text: filler(50, 'insulin')},
        {id: 'p2', title: 'AMPK and mTOR balance', text: filler(50, 'ampk')},
        {id: 'p3', title: 'Autophagy and mitochondria', text: filler(50, 'mito')},
      ],
    }],
    synthesisRows: [
      {id: 'row-a', conditionId: 'C1', drugId: 'FIX', sourceIds: ['S0']},
      {id: 'row-b', conditionId: 'C2', drugId: 'FIX', sourceIds: ['S1']},
    ],
    outcomeSummaries: [
      {id: 'sum-a', synthesisIds: ['row-a'], conditionId: 'C1', drugId: 'FIX', label: 'Symptom score', effect: {label: 'Small', detail: 'A small change on the symptom score.'}, grade: {label: 'Possible benefit'}},
      {id: 'sum-b', synthesisIds: ['row-b'], conditionId: 'C2', drugId: 'FIX', label: 'Hospital stay', effect: {label: 'Uncertain', detail: 'The trials did not establish a hospital difference.'}, grade: {label: 'Not demonstrated'}},
    ],
  });
  return {guide, context};
}

test('word count splits on punctuation and drops markup', () => {
  assert.equal(wordCount('500 mg twice-daily'), 4);
  assert.equal(wordCount('<p>One two</p>'), 2);
  assert.equal(wordCount(''), 0);
});

test('a complete fixture passes and each missing piece fails on its own', () => {
  const {guide, context} = readyLibrary();
  const ready = assessGuide(guide, context);
  assert.equal(ready.pass, true, ready.failing.join(','));
  assert.ok(ready.words >= MIN_BODY_WORDS);
  assert.equal(ready.distinctDois, MIN_DISTINCT_DOIS);

  const thinBody = structuredClone(guide);
  thinBody.sections = thinBody.sections.map(section => section.id === 'overview' ? {...section, paragraph: 'Short overview.'} : section);
  assert.ok(assessGuide(thinBody, context).failing.includes('body-words'));

  const fewDois = readyLibrary(MIN_DISTINCT_DOIS - 1);
  assert.ok(assessGuide(fewDois.guide, fewDois.context).failing.includes('distinct-dois'));

  const blocked = readyLibrary();
  const retracted = blocked.context.sourcesById.get('S0');
  blocked.context.sourcesById.set('S0', {...retracted, status: 'Quarantined', correction: 'Retracted.'});
  assert.ok(assessGuide(blocked.guide, blocked.context).failing.includes('distinct-dois'));

  const urlDoi = readyLibrary(MIN_DISTINCT_DOIS - 1);
  const extra = source('URLONLY', {doi: '', url: 'https://www.nejm.org/doi/abs/10.1056/NEJMoa9999999', sourceType: 'context', preview: 'Background.'});
  urlDoi.context.sourcesById.set(extra.id, extra);
  urlDoi.guide.sourceIds = [...urlDoi.guide.sourceIds, extra.id];
  assert.equal(assessGuide(urlDoi.guide, urlDoi.context).distinctDois, MIN_DISTINCT_DOIS);

  const twoPathways = readyLibrary();
  twoPathways.context.mechanisms[0].pathways = twoPathways.context.mechanisms[0].pathways.slice(0, 2);
  assert.ok(assessGuide(twoPathways.guide, twoPathways.context).failing.includes('mechanism-subsections'));

  const oneGroup = readyLibrary();
  oneGroup.context.outcomeSummaries = oneGroup.context.outcomeSummaries.slice(0, 1);
  assert.ok(assessGuide(oneGroup.guide, oneGroup.context).failing.includes('evidence-table'));

  const shortDose = readyLibrary();
  shortDose.guide.sections = shortDose.guide.sections.map(section => section.id === 'dosing' ? {...section, paragraph: 'The trial used 500 mg once.'} : section);
  assert.ok(assessGuide(shortDose.guide, shortDose.context).failing.includes('dosing'));

  const noInteractions = readyLibrary();
  noInteractions.guide.sections = noInteractions.guide.sections.filter(section => section.id !== 'interactions');
  assert.ok(assessGuide(noInteractions.guide, noInteractions.context).failing.includes('safety'));

  const boilerplateQuality = readyLibrary();
  boilerplateQuality.guide.sections = boilerplateQuality.guide.sections.map(section => section.id === 'quality'
    ? {...section, paragraph: 'FDA-approved generic medicines must match the reference product and demonstrate bioequivalence.'}
    : section);
  assert.ok(assessGuide(boilerplateQuality.guide, boilerplateQuality.context).failing.includes('quality'));

  const thinStudies = readyLibrary();
  for (const item of thinStudies.context.sourcesById.values()) if (item.sourceType === 'primary') item.preview = 'Too short.';
  assert.ok(assessGuide(thinStudies.guide, thinStudies.context).failing.includes('study-summaries'));

  const missing = readyLibrary();
  missing.guide.sourceIds = [...missing.guide.sourceIds, 'missing-source'];
  assert.ok(assessGuide(missing.guide, missing.context).failing.includes('unresolved-source'));

  assert.ok(assessGuide(guide, {...context, live: false}).failing.includes('not-live'));
  assert.ok(assessGuide({...guide, type: 'Glossary'}, context).failing.includes('type'));
});

test('metformin passes; source-backed prose fills do not waive the remaining topic readiness requirements', () => {
  const {guides, context} = loadReadinessInputs();
  const results = assessLibrary(guides, context);
  const byPath = new Map(results.map(result => [result.path, result]));
  const metformin = byPath.get('/drugs/metformin');
  const methylene = byPath.get('/drugs/methylene-blue');
  const itraconazole = byPath.get('/drugs/itraconazole');
  const melphalan = byPath.get('/drugs/melphalan');
  assert.equal(metformin.pass, true, metformin.failing.join(','));
  assert.ok(metformin.words >= MIN_BODY_WORDS);
  assert.ok(metformin.distinctDois >= MIN_DISTINCT_DOIS);
  assert.ok(metformin.distinctDois >= DOI_DEEPENING_TARGET);
  assert.equal(methylene.pass, false);
  assert.equal(itraconazole.pass, false);
  assert.equal(melphalan.pass, false);
  const methyleneMechanism = methylene.checks.find(item => item.id === 'mechanism-subsections');
  assert.equal(methyleneMechanism.pass, true);
  assert.match(methyleneMechanism.detail, /^3 named mechanism subsections/);
  const methyleneDosing = methylene.checks.find(item => item.id === 'dosing');
  assert.equal(methyleneDosing.pass, true);
  const methyleneDosingWords = Number(methyleneDosing.detail.match(/^(\d+) dosing words/)[1]);
  assert.ok(methyleneDosingWords >= MIN_DOSING_WORDS);
  const methyleneSafety = methylene.checks.find(item => item.id === 'safety');
  assert.equal(methyleneSafety.pass, true);
  assert.match(methyleneSafety.detail, /contraindications populated/);
  assert.match(methyleneSafety.detail, /interactions populated/);
  const methyleneQuality = methylene.checks.find(item => item.id === 'quality');
  assert.equal(methyleneQuality.pass, true);
  assert.match(methyleneQuality.detail, /formulation or product difference/);
  const methyleneStudies = methylene.checks.find(item => item.id === 'study-summaries');
  assert.equal(methyleneStudies.pass, true);
  for (const id of ['body-words', 'distinct-dois', 'evidence-table']) {
    assert.ok(methylene.failing.includes(id), `${methylene.path} should fail ${id}`);
  }
  const itraconazoleDosing = itraconazole.checks.find(item => item.id === 'dosing');
  assert.equal(itraconazoleDosing.pass, false);
  const itraconazoleDosingWords = Number(itraconazoleDosing.detail.match(/^(\d+) dosing words/)[1]);
  assert.ok(itraconazoleDosingWords < MIN_DOSING_WORDS, `${itraconazole.path} should fail dosing`);
  assert.ok(itraconazole.failing.includes('dosing'), `${itraconazole.path} should fail dosing`);
  assert.equal(melphalan.checks.find(item => item.id === 'quality').pass, true, 'The source-bound HEPZATO product and preparation section supplies Quality context without changing the indexing thresholds');
  const melphalanSafety = melphalan.checks.find(item => item.id === 'safety');
  assert.equal(melphalanSafety.pass, true, 'Verified product-specific contraindications and interactions now populate the existing safety check');
  assert.match(melphalanSafety.detail, /contraindications populated/);
  assert.match(melphalanSafety.detail, /interactions populated/);
  for (const id of ['body-words', 'distinct-dois', 'mechanism-subsections', 'evidence-table', 'dosing', 'study-summaries']) {
    assert.ok(melphalan.failing.includes(id), `${melphalan.path} should fail ${id}`);
  }
  assert.deepEqual(results.filter(result => result.pass).map(result => result.path), ['/drugs/metformin']);
  const queue = deepenQueue(results);
  assert.equal(queue[0].path, '/drugs/methylene-blue');
  assert.equal(queue[1].path, '/drugs/melphalan');
  const report = formatReadinessReport(results);
  assert.match(report, /Pages that pass[\s\S]*\/drugs\/metformin/);
  assert.match(report, /### \/drugs\/methylene-blue/);
  assert.match(report, /### \/drugs\/melphalan/);
  assert.equal(report.includes('—') || report.includes('–'), false);
});
