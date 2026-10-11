import type {Source} from '@/lib/peptides';
import type {ProseBlock} from '@/lib/canonical-guides';
import {CitedText} from './cited-text';
import {FaqItem} from './faq-item';

/** Question-led blocks collapse; ordinary explanations remain visible. */
export function CanonicalProse({blocks, sources, currentPage}: {blocks: ProseBlock[]; sources: Source[]; currentPage?:string}) {
  return <div className="guide-prose">{blocks.map(block => {
    const answer = <section className={block.title ? undefined : 'section-answer'} id={block.title ? undefined : block.id} data-prose-section>
      {block.anchors.map(anchor => <span id={anchor} key={anchor} aria-hidden="true"/>)}
      <p className="answer-paragraph" data-prose><CitedText sentences={block.sentences} references={sources} currentPage={currentPage}/></p>
    </section>;
    return block.title
      ? <FaqItem key={block.id} id={block.id} question={block.title}>{answer}</FaqItem>
      : <div key={block.id}>{answer}</div>;
  })}</div>;
}
