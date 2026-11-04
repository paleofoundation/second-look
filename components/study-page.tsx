import type {Guide,Source} from '@/lib/content';
import {content,guideUrl,isPrimarySource} from '@/lib/content';
import type {ReviewAccess,PublicReviewPreview} from '@/lib/review-access';
import {createCitationOrder,sourceReferenceId} from '@/components/shared-theme/citations';
import {buildStudyReviewPlan} from '@/lib/study-review-plan';
import {studyHeadline,studyTopics,sourceLocationText} from '@/lib/study-presentation';
import {CitedProse} from '@/components/article';
import {AuthorCard} from '@/components/author-card';
import {ArticleSharing} from '@/components/article-sharing';
import {SaveButton} from '@/components/library-controls';
import {ReviewAnswers} from '@/components/review-answers';
import {ReviewStatus} from '@/components/review-status';
import {StudyFacts,StudyIntegrity,StudyPublicSummary,StudySourceLocations} from '@/components/study-source-content';
import {SectionIcon} from '@/components/shared-theme/section-icon';
import {UpdateHistory} from '@/components/shared-theme/update-history';
import {articleUpdateDate,articleUpdatesForPath,pageCreatedDate} from '@/lib/update-history';

type StudyAccess=ReviewAccess|{kind:'unavailable';preview:PublicReviewPreview;message:string};

