import rawMechanisms from '@/data/public-mechanisms.json';
import {content, guideUrl, synthesisRows, type CitedSentence, type Guide, type SynthesisRow} from './content';

export type MechanismProse = {text: string; sourceIds: string[]; sentences?: CitedSentence[]};
export type MechanismRationale = {id: string; condition: string; conditionHref: string; rationale: MechanismProse; tested: MechanismProse; limits: MechanismProse};
export type EvidenceMechanism = {
  id: string;
  title: string;
  rationale: MechanismProse;
  tested?: MechanismProse;
  limits?: MechanismProse;
  sourceIds: string[];
  evidenceType?: string;
  locator?: string;
};
export type RationalePlacement = 'article' | 'evidence';
export type DrugMechanism = {
  drugId?: string;
  conditionId?: string;
  guideIds?: string[];
  summary?: MechanismProse;
  originalAction?: MechanismProse;
  questions?: (MechanismProse & {id: string; title: string})[];
  presentation?: 'pathway-table-pilot';
  pathways?: (MechanismProse & {id: string; title: string})[];
  rationales?: MechanismRationale[];
};
type MechanismContextRecord = {
  id: string; drugId: string; conditionIds: string[]; title: string;
  text: string; sourceIds: string[]; evidenceType: string; locator: string;
  clinicalMeaning: string;
};
const mechanisms = rawMechanisms as {contexts: MechanismContextRecord[]; drugs?: DrugMechanism[]};

function proseCitationIds(prose?: MechanismProse) {
  return prose?.sentences ? prose.sentences.flatMap(sentence => sentence.sources) : prose?.sourceIds || [];
}

function rationaleConditionIds(drugId: string, rationale: MechanismRationale) {
  const path = rationale.conditionHref.split(/[?#]/)[0].replace(/\/$/, '');
  const canonical = content.guides.find(guide => guide.type === 'Condition' && guideUrl(guide).replace(/\/$/, '') === path)?.entityId;
  // This authored rationale explicitly covers acute viral measurements and the
  // separate Long COVID prevention/treatment limits. Its primary route is C01;
  // C02 shares that exact source-bound explanation, not a new clinical claim.
  const additional = drugId === 'D01' && rationale.id === 'metformin-mechanism-1' ? ['C02'] : [];
  return [...new Set([...(canonical ? [canonical] : []), ...additional])];
}

/** Only exact authored drug/condition relationships enter an outcome drawer. */
export function evidenceMechanismsFor(drugId: string, conditionId: string): EvidenceMechanism[] {
  const rationales = mechanisms.drugs?.find(record => record.drugId === drugId)?.rationales || [];
  const authored = rationales.filter(rationale => rationaleConditionIds(drugId, rationale).includes(conditionId)).map(row => ({
    id: row.id,
    title: row.condition,
    rationale: row.rationale,
    tested: row.tested,
    limits: row.limits,
    sourceIds: [...new Set([row.rationale, row.tested, row.limits].flatMap(proseCitationIds))],
  }));
  if (authored.length) return authored;
  // A condition overview may describe several drugs or disease biology. Do not
  // infer a drug assignment from shared sources or attach that overview wholesale.
  return mechanisms.contexts.filter(context => context.drugId === drugId && context.conditionIds.includes(conditionId)).map(context => ({
    id: context.id,
    title: context.title,
    rationale: {text: context.text, sourceIds: context.sourceIds},
    ...(context.clinicalMeaning ? {limits: {text: context.clinicalMeaning, sourceIds: context.sourceIds}} : {}),
    sourceIds: context.sourceIds,
    evidenceType: context.evidenceType,
    locator: context.locator,
  }));
}

export function evidenceMechanismSourceIds(rows: Pick<SynthesisRow, 'drugId' | 'conditionId'>[]) {
  return [...new Set(rows.flatMap(row => evidenceMechanismsFor(row.drugId, row.conditionId).flatMap(mechanism => mechanism.sourceIds)))];
}

/** Preserve a rationale in the article when this page has no matching evidence row. */
export function mechanismEvidenceHref(guide: Guide, rationaleId: string) {
  const record = drugMechanismFor(guide);
  const rationale = record?.rationales?.find(row => row.id === rationaleId);
  if (!rationale || !record?.drugId) return undefined;
  const row = rationaleConditionIds(record.drugId, rationale).map(conditionId => synthesisRows.find(row => guide.synthesisIds?.includes(row.id) && row.drugId === record.drugId && row.conditionId === conditionId)).find(Boolean);
  return row ? `#${row.id}` : undefined;
}

export function drugMechanismFor(guide: Guide) {
  return mechanisms.drugs?.find(record =>
    (guide.type === 'Drug' && record.drugId === guide.entityId) ||
    (guide.type === 'Condition' && record.conditionId === guide.entityId) || record.guideIds?.includes(guide.id));
}

export function mechanismContextsFor(guide: Guide) {
  // Authored mechanisms incorporate the relevant context in the same reading order.
  if (drugMechanismFor(guide)) return [];
  return mechanisms.contexts.filter(context =>
    ((guide.type === 'Drug' && guide.entityId === context.drugId) ||
      (guide.type === 'Condition' && context.conditionIds.includes(guide.entityId || ''))) &&
    context.sourceIds.every(id => guide.sourceIds.includes(id)));
}

export function hasMechanismSection(guide: Guide) {
  return guide.type === 'Drug' || guide.type === 'Condition' ||
    !!drugMechanismFor(guide) || mechanismContextsFor(guide).length > 0;
}

/** Matches rendered prose, pathways, condition rows, question answers, then contexts. */
export function mechanismCitationIds(guide: Guide, rationalePlacement: RationalePlacement = 'article') {
  const record = drugMechanismFor(guide);
  return [
    ...proseCitationIds(record?.originalAction),
    ...proseCitationIds(record?.summary),
    ...(record?.pathways || []).flatMap(proseCitationIds),
    ...(record?.rationales || []).filter(row => rationalePlacement !== 'evidence' || !mechanismEvidenceHref(guide, row.id)).flatMap(row => [row.rationale, row.tested, row.limits].flatMap(proseCitationIds)),
    ...(record?.questions || []).flatMap(proseCitationIds),
    ...mechanismContextsFor(guide).flatMap(context => context.sourceIds),
  ];
}

export const mechanismPresentation = {
  heading: 'Mechanism of Action',
  detailLabels: {target: 'Target or pathway', action: 'Biological action', model: 'Population or model'},
};
