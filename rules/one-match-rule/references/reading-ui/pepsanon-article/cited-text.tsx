import {DiscussionSource,CommunityNote} from './discussion-source';
import copy from '@/lib/data/guide-copy.json';
import {FavoriteButton} from './account';
import type {Source} from '@/lib/peptides';
import {Citation} from './citations';
import {referencesInOrder} from '@/lib/citation-order';
import {proseSegments} from '@/lib/prose-links';
import {GlossarySegmentText} from './glossary-text';
export type CitedSentence = {text:string;sources:Source[]};
export function SourceMarkers({citations,references,linkToSource=false}:{citations:Source[];references:Source[];linkToSource?:boolean}) {
 const numbered=referencesInOrder(citations).map(source=>{const index=references.findIndex(s=>s.url===source.url)+1;if(!index)throw new Error(`Missing reference: ${source.url}`);return {source:references[index-1],index};}).sort((a,b)=>a.index-b.index);
 return <>{numbered.map(({source,index})=><Citation key={source.url} source={source} index={index} href={linkToSource?undefined:`#ref-${index}`}/>)}</>;
}
export function CitedText({sentences,references,linkToSource=false,currentPage}:{sentences:CitedSentence[];references:Source[];linkToSource?:boolean;currentPage?:string}) {
 const seen=new Set<string>(),guideSeen=new Set<string>();
 return <>{sentences.map((sentence,i)=>{
  const segments=proseSegments(sentence.text,{termSeen:seen,guideSeen,currentPage});
  const last=segments.pop()!;
  const split=(last.slug||last.href)?-1:last.text.lastIndexOf(' ');
  return <span key={i}>{i>0?' ':''}{segments.map((segment,index)=><GlossarySegmentText key={index} segment={segment}/>)}{split>=0?last.text.slice(0,split+1):null}<span className="citation-tail"><GlossarySegmentText segment={(last.slug||last.href)?last:{text:last.text.slice(split+1)}}/><SourceMarkers citations={sentence.sources} references={references} linkToSource={linkToSource}/></span></span>;
 })}</>;
}
export function References({sources,headingLevel=3}:{sources:Source[];headingLevel?:2|3}) {
 const Heading=headingLevel===2?'h2':'h3';
 // RevealAnchor owns the native open attribute when a saved citation is followed.
 // It can change before a streamed page hydrates; descendants still hydrate normally.
 return <section id="studies" className="source-section"><details className="references-disclosure" suppressHydrationWarning {...(!sources.length ? {'data-prose-section':true} : {})}><summary><Heading className="wp-block-heading">References</Heading><span className="reference-count">{sources.length} sources</span><span className="study-toggle" aria-hidden="true"/></summary>{!sources.length ? <p data-prose>{copy['missing-references']}</p> : null}<ol className="rgbc-references">{sources.map((s,i)=><li className="rgbc-references__item" id={`ref-${i+1}`} key={s.url}>{s.kind.startsWith('Community question')?<DiscussionSource title={s.title} url={s.url} date={s.year} community={s.kind.split('r/')[1]}/>:<><a className="rgbc-references__link" href={s.url} target="_blank" rel="noreferrer">{s.title}</a> <span>({s.year||`Accessed ${s.accessedAt||'2026-10-03'}`})</span><span className="source-kind">{s.kind}</span></>}{!s.kind.startsWith('Community question')&&!s.kind.startsWith('Commercial description')&&<FavoriteButton kind="study" itemId={s.url} title={s.title}/>}</li>)}</ol>{sources.some(source=>source.kind.startsWith('Community question'))&&<CommunityNote/>}</details></section>;
}