export function StudyPage({source,access}:{source:Source;access:StudyAccess}) {
 const path='/research/'+source.id;
 const isStudy=isPrimarySource(source)||source.sourceType==='review';
 const review=access.kind==='full'?access.review:null;
 const plan=review?buildStudyReviewPlan(review):null;
 const sources=review?content.sources.filter(item=>review.sourceIds.includes(item.id)||item.id===source.id):[source];
 const order=createCitationOrder([[source.id],...(plan?.sections.flatMap(section=>section.answers.map(answer=>answer.sources))||[]),...(review?[review.sourceIds]:[])],sources.map(item=>item.id));
 const renderProse=(text:string,sourceIds:string[])=><CitedProse text={text} sourceIds={sourceIds} sources={sources} order={order} currentPath={path}/>;
 const guide:Guide={id:source.id,slug:path,title:source.title,type:isStudy?'Study':'Background source',description:source.preview,topicIds:[],sections:[],faqs:[],sourceIds:order,related:[]};
 const topics=studyTopics(source),related=topics.slice(0,3);
 const uses=content.guides.filter(item=>item.sourceIds.includes(source.id)&&!['Drug','Condition'].includes(item.type));
 const date=articleUpdatesForPath(path)[0]?.date||pageCreatedDate(path);
 const state=review?'Full review':access.kind==='preview'&&access.preview.reviewState==='withdrawn'?'Review withdrawn':access.kind==='unavailable'?'Review availability temporarily unavailable':isStudy?'Study summary':'Source summary';
 const sections=[{id:'publication',label:'Publication'},{id:'source-summary',label:'Summary'},...(plan?plan.sections.filter(section=>section.answers.length).map(section=>({id:section.id,label:section.title})):[{id:'study-details',label:'Study details'}]),{id:'study-context',label:'Context and related research'},...(!review?[{id:'review-status',label:'Review status'}]:[]),{id:'update-history',label:'Update History'},{id:'sources',label:'References'}];
 const takeaway=Array.from(new Intl.Segmenter('en',{granularity:'sentence'}).segment(source.preview))[0]?.segment||source.preview;
 return <main id="main" className="study-page">
  <header className="study-page__hero">
   <div className="study-page__hero-main"><nav className="study-page__kind" aria-label="Breadcrumb"><a href="/">RemapRx</a><a href="/research">Research</a><span>{state}</span></nav><h1 className="study-page__title">{isStudy?studyHeadline(source):'Source summary'}</h1><p className="study-page__takeaway">{takeaway}</p></div>
   <aside className="study-page__author" aria-label="Review author"><AuthorCard guide={guide}/>{date?<p>Page history · <time dateTime={date}>{articleUpdateDate(date)}</time></p>:null}<SaveButton id={source.id} returnTo={path} label="Save study"/></aside>
  </header>
  <div className="study-page__layout">
   <nav className="study-page__nav" aria-label="On this page"><ul>{sections.map(section=><li key={section.id}><a href={'#'+section.id}><SectionIcon label={section.label}/><span>{section.label}</span></a></li>)}</ul></nav>
   <article className="study-page__body">
    <section className="study-publication" id="publication"><h2>Publication</h2><p className="study-publication__title">{source.title}</p>{source.authors?.length?<details><summary>Paper authors ({source.authors.length})</summary><p>{source.authors.join(', ')}</p></details>:null}<p>{source.year?<>Published {source.year}. </>:null}{source.design}</p><p>{source.doi?<>DOI: <a href={'https://doi.org/'+source.doi} target="_blank" rel="noreferrer">{source.doi}</a></>:null}{source.pmid?<> · <a href={'https://pubmed.ncbi.nlm.nih.gov/'+source.pmid+'/'} target="_blank" rel="noreferrer">PubMed record</a></>:null}</p>{/^https:\/\//.test(source.url)?<a href={source.url} target="_blank" rel="noreferrer">Read the original paper ↗</a>:null}</section>
    <StudyIntegrity source={source} renderProse={renderProse}/>
    <section id="source-summary" className="article-section"><span id="summary"/><h2>{isStudy?'Study summary':'Source summary'}</h2>{isStudy?<StudyPublicSummary source={source} renderProse={renderProse} headingLevel={3} idPrefix="study-summary"/>:renderProse(source.preview,[source.id])}{!review?<span id="limits"/>:null}</section>
    {review?<ReviewAnswers review={review} citationOrder={order}/>:<section className="article-section" id="study-details"><h2>Study details</h2><StudyFacts source={source}/><StudySourceLocations locations={sourceLocationText(source.locators)}/></section>}
    <section className="article-section" id="study-context"><h2>Context and related research</h2>{topics.length?<><p>This report is cited in the following drug and condition articles. Their outcome summaries explain how it fits with other evidence.</p>{topics.map(topic=><p key={topic.id}><a href={topic.href+'#research-feed'}>{topic.label}</a></p>)}</>:<p>This report's original source and available summary are listed on this page.</p>}{uses.length?<details><summary>Questions and guides using this source</summary>{uses.map(item=><p key={item.id}><a href={guideUrl(item)}>{item.title}</a></p>)}</details>:null}</section>
    {!review?<ReviewStatus sourceId={source.id} access={access.kind} reason={'reason' in access?access.reason:access.kind==='unavailable'?'temporarily_unavailable':'review_pending'}/>:null}
    <section className="article-section" id="update-history"><span id="edition"/><h2>Update History</h2><UpdateHistory pagePath={path} sectionIds={sections.map(section=>section.id)}/></section>
    <section className="article-section" id="sources"><span id="references"/><span id="source-note"/><h2>References</h2><ol className="bibliography">{order.map((id,index)=>{const item=sources.find(s=>s.id===id)!;return <li key={id} id={'ref-'+(index+1)} value={index+1}><span id={sourceReferenceId(id)}/>{/^https:\/\//.test(item.url)?<a href={item.url} target="_blank" rel="noreferrer">{item.title}</a>:<span>{item.title}</span>}. {item.year}. {item.doi?<>DOI: {item.doi}.</>:null}<StudySourceLocations locations={sourceLocationText(item.locators)}/></li>})}</ol></section>
   </article>
   <aside className="study-page__aside" aria-label="Sharing and related reading"><ArticleSharing path={path} title={source.title} kind="Study"/>{related.length?<nav aria-label="Related reading"><h2>Related reading</h2>{related.map(topic=><p key={topic.id}><a href={topic.href}>{topic.label}</a></p>)}</nav>:null}</aside>
  </div>
 </main>;
}
