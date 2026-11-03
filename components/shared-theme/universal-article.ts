/**
 * Shared drug/condition article composition. Page-authored headings never define
 * the left navigation. This module is data-only and preserves source section
 * objects and their legacy IDs except for retired presentation sections; it
 * performs no scientific transformation and never mutates source records.
 *
 * Render blocks in order. Within each module, render `sections` in order, then
 * its built-in mechanism/FAQ/research content where applicable. In Evidence,
 * render authored prose, then `scoped` details, then the evidence table last.
 * Citation traversal must consume that same sequence. Outcome synthesis belongs
 * in the single Evidence module; former findings links remain aliases there.
 */
export type UniversalPostType = 'Drug' | 'Condition';

export type UniversalArticleSection = { id: string; label: string };

export const ARTICLE_READER_TAIL = ['Evidence', 'FAQs', 'Research Feed', 'Update History', 'References'] as const;

export const UNIVERSAL_ARTICLE_LABELS = {
  Drug: ['Overview', 'Mechanisms', 'Benefits', 'Safety', 'Contraindications',
    'Interactions', 'Dosing', 'Results', 'Quality', 'Status', ...ARTICLE_READER_TAIL],
  Condition: ['Overview', 'Options', 'Mechanisms', 'Safety', 'Comparisons', ...ARTICLE_READER_TAIL],
} as const;

export type UniversalArticleLabel =
  (typeof UNIVERSAL_ARTICLE_LABELS)[UniversalPostType][number];

export type UniversalArticleNavItem = {
  id: string;
  label: UniversalArticleLabel;
  children?: { id: string; label: string }[];
};

export type UniversalArticleModule<S extends UniversalArticleSection> = {
  kind: 'prose' | 'mechanisms' | 'faqs' | 'research' | 'updates' | 'references';
  id: string;
  label: UniversalArticleLabel;
  title: string;
  sections: S[];
  scoped?: { id: 'condition-details'; title: string; sections: S[] };
};

export type UniversalArticleBlock<S extends UniversalArticleSection> =
  { kind: 'module'; module: UniversalArticleModule<S> };

export type UniversalArticleInput<S extends UniversalArticleSection> = {
  type: UniversalPostType;
  sections: readonly S[];
  scopedSections?: readonly S[];
  scopedSectionsTitle?: string;
};

export type UniversalArticlePlan<S extends UniversalArticleSection> = {
  type: UniversalPostType;
  modules: UniversalArticleModule<S>[];
  blocks: UniversalArticleBlock<S>[];
  navigation: UniversalArticleNavItem[];
};

function moduleId(label: UniversalArticleLabel): string {
  if (label === 'Mechanisms') return 'mechanisms';
  if (label === 'FAQs') return 'faqs';
  if (label === 'Research Feed') return 'research-feed';
  if (label === 'Update History') return 'update-history';
  if (label === 'References') return 'references';
  return 'section-' + label.toLowerCase();
}

function moduleKind(label: UniversalArticleLabel): UniversalArticleModule<UniversalArticleSection>['kind'] {
  if (label === 'Mechanisms') return 'mechanisms';
  if (label === 'FAQs') return 'faqs';
  if (label === 'Research Feed') return 'research';
  if (label === 'Update History') return 'updates';
  if (label === 'References') return 'references';
  return 'prose';
}

/** Legacy relationship prose stays in the data, outside the reading sequence. */
export function isRetiredArticleSection(section: UniversalArticleSection): boolean {
  return section.label.trim().toLowerCase() === 'connections';
}

function sectionDestination(type: UniversalPostType, label: string): UniversalArticleLabel | null {
  const normalized = label.trim().toLowerCase();
  if (normalized === 'connections') return null;
  if (normalized === 'research') return 'Research Feed';
  if (normalized === 'gaps') return type === 'Drug' ? 'Status' : 'Evidence';
  return UNIVERSAL_ARTICLE_LABELS[type].find(candidate => candidate.toLowerCase() === normalized)
    ?? (type === 'Drug' ? 'Benefits' : 'Options');
}

