import type {ReactNode} from 'react';

export function FaqItem({id,question,meta,children}:{id?:string;question:string;meta?:string;children:ReactNode}) {
 return <details className="rgbc-faq-item" id={id}>
  <summary><span className="rgbc-faq-icon" aria-hidden="true"/><span>{meta&&<span className="faq-peptide">{meta}</span>}<span className="faq-title">{question}</span></span></summary>
  <div className="rgbc-faq-a"><strong>Quick answer:</strong>{children}</div>
 </details>;
}
