/* eslint-disable @next/next/no-html-link-for-pages -- Use document navigation because this Vinext deployment does not support Link prefetch. */
'use client';
import {ArrowRight,BookOpen,Bookmark,FileText} from 'lucide-react';
import {SearchBox} from './search';
import {FavoriteButton,useAccount} from './account';
import {InvestigatorTeam} from './authors';
import {peptides} from '@/lib/peptides';
import {studies} from '@/lib/studies';
import statistics from '@/lib/data/library-statistics.json';
import styles from './home.module.css';
const cx=(value:string)=>value.split(' ').map(name=>styles[name]).join(' ');
const collections=[
 {number:'01',label:'RECOVERY & HORMONES',title:'Follow a peptide question',copy:'Explore injury recovery, growth hormone, and the limits of the human evidence.',ids:['bpc-157','tb-500','cjc-1295','ipamorelin']},
 {number:'02',label:'WEIGHT MANAGEMENT',title:'Compare the evidence',copy:'Find studies on weight reduction, comparative outcomes, and treatment withdrawal.',ids:['semaglutide','tirzepatide']},
 {number:'03',label:'SKIN & NUTRITION',title:'Look beyond the headline',copy:'Examine questions about formulation, skin outcomes, and joint symptoms.',ids:['ghk-cu','collagen']},
];
export function HomePage(){
 const {user,favorites,loading,error}=useAccount();const savedPeptides=favorites.filter(f=>f.kind==='peptide').length;const savedStudies=favorites.filter(f=>f.kind==='study').length;
 return <div className={styles.home}>
  <section className={cx('hero')} id="top">
    <div className={cx('hero__copy')}>
      <p className="section-kicker">THE PEPTIDE EVIDENCE LIBRARY</p>
      <h1>Peptide questions.<br/><em>Evidence</em> you can trace.</h1>
      <p className={cx('hero__intro')}>Understand the research behind the claims. Explore peptide guides, study findings, and the limits of the evidence.</p>
      <SearchBox/>
      <div className={cx('quick-searches')}><span>Start exploring</span><a href="/peptides/bpc-157">BPC-157</a><a href="/peptides/semaglutide">Semaglutide</a><a href="/stacks/wolverine-stack">Wolverine stack</a></div>
      <div className={cx('hero__actions')}><a className={cx('hero__guides')} href="/guides">Explore consumer guides</a><a className={cx('hero__browse')} href="/peptides">Explore all peptides</a></div>
    </div>
    <div className={cx('hero__art')} aria-hidden="true">
      <svg viewBox="0 0 560 610" fill="none" focusable="false">
        <circle cx="294" cy="306" r="220" className={styles['hero__orbit']}/>
        <circle cx="294" cy="306" r="272" className={styles['hero__orbit']}/>
        <path d="M37 581C48 508 158 507 181 438C207 360 73 353 81 255C87 177 170 146 231 162C327 187 250 321 349 336C443 350 511 239 461 161C432 116 371 96 405 28" className={styles['hero__trace']}/>
        <path d="M81 255L231 162L349 336L181 438M349 336L461 161" className={styles['hero__connections']}/>
        <circle cx="81" cy="255" r="34" className={styles['hero__node']}/>
        <circle cx="231" cy="162" r="51" className={styles['hero__node']}/>
        <circle cx="349" cy="336" r="66" className={styles['hero__node']}/>
        <circle cx="181" cy="438" r="43" className={styles['hero__node']}/>
        <circle cx="461" cy="161" r="27" className={styles['hero__node']}/>
        <circle cx="349" cy="336" r="44" className={styles['hero__core']}/>
        <circle cx="231" cy="162" r="8" fill="currentColor"/>
        <circle cx="181" cy="438" r="7" fill="currentColor"/>
      </svg>
      <span>Good questions. Clearer understanding.</span>
    </div>
  </section>
  <section className={cx('credibility')} aria-label="Explore the library"><a href="/peptides"><BookOpen size={18}/>{statistics.peptideGuides.toLocaleString('en-US')} peptide guides</a><a href="/questions">{statistics.researchQuestions.toLocaleString('en-US')} research questions</a><a href="/sources#study-records"><FileText size={18}/>{statistics.researchStudies.toLocaleString('en-US')} research studies</a></section>
  <section className={cx('section')} id="explore"><div className={cx('section-intro centered')}><p className="section-kicker">EXPLORE THE LIBRARY</p><h2>Start with what you want to understand.</h2><p>Browse peptides by research topic, or go straight to a question.</p></div><div className={cx('collection-grid')}>{collections.map(c=><article className={cx('collection-card')} key={c.number}><div className={cx('collection-card__top')}><span>{c.number}</span><small>{c.label}</small></div><h3>{c.title}</h3><p>{c.copy}</p><ul>{c.ids.map(id=>{const p=peptides.find(p=>p.id===id)!;return <li key={id}><a className="rgbc-archive__link" href={`/peptides/${id}`}>{p.name}</a></li>;})}</ul><a className={cx('card-link')} href="/peptides">Browse the peptide directory</a></article>)}</div></section>
  <section className={cx('library-strip')} id="your-library" aria-labelledby="home-library-title">
    <Bookmark size={30} aria-hidden="true"/>
    <div><h2 id="home-library-title">Your research, together.</h2><p>{user?'Return to your saved peptides and studies.':'Keep the peptides and studies you want to come back to.'}</p>{user&&!loading&&!error&&favorites.length>0&&<p className={styles['library-strip__counts']}>{savedPeptides} saved {savedPeptides===1?'peptide':'peptides'} · {savedStudies} saved {savedStudies===1?'study':'studies'}</p>}</div>
    <a href={user?'/profile':'/login'}>{user?'Open my library':'Create your library'}<ArrowRight size={20} aria-hidden="true"/></a>
  </section>
  <section className={cx('section method')} id="research"><div className={cx('method__heading')}><p className="section-kicker">THE RESEARCH BEHIND THE ANSWERS</p><h2>Read it.<br/>Question it.<br/>Keep it.</h2><p>Open the original studies, follow their place in a peptide guide, and save them for later.</p><a href="/sources" className={cx('text-link')}>Explore all research references</a></div><div className="home-study-list">{studies.filter(s=>s.kind==='Primary research').slice(0,3).map(s=><article key={s.id}><span className="section-kicker">{s.kind}{s.year?` · ${s.year}`:''}</span><h3><a href={s.href}>{s.title}</a></h3><div><a className="quiet-link" href={s.url} target="_blank" rel="noreferrer">Read original study</a><FavoriteButton kind="study" itemId={s.id} title={s.title}/></div></article>)}</div></section>
  <section className={cx('section')}><div className="home-team-heading"><p className="section-kicker">THE PEOPLE BEHIND THE PROJECT</p><h2>Meet the primary investigators.</h2></div><InvestigatorTeam/><a className="quiet-link" href="/methodology">Read our editorial standards</a></section>
 </div>;
}
