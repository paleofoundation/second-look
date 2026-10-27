#!/usr/bin/env node
/** Read-only citation/review audit. The only write is the explicitly named output file.
 * Run: node scripts/research-review-coverage.mjs --output <private-ledger.json>
 * Source classifications describe recorded metadata, not independent source verification.
 */
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const QUESTIONS = Array.from({length: 15}, (_, i) => `Q${String(i + 1).padStart(2, '0')}`);
const unique = values => [...new Set(values)].sort();
const sha256 = value => createHash('sha256').update(value).digest('hex');

export function resolveAlias(id, aliases = {}) {
  const seen = new Set();
  while (Object.hasOwn(aliases, id)) {
    if (seen.has(id)) throw new Error(`Source alias cycle: ${[...seen, id].join(' -> ')}`);
    seen.add(id);
    if (typeof aliases[id] !== 'string' || !aliases[id]) throw new Error(`Invalid source alias: ${id}`);
    id = aliases[id];
  }
  return id;
}

export function classifySource(source) {
  if (!source) return {kind: 'unclassified', basis: 'Citation has no canonical source record.'};
  const type = String(source.sourceType || '').toLowerCase();
  const design = String(source.design || '');
  const title = String(source.title || '');
  // A CONTEXT tier is not a publication type: secondary research still needs a review.
  if (type === 'textbook' || /textbook chapter/i.test(design)) return {kind: 'scholarly_book_chapter', basis: 'Recorded textbook/chapter classification; separate from the paper denominator.'};
  if (/^(official|us product label|fda drug-quality|national cancer institute)/i.test(design)) return {kind: 'nonresearch', basis: `Recorded document design: ${design}`};
  if (/trial protocol/i.test(design) && !source.doi && !source.pmid) return {kind: 'unclassified', basis: 'Protocol has no verified paper-versus-registry publication classification.'};
  if (['primary', 'primary research', 'review'].includes(type)) return {kind: 'scholarly_paper', basis: `Recorded sourceType: ${source.sourceType}`};
  if (/(trial|experiment|cohort|case report|case series|review|meta-analysis|mechanistic study|laboratory study|published correction)/i.test(design)) return {kind: 'scholarly_paper', basis: `Recorded research design: ${design}`};
  if (/^context \/ (terminology|research methods)$/i.test(design)) return {kind: 'nonresearch', basis: `Recorded reference type: ${design}`};
  if (type === 'context' && /^(NCATS:|NIDDK:|MedlinePlus(?: Genetics)?:|CDC:|NCI Dictionary:|NLM MeSH:)|US prescribing information/i.test(title)) return {kind: 'nonresearch', basis: 'Named official reference/label in canonical source title.'};
  return {kind: 'unclassified', basis: 'No sufficiently specific publication-type metadata; inspect source before deciding review obligation.'};
}

/** Enumerate typed citation keys only; IDs in arbitrary prose do not count. */
export function citationReferences(value, pointer = '', {skipRetired = false} = {}) {
  if (!value || typeof value !== 'object') return [];
  if (skipRetired && String(value.label || '').trim().toLowerCase() === 'connections') return [];
  if (Array.isArray(value)) return value.flatMap((item, i) => citationReferences(item, `${pointer}/${i}`, {skipRetired}));
  const refs = [];
  for (const [key, item] of Object.entries(value)) {
    const next = `${pointer}/${key.replaceAll('~', '~0').replaceAll('/', '~1')}`;
    if (['sources', 'sourceIds'].includes(key) && Array.isArray(item)) {
      item.forEach((id, i) => { if (typeof id === 'string') refs.push({sourceId: id, pointer: `${next}/${i}`}); });
    } else if (key === 'sourceId' && typeof item === 'string') refs.push({sourceId: item, pointer: next});
    else refs.push(...citationReferences(item, next, {skipRetired}));
  }
  return refs;
}

function routeFor(guide) { return guide.slug?.startsWith('/') ? guide.slug : `/answers/${guide.slug}`; }
function questionCoverage(review) {
  const answers = review?.questionAnswers || [];
  return QUESTIONS.map(id => {
    const matches = answers.filter(answer => answer.id === id);
    return {
      id, records: matches.length, status: matches.length === 1 ? matches[0].status : matches.length ? 'duplicate' : 'absent',
      missingness: unique(matches.flatMap(answer => (answer.locators || []).map(locator => locator.missingness).filter(Boolean))),
      locatorCount: matches.reduce((total, answer) => total + (answer.locators || []).length, 0),
      unresolvedRequiredInput: matches.some(answer => Boolean(answer.unresolvedInputReason?.trim())),
    };
  });
}

