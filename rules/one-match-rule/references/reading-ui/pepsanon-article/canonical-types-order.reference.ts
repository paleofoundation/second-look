export type ProseBlock = {id: string; title?: string; sentences: CitedSentence[]; anchors: string[]};
export type CanonicalGuide = {
  overview: CitedSentence[];
  sections: Record<string, ProseBlock[]>;
  faqs: {id: string; question: string; sentences: CitedSentence[]}[];
};
export function guideSentences(guide: CanonicalGuide): CitedSentence[] {
  return [...guide.overview, ...Object.values(guide.sections).flatMap(blocks => blocks.flatMap(block => block.sentences)), ...guide.faqs.flatMap(faq => faq.sentences)];
}
