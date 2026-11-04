import {content, guideUrl, type Source, type SourceDetail} from './content';

/** Presentation of already-public source fields. No extraction or appraisal occurs here. */
export function studyFacts(source: Source): {label: string; value: string}[] {
  const detail = source as SourceDetail;
  const values: [string, unknown][] = [
    ['Study design', source.design], ['Population or model', source.population],
    ['Randomized participants', source.randomizedN],
    ['Reported sample', detail.sampleDescription || (source.n !== source.randomizedN ? source.n : undefined)],
    ['Intervention', source.intervention], ['Comparator', source.comparator],
  ];
  return values.filter(([, value]) => value !== null && value !== undefined && String(value).trim() !== '' && !/^(unknown|not recorded|not extracted)$/i.test(String(value)))
    .map(([label, value]) => ({label, value: String(value)}));
}

export function studyTopics(source: Source) {
  return content.guides.filter(guide => ['Drug', 'Condition'].includes(guide.type) && guide.sourceIds.includes(source.id))
    .map(guide => ({id: guide.id, label: guide.title, href: guideUrl(guide), type: guide.type}));
}

export function studyHeadline(source: Source): string {
  const topics = studyTopics(source);
  const drug = topics.find(topic => topic.type === 'Drug');
  const conditions = topics.filter(topic => topic.type === 'Condition');
  if (drug && conditions.length === 1) return `${drug.label} and ${conditions[0].label}: study summary`;
  if (drug) return `${drug.label}: study summary`;
  if (conditions.length === 1) return `${conditions[0].label}: study summary`;
  return 'Research study summary';
}

export function sourceIntegrity(source: Source): {label: string; text: string} | null {
  if (source.status === 'Quarantined') return {label: 'Source integrity notice', text: source.correction || source.decisiveLimit || 'This source is quarantined and is not evidence for efficacy.'};
  if (source.correction) return {label: 'Correction notice', text: source.correction};
  return null;
}

export function sourceLocationText(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return [...new Set(value.filter(item => item && typeof item === 'object').map(item => {
    const record = item as Record<string, unknown>;
    return [record.chapter, record.section, record.table_figure,
      record.pdf_page != null ? `PDF page ${record.pdf_page}` : null,
      record.printed_page != null ? `Printed page ${record.printed_page}` : null,
      record.nativeLocator].filter(part => typeof part === 'string' && part.trim()).join(' · ');
  }).filter(Boolean))];
}

export const STUDY_QUESTIONS = [
  'What was studied?', 'Who was studied?',
  'What were the most important findings?', 'What are the greatest implications of this study?',
] as const;

export function studyDesignLabel(source: Source): string | undefined {
  const design=source.design;
  if (!design) return undefined;
  if (/systematic review|meta.analysis/i.test(design)) return 'Systematic review';
  if (/narrative review/i.test(design)) return 'Narrative review';
  if (/randomi[sz]ed/i.test(design)) return 'Randomized trial';
  if (/mouse|mice|rat\b|animal|cell|preclinical|hepatocyte|xenograft/i.test(design)) return 'Preclinical study';
  if (/cohort|observational|case.control|cross.sectional/i.test(design)) return 'Observational study';
  if (/protocol/i.test(design)) return 'Study protocol';
  return design;
}
