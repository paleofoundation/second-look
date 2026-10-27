'use client';
import Link from 'next/link';
import outcomeRegistry from '@/data/outcome-registry.json';
import sentenceMapData from '@/data/outcome-sentence-maps.json';
const sentenceMaps=sentenceMapData.rows as Record<string,{finding:{text:string;sources:string[]}[];magnitude:{text:string;sources:string[]}[]}>;
import {Fragment,useEffect,useState,useRef} from 'react';
import {ShieldCheck,MessagesSquare,ChartNoAxesColumnIncreasing,BookOpen} from 'lucide-react';
import {Popover,PopoverTrigger,PopoverContent} from '@/components/ui/popover';
import {SaveButton} from '@/components/library-controls';
import {content,guideUrl,synthesisRows,isPrimarySource,type Guide,type Source,type SourceDetail,type SynthesisRow} from '@/lib/content';
import {AuthorCard} from '@/components/author-card';
import {HeroActions} from '@/components/shared-theme/article-actions';
import {orderCitationGroup,normalizeCitationSentence,sourceReferenceId} from '@/components/shared-theme/citations';
import {guideCitationOrder,articleSectionGroups,hasArticleEvidence} from '@/lib/citation-plan';
import {buildUniversalArticlePlan,buildArticleReaderTail,type UniversalArticleModule} from '@/components/shared-theme/universal-article';
import {ArticleLayout,ThemeSectionNav} from '@/components/shared-theme/theme';
import {EvidenceTable,type EvidenceFinding,type EvidenceSource} from '@/components/shared-theme/evidence-table';
import {MedicalScopeNotice} from '@/components/shared-theme/guide-catalogue';
import {MechanismSection} from '@/components/shared-theme/mechanisms';
import {hasMechanismSection,drugMechanismFor,mechanismContextsFor,mechanismPresentation} from '@/lib/mechanisms';
import {InlineFaqs} from '@/components/shared-theme/faqs';
import {UpdateHistory} from '@/components/shared-theme/update-history';
import type {ProtectedReview,ReviewAccess} from '@/lib/review-access';
import {OutcomeFinder,type OutcomeOption} from '@/components/shared-theme/outcome-finder';
import {wikiText,wikiTextRenderer} from '@/lib/wiki-links';
import {relatedReadingFor} from '@/lib/related-reading';
import {studyDesignsFor} from '@/lib/evidence-presentation';

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
/** Caller supplies this body only after the protected endpoint grants access. */
export function InlineStudyReview({review,sources,order,currentPath}:{review:ProtectedReview;sources:Source[];order:string[];currentPath:string}){
 return <div className="study-summary__review">
  {review.openingBlocks?.map(block=><section key={block.id} id={'study-'+review.id+'-opening-'+block.id}>
   <h4>{block.title}</h4>{block.questionIds.map(id=>{
    const answer=review.questionAnswers?.find(question=>question.id===id);
    return answer?<div key={id} id={'study-'+review.id+'-opening-'+block.id+'-'+id}>
     <CitedProse text={answer.answer} sourceIds={answer.sources} sources={sources} order={order} currentPath={currentPath}/>
     {answer.locators.length?<ul className="small">{answer.locators.map((locator,index)=><li key={index}>{[locator.file||locator.filename,locator.chapter,locator.section,locator.table_figure,locator.pdf_page!=null?'PDF page '+locator.pdf_page:null,locator.printed_page!=null?'Printed page '+locator.printed_page:null,locator.nativeLocator].filter(Boolean).join(' · ')}</li>)}</ul>:null}
    </div>:null;
   })}
  </section>)}
  {review.sections.map(section=><div key={section.id} id={'study-'+review.id+'-review-'+section.id}><h4>{section.title}</h4><CitedProse text={section.paragraph} mapped={section.sentences} sourceIds={section.sources} sources={sources} order={order} currentPath={currentPath}/></div>)}
 </div>;
}
/** Only the authorized review endpoint may supply a complete authored review. */
function StudySummary({source,sources,order,currentPath}:{source:Source;sources:Source[];order:string[];currentPath:string}){
 const [review,setReview]=useState<ProtectedReview|null>(null);
 const [requested,setRequested]=useState(false);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState(false);
 async function loadReview(){
  if(requested||busy)return;
  setBusy(true);setError(false);
  try{
   const response=await fetch('/api/reviews/'+encodeURIComponent(source.id),{credentials:'same-origin',cache:'no-store'});
   if(response.status===404){setRequested(true);return;}
   if(!response.ok)throw new Error('Review unavailable');
   const result=await response.json() as ReviewAccess;
   if(result.kind==='full'&&result.review.id===source.id){
    const candidate=result.review;
    // The public summary reserves this study's citation before FAQs. A review
    // with other sources uses its dedicated page so expansion cannot introduce
    // an earlier citation, renumber this page, or silently drop an unknown source.
    if(canRenderStudyReviewInline(candidate,source.id,sources,order))setReview(candidate);
   }
   setRequested(true);
  }catch{setError(true);}finally{setBusy(false);}
 }
 return <details className="research-item study-summary" id={'study-'+source.id} data-study-id={source.id} onToggle={event=>{if(event.currentTarget.open)void loadReview()}}>
  <summary>{source.title}<span className="meta" style={{display:'block'}}>{[source.population,source.year,source.design].filter(Boolean).join(' · ')}</span>{source.status==='Quarantined'?<span className="evidence-tag">Quarantined · not evidence for efficacy</span>:null}</summary>
  <div className="research-item__body">
   <h4>Study summary</h4><CitedProse text={source.preview} sourceIds={[source.id]} sources={sources} order={order} currentPath={currentPath}/>
   {source.decisiveLimit?<p className="notice">{wikiText(source.decisiveLimit,currentPath)}</p>:null}
   {source.correction?<p className="notice">{wikiText(source.correction,currentPath)}</p>:null}
   {busy?<p className="small" role="status">Loading study review…</p>:null}
   {error?<p className="small" role="status">The study review could not be loaded. <button type="button" onClick={()=>void loadReview()}>Retry</button></p>:null}
   {review?<InlineStudyReview review={review} sources={sources} order={order} currentPath={currentPath}/>:null}
   <div className="inline-actions"><a href={'/research/'+source.id}>Open study summary</a><OriginalSource source={source}/></div>
  </div>
 </details>;
}
function ResearchStudies({sources,order,currentPath=''}:{sources:Source[];order:string[];currentPath?:string}){
 const primary=sources.filter(isPrimarySource);
 return <div id="studies" data-research-feed><h3>Study summaries</h3>{primary.length?primary.map(source=><StudySummary key={source.id} source={source} sources={sources} order={order} currentPath={currentPath}/>):<p>This profile draws on the sources listed in References.</p>}</div>;
}
function ReferenceList({sources,order,linkStudies=true}:{sources:Source[];order:string[];linkStudies?:boolean}){
 return <ol className="bibliography">{order.map((id,i)=>{const source=sources.find(item=>item.id===id);return source?<li key={id} id={'ref-'+(i+1)} data-source-id={id} value={i+1}><span id={sourceReferenceId(id)} className="reference-alias"/><ReferenceTitle source={source}/>. {source.year}. {source.doi?'DOI: '+source.doi+'. ':(source as SourceDetail).doiMissingReason==='not_printed'?'DOI NOT PRINTED. ':''}<span>{source.design||'Source'}.</span>{source.locators?<p className="small">{(source.locators as {section?:string;table_figure?:string;basis?:string}[]).map(locator=>[locator.section,locator.table_figure,locator.basis].filter(Boolean).join(' · ')).join('; ')}</p>:null}{linkStudies&&isPrimarySource(source)?<a href={'#study-'+id}>Study summary</a>:null}</li>:null})}</ol>;
}
/** Directory/outcome callers retain the combined catalogue; articles use separate modules. */
export function ResearchCatalog({sources,order=sources.map(source=>source.id),currentPath=''}:{sources:Source[];order?:string[];currentPath?:string}){
 return <><ResearchStudies sources={sources} order={order} currentPath={currentPath}/><section id="references" className="article-section"><h2>References</h2><ReferenceList sources={sources} order={order}/></section></>;
}
function RelatedReading({guide}:{guide:Guide}){const related=relatedReadingFor(guide);return related.length?<nav className="related-reading" aria-label="Related reading"><h2>Related reading</h2><ul>{related.map(g=><li key={g.id}><a href={guideUrl(g)}>{g.title}</a></li>)}</ul></nav>:null}
function ContextRail({guide,sources,order}:{guide:Guide;sources:Source[];order:string[]}){const available=(value:unknown)=>value!==undefined&&value!==null&&String(value).trim()!==''&&!/^(?:not extracted|not recorded|not in corpus|unknown)(?:[.;]|$)/i.test(String(value).trim());const primary=sources.filter(source=>isPrimarySource(source)&&available(source.population));const source=sources[0];const sample=(source as SourceDetail|undefined)?.sampleDescription||source?.n;const prose=wikiTextRenderer(guideUrl(guide));const fact=(label:string,value:React.ReactNode)=>available(value)?<Fragment key={label}><dt>{label}</dt><dd>{typeof value==='string'?prose(value):value}</dd></Fragment>:null;const term=content.glossary.find(t=>'/glossary/'+t.slug===guide.slug);const sourceFact=(s:Source,value:React.ReactNode)=><>{typeof value==='string'?prose(value):value}<Citation source={s} n={order.indexOf(s.id)+1}/></>;return <aside className="context-rail"><RelatedReading guide={guide}/><dl>{guide.type==='Background source'||guide.type==='Study'?<>
 {guide.type==='Background source'?fact('Evidence role','Background source'):null}
 {fact('Design',source?.design)}{fact('Population',source?.population)}{fact('Year',source?.year)}
 {/computational|in silico/i.test(source?.design||'')?fact('Evidence type','Computational model; no treatment trial'):fact('Randomized N',source?.randomizedN)}
 {fact('Reported sample',sample)}
 {source&&available(source.intervention)?<><dt>Intervention</dt><dd>{sourceFact(source,source.intervention)}</dd></>:null}
 {source&&available(source.comparator)?<><dt>Comparator</dt><dd>{sourceFact(source,source.comparator)}</dd></>:null}
 {source&&available(source.pmid)?<><dt>PMID</dt><dd><a href={'https://pubmed.ncbi.nlm.nih.gov/'+source.pmid+'/'}>{source.pmid}</a></dd></>:null}
 {fact('Corrections',source?.correction)}
 </>:guide.type==='Glossary'?<><dt>Reading context</dt><dd>{term?.slug==='relative-risk'?'Also called risk ratio.':term?.title}</dd>{term?.slug==='relative-risk'?<><dt>Units</dt><dd>Ratio; the compared risks use the same event and timepoint.</dd></>:null}</>:guide.type==='Practical guide'?<><dt>Audience</dt><dd>Readers checking a research claim</dd><dt>Scope</dt><dd>Source reading and question preparation</dd><dt>Edition</dt><dd>Draft · 8 October 2026</dd><dt>Downloads</dt><dd><a href="/downloads/second-look-worksheet.pdf">Free worksheet</a><br/><a href="/downloads/second-look-guide-preview.pdf">Guide preview</a></dd></>:guide.type==='Evidence comparison'?<><dt>Selection</dt><dd>Teaching comparison; selected reports</dd><dt>Search cutoff</dt><dd>8 October 2026</dd><dt>Independent studies</dt><dd>Not established; family links require verification.</dd><dt>Missing material</dt><dd>See each study’s access and correction state</dd></>:<><dt>{guide.type==='Drug'?'Entity':'Question scope'}</dt><dd>{guide.title}</dd><dt>Scope</dt><dd>{prose(guide.scope|| (guide.type==='Condition'?'Acute-infection prevention and established-illness treatment are separate questions.':guide.id==='G-MET-PREVENT'?'Acute infection → later long COVID outcomes':guide.id==='G-MET-TREAT'||guide.id==='G-NMV-TREAT'?'Established long COVID → symptom or recovery outcomes':'Prevention and treatment records; no product-wide verdict'))}</dd><dt>Form, population and comparison</dt><dd>Study-specific; inspect the linked report.</dd><dt>Selected source populations</dt><dd>{primary.filter(s=>s.status!=='Quarantined').map(s=><p key={s.id}>{sourceFact(s,s.population)}</p>)}</dd></>}</dl><p><Link href="/glossary">Scientific terms</Link><br/><Link href="/methods">How we assess evidence</Link></p><Link href="/corrections">Suggest a correction</Link></aside>}

