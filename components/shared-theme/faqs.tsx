'use client';
import {useEffect,useRef,type ReactNode} from 'react';
export type ThemeFaq={id:string;aliases?:string[];question:string;answer:ReactNode;status?:string};
/** Native Microbiome rgbc FAQ structure; authored content remains structured React. */
export function InlineFaqs({items,title='FAQs'}:{items:ThemeFaq[];title?:string}){
 const root=useRef<HTMLElement>(null);
 useEffect(()=>{const reveal=()=>{let id='';try{id=decodeURIComponent(window.location.hash.slice(1))}catch{return}const node=root.current?.querySelector<HTMLElement>(`[id="${CSS.escape(id)}"]`)?.closest<HTMLDetailsElement>('details');if(node)node.open=true};reveal();window.addEventListener('hashchange',reveal);const click=(event:MouseEvent)=>{const link=(event.target as Element).closest?.('a[href^="#"]');if(link)queueMicrotask(reveal)};document.addEventListener('click',click);return()=>{window.removeEventListener('hashchange',reveal);document.removeEventListener('click',click)}},[]);
 return <section className="article-section rgbc-faq-block" id="faqs" ref={root}><h2>{title}</h2>{items.length?items.map(item=><details className="rgbc-faq-item" key={item.id} id={item.id}><summary><span className="rgbc-faq-icon" aria-hidden="true"/><span className="rgbc-faq-q">{item.question}</span></summary>{item.aliases?.map(alias=><span id={alias} key={alias} className="faq-alias"/>)}<div className="rgbc-faq-a"><strong>Quick answer</strong>{item.answer}{item.status?<p className="faq-answer-state">{item.status}</p>:null}</div></details>):<p>Questions for this page are still being mapped. FAQ coverage is incomplete.</p>}</section>
}
