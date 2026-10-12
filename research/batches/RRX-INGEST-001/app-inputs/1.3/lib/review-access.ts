import { hasCurrentIntake, type ReaderProfile } from './account-contract';
import type { ReaderIdentity } from './profile-api';

export const REVIEW_ACCESS_POLICY = 'free_authenticated' as const;
export type PublicReviewPreview = {
  id: string; title: string; route: string; sourceUrl: string | null;
  preview: string; decisiveLimit: string; reviewState: 'pending' | 'released' | 'withdrawn';
  version: string; sourceIds: string[];
};
export type ReviewRelease = {
  state: 'pending' | 'released' | 'withdrawn'; version: string;
  contentSha256: string; approvedSha256: string | null;
  humanEditorialApproved: boolean;
  clinicalSafetyReviewRequired: boolean; qualifiedClinicalApproval: boolean;
};
export type ReviewEnvelope = { preview: PublicReviewPreview; release: ReviewRelease };
export type ReviewSection = {
  id: 'summary' | 'methods' | 'results' | 'limits' | 'sources'; title: string;
  paragraph: string; sources: string[];
  sentences?: { text: string; sources: string[] }[];
};
export type ReviewQuestionId = `Q${'01'|'02'|'03'|'04'|'05'|'06'|'07'|'08'|'09'|'10'|'11'|'12'|'13'|'14'|'15'}`;
export type ReviewQuestionStatus = 'complete' | 'not_applicable' | 'partial' | 'not_extracted' | 'not_checked' | 'not_accessible' | 'not_identifiable' | 'not_reported';
export type ReviewAnswerLocator = {
  paper_id?: string; sourceId?: string; source_url?: string | null;
  file?: string | null; filename?: string | null; sha256?: string | null;
  pdf_page?: number | null; printed_page?: number | string | null;
  section?: string | null; table_figure?: string | null; paragraph?: string | number | null;
  chapter?: string | null; nativeLocator?: string | null;
  basis?: string | null; missingness?: string | null;
};
export type ReviewQuestionAnswer = {
  id: ReviewQuestionId; question: string; answer: string; status: ReviewQuestionStatus;
  sources: string[]; locators: ReviewAnswerLocator[];
  render: { section: ReviewSection['id']; fragment: string; existingSection?: string; requiresAnswerDetailRender?: boolean };
  acceptedRecordPointer?: string; requiredInputFields?: string[]; extractionBasis?: string;
  unresolvedInputReason?: string | null; nextAction?: string; verificationState?: string; contentClass?: string;
};
export type ReviewOpeningBlock = { id: string; title: string; questionIds: ReviewQuestionId[] };
export type ProtectedReview = {
  id: string; version: string; contentSha256: string;
  sections: ReviewSection[]; sourceIds: string[];
  questionAnswers?: ReviewQuestionAnswer[]; openingBlocks?: ReviewOpeningBlock[];
};
export type ReviewRepository = {
  /** This method reads metadata/preview only, never a full-body file or database column. */
  getPublic(id: string): Promise<ReviewEnvelope | null>;
  /** Called only after a session, persisted intake and release grant. */
  readProtected(id: string): Promise<ProtectedReview | null>;
};
export type ReviewAccessReason = 'signed_out' | 'intake_required' | 'review_pending' | 'review_withdrawn' | 'approval_missing' | 'review_incomplete' | 'content_unavailable';
export type ReviewAccess =
  | { kind: 'not_found' }
  | { kind: 'preview'; policy: typeof REVIEW_ACCESS_POLICY; preview: PublicReviewPreview; reason: ReviewAccessReason }
  | { kind: 'full'; policy: typeof REVIEW_ACCESS_POLICY; preview: PublicReviewPreview; review: ProtectedReview };

