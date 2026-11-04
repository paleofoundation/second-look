/**
 * Metformin-grade readiness.
 *
 * /drugs/metformin is the reference ready page. A LIVE drug or condition
 * page is indexable only when assessGuide().pass is true. Sitemap URLs and
 * index/noindex metadata both use that result.
 *
 * The 4 November 2026 page-file count of about 44 DOIs on metformin repeated
 * each identifier (rendered bibliography plus the embedded payload). Distinct
 * valid DOIs on the current records are 18 for metformin, 8 for methylene
 * blue, and 12 for melphalan. The indexing floor is 15 so the exemplar passes
 * and those two pages fail. DOI_DEEPENING_TARGET (30) stays in the gap report
 * so a fill can keep adding cited papers. docs/READY.md is the short contract.
 */
import {readFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

export const MIN_BODY_WORDS = 5000;
export const MIN_DISTINCT_DOIS = 15;
export const DOI_DEEPENING_TARGET = 30;
export const MIN_MECHANISM_SUBSECTIONS = 3;
export const MIN_MECHANISM_SUBSECTION_WORDS = 40;
export const MIN_EVIDENCE_GROUPS = 2;
export const MIN_DOSING_WORDS = 250;
export const MIN_SAFETY_WORDS = 20;
export const MIN_RESTRICTION_WORDS = 15;
export const MIN_STUDY_SUMMARIES = 8;
export const MIN_STUDY_SUMMARY_WORDS = 1200;
export const MIN_STUDY_PREVIEW_WORDS = 20;

export const DEEPEN_CHECKS = [
  'mechanism-subsections',
  'evidence-table',
  'dosing',
  'safety',
  'quality',
  'study-summaries',
  'body-words',
  'distinct-dois',
];

const QUALITY_BOILERPLATE = /FDA-approved generic medicines must match|demonstrate bioequivalence/i;
const QUALITY_SPECIFIC = /differ|distinct|interchangeab|immediate-release|extended-release|delayed-release|release (profile|formulation)|veterinary|compounded|supplement|co-packaged|other formulations|formulations|salt and base|topical|combined with|combination/i;
const DOSE_PATTERN = /\d+(?:\.\d+)?\s*(?:mg|g|mcg|ug|µg|ml|mmol|%|iu)\b/i;
const SCHEDULE_PATTERN = /\b(?:daily|twice|weekly|week|weeks|cycle|cycles|month|months|hour|hours|day|days)\b/i;
const TRIAL_PATTERN = /\b(?:trial|trials|study|studies|pilot)\b/i;

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

export function wordCount(text) {
  return String(text || '').replace(/<[^>]+>/g, ' ').split(/[^\p{L}\p{N}]+/u).filter(Boolean).length;
}

export function normalizeDoi(value) {
  return String(value || '').trim().toLowerCase()
    .replace(/^https?:\/\/(?:dx\.)?doi\.org\//, '')
    .replace(/\\+$/g, '')
    .replace(/[)\].,;:]+$/g, '');
}

export function isBlockedSource(source) {
  if (!source) return false;
  const status = String(source.status || '');
  const correction = typeof source.correction === 'string' ? source.correction : '';
  return /quarantine|retract|withdraw|remov/i.test(`${status} ${correction}`);
}

function isPrimarySource(source) {
  return !!source && !['context', 'review', 'textbook', 'other'].includes(source.sourceType || 'primary');
}