export function OutcomeEvidence({rows,guide,sources,order,compact=true}:{rows:SynthesisRow[];guide?:Guide;sources:Source[];order:string[];compact?:boolean}){
 const outcomeMap=outcomeRegistry.rowOutcomeMap as Record<string,string>;
 const citations=(ids:string[])=><>{orderCitationGroup(ids,order).map(id=>{const source=sources.find(s=>s.id===id);return source?<Citation key={id} source={source} n={order.indexOf(id)+1}/>:null})}</>;
 const meta=(field:{value:unknown;status:string;reason:string|null;sources:string[]})=>field.value==null?'Unknown':<>{String(field.value)}{citations(field.sources)}</>;
 const records:OutcomeOption[]=rows.map(row=>{const outcome=outcomeRegistry.outcomes.find(o=>o.id===outcomeMap[row.id])!;return {id:row.id,canonicalOutcomeId:outcome.id,registryState:outcome.registryState.replaceAll('_',' '),title:row.title,definition:outcome.definition.text,definitionCitation:citations(outcome.definition.sources),aliases:[...outcome.aliases,row.title,row.use],entity:{id:row.drugId,label:content.guides.find(g=>g.entityId===row.drugId)?.title||row.drugId},condition:{id:row.conditionId,label:content.guides.find(g=>g.entityId===row.conditionId)?.title||row.conditionId},population:row.population||'Unknown',design:[...new Set(row.effects.map(e=>e.design||'Unknown'))].join('; ')||'Unknown',assessment:row.certainty.label||'Unknown',timepoint:row.timepoint,comparator:row.comparison,instrument:meta(outcome.instrument),hierarchy:meta(outcome.endpointHierarchy),endpointRole:meta(outcome.clinicalOrSurrogateRole),measuredDirection:meta(outcome.measuredDirection),scaleDirection:meta(outcome.favorableScaleDirection),meaningfulChange:meta(outcome.meaningfulChange),clinicalMeaning:meta(outcome.clinicalInterpretation)}});
 const sourceViews:EvidenceSource[]=sources.toSorted((a,b)=>order.indexOf(a.id)-order.indexOf(b.id)).map(s=>({id:s.id,title:s.title,url:s.url,year:s.year,kind:isPrimarySource(s)?'Primary report':s.sourceType||'Background',primary:isPrimarySource(s),quarantined:s.status==='Quarantined',preview:s.preview,decisiveLimit:s.decisiveLimit,access:s.access,status:s.status,correction:s.correction,population:s.population,design:s.design,reviewUrl:'/research/'+s.id,reviewLabel:'Source details',sampleDetails:[...(s.randomizedN!=null?[{label:'Randomized participants',value:String(s.randomizedN)}]:[]),...((s as SourceDetail).sampleDescription?[{label:'Reported sample',value:(s as SourceDetail).sampleDescription!}]:s.n!=null&&s.n!==s.randomizedN?[{label:'Reported sample',value:String(s.n)}]:[]),...(s.intervention?[{label:'Intervention',value:s.intervention}]:[]),...(s.comparator?[{label:'Comparator',value:s.comparator}]:[])],locators:[...new Set(rows.flatMap(r=>r.sourceLocators?.filter(l=>l.sourceId===s.id).map(l=>l.label)||[]))]}));
 const findings:EvidenceFinding[]=rows.map(row=>{const outcome=outcomeRegistry.outcomes.find(o=>o.id===outcomeMap[row.id])!;const peer=content.guides.find(g=>g.entityId===(guide?.type==='Condition'?row.drugId:row.conditionId));return {id:row.id,title:row.title,studyDesigns:studyDesignsFor(row,sources),peer:peer?{title:peer.title,href:guideUrl(peer)}:undefined,use:row.use,population:row.population,comparison:row.comparison,endpoint:row.endpoint,timepoint:row.timepoint,status:row.status.replaceAll('_',' '),finding:row.finding.text,findingSources:row.finding.sources,findingSentences:sentenceMaps[row.id]?.finding,magnitudeSentences:sentenceMaps[row.id]?.magnitude,magnitude:row.magnitudeText,certainty:row.certainty,evidenceBase:row.evidenceBase,limits:row.limitations.map(l=>({text:l.text,sourceIds:l.sources})),sourceIds:row.sourceIds,familyIds:row.studyFamilyIds,background:!row.countsAsPrimaryEvidence,pending:row.coverage.pending,details:outcome.clinicalInterpretation.value==null?[]:[{label:'Clinical importance',value:meta(outcome.clinicalInterpretation)}]}});
 const renderRows=(ids:string[])=><EvidenceTable emptyMessage={rows.length?'No recorded outcome matches these filters.':'No outcome findings are available in this table.'} rows={ids.map(id=>findings.find(row=>row.id===id)!).filter(Boolean)} sources={sourceViews} renderText={wikiTextRenderer(guide?guideUrl(guide):'')} cite={ids=><>{orderCitationGroup(ids,order).map(id=>{const source=sources.find(s=>s.id===id);return source?<Citation key={id} source={source} n={order.indexOf(id)+1}/>:null})}</>}/>;
 return rows.length?<OutcomeFinder records={records} renderRows={renderRows} compact={compact}/>:renderRows([]);
}
function EvidenceIntroduction(){return <p>Each assessment applies to the outcome, population and treatment studied. High, Moderate and Low describe confidence in the specific finding, including findings of no benefit or harm. Select a grade, outcome or evidence count to inspect the grading rationale, findings and study limitations. <Link href="/methods">How we assess evidence.</Link></p>}
function EvidenceContent({rows,guide,sources,order}:{rows:SynthesisRow[];guide:Guide;sources:Source[];order:string[]}){return <><span id="findings" className="reference-alias"/><p className="small"><Link href="/outcomes">Explore and compare recorded outcomes</Link></p><OutcomeEvidence rows={rows} guide={guide} sources={sources} order={order}/></>}

