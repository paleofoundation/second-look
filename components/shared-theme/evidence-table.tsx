'use client';

import {useRef,useState,type ReactNode} from 'react';
import Link from 'next/link';
import {Dialog} from 'radix-ui';
import {FileText,ChevronDown,X} from 'lucide-react';
import {normalizeCitationSentence} from './citations';
import {describeEvidenceConfidence,type ConfidenceRow} from './evidence-confidence';

/** PepsAnon EvidenceTable/ResearchPanel port. Canonical identities replace URL dedupe.
 * Body contains principal findings and public source previews only, never full reviews. */
export type EvidenceSource={id:string;title:string;url?:string|null;pdfUrl?:string|null;year?:string|number|null;kind:string;primary:boolean;quarantined?:boolean;preview:string;decisiveLimit?:string;access?:string;status?:string;correction?:string;population?:string;design?:string;sampleDetails?:{label:string;value:string}[];reviewUrl:string;reviewLabel:string;locators:string[]};
export type EvidenceFinding={id:string;title:string;peer?:{title:string;href:string};use:string;population:string;comparison:string;endpoint:string;timepoint:string;status:string;finding:string;findingSources?:string[];findingSentences?:{text:string;sources:string[]}[];magnitude:string;magnitudeSentences?:{text:string;sources:string[]}[];certainty:NonNullable<ConfidenceRow['certainty']>;evidenceBase:string;studyDesigns?:{text:string;sourceIds:string[]}[];limits:{text:string;sourceIds:string[]}[];sourceIds:string[];familyIds:string[];background:boolean;pending:string[];details?:{label:string;value:ReactNode}[]};
export type CitationRenderer=(sourceIds:string[])=>ReactNode;
export type EvidenceTextRenderer=(text:string,linked?:Set<string>)=>ReactNode;
const plainText:EvidenceTextRenderer=text=>text;
const validUrl=(url?:string|null)=>!!url&&(/^https:\/\//.test(url)||/^\/(?!\/)/.test(url));
function SourceLink({url,children}:{url?:string|null;children:ReactNode}){return validUrl(url)?<a href={url!} target={url!.startsWith('https:')?'_blank':undefined} rel="noreferrer">{children}</a>:<span>{children} unavailable</span>}

export function EvidenceTable({rows,sources,cite,renderText=plainText,emptyMessage='No outcome findings are available in this table.'}:{rows:EvidenceFinding[];sources:EvidenceSource[];cite:CitationRenderer;renderText?:EvidenceTextRenderer;emptyMessage?:string}){
 const cited=(text:string,ids:string[],mapped?:{text:string;sources:string[]}[])=>{
  const linked=new Set<string>();
  const sentences=mapped||Array.from(new Intl.Segmenter('en',{granularity:'sentence'}).segment(text),part=>({text:part.segment,sources:ids}));
  return sentences.map((part,i)=><span key={i}>{renderText(normalizeCitationSentence(part.text),linked)}{cite(part.sources)}{' '}</span>);
 };
 const [selected,setSelected]=useState<EvidenceFinding|null>(null);
 const [portalContainer,setPortalContainer]=useState<HTMLElement|undefined>(undefined);
 const opener=useRef<HTMLButtonElement|null>(null);
 const open=(row:EvidenceFinding,button:HTMLButtonElement)=>{opener.current=button;setPortalContainer(button.closest<HTMLElement>('.omr-theme')||undefined);setSelected(row)};
 const readerConfidence=(row:EvidenceFinding)=>{
  const confidence=describeEvidenceConfidence(row,sources);
  return {...confidence,label:confidence.category==='assessed'?confidence.label:'Not graded',basis:confidence.category==='unassessed'?row.evidenceBase:confidence.basis};
 };
 const sourceRecords=(row:EvidenceFinding)=>[...new Map(sources.filter(source=>row.sourceIds.includes(source.id)).map(source=>[source.id,source])).values()];
 const excluded=(source:EvidenceSource)=>source.quarantined||/quarantin|withdrawn/i.test(source.status||'');
 const counts=(row:EvidenceFinding)=>{
  const records=sourceRecords(row);
  return {total:records.length,reports:records.filter(source=>source.primary&&!excluded(source)).length,background:records.filter(source=>!source.primary).length,excluded:records.filter(source=>source.primary&&excluded(source)).length,families:new Set(row.familyIds).size};
 };
 const studyDesigns=(row:EvidenceFinding)=>{
  const recorded=row.studyDesigns?.filter(design=>design.text.trim());
  if(recorded?.length)return recorded;
  const grouped=new Map<string,string[]>();
  for(const source of sourceRecords(row)){
   if(source.design?.trim())grouped.set(source.design,[...(grouped.get(source.design)||[]),source.id]);
  }
  return grouped.size?[...grouped].map(([text,sourceIds])=>({text,sourceIds})):[{text:row.evidenceBase,sourceIds:row.sourceIds}];
 };
 const selectedSources=selected?sourceRecords(selected):[];
 const selectedConfidence=selected?readerConfidence(selected):null;
 const outcomeState=(row:EvidenceFinding)=>({background_only:'Background context',exploratory:'Exploratory analysis',computational_result:'Computer model',held:'Result on hold',provisional_correction_hold:'Correction notice'}[row.status.replaceAll(' ','_')]||'');
 const gradeClass=(label:string,assessed:boolean)=>{
  if(!assessed)return 'grade-none';
  const grade=label.trim().toLowerCase();
  return /^(high|moderate|low|very low)( certainty| confidence)?$/.test(grade)?`grade-${grade.replace(/ (certainty|confidence)$/,'').replaceAll(' ','-')}`:'grade-none';
 };

 return <Dialog.Root open={!!selected} onOpenChange={value=>{if(!value)setSelected(null)}}>
  <figure className="wp-block-table evidence-table evidence-assessments" role="region" aria-label="Evidence table" tabIndex={0}>
   <table>
    <thead><tr><th scope="col">Outcome and study design</th><th scope="col">Grade</th><th scope="col">Evidence</th></tr></thead>
    <tbody>{rows.length===0?<tr className="evidence-empty-row"><td colSpan={3}>{emptyMessage}</td></tr>:rows.map(row=>{
     const count=counts(row);
     const confidence=readerConfidence(row);
     return <tr id={row.id} key={row.id}>
      <td data-label="Outcome and study design">
       {row.peer?<a className="table-peer" href={row.peer.href}>{row.peer.title}</a>:null}
       <button type="button" className="research-outcome-trigger" onClick={event=>open(row,event.currentTarget)} aria-haspopup="dialog" aria-label={'Inspect outcome: '+row.title}>{row.title}</button>
       <span className="table-sub">{studyDesigns(row).map((design,index)=><span className="table-study-design" key={index}>{cited(design.text,design.sourceIds)}</span>)}</span>
       {outcomeState(row)?<span className="table-state">{outcomeState(row)}</span>:null}
      </td>
      <td data-label="Grade" className="evidence-grade-cell">
       <Link className={`grade ${gradeClass(confidence.label,confidence.category==='assessed')}`} data-confidence-state={confidence.category} href="/methods" title={confidence.category==='assessed'?'Read how evidence is assessed':'This outcome has no completed evidence grade. Read how evidence is assessed.'} aria-label={`${confidence.label}: ${row.title}. How we assess evidence.`}>{confidence.label}</Link>
      </td>
      <td data-label="Evidence">
       <button type="button" className="evidence-count-link" aria-haspopup="dialog" aria-label={'View evidence for '+row.title} onClick={event=>open(row,event.currentTarget)}><FileText aria-hidden="true"/><span>{count.reports?`${count.reports} ${count.reports===1?'report':'reports'}`:`${count.total} ${count.total===1?'source':'sources'}`}</span></button>
       {count.reports>0&&count.families>0?<span className="evidence-source-note">{count.families} {count.families===1?'study family':'study families'}</span>:null}
       {count.background>0?<span className="evidence-source-note">{count.reports>0?'+ ':''}{count.background} background {count.background===1?'source':'sources'}</span>:null}
       {count.excluded>0?<span className="evidence-source-note">{count.excluded} excluded {count.excluded===1?'report':'reports'}</span>:null}
      </td>
     </tr>;
    })}</tbody>
   </table>
  </figure>
  <Dialog.Portal container={portalContainer}>
   <Dialog.Overlay className="research-panel-backdrop" data-slot="sheet-overlay"/>
   <Dialog.Content aria-modal="true" className="research-detail-panel" data-slot="sheet-content" onCloseAutoFocus={event=>{event.preventDefault();opener.current?.focus({preventScroll:true})}}>
    <header className="research-detail-panel__header">
     <div><Dialog.Title data-slot="sheet-title">{selectedSources.length} {selectedSources.length===1?'source':'sources'}</Dialog.Title><Dialog.Description data-slot="sheet-description">{selected?.title}</Dialog.Description></div>
     <Dialog.Close className="research-panel-close" aria-label="Close research details"><X aria-hidden="true"/></Dialog.Close>
    </header>
    <div className="research-detail-panel__body">{selected?<>
     <details className="research-outcome-details">
      <summary>Findings and limitations <ChevronDown aria-hidden="true"/></summary>
      <div>
       <p>{cited(selected.finding,selected.findingSources||selected.sourceIds,selected.findingSentences)}</p>
       <p><strong>Magnitude:</strong> {cited(selected.magnitude,selected.sourceIds,selected.magnitudeSentences)}</p>
       <dl className="research-facts">
        <dt>Study design</dt><dd>{studyDesigns(selected).map((design,index)=><span className="table-study-design" key={index}>{cited(design.text,design.sourceIds)}</span>)}</dd>
        <dt>Use</dt><dd>{cited(selected.use,selected.sourceIds)}</dd>
        <dt>Population / model</dt><dd>{cited(selected.population,selected.sourceIds)}</dd>
        <dt>Comparator</dt><dd>{cited(selected.comparison,selected.sourceIds)}</dd>
        <dt>Outcome</dt><dd>{cited(selected.endpoint,selected.sourceIds)}</dd>
        <dt>Timepoint</dt><dd>{cited(selected.timepoint,selected.sourceIds)}</dd>
        {selected.details?.map((detail,index)=><div className="fact-pair" key={index}><dt>{detail.label}</dt><dd>{detail.value}</dd></div>)}
       </dl>
       <p>{renderText(selected.evidenceBase)}</p>
       {selectedConfidence?<><p><strong>{selectedConfidence.label}.</strong> {renderText(selectedConfidence.basis)}</p>{selectedConfidence.limitation.input!=='missing'?<p className="research-panel-limitation">{cited(selectedConfidence.limitation.text,selectedConfidence.limitation.sourceIds)}</p>:null}</>:null}
       {selected.limits.filter(limit=>limit.text!==selectedConfidence?.limitation.text).map((limit,index)=><p className="research-panel-limitation" key={index}>{cited(limit.text,limit.sourceIds)}</p>)}
      </div>
     </details>
     <ul className="research-source-list">{selectedSources.map(source=><li key={source.id} data-source-id={source.id}>
      <SourceLink url={source.url}><span className="research-source-title">{source.title}</span></SourceLink>
      <span className="research-source-meta">{source.kind} · {source.year||'Date not recorded'}{source.access?<><br/>{source.access}</>:null}</span>
      {excluded(source)?<p className="research-panel-limitation">This report is excluded from evidence conclusions.</p>:null}
      <details className="research-study-details">
       <summary aria-label={`${source.primary?'Study':'Source'} details: ${source.title}`}><span>{source.primary?'Study':'Source'} details</span><ChevronDown aria-hidden="true"/></summary>
       <div className="research-study-details__body">
        <dl className="research-facts">
         {source.design?<><dt>Design</dt><dd>{renderText(source.design)}</dd></>:null}
         {source.population?<><dt>Population / model</dt><dd>{renderText(source.population)}</dd></>:null}
         {source.sampleDetails?.map((detail,index)=><div className="fact-pair" key={index}><dt>{detail.label}</dt><dd>{renderText(detail.value)}</dd></div>)}
        </dl>
        <p>{cited(source.preview,[source.id])}</p>
        {source.decisiveLimit?<p className="research-panel-limitation">{cited(source.decisiveLimit,[source.id])}</p>:null}
        {source.correction&&source.correction!==source.decisiveLimit?<p className="research-panel-limitation">{cited(source.correction,[source.id])}</p>:null}
        {source.locators.length?<ul className="research-page-locators">{source.locators.map((locator,index)=><li key={index}>{locator}</li>)}</ul>:null}
        <div className="research-source-links"><SourceLink url={source.url}>Original source</SourceLink>{validUrl(source.pdfUrl)?<SourceLink url={source.pdfUrl}>Study PDF</SourceLink>:null}<a href={source.reviewUrl}>{source.reviewLabel}</a></div>
       </div>
      </details>
     </li>)}</ul>
    </>:null}</div>
   </Dialog.Content>
  </Dialog.Portal>
 </Dialog.Root>;
}
