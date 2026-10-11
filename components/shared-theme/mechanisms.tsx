import {Fragment, type ReactNode} from 'react';

export type MechanismPresentation = {
  heading: string;
  detailLabels: {target: string; action: string; model: string};
};
export type MechanismContext = {
  id: string;
  title: string;
  explanation: ReactNode;
  evidence: {
    basis: 'direct_measurement' | 'author_hypothesis' | 'computational_prediction' | 'secondary_description' | 'not_assessed';
    label: string;
    source: ReactNode;
    target?: string;
    action?: string;
    model?: string;
  };
  clinicalMeaning: string;
};

function ContextProse({context, content}: {context: MechanismContext; content: MechanismPresentation}) {
  const fields = (['target', 'action', 'model'] as const).filter(field => context.evidence[field]);
  return <>
    <p className="small muted" data-evidence-basis={context.evidence.basis}>{context.evidence.label}</p>
    {context.explanation}
    {fields.length > 0 && <p>{fields.map((field, index) => <Fragment key={field}>
      {index > 0 ? '; ' : ''}{content.detailLabels[field]}: {context.evidence[field]}
    </Fragment>)}</p>}
    {context.evidence.source}
    {context.clinicalMeaning && <p>{context.clinicalMeaning}</p>}
  </>;
}

/** One visible explanation; multiple bounded contexts reuse the canonical disclosure. */
export function MechanismSection({content, originalAction, summary, questions = [], contexts = []}: {
  content: MechanismPresentation;
  originalAction?: ReactNode;
  summary?: ReactNode;
  questions?: {id: string; title: string; answer: ReactNode}[];
  contexts?: MechanismContext[];
}) {
  return <section id="mechanisms" className="article-section mechanism-section">
    <h2>{content.heading}</h2>
    {originalAction}
    {summary}
    {questions.length > 0 && <div className="rgbc-faq-block">
      {questions.map(question => <details className="rgbc-faq-item" id={question.id} key={question.id}>
        <summary><span className="rgbc-faq-icon" aria-hidden="true"/><span className="rgbc-faq-q">{question.title}</span></summary>
        <div className="rgbc-faq-a"><strong>Quick answer</strong>{question.answer}</div>
      </details>)}
    </div>}
    {contexts.length === 1 && <div id={contexts[0].id}>
      <p><strong>{contexts[0].title}</strong></p>
      <ContextProse context={contexts[0]} content={content}/>
    </div>}
    {contexts.length > 1 && <div className="rgbc-faq-block">
      {contexts.map(context => <details className="rgbc-faq-item" id={context.id} key={context.id}>
        <summary><span className="rgbc-faq-icon" aria-hidden="true"/><span className="rgbc-faq-q">{context.title}</span></summary>
        <div className="rgbc-faq-a">
          <strong>Quick answer:</strong>
          <ContextProse context={context} content={content}/>
        </div>
      </details>)}
    </div>}
  </section>;
}