/** Explicit allowlist: added private properties never propagate into a public response. */
export function serializePublicPreview(value: PublicReviewPreview): PublicReviewPreview {
  const sourceUrl = value.sourceUrl && /^https:\/\//i.test(value.sourceUrl) ? value.sourceUrl : null;
  return {
    id: value.id, title: value.title, route: value.route, sourceUrl,
    preview: value.preview, decisiveLimit: value.decisiveLimit,
    reviewState: value.reviewState, version: value.version, sourceIds: [...value.sourceIds],
  };
}
function serializeLocator(value: ReviewAnswerLocator): ReviewAnswerLocator {
  // Explicitly exclude arbitrary document fields/instructions from the response/hash.
  const out: ReviewAnswerLocator = {};
  const keys = ['paper_id','sourceId','source_url','file','filename','sha256','pdf_page','printed_page','section','table_figure','paragraph','chapter','nativeLocator','basis','missingness'] as const;
  for (const key of keys) if (value[key] !== undefined) (out as Record<string, unknown>)[key] = value[key];
  return out;
}
function serializeQuestion(value: ReviewQuestionAnswer): ReviewQuestionAnswer {
  return {
    id: value.id, question: value.question, answer: value.answer, status: value.status,
    sources: [...value.sources], locators: value.locators.map(serializeLocator),
    render: { section: value.render.section, fragment: value.render.fragment,
      ...(value.render.existingSection !== undefined ? {existingSection: value.render.existingSection} : {}),
      ...(value.render.requiresAnswerDetailRender !== undefined ? {requiresAnswerDetailRender: value.render.requiresAnswerDetailRender} : {}) },
    ...(value.acceptedRecordPointer !== undefined ? {acceptedRecordPointer:value.acceptedRecordPointer} : {}),
    ...(value.requiredInputFields !== undefined ? {requiredInputFields:[...value.requiredInputFields]} : {}),
    ...(value.extractionBasis !== undefined ? {extractionBasis:value.extractionBasis} : {}),
    ...(value.unresolvedInputReason !== undefined ? {unresolvedInputReason:value.unresolvedInputReason} : {}),
    ...(value.nextAction !== undefined ? {nextAction:value.nextAction} : {}),
    ...(value.verificationState !== undefined ? {verificationState:value.verificationState} : {}),
    ...(value.contentClass !== undefined ? {contentClass:value.contentClass} : {}),
  };
}
function serializeProtectedReview(value: ProtectedReview): ProtectedReview {
  return { id: value.id, version: value.version, contentSha256: value.contentSha256,
    sourceIds: [...value.sourceIds], sections: value.sections.map(section => ({
      id: section.id, title: section.title, paragraph: section.paragraph, sources: [...section.sources],
      ...(section.sentences ? { sentences: section.sentences.map(sentence => ({ text: sentence.text, sources: [...sentence.sources] })) } : {}),
    })),
    ...(value.questionAnswers ? {questionAnswers:value.questionAnswers.map(serializeQuestion)} : {}),
    ...(value.openingBlocks ? {openingBlocks:value.openingBlocks.map(block=>({id:block.id,title:block.title,questionIds:[...block.questionIds]}))} : {}),
  };
}
/** Structural prerequisite only; genuine exact-version human review remains mandatory. */
export function reviewQuestionCompletionIssues(review: ProtectedReview): string[] {
  const issues: string[] = [];
  const expected = Array.from({length:15},(_,i)=>'Q'+String(i+1).padStart(2,'0'));
  const answers = review.questionAnswers;
  if (!answers || answers.length !== 15 || new Set(answers.map(q=>q.id)).size !== 15 || expected.some(id=>!answers.some(q=>q.id===id))) return ['Exactly one of every Q01–Q15 is required.'];
  const useful = (text: unknown): text is string => typeof text === 'string' && text.trim().length > 0 && !/^(pending|not (?:yet )?(?:extracted|checked|accessible|reported)|not in corpus|not applicable|not identifiable|n\/?a|tbd|unknown|none)[.!]?$/i.test(text.trim());
  const located = (locator: ReviewAnswerLocator, sources: string[]) => {
    const id = locator.paper_id || locator.sourceId;
    if (!id || !sources.includes(id) || (locator.paper_id && locator.sourceId && locator.paper_id !== locator.sourceId)) return false;
    const identity = useful(locator.file) || useful(locator.filename) || (typeof locator.sha256==='string' && /^[a-f0-9]{64}$/.test(locator.sha256)) || (typeof locator.source_url==='string' && /^https:\/\//.test(locator.source_url));
    const location = useful(locator.section) || useful(locator.nativeLocator) || useful(locator.table_figure) || useful(locator.chapter) || (typeof locator.pdf_page==='number' && locator.pdf_page>0) || (typeof locator.printed_page==='number' && locator.printed_page>=0) || useful(locator.printed_page) || useful(locator.paragraph) || (typeof locator.paragraph==='number' && locator.paragraph>0);
    return identity && location && useful(locator.basis) && !['not_extracted','not_checked','not_accessible'].includes(locator.missingness||'');
  };
  for (const q of answers) {
    if (!['complete','not_applicable'].includes(q.status)) issues.push(q.id+': question remains incomplete.');
    if (!useful(q.question) || !useful(q.answer)) issues.push(q.id+': substantive question/answer or design-specific non-applicability rationale is missing.');
    if (q.unresolvedInputReason?.trim()) issues.push(q.id+': unresolved required input remains.');
    if (!q.sources.length || q.sources.some(id=>!review.sourceIds.includes(id))) issues.push(q.id+': unresolved source relationship.');
    if (!q.locators.length || q.locators.some(locator=>!located(locator,q.sources)) || q.sources.some(id=>!q.locators.some(locator=>(locator.paper_id||locator.sourceId)===id))) issues.push(q.id+': every source requires a usable exact locator.');
    if (!q.render || !review.sections.some(section=>section.id===q.render.section) || !/^[a-z][a-z0-9-]*$/.test(q.render.fragment)) issues.push(q.id+': answer has no valid rendered section/fragment.');
  }
  if (new Set(answers.map(q=>q.render.fragment)).size!==15) issues.push('Question fragments must be unique.');
  if (!review.openingBlocks) issues.push('The four required opening blocks are missing.');
  else {
    const requiredOpenings=['what-was-studied','who-was-studied','important-findings','implications'];
    if (review.openingBlocks.length!==4 || new Set(review.openingBlocks.map(b=>b.id)).size!==4 || requiredOpenings.some(id=>!review.openingBlocks!.some(block=>block.id===id))) issues.push('Opening blocks require the four canonical reader questions.');
    for (const block of review.openingBlocks) if (!useful(block.id)||!useful(block.title)||!block.questionIds.length||new Set(block.questionIds).size!==block.questionIds.length||block.questionIds.some(id=>!expected.includes(id))) issues.push('Opening block has invalid question references.');
  }
  return issues;
}
function canonical(value: unknown): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  const record = value as Record<string, unknown>;
  return '{' + Object.keys(record).sort().map(key => JSON.stringify(key) + ':' + canonical(record[key])).join(',') + '}';
}
/** Hash the actual allowlisted content; contentSha256 itself is excluded. */
export async function protectedReviewSha256(value: ProtectedReview): Promise<string> {
  const { contentSha256: _hash, ...payload } = serializeProtectedReview(value);
  const bytes = new TextEncoder().encode(canonical(payload));
  const hash = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(hash)].map(byte => byte.toString(16).padStart(2, '0')).join('');
}
function fullReleaseGranted(release: ReviewRelease): boolean {
  return release.state === 'released' && release.humanEditorialApproved === true &&
    /^[a-f0-9]{64}$/.test(release.contentSha256) && release.approvedSha256 === release.contentSha256 &&
    typeof release.clinicalSafetyReviewRequired === 'boolean' &&
    (!release.clinicalSafetyReviewRequired || release.qualifiedClinicalApproval === true);
}
/** No role, subscription, owner-name or browser flag can supply this grant. */
export async function evaluateReviewAccess(
  repository: ReviewRepository, id: string, user: ReaderIdentity | null, profile: ReaderProfile | null,
): Promise<ReviewAccess> {
  const envelope = await repository.getPublic(id);
  if (!envelope || envelope.preview.id !== id) return { kind: 'not_found' };
  const preview = serializePublicPreview(envelope.preview);
  const locked = (reason: ReviewAccessReason): ReviewAccess => ({ kind: 'preview', policy: REVIEW_ACCESS_POLICY, preview, reason });
  // Release state is independent of login. No promise that intake unlocks a pending draft.
  if (envelope.release.state === 'withdrawn' || preview.reviewState === 'withdrawn') return locked('review_withdrawn');
  if (envelope.release.state !== 'released' || preview.reviewState !== 'released') return locked('review_pending');
  if (!fullReleaseGranted(envelope.release) || envelope.release.version !== preview.version) return locked('approval_missing');
  if (!user) return locked('signed_out');
  if (!hasCurrentIntake(profile, user.userId)) return locked('intake_required');
  let value: ProtectedReview | null;
  try {
    value = await repository.readProtected(id);
    if (!value || value.id !== id || value.version !== envelope.release.version || value.contentSha256 !== envelope.release.contentSha256) return locked('content_unavailable');
    const full = serializeProtectedReview(value);
    if (await protectedReviewSha256(full) !== envelope.release.contentSha256) return locked('content_unavailable');
    if (reviewQuestionCompletionIssues(full).length) return locked('review_incomplete');
    return { kind: 'full', policy: REVIEW_ACCESS_POLICY, preview, review: full };
  } catch { return locked('content_unavailable'); }
}
