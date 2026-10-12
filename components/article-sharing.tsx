'use client';
import {useState} from 'react';
import {Copy,Mail} from 'lucide-react';
import {articleShareLinks,canonicalArticleUrl} from '@/lib/article-sharing';
import {getTopicGuide} from '@/lib/topic-guides';
import {getGuideProduct} from '@/lib/guide-catalogue';
import {GuideOfferLink} from '@/components/guide-purchase-controls';
const glyphs:Record<string,React.ReactNode>={
 x:<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>,
 reddit:<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="15" rx="9" ry="6"/><path d="m12 9 1-6 5 1M4 11c-4-3-5 3-1 4m17-4c4-3 5 3 1 4M8 18c2 1.5 6 1.5 8 0"/><circle cx="20" cy="4" r="2"/><circle cx="8" cy="14" r="1" fill="currentColor"/><circle cx="16" cy="14" r="1" fill="currentColor"/></svg>,
 linkedin:<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M5.4 3a2.1 2.1 0 1 0 0 4.2 2.1 2.1 0 0 0 0-4.2ZM3.6 9h3.6v12H3.6V9Zm6 0H13v1.6h.1A3.8 3.8 0 0 1 16.5 8.7c3.6 0 4.3 2.4 4.3 5.5V21h-3.6v-6c0-1.4 0-3.1-1.9-3.1s-2.2 1.5-2.2 3V21H9.6V9Z"/></svg>,
 email:<Mail aria-hidden="true"/>
};
export function ArticleSharing({path,title,kind}:{path:string;title:string;kind:string}) {
  const [message,setMessage]=useState('');
  const topic=kind==='Drug'||kind==='Condition'?getTopicGuide(kind==='Drug'?'drug':'condition',path.split('/').at(-1)||''):undefined;
  const product=topic?getGuideProduct(topic.productId):undefined;
  async function copy(){try{await navigator.clipboard.writeText(canonicalArticleUrl(path));setMessage('Link copied.')}catch{setMessage('Copy this link: '+canonicalArticleUrl(path))}}
  return <div className="article-sharing-offer">
    <p className="article-share-label">Share this article</p>
    <nav className="article-share-row" aria-label="Share this article">
      {articleShareLinks(path,title).map(link=><a key={link.key} href={link.href} aria-label={link.label} title={link.label} target={link.key==='email'?undefined:'_blank'} rel={link.key==='email'?undefined:'noopener noreferrer'}>{glyphs[link.key]}</a>)}
      <button type="button" onClick={()=>void copy()} title="Copy link" aria-label="Copy article link"><Copy aria-hidden="true"/></button>
    </nav>
    <span className="article-share-status" role="status">{message}</span>
    {product?<div className="article-guide-offer"><GuideOfferLink product={product}/><p className="article-guide-price">$49 once · Included with $59/month membership.</p><p className="article-guide-availability">{product.releaseState==='released'?'Web guide + PDF · Future updates included.':'Guide in development. Membership coming after our first three guides.'}</p></div>:null}
  </div>;
}