export function buildUniversalArticlePlan<S extends UniversalArticleSection>(
  input: UniversalArticleInput<S>,
): UniversalArticlePlan<S> {
  const modules: UniversalArticleModule<S>[] = UNIVERSAL_ARTICLE_LABELS[input.type].map(label => ({
    kind: moduleKind(label),
    id: moduleId(label),
    label,
    title: label === 'Mechanisms' ? 'Mechanism of Action' : label,
    sections: [],
  }));
  for (const section of input.sections) {
    const destination = sectionDestination(input.type, section.label);
    if (destination === null) continue;
    modules.find(module => module.label === destination)!.sections.push(section);
  }
  const scopedSections = input.scopedSections?.filter(section => !isRetiredArticleSection(section)) || [];
  if (scopedSections.length) {
    modules.find(module => module.label === 'Evidence')!.scoped = {
      id: 'condition-details',
      title: input.scopedSectionsTitle || 'Condition-specific research details',
      sections: scopedSections,
    };
  }
  const blocks: UniversalArticleBlock<S>[] = modules.map(module => ({ kind: 'module', module }));
  const navigation: UniversalArticleNavItem[] = modules.map(module => ({
    id: module.id,
    label: module.label,
  }));
  return { type: input.type, modules, blocks, navigation };
}

/** Shared tail for other article types; navigation and body consume these modules. */
export function buildArticleReaderTail<S extends UniversalArticleSection>({
  includeEvidence = true, evidenceSections = [],
}: { includeEvidence?: boolean; evidenceSections?: S[] } = {}): UniversalArticleModule<S>[] {
  return ARTICLE_READER_TAIL.filter(label => includeEvidence || label !== 'Evidence').map(label => ({
    kind: moduleKind(label), id: moduleId(label), label, title: label,
    sections: label === 'Evidence' ? evidenceSections : [],
  }));
}

/** Pure acceptance checks, usable by generation and rendered-route checks. */
export function universalArticlePlanErrors<S extends UniversalArticleSection>(
  input: UniversalArticleInput<S>, plan: UniversalArticlePlan<S>,
): string[] {
  const errors: string[] = [];
  const expected = [...UNIVERSAL_ARTICLE_LABELS[input.type]];
  if (JSON.stringify(plan.navigation.map(item => item.label)) !== JSON.stringify(expected))
    errors.push('Navigation differs from the universal post-type contract.');
  if (JSON.stringify(plan.modules.map(module => module.label)) !== JSON.stringify(expected))
    errors.push('Module order differs from the universal post-type contract.');
  if (new Set(plan.navigation.map(item => item.id)).size !== expected.length)
    errors.push('Navigation targets are not unique.');
  if (plan.navigation.some(item => item.id !== moduleId(item.label)))
    errors.push('Navigation target differs from its canonical module ID.');
  const children = plan.navigation.flatMap(item => (item.children || []).map(child => [item.label, child.id, child.label]));
  if (children.length) errors.push('Research Feed and References are separate top-level sections.');
  const original = [...input.sections, ...(input.scopedSections || [])]
    .filter(section => !isRetiredArticleSection(section));
  const preserved = plan.modules.flatMap(module => [...module.sections, ...(module.scoped?.sections || [])]);
  if (preserved.some(isRetiredArticleSection))
    errors.push('Retired sections must not appear in article modules.');
  const counts = new Map<S, number>();
  for (const section of original) counts.set(section, (counts.get(section) || 0) + 1);
  for (const section of preserved) counts.set(section, (counts.get(section) || 0) - 1);
  if ([...counts.values()].some(count => count !== 0))
    errors.push('Active original section objects were lost, duplicated or replaced.');
  for (const articleModule of plan.modules) {
    const expectedSections = input.sections.filter(section => sectionDestination(input.type, section.label) === articleModule.label);
    if (expectedSections.length !== articleModule.sections.length || expectedSections.some((section, index) => articleModule.sections[index] !== section))
      errors.push('Section order or destination changed within ' + articleModule.label + '.');
    if (articleModule.scoped && articleModule.label !== 'Evidence') errors.push('Scoped sections must remain inside Evidence.');
  }
  const renderedModules = plan.blocks.flatMap(block => block.kind === 'module' ? [block.module] : []);
  if (renderedModules.length !== plan.modules.length || plan.modules.some((module, index) => renderedModules[index] !== module))
    errors.push('Rendering blocks differ from the canonical modules.');
  return errors;
}
