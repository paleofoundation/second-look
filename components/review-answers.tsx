import type {ProtectedReview} from '@/lib/review-access';
import {CitedProse} from '@/components/article';
import {content} from '@/lib/content';
/** Server caller supplies this body only after getReviewForRequest grants full. */
export function ReviewAnswers({review,citationOrder}:{review:ProtectedReview;citationOrder:string[]}){const sources=content.sources.filter(s=>review.sourceIds.includes(s.id));return <>
 {review.openingBlocks?.map(block=><section className="article-section" key={block.id} id={block.id}><h2>{block.title}</h2>{block.questionIds.map(id=>{const q=review.questionAnswers?.find(q=>q.id===id);return q?<CitedProse key={id} text={q.answer} sourceIds={q.sources} sources={sources} order={citationOrder}/>:null})}</section>)}
 <section className="article-section" id="appraisal"><h2>Full appraisal questions</h2>{review.questionAnswers?.map(q=><section id={q.render.fragment} key={q.id}><h3>{q.id} · {q.question}</h3><CitedProse text={q.answer} sourceIds={q.sources} sources={sources} order={citationOrder}/><p className="small">{q.status.replaceAll('_',' ')}</p><ul className="small">{q.locators.map((l,i)=><li key={i}>{[l.file||l.filename,l.chapter,l.section,l.table_figure,l.pdf_page!=null?'PDF page '+l.pdf_page:null,l.printed_page!=null?'Printed page '+l.printed_page:null,l.nativeLocator].filter(Boolean).join(' · ')}</li>)}</ul></section>)}</section></>}
