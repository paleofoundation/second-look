/**
 * Shared drug/condition article composition. Page-authored headings never define
 * the left navigation. This module is data-only and preserves source section
 * objects and their legacy IDs; it performs no scientific transformation.
 *
 * Render blocks in order. Within each module, render `sections` in order, then
 * its built-in mechanism/FAQ/research content where applicable, then `scoped`.
 * Citation traversal must consume that same sequence. The early findings block
 * is an Evidence projection, not an additional navigation section.
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
  /** Fallback for an unpopulated prose module; never a scientific conclusion. */
  emptyText: string;
  scoped?: { id: 'condition-details'; title: string; sections: S[] };
};

export type UniversalArticleBlock<S extends UniversalArticleSection> =
  | { kind: 'module'; module: UniversalArticleModule<S> }
  | { kind: 'findings'; id: 'findings' };

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

const missingText: Record<UniversalArticleLabel, string> = {
  Overview: 'An overview of this topic is not yet available in this article.',
  Mechanisms: 'A source-backed mechanism assessment is not yet available in this article.',
  Benefits: 'A drug-wide assessment of potential benefits is not yet available. Individual findings remain specific to their studied condition, population and outcome.',
  Safety: 'A complete safety assessment is not yet available in this article. Missing assessment is not evidence of safety.',
  Contraindications: 'Contraindications have not been fully assessed for this article.',
  Interactions: 'Drug interactions have not been fully assessed for this article.',
  Dosing: 'Studied doses and exposure have not been assessed across the uses covered here. This article does not provide personal dosing instructions.',
  Results: 'A complete results synthesis is not yet available. Individual reported outcomes retain their own populations, comparators and follow-up periods.',
  Quality: 'A complete assessment of source quality and study limitations is not yet available.',
  Status: 'Evidence coverage and assessment remain incomplete.',
  FAQs: 'Page-specific questions and answers are not yet available.',
  Evidence: 'A complete evidence assessment is not yet available for this article.',
  Connections: 'Related reading has not yet been mapped for this article.',
  Research: 'Source records are not yet available for this article.',
  Options: 'An assessment of the investigated drug options is not yet available for this condition.',
  Comparisons: 'A supported comparison of the investigated options is not yet available.',
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
    emptyText: missingText[label],
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
  const blocks: UniversalArticleBlock<S>[] = modules.flatMap(module =>
    module.kind === 'mechanisms'
      ? [{ kind: 'module', module }, { kind: 'findings', id: 'findings' }] as UniversalArticleBlock<S>[]
      : [{ kind: 'module', module }],
  );
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
  for (const module of plan.modules) {
    const expectedSections = input.sections.filter(section => sectionDestination(input.type, section.label) === module.label);
    if (expectedSections.length !== module.sections.length || expectedSections.some((section, index) => module.sections[index] !== section))
      errors.push('Section order or destination changed within ' + module.label + '.');
    if (module.scoped && module.label !== 'Evidence') errors.push('Scoped sections must remain inside Evidence.');
  }
  const findingsIndexes = plan.blocks.flatMap((block, index) => block.kind === 'findings' ? [index] : []);
  const mechanismIndex = plan.blocks.findIndex(block => block.kind === 'module' && block.module.kind === 'mechanisms');
  if (findingsIndexes.length !== 1 || findingsIndexes[0] !== mechanismIndex + 1)
    errors.push('Exactly one early findings projection must follow Mechanisms.');
  const renderedModules = plan.blocks.flatMap(block => block.kind === 'module' ? [block.module] : []);
  if (renderedModules.length !== plan.modules.length || plan.modules.some((module, index) => renderedModules[index] !== module))
    errors.push('Rendering blocks differ from the canonical modules.');
  return errors;
}
