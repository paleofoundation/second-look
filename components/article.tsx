'use client';
import Link from 'next/link';
import canonicalDrugPages from '@/data/canonical-drug-pages.json';
import outcomeRegistry from '@/data/outcome-registry.json';
import sentenceMapData from '@/data/outcome-sentence-maps.json';
const sentenceMaps=sentenceMapData.rows as Record<string,{finding:{text:string;sources:string[]}[];magnitude:{text:string;sources:string[]}[]}>;
import {Fragment,useEffect,useState,useRef} from 'react';
import {ShieldCheck,MessagesSquare,ChartNoAxesColumnIncreasing,BookOpen,FileText,Link as LinkIcon,Mail,Plus,Minus} from 'lucide-react';
import {Popover,PopoverTrigger,PopoverContent} from '@/components/ui/popover';
import {SaveButton} from '@/components/library-controls';
import {content,guideUrl,synthesisRows,isPrimarySource,type Guide,type Source,type SourceDetail,type SynthesisRow} from '@/lib/content';
import {AuthorCard} from '@/components/author-card';
import {ArticleSharing} from '@/components/article-sharing';
import {PageSnapshot} from '@/components/page-snapshot';
import {pageSnapshotFor} from '@/lib/page-snapshot';
import {HeroActions} from '@/components/shared-theme/article-actions';
import {orderCitationGroup,normalizeCitationSentence,sourceReferenceId} from '@/components/shared-theme/citations';
import {guideCitationOrder,articleSectionGroups,hasArticleEvidence,articleEvidenceSources,benefitQuestionPlan} from '@/lib/citation-plan';
import {buildUniversalArticlePlan,buildArticleReaderTail,type UniversalArticleModule} from '@/components/shared-theme/universal-article';
import {ArticleLayout,ThemeSectionNav} from '@/components/shared-theme/theme';
import {EvidenceTable,type EvidenceFinding,type EvidenceSource,type EvidenceSummary} from '@/components/shared-theme/evidence-table';
import {MedicalScopeNotice} from '@/components/shared-theme/guide-catalogue';
import {MechanismSection} from '@/components/shared-theme/mechanisms';
import {hasMechanismSection,drugMechanismFor,mechanismContextsFor,mechanismPresentation,evidenceMechanismsFor,mechanismEvidenceHref} from '@/lib/mechanisms';
import {InlineFaqs} from '@/components/shared-theme/faqs';
import {UpdateHistory} from '@/components/shared-theme/update-history';
import type {ProtectedReview,ReviewAccess} from '@/lib/review-access';
import {StudyFacts,StudyIntegrity,StudyPublicSummary,StudySourceLocations} from '@/components/study-source-content';
import {sourceLocationText,studyTopics,studyDesignLabel} from '@/lib/study-presentation';
import {buildStudyReviewPlan} from '@/lib/study-review-plan';
import {OutcomeFinder,type OutcomeOption} from '@/components/shared-theme/outcome-finder';
import {wikiText,wikiTextRenderer} from '@/lib/wiki-links';
import {relatedReadingFor} from '@/lib/related-reading';
import {studyDesignsFor} from '@/lib/evidence-presentation';
import {outcomeSummariesFor} from '@/lib/outcome-summary';
import {getTopicHeroArt} from '@/lib/hero-art';
import drugStatusTable from '@/data/drug-status-table.json';
import {TreatmentSuitability} from '@/components/shared-theme/treatment-suitability';
import {StatusInfo} from '@/components/status-info';
import {ContraindicationsInfo} from '@/components/contraindications-info';
import {suitabilityFor,suitabilityScope} from '@/lib/treatment-suitability';