function doiOf(source) {
  const field = normalizeDoi(source?.doi);
  if (/^10\.\d{4,9}\/\S+$/.test(field)) return field;
  const fromUrl = String(source?.url || '').match(/10\.\d{4,9}\/[^\s?#]+/i);
  const urlDoi = normalizeDoi(fromUrl?.[0] || '');
  return /^10\.\d{4,9}\/\S+$/.test(urlDoi) ? urlDoi : '';
}

function retired(section) {
  return String(section?.label || '').trim().toLowerCase() === 'connections';
}

function addIds(value, ids) {
  if (!value) return;
  if (Array.isArray(value)) {
    value.forEach(item => addIds(item, ids));
    return;
  }
  if (typeof value !== 'object') return;
  for (const source of value.sources || []) ids.add(typeof source === 'string' ? source : source?.id);
  for (const id of value.sourceIds || []) ids.add(id);
}

export function readinessContext({
  sources = [],
  mechanisms = [],
  suitability = {},
  synthesisRows = [],
  outcomeSummaries = [],
  status = {},
  live = true,
} = {}) {
  const sourcesById = sources instanceof Map ? new Map(sources) : new Map(sources.map(source => [source.id, source]));
  for (const source of suitability.sources || []) if (source?.id && !sourcesById.has(source.id)) sourcesById.set(source.id, source);
  const summaryRecords = Array.isArray(outcomeSummaries) ? outcomeSummaries : (outcomeSummaries.records || []);
  return {
    live,
    sourcesById,
    mechanisms: Array.isArray(mechanisms) ? mechanisms : (mechanisms.drugs || []),
    suitabilityRows: suitability.rows || [],
    suitabilityPages: suitability.pages || {},
    synthesisRows: Array.isArray(synthesisRows) ? synthesisRows : (synthesisRows.synthesisRows || []),
    outcomeSummaries: summaryRecords,
    statusBySlug: status.drugs || status,
  };
}

export function loadReadinessInputs() {
  const read = name => JSON.parse(readFileSync(resolve(root, name), 'utf8'));
  const content = read('data/public-content.json');
  return {
    guides: content.guides,
    sources: content.sources,
    context: readinessContext({
      sources: content.sources,
      mechanisms: read('data/public-mechanisms.json'),
      suitability: read('data/treatment-suitability.json'),
      synthesisRows: read('data/public-reader-evidence.json'),
      outcomeSummaries: read('data/outcome-summaries.json'),
      status: read('data/drug-status-table.json'),
    }),
  };
}

function mechanismFor(guide, context) {
  return (context.mechanisms || []).find(record =>
    (guide.type === 'Drug' && record.drugId === guide.entityId) ||
    (guide.type === 'Condition' && record.conditionId === guide.entityId) ||
    record.guideIds?.includes(guide.id));
}

function guideRows(guide, context) {
  const wanted = new Set(guide.synthesisIds || []);
  return (context.synthesisRows || []).filter(row => wanted.has(row.id));
}

function guideSummaries(guide, context) {
  const wanted = new Set(guide.synthesisIds || []);
  return (context.outcomeSummaries || []).filter(summary => (summary.synthesisIds || []).some(id => wanted.has(id)));
}

function suitabilityRowsFor(guide, context) {
  const names = new Set(context.suitabilityPages?.[guide.slug] || []);
  return (context.suitabilityRows || []).filter(row => names.has(row.drug));
}

function citedIds(guide, context) {
  const ids = new Set(guide.sourceIds || []);
  for (const section of guide.sections || []) {
    if (retired(section)) continue;
    addIds(section, ids);
    for (const sentence of section.sentences || []) addIds(sentence, ids);
    for (const question of section.questions || []) {
      addIds(question, ids);
      for (const sentence of question.sentences || []) addIds(sentence, ids);
    }
  }
  for (const section of guide.scopedSections || []) addIds(section, ids);
  for (const faq of guide.faqs || []) {
    addIds(faq, ids);
    for (const sentence of faq.sentences || []) addIds(sentence, ids);
  }
  const mechanism = mechanismFor(guide, context);
  if (mechanism) {
    for (const prose of [mechanism.originalAction, mechanism.summary, ...(mechanism.pathways || []), ...(mechanism.questions || [])]) addIds(prose, ids);
    for (const row of mechanism.rationales || []) {
      addIds(row.rationale, ids);
      addIds(row.tested, ids);
      addIds(row.limits, ids);
    }
  }
  for (const row of guideRows(guide, context)) addIds(row, ids);
  for (const summary of guideSummaries(guide, context)) addIds(summary, ids);
  for (const row of suitabilityRowsFor(guide, context)) addIds(row, ids);
  ids.delete(undefined);
  ids.delete(null);
  ids.delete('');
  return [...ids];
}

function renderedQuestionText(guide, context) {
  const evidenceIds = new Set(guideRows(guide, context).flatMap(row => row.sourceIds || []));
  const norm = text => String(text || '').toLowerCase().replace(/[^a-z0-9 ]/g, '').trim();
  const faqKeys = new Set((guide.faqs || []).flatMap(faq => [faq.id || '', norm(faq.question)]));
  const parts = [];
  for (const section of guide.sections || []) {
    if (retired(section)) continue;
    for (const question of section.questions || []) {
      if (section.label === 'Benefits') {
        const covered = faqKeys.has(question.id) || faqKeys.has(norm(question.question)) ||
          (!!question.sources?.length && question.sources.every(id => evidenceIds.has(id)));
        if (covered) continue;
      }
      parts.push(question.question, question.answer);
    }
  }
  return parts.filter(Boolean).join(' ');
}

function sectionByLabel(guide, label) {
  return (guide.sections || []).find(section => section.label === label && !retired(section));
}

function sectionText(section) {
  if (!section) return '';
  const paragraph = section.label === 'Quality'
    ? String(section.paragraph || '').split(/(?<=[.!?])\s+/).filter(sentence => !QUALITY_BOILERPLATE.test(sentence)).join(' ')
    : section.paragraph;
  return [paragraph, ...(section.questions || []).flatMap(question => [question.question, question.answer])].filter(Boolean).join(' ');
}

function sectionCited(section) {
  if (!section) return false;
  if ((section.sources || []).length) return true;
  if ((section.sentences || []).some(sentence => sentence.sources?.length)) return true;
  return (section.questions || []).some(question => question.sources?.length || question.sentences?.some(sentence => sentence.sources?.length));
}

/** Reader-facing article prose. Navigation, update history, and generic quality boilerplate are left out. */
export function substantiveText(guide, context) {
  const parts = [guide.description];
  for (const section of [...(guide.sections || []), ...(guide.scopedSections || [])]) {
    if (retired(section)) continue;
    const paragraph = section.label === 'Quality'
      ? String(section.paragraph || '').split(/(?<=[.!?])\s+/).filter(sentence => !QUALITY_BOILERPLATE.test(sentence)).join(' ')
      : section.paragraph;
    parts.push(section.title, paragraph);
  }
  parts.push(renderedQuestionText(guide, context));
  for (const faq of guide.faqs || []) parts.push(faq.question, faq.answer);
  const mechanism = mechanismFor(guide, context);
  if (mechanism) {
    parts.push(mechanism.originalAction?.text, mechanism.summary?.text);
    for (const pathway of mechanism.pathways || []) parts.push(pathway.title, pathway.text);
    for (const question of mechanism.questions || []) parts.push(question.title, question.text);
  }
  for (const row of suitabilityRowsFor(guide, context)) parts.push(row.label, row.text);
  for (const row of context.statusBySlug?.[guide.slug] || []) parts.push(row.use, row.regulator, row.status, row.year);
  for (const summary of guideSummaries(guide, context)) {
    parts.push(summary.label, summary.purpose, summary.grade?.label, summary.effect?.label, summary.effect?.detail);
  }
  const records = citedIds(guide, context).map(id => context.sourcesById.get(id)).filter(Boolean);
  for (const source of records.filter(isPrimarySource)) {
    parts.push(source.title, source.preview, source.design, source.population, source.intervention, source.comparator, source.decisiveLimit, source.sampleDescription);
  }
  for (const source of records) parts.push(source.title, source.year, source.design);
  return parts.filter(value => value !== undefined && value !== null).join(' ');
}

function restrictionReady(guide, context, label, category) {
  const section = sectionByLabel(guide, label);
  if (section && sectionCited(section) && wordCount(sectionText(section)) >= MIN_RESTRICTION_WORDS) return true;
  return suitabilityRowsFor(guide, context).some(row =>
    row.category === category && (row.sourceIds || []).length > 0 && wordCount(row.text) >= 8);
}

function check(id, pass, detail) {
  return {id, pass, detail};
}

export function assessGuide(guide, context) {
  const library = context?.sourcesById ? context : readinessContext(context);
  const failing = [];
  const checks = [];
  const push = item => {
    checks.push(item);
    if (!item.pass) failing.push(item.id);
  };
  if (library.live === false) push(check('not-live', false, 'Discovery-only or non-public guides stay out of the index.'));
  const isArticle = guide?.type === 'Drug' || guide?.type === 'Condition';
  if (!isArticle) push(check('type', false, 'Only drug and condition guides are indexed.'));

  const words = wordCount(substantiveText(guide || {}, library));
  push(check('body-words', words >= MIN_BODY_WORDS, `${words} substantive words; need ${MIN_BODY_WORDS}.`));

  const ids = citedIds(guide || {}, library);
  const missing = ids.filter(id => !library.sourcesById.get(id));
  if (missing.length) push(check('unresolved-source', false, `${missing.length} cited source ids do not resolve.`));
  const dois = new Set();
  for (const id of ids) {
    const source = library.sourcesById.get(id);
    if (!source || isBlockedSource(source)) continue;
    const doi = doiOf(source);
    if (doi) dois.add(doi);
  }
  push(check(
    'distinct-dois',
    dois.size >= MIN_DISTINCT_DOIS,
    `${dois.size} distinct valid DOIs; indexing floor ${MIN_DISTINCT_DOIS}; deepening target ${DOI_DEEPENING_TARGET}.`,
  ));

  const mechanism = mechanismFor(guide || {}, library);
  const subsections = (mechanism?.pathways || []).filter(pathway =>
    wordCount(pathway.title) >= 2 && wordCount(pathway.text) >= MIN_MECHANISM_SUBSECTION_WORDS);
  push(check(
    'mechanism-subsections',
    subsections.length >= MIN_MECHANISM_SUBSECTIONS,
    `${subsections.length} named mechanism subsections; need ${MIN_MECHANISM_SUBSECTIONS}.`,
  ));

  const summaries = guideSummaries(guide || {}, library);
  const groups = new Map();
  for (const summary of summaries) {
    const key = guide?.type === 'Condition' ? summary.drugId : summary.conditionId;
    if (!key) continue;
    const group = groups.get(key) || [];
    group.push(summary);
    groups.set(key, group);
  }
  const grouped = [...groups.values()].filter(group => group.some(summary => summary.label && (summary.effect?.detail || summary.effect?.label || summary.grade?.label)));
  push(check(
    'evidence-table',
    grouped.length >= MIN_EVIDENCE_GROUPS,
    `${grouped.length} evidence groups with outcome rows; need ${MIN_EVIDENCE_GROUPS}.`,
  ));

  const dosing = sectionByLabel(guide || {}, 'Dosing');
  const dosingText = sectionText(dosing);
  const dosingWords = wordCount(dosingText);
  const dosingReady = !!dosing && sectionCited(dosing) && dosingWords >= MIN_DOSING_WORDS &&
    DOSE_PATTERN.test(dosingText) && SCHEDULE_PATTERN.test(dosingText) && TRIAL_PATTERN.test(dosingText);
  push(check(
    'dosing',
    dosingReady,
    `${dosingWords} dosing words from cited trial schedules; need ${MIN_DOSING_WORDS} with a dose, a schedule, and a trial or study.`,
  ));

  const safety = sectionByLabel(guide || {}, 'Safety');
  const safetyWords = wordCount(sectionText(safety));
  const contraindications = restrictionReady(guide || {}, library, 'Contraindications', 'contraindication');
  const interactions = restrictionReady(guide || {}, library, 'Interactions', 'interaction');
  const safetyReady = !!safety && sectionCited(safety) && safetyWords >= MIN_SAFETY_WORDS && contraindications && interactions;
  const safetyGap = [
    safetyWords < MIN_SAFETY_WORDS ? `safety prose is ${safetyWords} words` : 'safety prose is present',
    contraindications ? 'contraindications populated' : 'contraindications empty',
    interactions ? 'interactions populated' : 'interactions empty',
  ].join('; ');
  push(check('safety', safetyReady, `${safetyGap}.`));

  const quality = sectionByLabel(guide || {}, 'Quality');
  const qualitySentences = String(quality?.paragraph || '').split(/(?<=[.!?])\s+/).filter(sentence => !QUALITY_BOILERPLATE.test(sentence));
  const qualityReady = !!quality && sectionCited(quality) && qualitySentences.some(sentence => QUALITY_SPECIFIC.test(sentence));
  push(check('quality', qualityReady, qualityReady ? 'Quality section names a formulation or product difference.' : 'No drug-specific Quality section.'));

  const records = ids.map(id => library.sourcesById.get(id)).filter(Boolean);
  const primary = records.filter(isPrimarySource);
  const substantiveStudies = primary.filter(source => wordCount(source.preview) >= MIN_STUDY_PREVIEW_WORDS);
  const studyWords = primary.reduce((sum, source) => sum + wordCount([
    source.title, source.preview, source.design, source.population, source.intervention, source.comparator, source.decisiveLimit, source.sampleDescription,
  ].filter(Boolean).join(' ')), 0);
  const studiesReady = substantiveStudies.length >= MIN_STUDY_SUMMARIES && studyWords >= MIN_STUDY_SUMMARY_WORDS;
  push(check(
    'study-summaries',
    studiesReady,
    `${studyWords} study-summary words; ${substantiveStudies.length} of ${primary.length} primary sources have a preview of at least ${MIN_STUDY_PREVIEW_WORDS} words; need ${MIN_STUDY_SUMMARY_WORDS} words and ${MIN_STUDY_SUMMARIES} such summaries.`,
  ));

  const order = new Map(DEEPEN_CHECKS.map((id, index) => [id, index]));
  failing.sort((a, b) => (order.get(a) ?? 50) - (order.get(b) ?? 50));
  const path = guide?.slug?.startsWith('/') ? guide.slug : `/${guide?.slug || ''}`;
  return {
    id: guide?.id || '',
    path,
    title: guide?.title || '',
    type: guide?.type || '',
    pass: failing.length === 0,
    words,
    distinctDois: dois.size,
    cited: ids.length,
    failing,
    checks,
  };
}

export function assessLibrary(guides, context) {
  return guides
    .filter(guide => guide.type === 'Drug' || guide.type === 'Condition')
    .map(guide => assessGuide(guide, context))
    .sort((a, b) => a.path.localeCompare(b.path));
}

/** Methylene blue, then melphalan, then the closest other failing pages. */
export function deepenQueue(results) {
  const priority = new Map([['/drugs/methylene-blue', 0], ['/drugs/melphalan', 1]]);
  return results.filter(result => !result.pass).sort((a, b) => {
    const rankA = priority.has(a.path) ? priority.get(a.path) : 99;
    const rankB = priority.has(b.path) ? priority.get(b.path) : 99;
    if (rankA !== rankB) return rankA - rankB;
    if (a.failing.length !== b.failing.length) return a.failing.length - b.failing.length;
    return b.words - a.words || a.path.localeCompare(b.path);
  });
}

export function formatReadinessReport(results) {
  const passing = results.filter(result => result.pass);
  const lines = [
    '# Metformin-grade readiness',
    '',
    `Indexing bar: substantive body >= ${MIN_BODY_WORDS} words; >= ${MIN_DISTINCT_DOIS} distinct valid DOIs; >= ${MIN_MECHANISM_SUBSECTIONS} named mechanism subsections; evidence grouped by condition; dosing from cited trial schedules; safety with contraindications and interactions; study summaries; a drug-specific Quality section.`,
    `Distinct-DOI deepening target: ${DOI_DEEPENING_TARGET}. The indexing floor is ${MIN_DISTINCT_DOIS} because metformin currently has fewer than 30 distinct valid DOIs.`,
    '',
    '## Pages that pass',
    '',
  ];
  if (!passing.length) lines.push('None.');
  else for (const result of passing) lines.push(`- ${result.path} (${result.words} words, ${result.distinctDois} distinct valid DOIs)`);
  lines.push('', '## Gaps', '');
  const queue = deepenQueue(results);
  if (!queue.length) lines.push('No drug or condition page is below the bar.');
  for (const result of queue) {
    lines.push(`### ${result.path}`);
    for (const id of result.failing) {
      const item = result.checks.find(checkItem => checkItem.id === id);
      lines.push(`- ${id}: ${item?.detail || 'fail'}`);
    }
    lines.push('');
  }
  return lines.join('\n');
}

function main() {
  const {guides, context} = loadReadinessInputs();
  const results = assessLibrary(guides, context);
  if (process.argv.includes('--json')) {
    console.log(JSON.stringify({
      passing: results.filter(result => result.pass).map(result => result.path),
      queue: deepenQueue(results).map(result => ({path: result.path, failing: result.failing, words: result.words, distinctDois: result.distinctDois})),
      pages: results,
    }, null, 2));
    return;
  }
  console.log(formatReadinessReport(results));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
