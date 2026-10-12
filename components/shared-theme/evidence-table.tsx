'use client';

import {Fragment,useEffect,useRef,useState,type ReactNode} from 'react';
import Link from 'next/link';
import {Dialog,Popover} from 'radix-ui';
import {FileText,ChevronDown,X,Info,UserRound,ArrowDown,ArrowUp} from 'lucide-react';
import {evidenceForSummaries,type OutcomeSummary} from '@/lib/outcome-summary';
import type {EvidenceMechanism} from '@/lib/mechanisms';
import {normalizeCitationSentence} from './citations';
import {type ConfidenceRow} from './evidence-confidence';

/** PepsAnon EvidenceTable/ResearchPanel port. Canonical identities replace URL dedupe.
 * Body contains principal findings and public source previews only, never full reviews. */
export type EvidenceSource={id:string;title:string;url?:string|null;pdfUrl?:string|null;year?:string|number|null;kind:string;primary:boolean;quarantined?:boolean;preview:string;decisiveLimit?:string;access?:string;status?:string;correction?:string;population?:string;design?:string;sampleDetails?:{label:string;value:string}[];reviewUrl:string;reviewLabel:string;locators:string[]};
export type EvidenceFinding={id:string;title:string;peer?:{title:string;href:string};use:string;population:string;comparison:string;endpoint:string;timepoint:string;status:string;finding:string;findingSources?:string[];findingSentences?:{text:string;sources:string[]}[];magnitude:string;magnitudeSentences?:{text:string;sources:string[]}[];certainty:NonNullable<ConfidenceRow['certainty']>;evidenceBase:string;studyDesigns?:{text:string;sourceIds:string[]}[];limits:{text:string;sourceIds:string[]}[];sourceIds:string[];familyIds:string[];background:boolean;pending:string[];details?:{label:string;value:ReactNode}[]};
export type CitationRenderer=(sourceIds:string[])=>ReactNode;
export type EvidenceTextRenderer=(text:string,linked?:Set<string>)=>ReactNode;
const plainText:EvidenceTextRenderer=text=>text;
const validUrl=(url?:string|null)=>!!url&&(/^https:\/\//.test(url)||/^\/(?!\/)/.test(url));
function SourceLink({url,children}:{url?:string|null;children:ReactNode}){return validUrl(url)?<a href={url!} target={url!.startsWith('https:')?'_blank':undefined} rel="noreferrer">{children}</a>:<span>{children} unavailable</span>}

export type EvidenceSummary = OutcomeSummary & {
 peer?: {title:string;href:string};
 mechanisms?: EvidenceMechanism[];
};
const headerHelp = {
 condition: 'The health condition or goal that was studied.',
 intervention: 'What was tested: the repurposed drug or exact drug regimen.',
 outcome: 'The specific, measurable endpoints that were studied.',
 grade: 'The A–F letter grade indicates how likely an intervention is to benefit this outcome. It considers the number of independent trials, consistency, study limitations and strength of the observed effects. Grades can change as the evidence evolves. See Methods for the RemapRx grading scale.',
 effect: 'How big the change was, summarized across compatible trials. Numerical estimates are shown when a small, moderate or large classification is not established.',
 evidence: 'The number of independent randomized controlled trials and the participants contributing to this outcome. Multiple reports from the same trial count once; other evidence is identified separately.',
};
function HeaderHelp({label,text}:{label:string;text:string}) {
 const [open,setOpen]=useState(false);
 return <Popover.Root open={open} onOpenChange={setOpen}><Popover.Trigger asChild><button className="evidence-header-help" type="button" aria-label={'About '+label} onMouseEnter={()=>setOpen(true)} onFocus={()=>setOpen(true)} onBlur={()=>setOpen(false)} onClick={event=>{event.preventDefault();setOpen(true)}}><Info aria-hidden="true"/></button></Popover.Trigger><Popover.Portal><Popover.Content className="evidence-header-tooltip" role="tooltip" sideOffset={10} onCloseAutoFocus={event=>event.preventDefault()} onOpenAutoFocus={event=>event.preventDefault()} onMouseLeave={()=>setOpen(false)}>{text}<Popover.Arrow/></Popover.Content></Popover.Portal></Popover.Root>;
}
function EvidenceCount({summaries,title,onOpen,participants=true}:{summaries:EvidenceSummary[];title:string;onOpen:(button:HTMLButtonElement)=>void;participants?:boolean}) {
 const evidence=evidenceForSummaries(summaries);
 return <><button type="button" className="evidence-count-link" aria-haspopup="dialog" aria-label={'View evidence for '+title} onClick={event=>onOpen(event.currentTarget)}><FileText aria-hidden="true"/><span>{evidence.rctCount} {evidence.rctCount===1?'RCT':'RCTs'}</span></button>{participants&&<span className="evidence-participants"><UserRound aria-hidden="true"/><span>Participants: {evidence.participants===null?'Not totaled':evidence.participants.toLocaleString('en-US')}</span></span>}{evidence.rctCount===0?<span className="evidence-source-note">View other evidence</span>:null}</>;
}

export function EvidenceTable({rows,summaries=[],sources,cite,renderText=plainText,variant='drug',emptyMessage='No outcome findings are available in this table.'}:{rows:EvidenceFinding[];summaries?:EvidenceSummary[];sources:EvidenceSource[];cite:CitationRenderer;renderText?:EvidenceTextRenderer;variant?:'drug'|'condition';emptyMessage?:string}) {
 const [selection,setSelection]=useState<{title:string;items:EvidenceSummary[]}|null>(null);
 const [collapsed,setCollapsed]=useState<Set<string>>(()=>new Set());
 const [portalContainer,setPortalContainer]=useState<HTMLElement|undefined>();
 const tableRef=useRef<HTMLElement|null>(null);
 const [opener,setOpener]=useState<HTMLButtonElement|null>(null);
 const groups=Object.values(summaries.reduce<Record<string,{id:string;title:string;href?:string;items:EvidenceSummary[]}>>((all,item)=>{
  const id=variant==='condition'?item.drugId:item.conditionId;
  (all[id]||=( {id,title:item.peer?.title||id,href:item.peer?.href,items:[]} )).items.push(item);
  return all;
 },{}));
 const open=(items:EvidenceSummary[],title:string,button:HTMLButtonElement)=>{setOpener(button);setPortalContainer(button.closest<HTMLElement>('.omr-theme')||undefined);setSelection({items,title})};
 const summariesRef=useRef(summaries);
 useEffect(()=>{summariesRef.current=summaries},[summaries]);
 useEffect(()=>{
  const reveal=()=>{
   let fragment:string;try{fragment=decodeURIComponent(location.hash.slice(1))}catch{return}
   const summary=summariesRef.current.find(item=>item.id===fragment||item.synthesisIds.includes(fragment));
   if(!summary)return;
   setCollapsed(current=>{const next=new Set(current);next.delete(variant==='condition'?summary.drugId:summary.conditionId);return next});
   const button=tableRef.current?.querySelector<HTMLButtonElement>(`[data-summary-id="${summary.id}"]`);
   if(button)open([summary],summary.label,button);
  };
  const click=(event:MouseEvent)=>{const link=(event.target as Element).closest?.('a[href^="#"]');if(link&&!event.defaultPrevented)requestAnimationFrame(reveal)};
  reveal();window.addEventListener('hashchange',reveal);document.addEventListener('click',click);
  return()=>{window.removeEventListener('hashchange',reveal);document.removeEventListener('click',click)};
 },[variant]);
 const cited=(text:string,ids:string[],mapped?:{text:string;sources:string[]}[])=>{
  const linked=new Set<string>();
  return (mapped||Array.from(new Intl.Segmenter('en',{granularity:'sentence'}).segment(text),part=>({text:part.segment,sources:ids}))).map((part,i)=><span key={i}>{renderText(normalizeCitationSentence(part.text),linked)}{cite(part.sources)}{' '}</span>);
 };
 const selectedRows=rows.filter(row=>selection?.items.some(item=>item.synthesisIds.includes(row.id)));
 const mechanisms=[...new Map((selection?.items.flatMap(item=>item.mechanisms||[])||[]).map(item=>[item.id,item])).values()];
 const clinicalIds=new Set(selection?.items.flatMap(item=>item.sourceIds)||[]);
 const selectedIds=new Set([...clinicalIds,...mechanisms.flatMap(item=>item.sourceIds)]);
 const selectedSources=sources.filter(source=>selectedIds.has(source.id));
 const excluded=(source:EvidenceSource)=>source.quarantined||/quarantin|withdrawn/i.test(source.status||'');
 const primarySources=selectedSources.filter(source=>source.primary&&clinicalIds.has(source.id)&&!excluded(source));
 const additionalSources=selectedSources.filter(source=>!primarySources.includes(source));
 const evidence=selection?evidenceForSummaries(selection.items):null;
 const sourceCards=(records:EvidenceSource[])=> <ul className="research-source-list">{records.map(source=><li key={source.id} data-source-id={source.id}>
  <SourceLink url={source.url}><span className="research-source-title">{source.title}</span></SourceLink>
  <span className="research-source-meta">{source.kind} · {source.year||'Date not recorded'}</span>
  {excluded(source)?<p className="research-panel-limitation">This report is excluded from evidence conclusions.</p>:null}
  <details className="research-study-details"><summary aria-label={`${source.primary?'Study':'Source'} details: ${source.title}`}><span>{source.primary?'Study':'Source'} details</span><ChevronDown aria-hidden="true"/></summary>
   <div className="research-study-details__body"><div className="research-study-summary"><h3>Study summary</h3><p>{cited(source.preview,[source.id])}</p></div>
    <dl className="research-facts">{source.design?<><dt>Trial design</dt><dd>{renderText(source.design)}</dd></>:null}{source.population?<><dt>Population / model</dt><dd>{renderText(source.population)}</dd></>:null}{source.sampleDetails?.map((detail,index)=><Fragment key={index}><dt>{detail.label}</dt><dd>{renderText(detail.value)}</dd></Fragment>)}{source.access?<><dt>Source access</dt><dd>{source.access}</dd></>:null}</dl>
    {source.decisiveLimit?<p className="research-panel-limitation">{cited(source.decisiveLimit,[source.id])}</p>:null}{source.correction&&source.correction!==source.decisiveLimit?<p className="research-panel-limitation">{cited(source.correction,[source.id])}</p>:null}
    {source.locators.length?<details><summary>Source locations</summary><ul className="research-page-locators">{source.locators.map((locator,index)=><li key={index}>{locator}</li>)}</ul></details>:null}
    <div className="research-source-links"><SourceLink url={source.url}>Original source</SourceLink>{validUrl(source.pdfUrl)?<SourceLink url={source.pdfUrl}>Study PDF</SourceLink>:null}<a href={source.reviewUrl}>{source.reviewLabel}</a></div>
   </div>
  </details>
 </li>)}</ul>;
 return <Dialog.Root open={!!selection} onOpenChange={value=>{if(!value)setSelection(null)}}>
  {groups.length>0?<div className="evidence-expansion-controls"><button type="button" onClick={()=>setCollapsed(new Set())}>Expand all <ArrowDown aria-hidden="true"/></button><button type="button" onClick={()=>setCollapsed(new Set(groups.map(group=>group.id)))}>Collapse all <ArrowUp aria-hidden="true"/></button></div>:null}
  <figure ref={tableRef} className="wp-block-table evidence-table evidence-assessments outcome-summary-table" role="region" aria-label="Evidence table" tabIndex={0}>
   <table><thead><tr>{[
    [variant==='condition'?'Intervention':'Health condition',variant==='condition'?headerHelp.intervention:headerHelp.condition],['Outcome',headerHelp.outcome],['Grade',headerHelp.grade],['Effect',headerHelp.effect],['Evidence',headerHelp.evidence],
   ].map(([label,help])=><th scope="col" key={label}><span>{label}</span><HeaderHelp label={label} text={help}/></th>)}</tr></thead>
   <tbody>{groups.length===0?<tr className="evidence-empty-row"><td colSpan={5}>{emptyMessage}</td></tr>:groups.map(group=><Fragment key={group.id}>
    <tr className="evidence-group-row" data-group-id={group.id}><th scope="rowgroup"><span className="evidence-group-heading">{group.href?<a href={group.href}>{group.title}</a>:group.title}<button type="button" className="evidence-group-toggle" aria-label={`${collapsed.has(group.id)?'Expand':'Collapse'} ${group.title} outcomes`} aria-expanded={!collapsed.has(group.id)} onClick={()=>setCollapsed(current=>{const next=new Set(current);if(next.has(group.id))next.delete(group.id);else next.add(group.id);return next})}><ChevronDown aria-hidden="true"/></button></span></th><td>{group.items.length} {group.items.length===1?'outcome':'outcomes'}</td><td/><td/><td><EvidenceCount summaries={group.items} title={group.title} participants={false} onOpen={button=>open(group.items,group.title,button)}/></td></tr>
    {group.items.map(summary=><tr id={summary.synthesisIds[0]} key={summary.id} data-outcome-summary={summary.id} hidden={collapsed.has(group.id)}>
     <td className="evidence-group-spacer"><span className="sr-only">{group.title}</span></td>
     <td data-label="Outcome">{summary.synthesisIds.slice(1).map(id=><span className="reference-alias" id={id} key={id}/>)}<button type="button" data-summary-id={summary.id} className="research-outcome-trigger" onClick={event=>open([summary],summary.label,event.currentTarget)} aria-haspopup="dialog" aria-label={'Inspect outcome: '+summary.label}>{summary.label}</button><span className="outcome-purpose">{summary.purpose}</span></td>
     <td data-label="Grade" className="evidence-grade-cell"><button type="button" className={`evidence-grade-trigger benefit-grade grade-${summary.grade.value?.toLowerCase()||'ungraded'}`} aria-haspopup="dialog" title={summary.grade.label} aria-label={`${summary.grade.value?'Grade '+summary.grade.value:summary.grade.label}: ${summary.label}`} onClick={event=>open([summary],summary.label,event.currentTarget)}>{summary.grade.value||'—'}</button>{!summary.grade.value?<span className="evidence-ungraded-label">{summary.grade.label}</span>:null}</td>
     <td data-label="Effect" className="evidence-effect-cell"><span className="evidence-effect-label">{summary.effect.label}</span><span className="evidence-effect-detail">{renderText(summary.effect.detail)}</span><span className="evidence-effect-citations">{cite(summary.sourceIds)}</span></td>
     <td data-label="Evidence"><EvidenceCount summaries={[summary]} title={summary.label} onOpen={button=>open([summary],summary.label,button)}/></td>
    </tr>)}
   </Fragment>)}</tbody></table>
  </figure>
  <Dialog.Portal container={portalContainer}><Dialog.Overlay className="research-panel-backdrop" data-slot="sheet-overlay"/><Dialog.Content aria-modal="true" className="research-detail-panel" data-slot="sheet-content" onCloseAutoFocus={event=>{event.preventDefault();opener?.focus({preventScroll:true})}}>
   <header className="research-detail-panel__header"><div><Dialog.Title data-slot="sheet-title">{evidence?.rctCount?`${evidence.rctCount} randomized ${evidence.rctCount===1?'trial':'trials'}`:'Research evidence'}</Dialog.Title><Dialog.Description data-slot="sheet-description">{selection?.title}</Dialog.Description></div><Dialog.Close className="research-panel-close" aria-label="Close research details"><X aria-hidden="true"/></Dialog.Close></header>
   <div className="research-detail-panel__body">{selection?<>
    <p className="research-evidence-counts">{evidence?.participants!==null?`${evidence?.participants.toLocaleString('en-US')} participants · `:''}{primarySources.length} {primarySources.length===1?'primary report':'primary reports'}. {evidence?.participantBasis}</p>
    <h3 className="research-studies-heading">Studies</h3>{primarySources.length?sourceCards(primarySources):<p>No completed randomized trial contributes to this assessment. The available supporting sources are listed below.</p>}
    {selection.items.map(summary=><details className="research-outcome-details research-summary-assessment" key={summary.id}><summary>{summary.label}: grade and effect <ChevronDown aria-hidden="true"/></summary><div><div className="research-assessment-line"><span className={`benefit-grade grade-${summary.grade.value?.toLowerCase()||'ungraded'}`}>{summary.grade.value||'—'}</span><div><strong>{summary.grade.label}</strong><p>{summary.effect.detail}</p></div></div><p>{cited(summary.grade.rationale,summary.grade.sourceIds)}</p><details className="research-outcome-details"><summary>Effect and assessment details <ChevronDown aria-hidden="true"/></summary><div><p>{cited(summary.effect.rationale,summary.sourceIds)}</p><p>{summary.aggregationNote}</p><p><Link href="/methods">How RemapRx grades outcomes</Link></p></div></details></div></details>)}
    {mechanisms.length?<details className="research-outcome-details research-mechanisms"><summary>Proposed mechanisms <ChevronDown aria-hidden="true"/></summary><div>{mechanisms.map(mechanism=><section key={mechanism.id}><h3>{mechanism.title}</h3>{mechanism.evidenceType?<p className="small">{mechanism.evidenceType} · {mechanism.locator}</p>:null}<p>{cited(mechanism.rationale.text,mechanism.rationale.sourceIds,mechanism.rationale.sentences)}</p>{mechanism.tested?<p><strong>What was tested. </strong>{cited(mechanism.tested.text,mechanism.tested.sourceIds,mechanism.tested.sentences)}</p>:null}{mechanism.limits?<p className="research-panel-limitation">{cited(mechanism.limits.text,mechanism.limits.sourceIds,mechanism.limits.sentences)}</p>:null}</section>)}</div></details>:null}
    <details className="research-outcome-details"><summary>Findings, scope and limitations <ChevronDown aria-hidden="true"/></summary><div>{selectedRows.map(row=><section key={row.id}><h3>{row.title}</h3><p>{cited(row.finding,row.findingSources||row.sourceIds,row.findingSentences)}</p><p><strong>Magnitude: </strong>{cited(row.magnitude,row.sourceIds,row.magnitudeSentences)}</p><dl className="research-facts"><dt>Use</dt><dd>{renderText(row.use)}</dd><dt>Population / model</dt><dd>{renderText(row.population)}</dd><dt>Comparator</dt><dd>{renderText(row.comparison)}</dd><dt>Outcome</dt><dd>{renderText(row.endpoint)}</dd><dt>Timepoint</dt><dd>{renderText(row.timepoint)}</dd>{row.details?.map((detail,index)=><Fragment key={index}><dt>{detail.label}</dt><dd>{detail.value}</dd></Fragment>)}</dl>{row.limits.map((limit,index)=><p className="research-panel-limitation" key={index}>{cited(limit.text,limit.sourceIds)}</p>)}<details className="research-outcome-details"><summary>Evidence certainty: {row.certainty.label} <ChevronDown aria-hidden="true"/></summary><div><p>{cited(row.certainty.rationale,row.certainty.sourceIds||row.sourceIds)}</p>{row.certainty.domains?.map(domain=><p key={domain.name}><strong>{domain.name}: </strong>{cited(domain.text,domain.sourceIds)}</p>)}<p>{row.certainty.scope}</p>{row.certainty.basis?.length?<details className="research-study-details"><summary>Assessment source locations <ChevronDown aria-hidden="true"/></summary><ul>{row.certainty.basis.map((basis,index)=><li key={index}>{cited(basis.locator,[basis.sourceId])}</li>)}</ul></details>:null}<p className="small">{row.certainty.method} · {row.certainty.assessedAt}. Confidence in this finding is assessed separately from likelihood of benefit.</p></div></details></section>)}</div></details>
    {additionalSources.length?<details className="research-additional-sources"><summary>Additional sources ({additionalSources.length}) <ChevronDown aria-hidden="true"/></summary>{sourceCards(additionalSources)}</details>:null}
   </>:null}</div>
  </Dialog.Content></Dialog.Portal>
 </Dialog.Root>;
}
