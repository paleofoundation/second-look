import projection from '@/data/ingested-topic-pages.json';

type Cell = {label:string;value:string|number|boolean|null;reason:string|null;source_pointer:string};
type LocatedResult = {id:string;paper_id:string;source_record:string;quarantined:false;cells:Cell[];arms:{id:string;cells:Cell[]}[];locators:{source_url:string;fields:Cell[]}[]};
type QuarantinedResult = {id:string;paper_id:string;source_record:string;quarantined:true;reason:string};
export type IngestedTopicPage = {
 topic_id:string;title:string;path:string;aliases:string[];
 verification_state:'pending';human_review_status:'pending';publication_state:'draft';coverage_state:'INCOMPLETE';
 notice:string;next_action:string;next_action_source:string;flags:string[];
 results:(LocatedResult|QuarantinedResult)[];quarantined_papers:{id:string;reason:string}[];
};
export const ingestedTopicPages = (projection as unknown as {pages:IngestedTopicPage[]}).pages;
export function ingestedTopicForPath(path:string){
 const normalized=path.startsWith('/')?path:'/'+path;
 return ingestedTopicPages.find(page=>page.path===normalized||page.aliases.includes(normalized));
}
function Fields({cells}:{cells:Cell[]}){
 return <dl className="ingest-fields">{cells.map(cell=><div key={cell.source_pointer}><dt>{cell.label}</dt><dd data-result-field={cell.source_pointer}>{cell.value===null?'null — '+(cell.reason||'NOT IN CORPUS — missing reason not recorded'):String(cell.value)}</dd></div>)}</dl>;
}
export function IngestedTopic({page}:{page:IngestedTopicPage}){
 return <article className="ingest-topic">
  <style>{`.ingest-topic{max-width:1000px;margin:32px auto;overflow-wrap:anywhere}.ingest-topic h1{font-size:clamp(1.8rem,4vw,2.7rem);line-height:1.2}.ingest-state{color:#4e6275}.ingest-result{background:#fff;border:1px solid #ccd8e2;padding:24px;margin:24px 0}.ingest-quarantine{border-left:4px solid #994539}.ingest-fields>div{display:grid;grid-template-columns:minmax(140px,1fr) 3fr;gap:8px 20px;margin:8px 0}.ingest-fields dt{font-weight:600}.ingest-fields dd{margin:0}.ingest-topic details{border-top:1px solid #ccd8e2;padding-top:14px;margin-top:16px}.ingest-topic summary{cursor:pointer;font-weight:600}.ingest-source{font-size:.9rem}.ingest-topic li{margin:10px 0}@media(max-width:600px){.ingest-fields>div{display:block}.ingest-fields dd{margin:0 0 14px}.ingest-result{padding:16px}}`}</style>
  <p><a href="/questions">All reader questions</a></p>
  <p className="ingest-state">{page.topic_id} · {page.coverage_state} · Private draft</p>
  <h1>{page.title}</h1>
  <div className="notice"><strong>Evidence incomplete</strong><p>{page.notice}</p><p>Verification: {page.verification_state} · Human review: {page.human_review_status} · Publication: {page.publication_state}</p></div>
  <section><h2>Next action</h2><p>{page.next_action}</p><p className="ingest-source">{page.next_action_source}</p></section>
  <section><h2>Unresolved flags</h2><ul>{page.flags.map(flag=><li key={flag}>{flag}</li>)}</ul></section>
  <section><h2>Recorded results</h2><p>Source-located records awaiting review. These records do not form a topic verdict.</p>
   {!page.results.length?<p>NOT IN CORPUS — no result records are mapped to this topic.</p>:page.results.map(result=>result.quarantined?
    <section className="ingest-result ingest-quarantine" key={result.id}><h3>{result.id}</h3><p>{result.reason}</p></section>:
    <section className="ingest-result" key={result.id}><h3>{result.id}</h3><p className="ingest-source">{result.paper_id} · {result.source_record}</p><Fields cells={result.cells}/>
     {result.arms.length?result.arms.map(arm=><section key={arm.id}><h4>{arm.id}</h4><Fields cells={arm.cells}/></section>):<p>Arm data: NOT IN CORPUS.</p>}
     <details open><summary>Source locators</summary>{result.locators.map((locator,index)=><section key={index}><p><a href={locator.source_url} target="_blank" rel="noreferrer">Source locator</a></p><Fields cells={locator.fields}/></section>)}</details>
    </section>)}
  </section>
  {page.quarantined_papers.length>0?<section><h2>Quarantined sources</h2><ul>{page.quarantined_papers.map(paper=><li key={paper.id}>{paper.id}: {paper.reason}</li>)}</ul></section>:null}
 </article>;
}