export function Article({guide,sources,children,additionalCitationGroups=[]}:{guide:Guide;additionalCitationGroups?:string[][];sources:Source[];children?:React.ReactNode;acquisitionStatus?:{coverage_state:string;readerSummary:string;readerNextStep:string}}){
 const isRecord=['Study','Background source','Glossary'].includes(guide.type);const terminal=isRecord?'sources':'research-feed';const terminalLabel=isRecord?'Sources':'Research Feed';
 const rows=(guide.synthesisIds||[]).map(id=>synthesisRows.find(r=>r.id===id)).filter((r):r is SynthesisRow=>!!r);
 const hasEvidence=hasArticleEvidence(guide);
 const evidenceTarget=hasEvidence?'#section-evidence':'#'+(guide.sections.find(section=>section.label==='Evidence')?.id||terminal);
 const showMechanisms=hasMechanismSection(guide);const mechanismContexts=mechanismContextsFor(guide);const drugMechanism=drugMechanismFor(guide);
 const {first,rest,scoped,later,evidence}=articleSectionGroups(guide);
 const universal=guide.type==='Drug'||guide.type==='Condition'?buildUniversalArticlePlan({...guide,type:guide.type}):null;
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
 const primary=sources.filter(s=>isPrimarySource(s)&&s.status!=='Quarantined');
 const railLabel=(label:string)=>label.replace(/[^a-zA-Z0-9 ]/g,'').split(' ')[0]||'Overview';
 const groups=universal?.navigation||[...first.map(section=>({id:section.id,label:railLabel(section.label)})),...(showMechanisms?[{id:'mechanisms',label:'Mechanisms'}]:[]),...rest.map(section=>({id:section.id,label:railLabel(section.label)})),...(scoped.length?[{id:'condition-details',label:'Details'}]:[]),...later.map(section=>({id:section.id,label:railLabel(section.label)})),...(isRecord?[{id:'update-history',label:'Update History'},{id:terminal,label:terminalLabel}]:readerTail.map(module=>({id:module.id,label:module.label})))];
 const parent=guide.type==='Drug'?{label:'Drugs',href:'/drugs'}:guide.type==='Condition'?{label:'Conditions',href:'/conditions'}:isRecord?{label:guide.type==='Glossary'?'Glossary':'Research',href:guide.type==='Glossary'?'/glossary':'/research'}:{label:'Questions',href:'/questions'};

 const mechanismProse=(prose:NonNullable<typeof drugMechanism>['summary'])=>prose?<CitedProse text={prose.text} mapped={prose.sentences} currentPath={guideUrl(guide)} sourceIds={prose.sourceIds} sources={sources} order={ordered}/>:null;
 const mechanismsContent=<MechanismSection content={mechanismPresentation} renderText={wikiTextRenderer(guideUrl(guide))} originalAction={mechanismProse(drugMechanism?.originalAction)} summary={mechanismProse(drugMechanism?.summary)} pathways={(drugMechanism?.pathways||[]).map(pathway=>({id:pathway.id,title:pathway.title,explanation:mechanismProse(pathway)}))} rationales={(drugMechanism?.rationales||[]).map(row=>({id:row.id,condition:row.condition,conditionHref:row.conditionHref,rationale:mechanismProse(row.rationale),tested:mechanismProse(row.tested),limits:mechanismProse(row.limits)}))} questions={(drugMechanism?.questions||[]).map(question=>({id:question.id,title:question.title,answer:mechanismProse(question)}))} contexts={mechanismContexts.map(context=>({id:context.id,title:context.title,evidence:{basis:'secondary_description' as const,label:context.evidenceType,source:<p className="small muted">{context.locator}</p>},clinicalMeaning:context.clinicalMeaning,explanation:<><CitedProse text={context.text} currentPath={guideUrl(guide)} sourceIds={context.sourceIds} sources={sources} order={ordered}/></>}))}/>;
 const faqContent=guide.faqs.length?<InlineFaqs items={guide.faqs.map((f,i)=>({id:f.id||'question-'+i,aliases:f.id?['question-'+i]:[],question:f.question,answer:<CitedProse text={f.answer} mapped={f.sentences} currentPath={guideUrl(guide)} sourceIds={f.sources} sources={sources} order={ordered}/>}))}/>:<section id="faqs" className="article-section"><h2>FAQs</h2></section>;
 const sectionIds=[...groups.map(group=>group.id),...guide.sections.map(section=>section.id),'research','studies','edition','references'];
 const researchContent=(authored?:React.ReactNode)=><section className="article-section" id="research-feed" data-universal-section="Research Feed"><span id="research" className="reference-alias"/><h2>Research Feed</h2>{authored}{children}<ResearchStudies sources={sources} order={ordered} currentPath={guideUrl(guide)}/></section>;
 const referencesContent=(authored?:React.ReactNode)=><section className="article-section" id="references" data-universal-section="References"><h2>References</h2>{authored}<ReferenceList sources={sources} order={ordered}/></section>;
 const updatesContent=(authored?:React.ReactNode)=><section className="article-section" id="update-history" data-universal-section="Update History"><span id="edition" className="reference-alias"/><h2>Update History</h2>{authored}<UpdateHistory pagePath={guideUrl(guide)} sectionIds={sectionIds}/></section>;
 const sourceContent=<section className="article-section" id="sources"><h2>Sources</h2><div id="references"><ReferenceList sources={sources} order={ordered} linkStudies={false}/></div></section>;
 const renderModule=(module:UniversalArticleModule<Guide['sections'][number]>)=>{
  const authored=module.sections.map(section=>renderSection(section,true,module.label!=='Overview'&&!(module.label==='Evidence'&&hasEvidence)));
  if(module.kind==='mechanisms')return <Fragment key={module.id}>{authored}{mechanismsContent}</Fragment>;
  if(module.kind==='faqs')return <Fragment key={module.id}>{authored}{faqContent}</Fragment>;
  if(module.kind==='research')return <Fragment key={module.id}>{researchContent(authored)}</Fragment>;
  if(module.kind==='updates')return <Fragment key={module.id}>{updatesContent(authored)}</Fragment>;
  if(module.kind==='references')return <Fragment key={module.id}>{referencesContent(authored)}</Fragment>;
  return <section key={module.id} id={module.id} className="article-section universal-section" data-universal-section={module.label}>
   <h2>{module.title}</h2>{module.label==='Evidence'&&hasEvidence&&!module.sections.some(section=>section.paragraph)?<EvidenceIntroduction/>:null}{authored}{module.label==='Evidence'&&hasEvidence&&module.sections.some(section=>section.paragraph)?<EvidenceIntroduction/>:null}
   {module.scoped?<details className="research-item scoped-reading" id={module.scoped.id}><summary>{module.scoped.title}</summary><div className="research-item__body">{module.scoped.sections.map(section=>renderSection(section,true))}</div></details>:null}
   {module.label==='Evidence'&&hasEvidence?<EvidenceContent rows={rows} guide={guide} sources={sources} order={ordered}/>:null}
  </section>;
 };
 return <ArticleLayout hero={{title:guide.title,description:guide.description,breadcrumbs:[{label:'Second Look',href:'/'},parent],kindLabel:guide.researchGoal?'Research goal':guide.type,art:{src:'/art/second-look-study.svg',alt:'A lens over a source page and its evidence trail',width:600,height:700},authorSlot:<div className="sl-hero-author"><AuthorCard guide={guide}/></div>,updatedLabel:'Reader edition · 11 October 2026',actions:<HeroActions saveSlot={<SaveButton id={guide.id} returnTo={guideUrl(guide)} label={'Save '+(guide.type==='Drug'?guide.title:'article')} className="research-hero__center-tag"/>} links={[...(universal||guide.sections.some(section=>section.id==='safety')?[{label:'Safety',href:universal?'#section-safety':'#safety',icon:<ShieldCheck/>}]:[]),...(!isRecord&&guide.faqs.length?[{label:'FAQs',href:'#faqs',icon:<MessagesSquare/>}]:[]),{label:'Evidence',href:evidenceTarget,icon:<ChartNoAxesColumnIncreasing/>},{label:'References',href:'#references',icon:<BookOpen/>}]}/>,snapshot:<div className="sl-hero-snapshot"><strong>Research sources</strong><p>{primary.length} primary report records · {sources.filter(s=>!isPrimarySource(s)).length} background sources</p><a href={'#'+terminal}>Inspect the source set</a>{hasEvidence?<a href="#section-evidence">Evidence</a>:null}</div>}} leftRail={<ThemeSectionNav groups={groups}/>} rightRail={<ContextRail guide={guide} sources={sources} order={ordered}/> }>
 {guide.coverageLabel?<p className="coverage-label">{guide.coverageLabel}</p>:null}
 {/cancer/i.test(guide.title+' '+(guide.scope||''))?<MedicalScopeNotice cancer/>:null}{universal?universal.blocks.map(block=>renderModule(block.module)):<Fragment>{first.map(section=>renderSection(section))}{showMechanisms?mechanismsContent:null}{rest.map(section=>renderSection(section))}
 {scoped.length?<details className="research-item scoped-reading" id="condition-details"><summary>{guide.scopedSectionsTitle||'Condition-specific research details'}</summary><div className="research-item__body">{scoped.map(section=>renderSection(section))}</div></details>:null}
 {later.map(section=>renderSection(section))}{isRecord?<>{children}{updatesContent()}{sourceContent}</>:readerTail.map(renderModule)}</Fragment>}
 </ArticleLayout>
}

export function ResearchLibrary({sources}:{sources:Source[]}){const [query,setQuery]=useState('');const filtered=sources.filter(s=>(s.title+' '+s.preview+' '+(s.doi||'')).toLowerCase().includes(query.toLowerCase().trim()));return <><label htmlFor="research-filter" className="form-label">Filter source records</label><input className="field" id="research-filter" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Drug, title or DOI"/><p className="small muted">{filtered.filter(isPrimarySource).length} primary report {filtered.filter(isPrimarySource).length===1?'record':'records'} · {filtered.filter(s=>!isPrimarySource(s)).length} background sources. Background sources appear in References and do not add primary results.</p>{filtered.length?<ResearchCatalog sources={filtered}/>:<p role="status">No source records match this search. Try a drug name, title or DOI.</p>}</>}