export async function buildCoverage(input, contracts) {
  const {canonical, publicContent, discovery = [], reader = {}, mechanisms = {}, reviews = {}, envelopes = {}, aliases = {}} = input;
  const sources = new Map(canonical.sources.map(source => [source.id, source]));
  const publicSources = new Map(publicContent.sources.map(source => [source.id, source]));
  const rows = new Map((reader.synthesisRows || []).map(row => [row.id, row]));
  const citations = new Map();
  const issues = [];
  const add = (sourceId, citation) => {
    const id = resolveAlias(sourceId, aliases);
    const list = citations.get(id) || [];
    list.push({...citation, citedAs: sourceId});
    citations.set(id, list);
    if (!sources.has(id)) issues.push({type: 'missing_canonical_source', sourceId: id, ...citation});
  };
  const scan = (value, file, pointer, scope, route) => citationReferences(value, pointer, {skipRetired: true}).forEach(ref => add(ref.sourceId, {file, pointer: ref.pointer, scope, route}));
  const guides = [...publicContent.guides, ...discovery.filter(page => !publicContent.guides.some(guide => guide.id === page.id || guide.slug === page.slug))];
  for (const guide of guides) {
    const route = routeFor(guide);
    const file = publicContent.guides.includes(guide) ? 'data/public-content.json' : 'data/discovery-pages.json';
    const sourceList = publicContent.sources.filter(source => guide.sourceIds.includes(source.id));
    const rendered = new Set(contracts.guideCitationOrder(guide, sourceList));
    rendered.forEach(id => add(id, {scope: 'public_citation', file, pointer: `guide:${guide.id}/rendered-citation-order`, route}));
    for (const ref of citationReferences(guide, `guide:${guide.id}`, {skipRetired: true})) {
      // Bibliography entries are citations too. Nested citations not in the renderer are defects, not silently discarded.
      const visible = rendered.has(ref.sourceId);
      add(ref.sourceId, {scope: visible ? 'public_citation' : 'unrendered_guide_reference', file, pointer: ref.pointer, route});
      if (!visible) issues.push({type: 'guide_reference_not_in_rendered_citations', guideId: guide.id, sourceId: ref.sourceId, pointer: ref.pointer});
    }
    for (const rowId of guide.synthesisIds || []) {
      const row = rows.get(rowId);
      if (!row) issues.push({type: 'missing_synthesis_row', guideId: guide.id, rowId});
      else scan(row, 'data/public-reader-evidence.json', `synthesis:${rowId}`, 'public_evidence_panel', route);
    }
    // The actual mechanism contract decides which context/source IDs the renderer uses.
    for (const id of contracts.mechanismCitationIds(guide)) add(id, {scope: 'public_citation', file: 'data/public-mechanisms.json', pointer: `guide:${guide.id}/mechanism-citations`, route});
  }
  for (const row of rows.values()) scan(row, 'data/public-reader-evidence.json', `synthesis:${row.id}`, 'public_outcome_page', '/outcomes');
  for (const term of publicContent.glossary || []) scan(term, 'data/public-content.json', `glossary:${term.slug}`, 'public_citation', `/glossary/${term.slug}`);
  for (const guide of canonical.guides) scan(guide, 'data/content.json', `guide:${guide.id}`, 'canonical_draft_reference', routeFor(guide));
  for (const source of canonical.sources) {
    // Review sentence maps can cite companion reports; never count source-catalogue existence as a citation.
    scan(source.reviewSentences, 'data/content.json', `source:${source.id}/reviewSentences`, 'canonical_review_reference', `/research/${resolveAlias(source.id, aliases)}`);
    scan(source.recordSections, 'data/content.json', `source:${source.id}/recordSections`, 'canonical_review_reference', `/research/${resolveAlias(source.id, aliases)}`);
  }
  for (const [id, review] of Object.entries(reviews)) scan(review, 'data/private-reviews.json', `review:${id}`, 'private_review_reference', `/research/${resolveAlias(id, aliases)}`);
  for (const [id, envelope] of Object.entries(envelopes)) scan(envelope.preview, 'data/review-envelopes.json', `review:${id}/preview`, 'review_preview_reference', `/research/${resolveAlias(id, aliases)}`);

  const aliasRoutes = Object.keys(aliases).sort().map(id => {
    const canonicalId = resolveAlias(id, aliases);
    if (!sources.has(canonicalId)) issues.push({type: 'alias_target_missing', alias: id, canonicalId});
    return {alias: id, canonicalId, route: `/research/${id}`, canonicalRoute: `/research/${canonicalId}`,
      status: publicSources.has(canonicalId) ? 'redirect_to_canonical_route' : 'target_missing',
      legacyReviewShadow: Object.hasOwn(reviews, id), legacyEnvelopeShadow: Object.hasOwn(envelopes, id)};
  });
  // Flag duplicate identities; DOI/PMID matches need reconciliation, not an unreviewed automatic merge.
  for (const field of ['doi', 'pmid']) {
    const groups = new Map();
    for (const [id, source] of sources) {
      // Chapters may correctly share a parent book DOI. They are separate units,
      // and are not duplicate papers merely because the book identifier matches.
      if (classifySource(source).kind !== 'scholarly_paper') continue;
      const value = String(source[field] || '').trim().toLowerCase().replace(/^https?:\/\/(?:dx\.)?doi\.org\//, '');
      if (!value) continue;
      const set = groups.get(value) || new Set(); set.add(resolveAlias(id, aliases)); groups.set(value, set);
    }
    for (const [value, ids] of groups) if (ids.size > 1 && [...ids].some(id => citations.has(id))) issues.push({type: 'unreconciled_paper_identity', field, value, sourceIds: [...ids].sort()});
  }

  const records = [];
  for (const id of [...citations.keys()].sort()) {
    const source = sources.get(id);
    const classification = classifySource(source);
    const review = reviews[id];
    const envelope = envelopes[id];
    const completionIssues = review ? contracts.reviewQuestionCompletionIssues(review) : ['Canonical private review is absent.'];
    if (review && review.id !== id) completionIssues.push('Canonical review object ID does not match its key.');
    const actualContentSha256 = review ? await contracts.protectedReviewSha256(review) : null;
    const release = envelope?.release;
    const contentHashMatches = Boolean(review && actualContentSha256 === review.contentSha256 && actualContentSha256 === release?.contentSha256);
    const exactVersionApprovalRecorded = Boolean(contentHashMatches && release?.humanEditorialApproved === true && release.approvedSha256 === actualContentSha256 && release.version === review?.version && envelope?.preview?.version === review?.version);
    const releasedAndGateEligible = Boolean(exactVersionApprovalRecorded && release.state === 'released' && envelope.preview.reviewState === 'released' && typeof release.clinicalSafetyReviewRequired === 'boolean' && (!release.clinicalSafetyReviewRequired || release.qualifiedClinicalApproval === true) && completionIssues.length === 0);
    const refs = citations.get(id);
    const publicCited = refs.some(ref => ['public_citation', 'public_evidence_panel', 'public_outcome_page'].includes(ref.scope));
    const reviewKeys = Object.keys(reviews).filter(key => resolveAlias(key, aliases) === id).sort();
    records.push({
      paperId: id, title: source?.title || null, classification, publicCited,
      dedicatedPaperReviewRequired: classification.kind === 'scholarly_paper' ? true : classification.kind === 'unclassified' ? null : false,
      canonicalReviewId: id, canonicalRoute: `/research/${id}`,
      routeStatus: !publicSources.has(id) ? 'source_route_missing' : !envelope ? 'public_source_preview_without_review_envelope' : !review ? 'review_envelope_without_private_body' : 'canonical_review_route_present',
      aliases: aliasRoutes.filter(alias => alias.canonicalId === id).map(alias => alias.alias),
      reviewRecordKeys: reviewKeys, legacyReviewShadows: reviewKeys.filter(key => key !== id),
      questionCoverage: questionCoverage(review), structuralCompletionIssues: completionIssues,
      structurallyComplete: completionIssues.length === 0,
      reviewVersion: review?.version || null, reviewContentHashMatches: contentHashMatches,
      exactVersionApprovalRecorded, releasedAndGateEligible,
      integrityStatus: source?.status || null, correction: source?.correction || null,
      citationScopes: unique(refs.map(ref => ref.scope)), citations: refs,
      nextAction: classification.kind === 'unclassified' ? 'Resolve publication type before finalizing the cited-paper denominator.' : classification.kind !== 'scholarly_paper' ? 'Preserve source traceability; do not count this reference as a scholarly paper.' : !review ? 'Create a source-bound Q01–Q15 review only after required source inputs are inspected.' : completionIssues.length ? 'Complete the recorded Q01–Q15 input gaps and independent checks; preserve current release state.' : 'Reconcile exact-version human review and release gates separately from structural coverage.',
    });
  }
  const count = predicate => records.filter(predicate).length;
  const unresolved = records.filter(record => record.classification.kind === 'unclassified').map(record => record.paperId);
  return {
    schemaVersion: 'remaprx-review-obligations/1.0', accessPolicy: 'free_authenticated',
    method: 'Canonical and rendered citation references, plus protected-review references. Existing catalogue size is never the cited-paper denominator. Retired Connections sections are excluded. Source classes describe recorded metadata; no raw source was acquired or extracted.',
    denominatorStatus: unresolved.length || issues.some(issue => ['missing_canonical_source', 'unreconciled_paper_identity', 'alias_target_missing'].includes(issue.type)) ? 'provisional_unresolved_classification_or_identity' : 'resolved_from_recorded_metadata',
    scientificReviewCompletion: 'Not certified by this structural ledger; source verification, appraisal and human approval remain separate.',
    counts: {
      citedCanonicalReferences: records.length,
      scholarlyPapers: count(record => record.classification.kind === 'scholarly_paper'),
      publicCitedScholarlyPapers: count(record => record.publicCited && record.classification.kind === 'scholarly_paper'),
      scholarlyBookChapters: count(record => record.classification.kind === 'scholarly_book_chapter'),
      nonresearchReferences: count(record => record.classification.kind === 'nonresearch'), unclassifiedReferences: unresolved.length,
      scholarlyPapersWithCanonicalReview: count(record => record.classification.kind === 'scholarly_paper' && reviews[record.paperId]),
      scholarlyPapersWithAllFifteenQuestions: count(record => record.classification.kind === 'scholarly_paper' && record.questionCoverage.every(question => question.records === 1)),
      structurallyCompleteScholarlyReviews: count(record => record.classification.kind === 'scholarly_paper' && record.structurallyComplete),
      scholarlyReviewsWithExactVersionApprovalRecorded: count(record => record.classification.kind === 'scholarly_paper' && record.exactVersionApprovalRecorded),
      releasedAndGateEligibleScholarlyReviews: count(record => record.classification.kind === 'scholarly_paper' && record.releasedAndGateEligible),
    }, unresolvedClassificationIds: unresolved, issues, aliasRoutes, records,
    unreferencedSourceIds: [...sources.keys()].filter(id => !citations.has(resolveAlias(id, aliases))).sort(),
    unreferencedMechanismRecords: (mechanisms.contexts || []).filter(context => !context.sourceIds?.some(id => citations.has(resolveAlias(id, aliases)))).map(context => context.id),
  };
}

/** Use the real current renderer/access contracts, as the existing repository checks do. */
export function loadContracts(root = ROOT) {
  const require = createRequire(import.meta.url);
  const ts = require('typescript');
  const cache = new Map();
  function load(file) {
    if (file.endsWith('.json')) return JSON.parse(fs.readFileSync(file, 'utf8'));
    if (cache.has(file)) return cache.get(file).exports;
    const module = {exports: {}}; cache.set(file, module);
    const code = ts.transpileModule(fs.readFileSync(file, 'utf8'), {fileName: file, compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true}}).outputText;
    const localRequire = id => {
      if (!id.startsWith('.') && !id.startsWith('@/')) return require(id);
      const base = id.startsWith('@/') ? path.join(root, id.slice(2)) : path.resolve(path.dirname(file), id);
      const target = [base, `${base}.ts`, `${base}.tsx`, `${base}.json`].find(candidate => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
      if (!target) throw new Error(`Cannot resolve ${id} from ${file}`);
      return load(target);
    };
    new Function('require', 'module', 'exports', code)(localRequire, module, module.exports);
    return module.exports;
  }
  return {...load(path.join(root, 'lib/citation-plan.ts')), ...load(path.join(root, 'lib/mechanisms.ts')), ...load(path.join(root, 'lib/review-access.ts'))};
}

export async function auditRepository(root = ROOT) {
  const files = {canonical: 'data/content.json', publicContent: 'data/public-content.json', discovery: 'data/discovery-pages.json', reader: 'data/public-reader-evidence.json', mechanisms: 'data/public-mechanisms.json', reviews: 'data/private-reviews.json', envelopes: 'data/review-envelopes.json', aliases: 'editorial/reader-source-aliases.json'};
  const inputs = {}, inputHashes = {};
  for (const [key, file] of Object.entries(files)) {
    const bytes = fs.readFileSync(path.join(root, file)); inputs[key] = JSON.parse(bytes); inputHashes[file] = sha256(bytes);
  }
  for (const file of ['lib/citation-plan.ts', 'lib/mechanisms.ts', 'lib/review-access.ts', 'components/shared-theme/universal-article.ts']) inputHashes[file] = sha256(fs.readFileSync(path.join(root, file)));
  return {...await buildCoverage(inputs, loadContracts(root)), inputHashes};
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const args = process.argv.slice(2);
    if (args.length !== 2 || args[0] !== '--output') throw new Error('Usage: node scripts/research-review-coverage.mjs --output <private-ledger.json>');
    const output = path.resolve(args[1]);
    for (const directory of ['data', 'public', 'dist', 'editorial']) if (output === path.join(ROOT, directory) || output.startsWith(path.join(ROOT, directory) + path.sep)) throw new Error('Ledger output must be outside canonical data, editorial inputs and public/build assets.');
    const ledger = await auditRepository();
    fs.mkdirSync(path.dirname(output), {recursive: true});
    fs.writeFileSync(output, JSON.stringify(ledger, null, 2) + '\n', {mode: 0o600});
    console.log(JSON.stringify({output, denominatorStatus: ledger.denominatorStatus, counts: ledger.counts, issues: ledger.issues.length}));
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
