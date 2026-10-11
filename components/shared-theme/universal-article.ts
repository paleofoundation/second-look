/**
 * Shared drug/condition article composition. Page-authored headings never define
 * the left navigation. This module is data-only and preserves source section
 * objects and their legacy IDs; it performs no scientific transformation.
 *
 * Render blocks in order. Within each module, render `sections` in order, then
 * its built-in mechanism/FAQ/research content where applicable, then `scoped`.
 * Citation traversal must consume that same sequence. Outcome synthesis belongs
 * in the single Evidence module; former findings links remain aliases there.
 */
export type UniversalPostType = 'Drug' | 'Condition';

export type UniversalArticleSection = { id: string; label: string };

export const UNIVERSAL_ARTICLE_LABELS = {
  Drug: ['Overview', 'Mechanisms', 'Benefits', 'Safety', 'Contraindications',
    'Interactions', 'Dosing', 'Results', 'Quality', 'Status', 'FAQs',
    'Evidence', 'Connections', 'Research'],
  Condition: ['Overview', 'Options', 'Mechanisms', 'Evidence', 'Safety',
    'Comparisons', 'FAQs', 'Connections', 'Research'],
} as const;

export type UniversalArticleLabel =
  (typeof UNIVERSAL_ARTICLE_LABELS)[UniversalPostType][number];

export type UniversalArticleNavItem = {
  id: string;
  label: UniversalArticleLabel;
  children?: { id: string; label: 'Studies' | 'References' }[];
};

export type UniversalArticleModule<S extends UniversalArticleSection> = {
  kind: 'prose' | 'mechanisms' | 'faqs' | 'research';
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
  if (label === 'Research') return 'research';
  return 'section-' + label.toLowerCase();
}

function moduleKind(label: UniversalArticleLabel): UniversalArticleModule<UniversalArticleSection>['kind'] {
  if (label === 'Mechanisms') return 'mechanisms';
  if (label === 'FAQs') return 'faqs';
  if (label === 'Research') return 'research';
  return 'prose';
}

function sectionDestination(type: UniversalPostType, label: string): UniversalArticleLabel {
  const normalized = label.trim().toLowerCase();
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
    modules.find(module => module.label === destination)!.sections.push(section);
  }
  if (input.scopedSections?.length) {
    modules.find(module => module.label === 'Evidence')!.scoped = {
      id: 'condition-details',
      title: input.scopedSectionsTitle || 'Condition-specific research details',
      sections: [...input.scopedSections],
    };
  }
  const blocks: UniversalArticleBlock<S>[] = modules.map(module => ({ kind: 'module', module }));
  const navigation: UniversalArticleNavItem[] = modules.map(module => ({
    id: module.id,
    label: module.label,
    ...(module.kind === 'research' ? {
      children: [{ id: 'studies', label: 'Studies' }, { id: 'references', label: 'References' }] as UniversalArticleNavItem['children'],
    } : {}),
  }));
  return { type: input.type, modules, blocks, navigation };
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
  if (JSON.stringify(children) !== JSON.stringify([['Research', 'studies', 'Studies'], ['Research', 'references', 'References']]))
    errors.push('Only Research may have children, exactly Studies and References.');
  const original = [...input.sections, ...(input.scopedSections || [])];
  const preserved = plan.modules.flatMap(module => [...module.sections, ...(module.scoped?.sections || [])]);
  const counts = new Map<S, number>();
  for (const section of original) counts.set(section, (counts.get(section) || 0) + 1);
  for (const section of preserved) counts.set(section, (counts.get(section) || 0) - 1);
  if ([...counts.values()].some(count => count !== 0))
    errors.push('Original section objects were lost, duplicated or replaced.');
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