function OriginalSource({source}:{source:Source}){return /^https:\/\//.test(source.url)?<a href={source.url} target="_blank" rel="noreferrer">Original source</a>:<span className="small">Original source URL not recorded</span>}
function ReferenceTitle({source}:{source:Source}){return /^https:\/\//.test(source.url)?<a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>:<span>{source.title}</span>}
function revealFragment(){const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(!target)return;let parent:HTMLElement|null=target;while(parent){if(parent instanceof HTMLDetailsElement)parent.open=true;parent=parent.parentElement}requestAnimationFrame(()=>{target.setAttribute('tabindex','-1');target.focus({preventScroll:true});target.scrollIntoView({block:'start'});});}
export function Citation({source,n}:{source:Source;n:number}){const[open,setOpen]=useState(false);const trigger=useRef<HTMLAnchorElement>(null);const restoreFocus=useRef(true);return n>0?<sup className="citation-sup" data-source-id={source.id}><Popover open={open} onOpenChange={setOpen}><PopoverTrigger asChild><a ref={trigger} href={'#'+sourceReferenceId(source.id)} className="citation-trigger" aria-label={`Citation ${n}: ${source.title}`} onClick={e=>{e.preventDefault();restoreFocus.current=true;setOpen(true)}} onMouseEnter={()=>setOpen(true)}>[{n}]</a></PopoverTrigger><PopoverContent onCloseAutoFocus={event=>{event.preventDefault();if(restoreFocus.current)trigger.current?.focus()}} className="citation-card" onMouseLeave={()=>setOpen(false)}><strong>{source.title}</strong>{source.authors?.length?<p className="small">{source.authors.slice(0,3).join(', ')}{source.authors.length>3?' et al.':''} {source.year}</p>:null}<p className="small" style={{marginTop:12}}>{source.preview}</p><div className="inline-actions small"><a href={`/research/${source.id}`}>Source details</a><OriginalSource source={source}/><a href={'#'+sourceReferenceId(source.id)} onClick={()=>{restoreFocus.current=false;setOpen(false);setTimeout(revealFragment,10)}}>Reference [{n}]</a></div></PopoverContent></Popover></sup>:null}
export function CitedProse({text,sourceIds,sources,order,mapped,currentPath=''}:{text:string;sourceIds:string[];sources:Source[];order:string[];mapped?:{text:string;sources:string[]}[];currentPath?:string}){
 const sentences=mapped||Array.from(new Intl.Segmenter('en',{granularity:'sentence'}).segment(text),v=>({text:v.segment,sources:sourceIds}));
 const linked=new Set<string>();
 return <p>{sentences.map((sentence,i)=><span key={i}>{wikiText(normalizeCitationSentence(sentence.text),currentPath,linked)}{orderCitationGroup(sentence.sources,order).map(id=>{const s=sources.find(x=>x.id===id);return s?<Citation key={id} source={s} n={order.indexOf(id)+1}/>:null})}{' '}</span>)}</p>;
}
/** Preserve this page's frozen citations when an authorized study opens. */
export function canRenderStudyReviewInline(review:ProtectedReview,sourceId:string,sources:Source[],order:string[]){
 const openingAnswers=(review.openingBlocks||[]).flatMap(block=>block.questionIds.map(id=>review.questionAnswers?.find(answer=>answer.id===id)));
 if(openingAnswers.some(answer=>!answer))return false;
 const citedIds=[...review.sourceIds,...review.sections.flatMap(section=>[
  ...section.sources,...(section.sentences||[]).flatMap(sentence=>sentence.sources),
 ]),...openingAnswers.flatMap(answer=>answer?.sources||[])];
 return review.id===sourceId&&citedIds.every(id=>id===sourceId&&sources.some(source=>source.id===id)&&order.includes(id));
}
/** Only authorized opening answers are projected into the inline card. */
export function InlineStudyReview({review,sources,order,currentPath}:{review:ProtectedReview;sources:Source[];order:string[];currentPath:string}){
 const plan=buildStudyReviewPlan(review);
 return <div className="study-summary__review">{plan.openings.map(block=><section className="study-question" key={block.id} id={'study-'+review.id+'-opening-'+block.id}>
  <h4>{block.title}</h4>{block.answers.map(answer=><div key={answer.id} id={'study-'+review.id+'-opening-'+block.id+'-'+answer.id}>
   <CitedProse text={answer.answer} sourceIds={answer.sources} sources={sources} order={order} currentPath={currentPath}/>
   <StudySourceLocations locations={sourceLocationText(answer.locators)}/>
  </div>)}
 </section>)}</div>;
}
/** Only the authorized review endpoint may supply a complete authored review. */
function StudySummary({source,sources,order,currentPath}:{source:Source;sources:Source[];order:string[];currentPath:string}){
 const [review,setReview]=useState<ProtectedReview|null>(null);
 const [availability,setAvailability]=useState<string|null>(null);
 const [requested,setRequested]=useState(false);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState(false);
 async function loadReview(){
  if(requested||busy)return;
  setBusy(true);setError(false);
  try{
   const response=await fetch('/api/reviews/'+encodeURIComponent(source.id),{credentials:'same-origin',cache:'no-store'});
   if(response.status===404){setAvailability('pending');setRequested(true);return;}
   if(!response.ok)throw new Error('Review unavailable');
   const result=await response.json() as ReviewAccess;
   if(result.kind==='full'&&result.review.id===source.id){
    if(canRenderStudyReviewInline(result.review,source.id,sources,order))setReview(result.review);
    else setAvailability('dedicated');
   }else if(result.kind==='preview')setAvailability(result.preview.reviewState==='released'?'released':result.preview.reviewState);
   setRequested(true);
  }catch{setError(true);}finally{setBusy(false);}
 }
 const canonicalDrug=canonicalDrugPages.pages.includes(currentPath);
 const topics=studyTopics(source).slice(0,3);
 const renderProse=(text:string,sourceIds:string[])=><CitedProse text={text} sourceIds={sourceIds} sources={sources} order={order} currentPath={currentPath}/>;
 const excerpt=Array.from(new Intl.Segmenter('en',{granularity:'sentence'}).segment(source.preview))[0]?.segment||source.preview;
 return <div className="research-feed__item study-summary-card" data-study-id={source.id}>
  <details className="research-item study-summary" id={'study-'+source.id} onToggle={event=>{if(event.currentTarget.open)void loadReview()}}>
   <summary className="research-feed__header-wrap"><span className="research-feed__toggle-icon" aria-hidden="true"><Plus className="research-feed__plus"/><Minus className="research-feed__minus"/></span><span><span className="research-feed__title">{source.title}</span><span className="research-feed__sub-header">{source.year?<span>{source.year}</span>:null}{source.design?<span>{studyDesignLabel(source)}</span>:null}</span></span></summary>
   <div className="research-feed__content research-item__body">
    <StudyIntegrity source={source} renderProse={renderProse}/>
    <StudyFacts source={source}/>
    {review?<InlineStudyReview review={review} sources={sources} order={order} currentPath={currentPath}/>:<StudyPublicSummary source={source} renderProse={renderProse} canonicalDrug={canonicalDrug}/>}
    {busy?<p className="small" role="status">Loading study review…</p>:null}
    {error?<p className="small" role="status">The study review could not be loaded. <button type="button" onClick={()=>void loadReview()}>Retry</button></p>:null}
    {!review&&availability&&(!canonicalDrug||availability==='released'||availability==='dedicated'||availability==='withdrawn')?<p className="study-review-state">{availability==='released'?'The complete review is available with free sign-in.':availability==='dedicated'?'Open the study page to read the complete review and its supporting sources.':availability==='withdrawn'?'The complete review has been withdrawn. See the source notice and study page for context.':'The complete appraisal is not yet available. This summary shows the source information currently available.'}</p>:null}
   </div>
  </details>
  <p className="research-feed__excerpt">{excerpt}</p>
  {source.status==='Quarantined'?<p className="study-integrity-label">Quarantined · not evidence for efficacy</p>:source.correction?<p className="study-integrity-label">Correction notice</p>:null}
  {topics.length?<div className="research-feed__sub-header research-feed__categories">{topics.map(topic=><a key={topic.id} href={topic.href}>{topic.label}</a>)}</div>:null}
  <div className="research-feed__footer"><div>
   <a className="study-action" href={'/research/'+source.id} aria-label={'Open study summary: '+source.title}><FileText aria-hidden="true"/>Open</a>
   {/^https:\/\//.test(source.url)?<a className="study-action" href={source.url} target="_blank" rel="noreferrer" aria-label={'Original paper: '+source.title}><LinkIcon aria-hidden="true"/>Link</a>:null}
   <a className="study-action" href={'mailto:?subject='+encodeURIComponent(source.title)+'&body='+encodeURIComponent('https://remaprx.com/research/'+source.id+'\n\nOriginal source: '+source.url)} aria-label={'Email study summary: '+source.title}><Mail aria-hidden="true"/>Email</a>
  </div></div>
 </div>;
}
function ResearchStudies({sources,order,currentPath='',showHeading=true}:{sources:Source[];order:string[];currentPath?:string;showHeading?:boolean}){
 const primary=sources.filter(isPrimarySource);
 return <div id="studies" data-research-feed>{showHeading?<h3>Study summaries</h3>:null}{primary.length?primary.map(source=><StudySummary key={source.id} source={source} sources={sources} order={order} currentPath={currentPath}/>):<p>This profile draws on the sources listed in References.</p>}</div>;
}
function ReferenceList({sources,order,linkStudies=true}:{sources:Source[];order:string[];linkStudies?:boolean}){
 return <ol className="bibliography">{order.map((id,i)=>{const source=sources.find(item=>item.id===id);return source?<li key={id} id={'ref-'+(i+1)} data-source-id={id} value={i+1}><span id={sourceReferenceId(id)} className="reference-alias"/><ReferenceTitle source={source}/>. {source.year}. {source.doi?'DOI: '+source.doi+'. ':(source as SourceDetail).doiMissingReason==='not_printed'?'DOI NOT PRINTED. ':''}<span>{source.design||'Source'}.</span>{source.locators?<p className="small">{(source.locators as {section?:string;table_figure?:string;basis?:string}[]).map(locator=>[locator.section,locator.table_figure,locator.basis].filter(Boolean).join(' · ')).join('; ')}</p>:null}{linkStudies&&isPrimarySource(source)?<a href={'#study-'+id}>Study summary</a>:null}</li>:null})}</ol>;
}
/** Directory/outcome callers retain the combined catalogue; articles use separate modules. */
export function ResearchCatalog({sources,order=sources.map(source=>source.id),currentPath=''}:{sources:Source[];order?:string[];currentPath?:string}){
 return <><ResearchStudies sources={sources} order={order} currentPath={currentPath}/><section id="references" className="article-section"><h2>References</h2><ReferenceList sources={sources} order={order}/></section></>;
}
type StatusRow={use:string;regulator:string;status:string;year:number|null;sourceIds:string[]};
const STATUS_ROWS=(drugStatusTable as unknown as {drugs:Record<string,StatusRow[]>}).drugs;
const QUALITY_BOILERPLATE=/FDA-approved generic medicines must match|demonstrate bioequivalence/i;
const QUALITY_SPECIFIC=/differ|distinct|interchangeab|immediate-release|extended-release|delayed-release|release (profile|formulation)|veterinary|compounded|supplement|co-packaged|other formulations|formulations|salt and base|topical|combined with|combination/i;
/** Quality renders only when, after generic boilerplate is removed, a sentence describes a drug-specific formulation/product difference. */
function hasSpecificQuality(sections:{paragraph?:string}[]){return sections.some(section=>(section.paragraph||'').split(/(?<=[.!?])\s+/).filter(sentence=>!QUALITY_BOILERPLATE.test(sentence)).some(sentence=>QUALITY_SPECIFIC.test(sentence)))}
const OVERVIEW_CHILDREN=['Mechanisms','Benefits','Safety','Contraindications','Interactions','Dosing'];
function nestOverview<G extends {id:string;label:string;children?:{id:string;label:string}[]}>(items:G[]):G[]{const overview=items.find(item=>item.label==='Overview');if(!overview)return items;const kids=items.filter(item=>OVERVIEW_CHILDREN.includes(item.label));if(!kids.length)return items;return items.filter(item=>!kids.includes(item)).map(item=>item===overview?{...item,collapsible:true,children:[...(item.children||[]),...kids.map(kid=>({id:kid.id,label:kid.label}))]}:item)}
function RelatedReading({guide}:{guide:Guide}){const related=relatedReadingFor(guide);return related.length?<nav className="related-reading" aria-label="Related reading"><h2>Related reading</h2><ul>{related.map(g=><li key={g.id}><a href={guideUrl(g)}>{g.title}</a></li>)}</ul></nav>:null}

export function OutcomeEvidence({rows:inputRows,guide,sources,order,compact=true}:{rows:SynthesisRow[];guide?:Guide;sources:Source[];order:string[];compact?:boolean}){
 const completeIds=new Set(outcomeSummariesFor(inputRows).flatMap(summary=>summary.synthesisIds));
 const rows=synthesisRows.filter(row=>completeIds.has(row.id));
 const outcomeMap=outcomeRegistry.rowOutcomeMap as Record<string,string>;
 const citations=(ids:string[])=><>{orderCitationGroup(ids,order).map(id=>{const source=sources.find(s=>s.id===id);return source?<Citation key={id} source={source} n={order.indexOf(id)+1}/>:null})}</>;
 const meta=(field:{value:unknown;status:string;reason:string|null;sources:string[]})=>field.value==null?'Unknown':<>{String(field.value)}{citations(field.sources)}</>;
 const records:OutcomeOption[]=rows.map(row=>{const outcome=outcomeRegistry.outcomes.find(o=>o.id===outcomeMap[row.id])!;return {id:row.id,canonicalOutcomeId:outcome.id,registryState:outcome.registryState.replaceAll('_',' '),title:row.title,definition:outcome.definition.text,definitionCitation:citations(outcome.definition.sources),aliases:[...outcome.aliases,row.title,row.use],entity:{id:row.drugId,label:content.guides.find(g=>g.entityId===row.drugId)?.title||row.drugId},condition:{id:row.conditionId,label:content.guides.find(g=>g.entityId===row.conditionId)?.title||row.conditionId},population:row.population||'Unknown',design:[...new Set(row.effects.map(e=>e.design||'Unknown'))].join('; ')||'Unknown',assessment:row.certainty.label||'Unknown',timepoint:row.timepoint,comparator:row.comparison,instrument:meta(outcome.instrument),hierarchy:meta(outcome.endpointHierarchy),endpointRole:meta(outcome.clinicalOrSurrogateRole),measuredDirection:meta(outcome.measuredDirection),scaleDirection:meta(outcome.favorableScaleDirection),meaningfulChange:meta(outcome.meaningfulChange),clinicalMeaning:meta(outcome.clinicalInterpretation)}});
 const sourceViews:EvidenceSource[]=sources.toSorted((a,b)=>order.indexOf(a.id)-order.indexOf(b.id)).map(s=>({id:s.id,title:s.title,url:s.url,year:s.year,kind:isPrimarySource(s)?'Primary report':s.sourceType||'Background',primary:isPrimarySource(s),quarantined:s.status==='Quarantined',preview:s.preview,decisiveLimit:s.decisiveLimit,access:s.access,status:s.status,correction:s.correction,population:s.population,design:s.design,reviewUrl:'/research/'+s.id,reviewLabel:'Source details',sampleDetails:[...(s.randomizedN!=null?[{label:'Randomized participants',value:String(s.randomizedN)}]:[]),...((s as SourceDetail).sampleDescription?[{label:'Reported sample',value:(s as SourceDetail).sampleDescription!}]:s.n!=null&&s.n!==s.randomizedN?[{label:'Reported sample',value:String(s.n)}]:[]),...(s.intervention?[{label:'Intervention',value:s.intervention}]:[]),...(s.comparator?[{label:'Comparator',value:s.comparator}]:[])],locators:[...new Set(rows.flatMap(r=>r.sourceLocators?.filter(l=>l.sourceId===s.id).map(l=>l.label)||[]))]}));
 const findings:EvidenceFinding[]=rows.map(row=>{const outcome=outcomeRegistry.outcomes.find(o=>o.id===outcomeMap[row.id])!;const peer=content.guides.find(g=>g.entityId===(guide?.type==='Condition'?row.drugId:row.conditionId));return {id:row.id,title:row.title,studyDesigns:studyDesignsFor(row,sources),peer:peer?{title:peer.title,href:guideUrl(peer)}:undefined,use:row.use,population:row.population,comparison:row.comparison,endpoint:row.endpoint,timepoint:row.timepoint,status:row.status.replaceAll('_',' '),finding:row.finding.text,findingSources:row.finding.sources,findingSentences:sentenceMaps[row.id]?.finding,magnitudeSentences:sentenceMaps[row.id]?.magnitude,magnitude:row.magnitudeText,certainty:row.certainty,evidenceBase:row.evidenceBase,limits:row.limitations.map(l=>({text:l.text,sourceIds:l.sources})),sourceIds:row.sourceIds,familyIds:row.studyFamilyIds,background:!row.countsAsPrimaryEvidence,pending:row.coverage.pending,details:outcome.clinicalInterpretation.value==null?[]:[{label:'Clinical importance',value:meta(outcome.clinicalInterpretation)}]}});
 const summaries:EvidenceSummary[]=outcomeSummariesFor(rows).map(summary=>{const peer=content.guides.find(g=>g.entityId===(guide?.type==='Condition'?summary.drugId:summary.conditionId));return {...summary,peer:peer?{title:peer.title,href:guideUrl(peer)}:undefined,mechanisms:evidenceMechanismsFor(summary.drugId,summary.conditionId)}});
 const summaryRecords:OutcomeOption[]=summaries.map(summary=>{const members=records.filter(record=>summary.synthesisIds.includes(record.id));return {...members[0],id:summary.id,title:summary.label,aliases:[...members.flatMap(member=>member.aliases),summary.purpose,members[0]?.entity.label||'',members[0]?.condition.label||''],assessment:summary.grade.value?`Grade ${summary.grade.value}`:summary.grade.label}});
 const renderRows=(ids:string[])=><EvidenceTable variant={guide?.type==='Condition'?'condition':'drug'} summaries={ids.map(id=>summaries.find(summary=>summary.id===id)!).filter(Boolean)} emptyMessage={rows.length?'No recorded outcome matches these filters.':'No outcome findings are available in this table.'} rows={findings} sources={sourceViews} renderText={wikiTextRenderer(guide?guideUrl(guide):'')} cite={ids=><>{orderCitationGroup(ids,order).map(id=>{const source=sources.find(s=>s.id===id);return source?<Citation key={id} source={source} n={order.indexOf(id)+1}/>:null})}</>}/>;
 return rows.length?<OutcomeFinder records={summaryRecords} renderRows={renderRows} compact={compact}/>:renderRows([]);
}
function EvidenceIntroduction(){return <p>Compare the outcomes studied for each drug and condition. The A–F grade assesses the likelihood of benefit, Effect summarizes the size of the change, and Evidence counts independent randomized trials and their participants. Select an outcome or study count for the findings, proposed mechanisms and study details. <Link href="/methods">How we grade outcomes.</Link></p>}
function EvidenceContent({rows,guide,sources,order}:{rows:SynthesisRow[];guide:Guide;sources:Source[];order:string[]}){return <><span id="findings" className="reference-alias"/><OutcomeEvidence rows={rows} guide={guide} sources={sources} order={order}/></>}

export function Article({guide,sources:inputSources,children,additionalCitationGroups=[]}:{guide:Guide;additionalCitationGroups?:string[][];sources:Source[];children?:React.ReactNode;acquisitionStatus?:{coverage_state:string;readerSummary:string;readerNextStep:string}}){
 const isRecord=['Study','Background source','Glossary'].includes(guide.type);const terminal=isRecord?'sources':'research-feed';const terminalLabel=isRecord?'Sources':'Research Feed';
 const rows=(guide.synthesisIds||[]).map(id=>synthesisRows.find(r=>r.id===id)).filter((r):r is SynthesisRow=>!!r);
 const sources=articleEvidenceSources(guide,inputSources);
 const hasEvidence=hasArticleEvidence(guide);
 const evidenceTarget=hasEvidence?'#section-evidence':'#'+(guide.sections.find(section=>section.label==='Evidence')?.id||terminal);
 const canonicalDrug=guide.type==='Drug'&&canonicalDrugPages.pages.includes(guideUrl(guide));
 const hasCancerContext=/cancer/i.test(guide.title+' '+(guide.scope||''))||(canonicalDrug&&/cancer|tumor|leukemia|lymphoma|myeloma|glioblastoma|carcinoma|melanoma|sarcoma/i.test(guide.sections.map(section=>section.paragraph).join(' ')));
 const showMechanisms=hasMechanismSection(guide);const mechanismContexts=mechanismContextsFor(guide);const drugMechanism=drugMechanismFor(guide);
 const {first,rest,scoped,later,evidence}=articleSectionGroups(guide);
 const universal=guide.type==='Drug'||guide.type==='Condition'?buildUniversalArticlePlan({...guide,type:guide.type}):null;
 const hiddenModules=new Set(universal&&guide.type==='Drug'?['section-results','section-benefits',...(hasSpecificQuality(universal.modules.find(module=>module.label==='Quality')?.sections||[])?[]:['section-quality'])]:[]);
 const readerTail=buildArticleReaderTail({includeEvidence:hasEvidence||evidence.length>0,evidenceSections:evidence});
 const ordered=guideCitationOrder(guide,sources,additionalCitationGroups);
 const renderSection=(section:Guide['sections'][number],nested=false,showTitle=true)=><section className={nested?'article-subsection':'article-section'} id={section.id} key={section.id}>
  {showTitle&&section.title&&(nested?<h3>{section.title}</h3>:<h2>{section.title}</h2>)}
  {section.paragraph&&<CitedProse text={section.paragraph} mapped={section.sentences} currentPath={guideUrl(guide)} sourceIds={section.sources} sources={sources} order={ordered}/>}
  {!!section.questions?.length&&<div className="rgbc-faq-block">{section.questions.map(question=><details className="rgbc-faq-item" key={question.id} id={question.id}>
   <summary><span className="rgbc-faq-icon" aria-hidden="true"/><span className="rgbc-faq-q">{question.question}</span></summary>
   <div className="rgbc-faq-a"><strong>Quick answer</strong><CitedProse text={question.answer} mapped={question.sentences} currentPath={guideUrl(guide)} sourceIds={question.sources} sources={sources} order={ordered}/></div>
  </details>)}</div>}
 </section>;
 useEffect(()=>{const reveal=()=>revealFragment();const click=(event:MouseEvent)=>{const link=(event.target as Element).closest?.('a[href^="#"]');if(link&&!event.defaultPrevented)requestAnimationFrame(reveal)};reveal();window.addEventListener('hashchange',reveal);document.addEventListener('click',click);return()=>{window.removeEventListener('hashchange',reveal);document.removeEventListener('click',click)}},[guide.id]);
 const snapshot=pageSnapshotFor(guide,sources,ordered);
 const railLabel=(label:string)=>label.replace(/[^a-zA-Z0-9 ]/g,'').split(' ')[0]||'Overview';
 const flatGroups=universal?.navigation.filter(item=>!hiddenModules.has(item.id))||[...first.map(section=>({id:section.id,label:railLabel(section.label)})),...(showMechanisms?[{id:'mechanisms',label:'Mechanisms'}]:[]),...rest.map(section=>({id:section.id,label:railLabel(section.label)})),...(scoped.length?[{id:'condition-details',label:'Details'}]:[]),...later.map(section=>({id:section.id,label:railLabel(section.label)})),...(isRecord?[{id:'update-history',label:'Update History'},{id:terminal,label:terminalLabel}]:readerTail.map(module=>({id:module.id,label:module.label})))];
 const groups=nestOverview(flatGroups);
 const parent=guide.type==='Drug'?{label:'Drugs',href:'/drugs'}:guide.type==='Condition'?{label:'Conditions',href:'/conditions'}:isRecord?{label:guide.type==='Glossary'?'Glossary':'Research',href:guide.type==='Glossary'?'/glossary':'/research'}:{label:'Questions',href:'/questions'};

 const mechanismProse=(prose:NonNullable<typeof drugMechanism>['summary'])=>prose?<CitedProse text={prose.text} mapped={prose.sentences} currentPath={guideUrl(guide)} sourceIds={prose.sourceIds} sources={sources} order={ordered}/>:null;
 const mechanismsContent=<MechanismSection showRationales={guide.id!=='G-METFORMIN'&&!canonicalDrug} visibleQuestions={canonicalDrug} rationalePlacement={guide.type==='Drug'||guide.type==='Condition'?'evidence':'article'} collapsiblePathways={guide.id==='G-METFORMIN'} content={mechanismPresentation} renderText={wikiTextRenderer(guideUrl(guide))} originalAction={mechanismProse(drugMechanism?.originalAction)} summary={mechanismProse(drugMechanism?.summary)} pathways={(drugMechanism?.pathways||[]).map(pathway=>({id:pathway.id,title:pathway.title,explanation:mechanismProse(pathway)}))} rationales={(drugMechanism?.rationales||[]).map(row=>({id:row.id,condition:row.condition,conditionHref:row.conditionHref,evidenceHref:mechanismEvidenceHref(guide,row.id),rationale:mechanismProse(row.rationale),tested:mechanismProse(row.tested),limits:mechanismProse(row.limits)}))} questions={(drugMechanism?.questions||[]).map(question=>({id:question.id,title:question.title,answer:mechanismProse(question)}))} contexts={mechanismContexts.map(context=>({id:context.id,title:context.title,evidence:{basis:'secondary_description' as const,label:context.evidenceType,source:<p className="small muted">{context.locator}</p>},clinicalMeaning:context.clinicalMeaning,explanation:<><CitedProse text={context.text} currentPath={guideUrl(guide)} sourceIds={context.sourceIds} sources={sources} order={ordered}/></>}))}/>;
 const movedBenefitQuestions=hiddenModules.has('section-benefits')?benefitQuestionPlan(guide,rows).moved:[];
 const faqContent=guide.faqs.length||movedBenefitQuestions.length?<InlineFaqs items={[...guide.faqs.map((f,i)=>({id:f.id||'question-'+i,aliases:f.id?['question-'+i]:[],question:f.question,answer:<CitedProse text={f.answer} mapped={f.sentences} currentPath={guideUrl(guide)} sourceIds={f.sources} sources={sources} order={ordered}/>})),...movedBenefitQuestions.map(q=>({id:q.id,aliases:[] as string[],question:q.question,answer:<CitedProse text={q.answer} mapped={q.sentences} currentPath={guideUrl(guide)} sourceIds={q.sources} sources={sources} order={ordered}/>}))]}/>:<section id="faqs" className="article-section"><h2>FAQs</h2></section>;
 const sectionIds=[...groups.map(group=>group.id),...guide.sections.map(section=>section.id),'research','studies','edition','references'];
 const researchContent=(authored?:React.ReactNode)=><section className="article-section" id="research-feed" data-universal-section="Research Feed"><span id="research" className="reference-alias"/><h2>Research Feed</h2>{authored}{children}<ResearchStudies sources={sources} order={ordered} currentPath={guideUrl(guide)} showHeading={false}/></section>;
 const referencesContent=(authored?:React.ReactNode)=><section className="article-section" id="references" data-universal-section="References"><h2>References</h2>{authored}<ReferenceList sources={sources} order={ordered}/></section>;
 const updatesContent=(authored?:React.ReactNode)=><section className="article-section" id="update-history" data-universal-section="Update History"><span id="edition" className="reference-alias"/><h2>Update History</h2>{authored}<UpdateHistory pagePath={guideUrl(guide)} sectionIds={sectionIds}/></section>;
 const sourceContent=<section className="article-section" id="sources"><h2>Sources</h2><div id="references"><ReferenceList sources={sources} order={ordered} linkStudies={false}/></div></section>;
 const suitability=suitabilityFor(guideUrl(guide));
 const restrictionPeers=guide.type==='Condition'?content.guides.filter(g=>g.type==='Drug'&&(rows.some(row=>row.drugId===g.entityId)||suitability.some(row=>row.drug===g.title))):[];
 const statusRows=guide.type==='Drug'?STATUS_ROWS[guide.slug]:undefined;
 const statusCite=(ids:string[])=><>{orderCitationGroup(ids,ordered).map(id=>{const source=sources.find(item=>item.id===id);return source?<Citation key={id} source={source} n={ordered.indexOf(id)+1}/>:null})}</>;
 const statusTable=statusRows?.length?<div className="status-table-wrap"><table className="clinical-table status-table"><caption className="sr-only">Regulatory status by use</caption><thead><tr><th scope="col">Use / indication</th><th scope="col">Regulatory status</th></tr></thead><tbody>{statusRows.map(row=><tr key={row.use}><th scope="row">{row.use}</th><td><div className="status-table__value"><span className={row.status==='Approved'?'status-pill status-pill--approved':'status-pill status-pill--research'}>{row.status}</span>{statusCite(row.sourceIds)}</div><div className="status-table__meta"><span>Regulator: {row.regulator}</span><span>Year approved: {row.year??'—'}</span></div></td></tr>)}</tbody></table></div>:null;
 const renderModule=(module:UniversalArticleModule<Guide['sections'][number]>)=>{
  const authored=module.label==='Status'&&statusTable?<Fragment key="status-table">{!canonicalDrug?<span id={module.sections[0]?.id} className="reference-alias"/>:null}{canonicalDrug?module.sections.map(section=>renderSection(section,true,false)):null}{statusTable}</Fragment>:module.sections.map(section=>renderSection(section,true,module.label!=='Overview'&&!(module.label==='Evidence'&&hasEvidence)));
  const benefitSummary=module.label==='Overview'&&hiddenModules.has('section-benefits')?(universal?.modules.find(item=>item.label==='Benefits')?.sections||[]).map(section=>renderSection({...section,title:'',questions:[]},true,false)):null;
  if(module.kind==='mechanisms')return <Fragment key={module.id}>{authored}{mechanismsContent}</Fragment>;
  if(module.kind==='faqs')return <Fragment key={module.id}>{authored}{faqContent}</Fragment>;
  if(module.kind==='research')return <Fragment key={module.id}>{researchContent(authored)}</Fragment>;
  if(module.kind==='updates')return <Fragment key={module.id}>{updatesContent(authored)}</Fragment>;
  if(module.kind==='references')return <Fragment key={module.id}>{referencesContent(authored)}</Fragment>;
  return <section key={module.id} id={module.id} className="article-section universal-section" data-universal-section={module.label}>
   <h2 className={(module.label==='Status'&&statusTable)||(guide.type==='Drug'&&module.label==='Contraindications')?'status-heading':undefined}>{module.title}{guide.type==='Drug'&&module.label==='Contraindications'?<ContraindicationsInfo scope={suitability.length?suitabilityScope:undefined}/>:null}{module.label==='Status'&&statusTable?<StatusInfo/>:null}</h2>{module.label==='Evidence'&&hasEvidence&&!module.sections.some(section=>section.paragraph)?<EvidenceIntroduction/>:null}{authored}{benefitSummary}{module.label==='Evidence'&&hasEvidence&&module.sections.some(section=>section.paragraph)?<EvidenceIntroduction/>:null}
   {((guide.type==='Drug'&&module.label==='Contraindications')||(guide.type==='Condition'&&module.label==='Safety'))&&suitability.length>0?<TreatmentSuitability showHeading={guide.type!=='Drug'} rows={suitability} scope={canonicalDrug?'Selected restrictions from the cited U.S. product label. Contraindications, precautions, interaction concerns and evidence applicability are different categories. This table does not replace the complete label.':suitabilityScope} renderStatement={row=><CitedProse text={row.text} sourceIds={row.sourceIds} sources={sources} order={ordered} currentPath={guideUrl(guide)}/>}/>:null}
   {guide.type==='Condition'&&module.label==='Safety'&&restrictionPeers.length>0?<div className="treatment-suitability-links"><h3>Contraindications by intervention</h3><p>Check the drug-specific restrictions for the interventions discussed on this page.</p>{restrictionPeers.map(peer=><Link key={peer.id} href={guideUrl(peer)+'#section-contraindications'}>{peer.title}</Link>)}</div>:null}
   {module.scoped?<details className="research-item scoped-reading" id={module.scoped.id}><summary>{module.scoped.title}</summary><div className="research-item__body">{module.scoped.sections.map(section=>renderSection(section,true))}</div></details>:null}
   {module.label==='Evidence'&&hasEvidence?<EvidenceContent rows={rows} guide={guide} sources={sources} order={ordered}/>:null}
  </section>;
 };
 const topicArt=getTopicHeroArt(guideUrl(guide));
 const art=topicArt?{src:topicArt.src,srcSet:topicArt.srcSet,sizes:'(max-width: 767px) 200px, (max-width: 1199px) 30vw, 25vw',alt:topicArt.alt,title:topicArt.title,width:topicArt.width,height:topicArt.height}:{src:'/art/second-look-study.svg',alt:'A lens over a source page and its evidence trail',width:600,height:700};
 return <ArticleLayout hero={{title:guide.title,description:guide.description,breadcrumbs:[{label:'RemapRx',href:'/'},parent],kindLabel:guide.researchGoal?'Research goal':guide.type,art,artVariant:topicArt?'topic':undefined,authorSlot:<div className="sl-hero-author"><AuthorCard guide={guide}/></div>,updatedLabel:canonicalDrug?'Reader edition · November 5, 2026':'Reader edition · October 11, 2026',actions:<HeroActions saveSlot={<SaveButton id={guide.id} returnTo={guideUrl(guide)} label={'Save '+(guide.type==='Drug'?guide.title:'article')} className="research-hero__center-tag"/>} links={[...(universal||guide.sections.some(section=>section.id==='safety')?[{label:'Safety',href:universal?'#section-safety':'#safety',icon:<ShieldCheck/>}]:[]),...(!isRecord&&guide.faqs.length?[{label:'FAQs',href:'#faqs',icon:<MessagesSquare/>}]:[]),{label:'Evidence',href:evidenceTarget,icon:<ChartNoAxesColumnIncreasing/>},{label:'References',href:'#references',icon:<BookOpen/>}]}/>,snapshot:<PageSnapshot snapshot={snapshot} studiesHref={isRecord?'#references':'#research-feed'}/>}} leftRail={<ThemeSectionNav groups={groups}/>} shareRail={<ArticleSharing path={guideUrl(guide)} title={guide.title} kind={guide.type}/>} rightRail={<RelatedReading guide={guide}/> }>
 {guide.coverageLabel?<p className="coverage-label">{guide.coverageLabel}</p>:null}
 {hasCancerContext?<MedicalScopeNotice cancer/>:null}{universal?universal.blocks.filter(block=>!hiddenModules.has(block.module.id)).map(block=>renderModule(block.module)):<Fragment>{first.map(section=>renderSection(section))}{showMechanisms?mechanismsContent:null}{rest.map(section=>renderSection(section))}
 {scoped.length?<details className="research-item scoped-reading" id="condition-details"><summary>{guide.scopedSectionsTitle||'Condition-specific research details'}</summary><div className="research-item__body">{scoped.map(section=>renderSection(section))}</div></details>:null}
 {later.map(section=>renderSection(section))}{isRecord?<>{children}{guide.type!=='Glossary'&&sources[0]?<StudyFacts source={sources[0]}/>:null}{updatesContent()}{sourceContent}</>:readerTail.map(renderModule)}</Fragment>}
 </ArticleLayout>
}

export function ResearchLibrary({sources}:{sources:Source[]}){const [query,setQuery]=useState('');const filtered=sources.filter(s=>(s.title+' '+s.preview+' '+(s.doi||'')).toLowerCase().includes(query.toLowerCase().trim()));return <><label htmlFor="research-filter" className="form-label">Filter source records</label><input className="field" id="research-filter" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Drug, title or DOI"/><p className="small muted">{filtered.filter(isPrimarySource).length} primary report {filtered.filter(isPrimarySource).length===1?'record':'records'} · {filtered.filter(s=>!isPrimarySource(s)).length} background sources. Background sources appear in References and do not add primary results.</p>{filtered.length?<ResearchCatalog sources={filtered}/>:<p role="status">No source records match this search. Try a drug name, title or DOI.</p>}</>}
