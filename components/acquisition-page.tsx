import projection from '@/data/acquisition-pages.json';

type Inventory = {
 source_id:string;report_id:string;collection:string;context_tier:string|null;context_tier_reason:string;
 effective_collection:string;effective_context_tier:string|null;effective_tier_reason:string;
 report_role:string;design:string|null;access_state:string;access_label:string;media_type:string|null;media_type_reason:string|null;
 mapping_state:'candidate'|'held';clinical_relevance:'unverified';excluded_from_clinical_support:true;source_locator:string;hold_reason?:string|null;
};
export type AcquisitionPageData = {
 request_id:string;batch_id:string;title:string;path:string;coverage_state:'INCOMPLETE';
 verification_state:'pending';human_review_status:'pending';publication_state:'draft';notice:string;
 next_action:string;coverage_locator:string;independent_study_families:null;family_count_reason:string;
 source_inventory:Inventory[];candidate_itraconazole_links:Inventory[];missing_areas:string[];
 unresolved_gaps:{id:string;kind:string;state:'unresolved';next_action:string}[];
};
export const acquisitionPages=(projection as unknown as {pages:AcquisitionPageData[]}).pages;
export function acquisitionPageForPath(path:string){const normalized=path.startsWith('/')?path:'/'+path;return acquisitionPages.find(page=>page.path===normalized)}

function InventoryRow({row}:{row:Inventory}){
 const fields=[['Source ID',row.source_id],['Effective display tier',row.effective_collection+(row.effective_context_tier?' / '+row.effective_context_tier:'')],
  ['Display tier reason',row.effective_tier_reason],['Original collection',row.collection||'NOT IN CORPUS'],
  ['Original context tier',row.context_tier===null?'null — '+row.context_tier_reason:row.context_tier],
  ['Report role',row.report_role||'NOT IN CORPUS'],['Acquisition design label — unverified',row.design||'NOT IN CORPUS'],
  ['Access',row.access_label],['Declared MIME',row.media_type||'null — '+row.media_type_reason],
  ['Mapping',row.mapping_state+'; clinical relevance unverified; excluded from clinical support']];
 return <article className={'acq-source-row'+(row.mapping_state==='held'?' acq-held':'')}><dl>{fields.map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
  {row.hold_reason?<p><strong>HOLD:</strong> {row.hold_reason}</p>:null}<p className="acq-source">{row.source_locator}</p></article>;
}
function InventoryGroups({rows}:{rows:Inventory[]}){
 const groups:Record<string,Inventory[]>={};
 for(const row of rows){const key=row.effective_collection+(row.effective_context_tier?' / '+row.effective_context_tier:'')+' · '+row.report_role;(groups[key]??=[]).push(row)}
 return <>{Object.keys(groups).sort().map(key=><details className="acq-group" key={key} open><summary>{key}</summary>{[...groups[key]].sort((a,b)=>a.source_id.localeCompare(b.source_id)).map(row=><InventoryRow key={row.source_id} row={row}/>)}</details>)}</>;
}
export function AcquisitionPage({page}:{page:AcquisitionPageData}){
 return <article className="acq-page">
  <style>{`.acq-page{margin:32px auto;overflow-wrap:anywhere}.acq-page h1{font-size:clamp(1.8rem,4vw,2.7rem);line-height:1.2;max-width:1000px}.acq-state{color:#4e6275}.acq-layout{display:grid;grid-template-columns:minmax(220px,1fr) minmax(0,3fr);gap:36px}.acq-layout aside{font-size:.95rem}.acq-group{border:1px solid #ccd8e2;padding:16px;margin:20px 0;background:#fff}.acq-group summary{cursor:pointer;font-weight:650}.acq-source{font-size:.85rem;overflow-wrap:anywhere}.acq-source-row{border-top:1px solid #ccd8e2;padding:16px 0;overflow-wrap:anywhere}.acq-source-row:first-of-type{border-top:0}.acq-source-row dl>div{display:grid;grid-template-columns:minmax(120px,1fr) 3fr;gap:5px 20px;margin:5px 0}.acq-source-row dt{font-weight:600}.acq-source-row dd{margin:0}.acq-page li{margin:10px 0}.acq-held{border-left:4px solid #994539;padding-left:16px}@media(max-width:760px){.acq-layout{display:block}.acq-source-row dl>div{display:block}.acq-source-row dd{margin-bottom:12px}}`}</style>
  <p><a href={page.path.startsWith('/drugs/')?'/drugs':'/conditions'}>Return to directory</a></p>
  <p className="acq-state">{page.request_id} · {page.coverage_state} · Private draft</p><h1>{page.title}</h1>
  <div className="notice"><strong>Evidence incomplete</strong><p>{page.notice}</p><p>Verification: {page.verification_state} · Human review: {page.human_review_status} · Publication: {page.publication_state}</p></div>
  <section><h2>Next action</h2><p>{page.next_action}</p><p className="acq-source">{page.coverage_locator}</p></section>
  <div className="acq-layout"><aside><h2>Missing coverage in this return</h2><ul>{page.missing_areas.map(area=><li key={area}>{area}</li>)}</ul><p>Independent study count: null — {page.family_count_reason}</p></aside><div>
   <section><h2>Source inventory</h2><p>Inventory labels describe acquired material. Paper-to-request mappings are candidate and unverified; they do not establish clinical relevance.</p>
    {page.source_inventory.length?<InventoryGroups rows={page.source_inventory}/>:<p>NOT IN CORPUS — no acquired source records are mapped to this request.</p>}
   </section>
   {page.candidate_itraconazole_links.length?<section><h2>Itraconazole catalog candidates</h2><p>Unverified catalog references only. Candidate and held mappings do not establish clinical relevance and are excluded from clinical support.</p><InventoryGroups rows={page.candidate_itraconazole_links}/></section>:null}
   <details className="acq-group"><summary>Unresolved acquisition gaps</summary><ul>{page.unresolved_gaps.map(gap=><li key={gap.id}><strong>{gap.id}</strong> · {gap.kind} · unresolved<p>{gap.next_action}</p></li>)}</ul></details>
  </div></div>
 </article>;
}
