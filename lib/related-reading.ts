import {content, guideUrl, type Guide} from './content';
import {drugMechanismFor} from './mechanisms';
import {wikiTokens} from './wiki-links';

function readingParagraphs(guide: Guide) {
  const mechanism = drugMechanismFor(guide);
  return [guide.description,
    ...[...guide.sections, ...(guide.scopedSections || [])]
      .filter(section => section.label.trim().toLowerCase() !== 'connections')
      .flatMap(section => [section.paragraph, ...(section.questions || []).map(question => question.answer)]),
    ...guide.faqs.map(faq => faq.answer), mechanism?.originalAction?.text,
    mechanism?.summary?.text, ...(mechanism?.pathways || []).map(pathway => pathway.text), ...(mechanism?.rationales || []).flatMap(row => [row.condition, row.rationale.text, row.tested.text, row.limits.text]), ...(mechanism?.questions || []).map(question => question.text),
  ].filter((text): text is string => !!text);
}

/** Editorial priority first; paragraph relevance fills gaps, never efficacy. */
export function relatedReadingFor(guide: Guide): Guide[] {
  const selected: Guide[] = [];
  const seen = new Set([guideUrl(guide)]);
  const add = (candidate?: Guide) => {
    if (!candidate || seen.has(guideUrl(candidate)) || selected.length >= 3) return;
    seen.add(guideUrl(candidate));
    selected.push(candidate);
  };
  // Resolve in authored order rather than filtering the global guide catalogue.
  guide.related.forEach(id => add(content.guides.find(candidate => candidate.id === id)));
  if (selected.length === 3) return selected;

  const mentions = new Map<string, number>();
  for (const paragraph of readingParagraphs(guide)) {
    for (const href of new Set(wikiTokens(paragraph, guideUrl(guide)).flatMap(token => token.href ? [token.href] : [])))
      mentions.set(href, (mentions.get(href) || 0) + 1);
  }
  if (guide.type === 'Glossary') {
    for (const candidate of content.guides) {
      const count = readingParagraphs(candidate).filter(paragraph =>
        wikiTokens(paragraph, guideUrl(candidate)).some(token => token.href === guideUrl(guide))).length;
      if (count) mentions.set(guideUrl(candidate), count);
    }
  }
  const opposite = guide.type === 'Drug' ? 'Condition' : guide.type === 'Condition' ? 'Drug' : '';
  content.guides.filter(candidate => mentions.has(guideUrl(candidate)))
    .sort((a, b) => Number(b.type === opposite) - Number(a.type === opposite)
      || mentions.get(guideUrl(b))! - mentions.get(guideUrl(a))!
      || a.title.localeCompare(b.title) || guideUrl(a).localeCompare(guideUrl(b)))
    .forEach(add);
  // Retain valid canonical relationships when prose offers fewer than three.
  for (const link of guide.candidateLinks || [])
    add(content.guides.find(candidate => guideUrl(candidate) === link.url));
  return selected;
}
