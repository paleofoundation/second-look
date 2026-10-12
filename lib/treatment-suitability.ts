import data from '@/data/treatment-suitability.json';

export const suitabilityCategoryLabels = {
  contraindication: 'Contraindication / label restriction',
  precaution: 'Precaution / individual review',
  interaction: 'Interaction review',
  applicability: 'Evidence applicability',
} as const;
export type SuitabilityCategory = keyof typeof suitabilityCategoryLabels;
export type SuitabilityRow = {
  id: string; drug: string; category: SuitabilityCategory; label: string;
  text: string; sourceIds: string[];
};
export const suitabilityScope = data.scope;
export const suitabilityCheckedOn = data.checkedOn;
export const suitabilitySources = data.sources;
export function suitabilityFor(path: string): SuitabilityRow[] {
  const drugs = (data.pages as Record<string, string[]>)[path] || [];
  return (data.rows as SuitabilityRow[]).filter(row => drugs.includes(row.drug));
}
export function suitabilityCitationIds(path: string): string[] {
  return [...new Set(suitabilityFor(path).flatMap(row => row.sourceIds))];
}
