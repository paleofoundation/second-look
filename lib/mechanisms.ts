import mechanisms from '@/data/public-mechanisms.json';
import type {Guide} from './content';

export function hasMechanismSection(guide: Guide) {
  return !['Glossary', 'Practical guide'].includes(guide.type);
}

export function mechanismContextsFor(guide: Guide) {
  return mechanisms.contexts.filter(context => ((guide.type === 'Drug' && guide.entityId === context.drugId) || (guide.type === 'Condition' && context.conditionIds.includes(guide.entityId || ''))) && context.sourceIds.every(id => guide.sourceIds.includes(id)));
}

export const mechanismPresentation = {
  heading: 'Mechanism of Action',
  introduction: 'A mechanism describes how a drug affects a biological target or process. The reason it is being studied for another condition is a separate question from whether it improves outcomes in people.',
  originalHeading: 'Action in its original use',
  originalUnavailable: 'A source-backed explanation of the drug’s original action is not yet available in this article.',
  proposedHeading: 'Rationale for other uses',
  proposedUnavailable: 'A reviewed, condition-specific mechanism summary is not yet available here.',
  evidenceBoundary: 'Laboratory activity, a proposed pathway or a change in a biomarker does not by itself establish a clinical benefit.',
  detailLabels: {target: 'Target or pathway', action: 'Biological action', model: 'Population or model'},
};
