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

type MechanismTextRenderer = (text: string, linked?: Set<string>) => ReactNode;
const plainText: MechanismTextRenderer = text => text;

function ContextProse({context, content, renderText}: {context: MechanismContext; content: MechanismPresentation; renderText: MechanismTextRenderer}) {
  const fields = (['target', 'action', 'model'] as const).filter(field => context.evidence[field]);
  const linked = new Set<string>();
  return <>
    <p className="small muted" data-evidence-basis={context.evidence.basis}>{renderText(context.evidence.label)}</p>
    {context.explanation}
    {fields.length > 0 && <p>{fields.map((field, index) => <Fragment key={field}>
      {index > 0 ? '; ' : ''}{content.detailLabels[field]}: {renderText(context.evidence[field]!, linked)}
    </Fragment>)}</p>}
    {context.evidence.source}
    {context.clinicalMeaning && <p>{renderText(context.clinicalMeaning)}</p>}
  </>;
}

/** One visible explanation; multiple bounded contexts reuse the canonical disclosure. */
export function MechanismSection({content, originalAction, summary, pathways = [], collapsiblePathways = false, rationales = [], rationalePlacement = 'article', showRationales = true, visibleQuestions = false, questions = [], contexts = [], renderText = plainText}: {
  content: MechanismPresentation;
  renderText?: MechanismTextRenderer;
  originalAction?: ReactNode;
  summary?: ReactNode;
  pathways?: {id: string; title: string; explanation: ReactNode}[];
  collapsiblePathways?: boolean;
  rationales?: {id: string; condition: string; conditionHref: string; evidenceHref?: string; rationale: ReactNode; tested: ReactNode; limits: ReactNode}[];
  rationalePlacement?: 'article' | 'evidence';
  showRationales?: boolean;
  visibleQuestions?: boolean;
  questions?: {id: string; title: string; answer: ReactNode}[];
  contexts?: MechanismContext[];
}) {
  const movedRationales = rationalePlacement === 'evidence' ? rationales.filter(row => row.evidenceHref) : [];
  const articleRationales = rationales.filter(row => !movedRationales.includes(row));
  return <section id="mechanisms" className={`article-section mechanism-section${showRationales && articleRationales.length ? ' mechanism-pilot' : ''}`}>
    <h2>{content.heading}</h2>
    {originalAction}
    {summary}
    {collapsiblePathways ? <div className="rgbc-faq-block mechanism-pathway-disclosures">
      {pathways.map(pathway => <details className="rgbc-faq-item" id={pathway.id} key={pathway.id}>
        <summary><span className="rgbc-faq-icon" aria-hidden="true"/><h3 className="rgbc-faq-q">{pathway.title}</h3></summary>
        <div className="rgbc-faq-a">{pathway.explanation}</div>
      </details>)}
    </div> : pathways.map(pathway => <div className="mechanism-pathway" id={pathway.id} key={pathway.id}>
      <h3>{pathway.title}</h3>{pathway.explanation}
    </div>)}
    {!showRationales && <><span id="condition-rationales" aria-hidden="true"/>{rationales.map(row => visibleQuestions ? <div className="mechanism-rationale-prose" id={row.id} key={row.id}><h3>{row.condition}</h3>{row.rationale}{row.tested}{row.limits}{row.evidenceHref?<p><a href={row.evidenceHref}>View the corresponding evidence</a></p>:null}</div> : <span id={row.id} key={row.id} aria-hidden="true"/>)}</>}
    {showRationales && rationales.length > 0 && <>
      <h3 id="condition-rationales">Rationale by condition</h3>
      {movedRationales.length > 0 && <div className="mechanism-evidence-links">
        <p>Proposed mechanisms, measurements and limitations are included with the studies in Evidence.</p>
        <p className="small mechanism-evidence-link">{movedRationales.map((row, index) => <Fragment key={row.id}>
          {index > 0 ? ' · ' : ''}<span id={row.id}><a href={row.evidenceHref}>{row.condition}</a></span>
        </Fragment>)}</p>
      </div>}
      {articleRationales.length > 0 && <>
      <figure className="wp-block-table mechanism-rationale-table">
        <table role="table" aria-labelledby="condition-rationales">
          <thead role="rowgroup"><tr role="row">
            {['Condition', 'Mechanism and rationale', 'What was tested', 'Limits'].map(label => <th role="columnheader" scope="col" key={label}>{label}</th>)}
          </tr></thead>
          <tbody role="rowgroup">{articleRationales.map(row => <tr role="row" id={row.id} key={row.id}>
            <th role="rowheader" scope="row"><a href={row.conditionHref}>{row.condition}</a></th>
            {(['rationale', 'tested', 'limits'] as const).map((field, index) => <td role="cell" key={field}>
              <span className="mechanism-cell-label" aria-hidden="true">{['Mechanism and rationale', 'What was tested', 'Limits'][index]}</span>
              {row[field]}
            </td>)}
          </tr>)}</tbody>
        </table>
      </figure>
      <p className="small mechanism-evidence-link">For treatment outcomes, see <a href="#section-evidence">Evidence</a>.</p>
      </>}
    </>}
    {visibleQuestions && questions.map(question => <div className="mechanism-pathway" id={question.id} key={question.id}><h3>{question.title}</h3>{question.answer}</div>)}
    {!visibleQuestions && questions.length > 0 && <div className="rgbc-faq-block">
      {questions.map(question => <details className="rgbc-faq-item" id={question.id} key={question.id}>
        <summary><span className="rgbc-faq-icon" aria-hidden="true"/><span className="rgbc-faq-q">{question.title}</span></summary>
        <div className="rgbc-faq-a"><strong>Quick answer</strong>{question.answer}</div>
      </details>)}
    </div>}
    {contexts.length === 1 && <div id={contexts[0].id}>
      <p><strong>{contexts[0].title}</strong></p>
      <ContextProse context={contexts[0]} content={content} renderText={renderText}/>
    </div>}
    {contexts.length > 1 && <div className="rgbc-faq-block">
      {contexts.map(context => <details className="rgbc-faq-item" id={context.id} key={context.id}>
        <summary><span className="rgbc-faq-icon" aria-hidden="true"/><span className="rgbc-faq-q">{context.title}</span></summary>
        <div className="rgbc-faq-a">
          <strong>Quick answer:</strong>
          <ContextProse context={context} content={content} renderText={renderText}/>
        </div>
      </details>)}
    </div>}
  </section>;
}
