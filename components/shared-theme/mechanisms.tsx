import type {ReactNode} from 'react';

export type MechanismPresentation = {
  heading: string;
  introduction: string;
  originalHeading: string;
  originalUnavailable: string;
  proposedHeading: string;
  proposedUnavailable: string;
  evidenceBoundary: string;
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

/** Shared structure; the host supplies topic language and source-authorized content. */
export function MechanismSection({content, originalAction, contexts = [], originalActionApplicable = true}: {
  content: MechanismPresentation;
  originalAction?: ReactNode;
  contexts?: MechanismContext[];
  originalActionApplicable?: boolean;
}) {
  return <section id="mechanisms" className="article-section mechanism-section">
    <h2>{content.heading}</h2><p>{content.introduction}</p>
    {originalActionApplicable && <div><h3>{content.originalHeading}</h3>{originalAction || <p>{content.originalUnavailable}</p>}</div>}
    <h3>{content.proposedHeading}</h3>
    {contexts.length ? contexts.map(context => <div className="mechanism-context" key={context.id}>
      <h4>{context.title}</h4><p className="small muted" data-evidence-basis={context.evidence.basis}>{context.evidence.label}</p>
      {context.explanation}
      {(context.evidence.target || context.evidence.action || context.evidence.model) && <dl>{(['target','action','model'] as const).map(field => context.evidence[field] ? <div key={field}><dt>{content.detailLabels[field]}</dt><dd>{context.evidence[field]}</dd></div> : null)}</dl>}
      {context.evidence.source}<p>{context.clinicalMeaning}</p>
    </div>) : <p>{content.proposedUnavailable}</p>}
    <p className="small muted">{content.evidenceBoundary}</p>
  </section>;
}
