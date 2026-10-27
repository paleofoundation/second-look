'use client';
import {useEffect, useRef, useState} from 'react';
import {readerSignInPath} from '@/lib/account-paths';
import type {GuideProductView} from '@/components/shared-theme/guide-catalogue';

type Available = {productId:string;editionId:string;version:string};
function useOwnedGuide(product: GuideProductView) {
  const [edition,setEdition]=useState<Available|null>(null);
  useEffect(()=>{
    let current=true; setEdition(null);
    if(product.releaseState!=='released')return;
    fetch('/api/purchases',{cache:'no-store',credentials:'same-origin'}).then(async response=>{
      if(!response.ok)return;
      const data=await response.json() as {availableGuides?:Available[]};
      const owned=data.availableGuides?.find(guide=>guide.productId===product.id);
      if(current&&owned)setEdition(owned);
    }).catch(()=>{});
    return()=>{current=false};
  },[product.id,product.releaseState]);
  return edition;
}
export function GuideOfferLink({product}:{product:GuideProductView}) {
  const edition=useOwnedGuide(product);
  return <a className="topic-guide-cta" href={edition?'/guides/read/'+encodeURIComponent(edition.editionId):'/guides/products/'+product.slug}>
    {edition?'Open your guide':`${product.releaseState==='released'?'Get':'Explore'} the ${product.topic} Guide`}
  </a>;
}
export function CheckoutButton({productId,kind='guide',label}:{productId?:string;kind?:'guide'|'membership';label:string}) {
  const [busy,setBusy]=useState(false),[error,setError]=useState(''),[signIn,setSignIn]=useState(false);
  const attempt=useRef<string|null>(null);
  async function checkout(){
    if(busy)return;
    setBusy(true);setError('');
    try {
      attempt.current??=crypto.randomUUID();
      const response=await fetch('/api/checkout',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','Idempotency-Key':attempt.current},body:JSON.stringify(kind==='guide'?{kind,productId}:{kind})});
      if(response.status===401){setSignIn(true);return;}
      const result=await response.json() as {url?:string;error?:string};
      if(!response.ok||!result.url)throw new Error(result.error||'Checkout is temporarily unavailable. Please retry.');
      const url=new URL(result.url);
      if(url.protocol!=='https:'||url.hostname!=='checkout.stripe.com')throw new Error('Checkout could not be verified. Please retry.');
      window.location.assign(url.href);
    } catch(error){setError(error instanceof Error?error.message:'Checkout is temporarily unavailable.');}
    finally{setBusy(false);}
  }
  return <div className="guide-checkout-control">{signIn?<a className="topic-guide-cta" target="_top" href={readerSignInPath(typeof window==='undefined'?'/guides':window.location.pathname)}>Sign in to continue</a>:<button className="topic-guide-cta" type="button" disabled={busy} aria-busy={busy} onClick={()=>void checkout()}>{busy?'Opening secure checkout…':label}</button>}{error?<p className="small" role="alert">{error}</p>:null}</div>;
}
export function GuidePurchaseControls({product}:{product:GuideProductView}) {
  const edition=useOwnedGuide(product);
  if(edition)return <a className="topic-guide-cta" href={'/guides/read/'+encodeURIComponent(edition.editionId)}>Open your guide</a>;
  if(product.releaseState!=='released')return <span className="omr-guide-state">In development · not available to buy</span>;
  return <CheckoutButton productId={product.id} label="Get this guide · $49"/>;
}
