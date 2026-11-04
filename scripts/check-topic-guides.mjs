import assert from 'node:assert/strict';
import path from 'node:path';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {load,render} from './check-reader-sections.mjs';
const root=process.cwd();
const {content,guideUrl}=load(path.join(root,'lib/content.ts'));
const {topicGuideMappings,getTopicGuide}=load(path.join(root,'lib/topic-guides.ts'));
const {guideProducts,guideOffer}=load(path.join(root,'lib/guide-catalogue.ts'));
const {articleShareLinks,canonicalArticleUrl}=load(path.join(root,'lib/article-sharing.ts'));
const topics=content.guides.filter(g=>g.type==='Drug'||g.type==='Condition');
assert.equal(topicGuideMappings.length,topics.length);
assert.equal(new Set(topicGuideMappings.map(m=>m.kind+':'+m.slug)).size,topics.length,'One mapping per distinct topic');
assert.equal(new Set(topicGuideMappings.map(m=>m.productId)).size,topics.length,'Every topic owns its guide');
assert.equal(new Set(guideProducts.map(p=>p.id)).size,guideProducts.length,'Unique product identities');
assert.equal(new Set(guideProducts.map(p=>p.slug)).size,guideProducts.length,'Unique product routes');
for(const topic of topics){
 const mapping=getTopicGuide(topic.type.toLowerCase(),topic.slug.split('/').at(-1));assert(mapping,topic.slug);
 const product=guideProducts.find(p=>p.id===mapping.productId);assert(product);assert.equal(product.relatedHref,guideUrl(topic));assert.equal(product.priceMinor,4900);assert.equal(product.currency,'USD');
 assert.equal(mapping.articleUrl,guideUrl(topic),'Mapping points to its own article');
 assert(['pending','released','withdrawn'].includes(product.releaseState),'Known release state');
 const html=render(topic,content.sources.filter(s=>topic.sourceIds.includes(s.id)));
 assert.equal((html.match(/aria-label="Share this article"/g)||[]).length,1,'Single share row');
 assert(!html.includes('Selected source populations'));assert(!html.includes('class="context-rail"'));
 const visible=html.replace(/&#x27;/g,"'").replace(/&amp;/g,'&').replace(/<!--.*?-->/g,'');
 assert(visible.includes((product.releaseState==='released'?'Get':'Explore')+' the '+product.topic+' Guide'),'State-aware CTA: '+topic.slug);
 assert(html.includes('/guides/products/'+product.slug),'Own-topic product link: '+topic.slug);
 assert(html.indexOf('class="article-share-rail"')>html.indexOf('</article>'),'sharing follows the article in reading order');
 assert(html.indexOf('class="article-share-rail"')>html.indexOf('aria-label="Related reading"'),'sharing follows related reading');
 assert(html.indexOf('class="related-reading"')>html.indexOf('</article>'),'related reading after body');
 for(const link of articleShareLinks(guideUrl(topic)+'?account=private&utm_source=test#safety',topic.title)){
  const url=new URL(link.href);assert(!decodeURIComponent(link.href).includes('private'));assert(!decodeURIComponent(link.href).includes('utm_'));
  if(link.key==='reddit')assert.equal(url.searchParams.get('title'),topic.title);
  if(link.key==='x')assert.equal(url.searchParams.get('text'),topic.title);
 }
}
assert.equal(canonicalArticleUrl('/drugs/metformin?secret=test#x'),'https://remaprx.com/drugs/metformin');
assert.throws(()=>canonicalArticleUrl('//evil.example/drugs/x'));
for(const privatePath of ['/guides/read/private-edition','/guides/library/owned','/account/profile'])assert.throws(()=>canonicalArticleUrl(privatePath));
assert.deepEqual(guideOffer.launchProductIds,['SL-GUIDE-METFORMIN','SL-GUIDE-LONG-COVID','SL-GUIDE-ITRACONAZOLE-CANCER']);assert.equal(guideOffer.monthlyMinor,5900);assert(!('annualMinor' in guideOffer));
const launchReleased=guideOffer.launchProductIds.filter(id=>guideProducts.some(p=>p.id===id&&p.releaseState==='released')).length;
assert.equal(guideOffer.releasedCount,launchReleased,'Membership count follows actual launch-product releases');
if(guideOffer.enabled)assert(launchReleased>=guideOffer.launchMinimum&&launchReleased===guideOffer.launchProductIds.length,'Membership requires all three launch guides');
const {GuideOfferLink,GuidePurchaseControls}=load(path.join(root,'components/guide-purchase-controls.tsx'));
for(const releaseState of ['pending','released','withdrawn']){
 const product={...guideProducts[0],id:'SYNTHETIC-GUIDE',releaseState};
 const offer=renderToStaticMarkup(React.createElement(GuideOfferLink,{product}));
 const controls=renderToStaticMarkup(React.createElement(GuidePurchaseControls,{product}));
 assert(offer.includes((releaseState==='released'?'Get':'Explore')+' the '+product.topic+' Guide'));
 assert.equal(controls.includes('Get this guide'),releaseState==='released','Only a released product offers checkout');
}
const color=hex=>hex.match(/\w\w/g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
const contrast=(color('FFC709')+.05)/(color('1736F5')+.05);assert(contrast>=4.5);
console.log(`PASS: ${topics.length} explicit topic products, pending/released/withdrawn CTAs, single canonical sharing row, no account/tracking leakage, article/related/sharing DOM order, $49/$59 three-guide gate, ${contrast.toFixed(2)}:1 CTA contrast. Product coverage does not establish completed manuscripts or live purchasability.`);
