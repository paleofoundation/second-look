'use client';
import {useEffect,useState} from 'react';
import type {GuideManuscript} from '@/lib/guide-manuscript';
import {readerSignInPath} from '@/lib/account-paths';
import {GuideViewedMarker} from '@/components/library-controls';
type ReaderData={manuscript:GuideManuscript;access:'owned'|'membership'};
export function GuideReader({editionId}:{editionId:string}) {
 const [data,setData]=useState<ReaderData|null>(null),[error,setError]=useState(''),[signIn,setSignIn]=useState(false),[attempt,setAttempt]=useState(0);
 useEffect(()=>{let active=true;setData(null);setError('');setSignIn(false);
  fetch('/api/guides/'+encodeURIComponent(editionId)+'/reader',{credentials:'same-origin',cache:'no-store'}).then(async response=>{
   const result=await response.json() as ReaderData&{error?:string};
   if(!active)return;
   if(response.status===401)setSignIn(true);
   if(!response.ok){setError(result.error||'This guide is currently unavailable.');return;}
   setData(result);
  }).catch(()=>{if(active)setError('Your guide could not load. Please retry.');});return()=>{active=false};
 },[editionId,attempt]);
 if(!data)return <div className="guide-reader-empty"><a href="/guides/library">← My guides</a><h1>Your guide</h1>{error?<p role="alert">{error}</p>:<p role="status">Opening your guide…</p>}{signIn?<a className="button accent" target="_top" href={readerSignInPath('/guides/read/'+editionId)}>Sign in to read</a>:error?<button className="button ghost" onClick={()=>setAttempt(value=>value+1)}>Try again</button>:null}</div>;
 const m=data.manuscript;
 const cite=(ids:string[])=><>{ids.map(id=>{const index=m.references.findIndex(ref=>ref.id===id);return <sup key={id}><a href={'#source-'+id} aria-label={'Source '+(index+1)}>[{index+1}]</a></sup>})}</>;
 return <><GuideViewedMarker productId={m.productId} editionId={m.editionId}/><header className="guide-reader-hero"><a href="/guides/library">← My guides</a><span className="eyebrow">{data.access==='owned'?'Your topic guide':'Included with your membership'}</span><h1>{m.title}</h1><p>{m.description}</p><p className="small">Edition {m.version} · Evidence through {m.evidenceCutoff}</p><div className="inline-actions"><a className="button accent" href={'/api/guides/'+encodeURIComponent(editionId)+'/download'}>Download PDF</a><a className="button ghost" href={'/api/guides/'+encodeURIComponent(editionId)+'/download?format=summary'}>Printable summary</a><a href="#guide-changes">What changed</a></div></header><div className="guide-reader-layout"><nav aria-label="Guide contents"><h2>Inside this guide</h2><ol>{m.chapters.map(chapter=><li key={chapter.id}><a href={'#chapter-'+chapter.id}>{chapter.title}</a></li>)}</ol><a href="#guide-sources">Sources and credits</a></nav><article><aside className="omr-medical-notice">{m.medicalNotice}</aside>{m.chapters.map(chapter=><section key={chapter.id} id={'chapter-'+chapter.id}><h2>{chapter.title}</h2>{chapter.blocks.map((block,index)=><div className={'guide-block guide-block--'+block.type} key={index}>
 {block.type==='paragraph'?<p>{block.text}{cite(block.sourceIds)}</p>:block.type==='callout'?<aside><h3>{block.title}</h3><p>{block.text}{cite(block.sourceIds)}</p></aside>:block.type==='list'?<><ul>{block.items.map((item,i)=><li key={i}>{item}</li>)}</ul>{cite(block.sourceIds)}</>:block.type==='questions'?<section><h3>{block.title}</h3><ol>{block.items.map((item,i)=><li key={i}>{item}</li>)}</ol>{cite(block.sourceIds)}</section>:<><div className="guide-table-scroll" tabIndex={0} role="region" aria-label={block.caption}><table><caption>{block.caption}</caption><thead><tr>{block.columns.map((column,i)=><th scope="col" key={i}>{column}</th>)}</tr></thead><tbody>{block.rows.map((row,i)=><tr key={i}>{row.map((cell,j)=><td key={j}>{cell}</td>)}</tr>)}</tbody></table></div>{cite(block.sourceIds)}</>}
 </div>)}</section>)}<section id="guide-changes"><h2>What changed</h2><p>{m.changeSummary}</p><p className="small">Updated {new Date(m.updatedAt).toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric',timeZone:'UTC'})}</p></section><section id="guide-sources"><h2>Sources and credits</h2><ol>{m.references.map(ref=><li id={'source-'+ref.id} key={ref.id}><a href={ref.url} target="_blank" rel="noreferrer">{ref.title}</a>{ref.note?<p className="small">{ref.note}</p>:null}</li>)}</ol>{m.contributors.map((person,index)=><div key={index}><h3>{person.name}</h3><p>{person.role}{person.qualifications?' · '+person.qualifications:''}</p><p className="small">Conflicts: {person.conflicts}</p>{person.orcid?<a href={person.orcid} target="_blank" rel="noreferrer">ORCID</a>:null}</div>)}</section></article></div></>;
}
