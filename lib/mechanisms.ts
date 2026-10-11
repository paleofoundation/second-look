import rawMechanisms from '@/data/public-mechanisms.json';
import type {CitedSentence, Guide} from './content';

export type MechanismProse = {text: string; sourceIds: string[]; sentences?: CitedSentence[]};
export type DrugMechanism = {
  drugId?: string;
  conditionId?: string;
  guideIds?: string[];
  summary?: MechanismProse;
  originalAction?: MechanismProse;
  questions?: (MechanismProse & {id: string; title: string})[];
};
type MechanismContextRecord = {
  id: string; drugId: string; conditionIds: string[]; title: string;
  text: string; sourceIds: string[]; evidenceType: string; locator: string;
  clinicalMeaning: string;
};
const mechanisms = rawMechanisms as {contexts: MechanismContextRecord[]; drugs?: DrugMechanism[]};

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

/** Matches MechanismSection's visible prose, question answers, then contexts. */
export function mechanismCitationIds(guide: Guide) {
  const record = drugMechanismFor(guide);
  const proseIds = (prose?: MechanismProse) =>
    prose?.sentences ? prose.sentences.flatMap(sentence => sentence.sources) : prose?.sourceIds || [];
  return [
    ...proseIds(record?.originalAction),
    ...proseIds(record?.summary),
    ...(record?.questions || []).flatMap(proseIds),
    ...mechanismContextsFor(guide).flatMap(context => context.sourceIds),
  ];
}

export const mechanismPresentation = {
  heading: 'Mechanism of Action',
  detailLabels: {target: 'Target or pathway', action: 'Biological action', model: 'Population or model'},
};
