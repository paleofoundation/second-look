import type {ProtectedReview} from '@/lib/review-access';
import {CitedProse} from '@/components/article';
import {content} from '@/lib/content';
import {buildStudyReviewPlan} from '@/lib/study-review-plan';
import {sourceLocationText} from '@/lib/study-presentation';
import {StudySourceLocations} from '@/components/study-source-content';
/** The server supplies this component only after the full-review grant. */
export function ReviewAnswers({review,citationOrder}:{review:ProtectedReview;citationOrder:string[]}) {
 const sources=content.sources.filter(source=>review.sourceIds.includes(source.id));
 const plan=buildStudyReviewPlan(review);
 return <div id="appraisal">{plan.sections.filter(section=>section.answers.length).map(section=><section className="article-section" id={section.id} key={section.id}>
  <h2>{section.title}</h2>{section.answers.map(answer=><section className="study-question" id={answer.render.fragment} key={answer.id} data-review-question={answer.id}>
   <h3>{answer.question}</h3><CitedProse text={answer.answer} sourceIds={answer.sources} sources={sources} order={citationOrder} currentPath={'/research/'+review.id}/>
   <StudySourceLocations locations={sourceLocationText(answer.locators)}/>
  </section>)}
 </section>)}</div>;
}
