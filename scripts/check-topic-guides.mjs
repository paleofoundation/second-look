import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {load,render} from './check-reader-sections.mjs';
const root=process.cwd();
const {content,guideUrl}=load(path.join(root,'lib/content.ts'));
const {topicGuideMappings,getTopicGuide}=load(path.join(root,'lib/topic-guides.ts'));
const {guideProducts,guideOffer}=load(path.join(root,'lib/guide-catalogue.ts'));
const {articleShareLinks,canonicalArticleUrl}=load(path.join(root,'lib/article-sharing.ts'));
const topics=content.guides.filter(g=>g.type==='Drug'||g.type==='Condition');
assert.equal(topicGuideMappings.length,topics.length);
assert.equal(new Set(topicGuideMappings.map(m=>m.productId)).size,topics.length,'Every topic owns its guide');
for(const topic of topics){
 const mapping=getTopicGuide(topic.type.toLowerCase(),topic.slug.split('/').at(-1));assert(mapping,topic.slug);
 const product=guideProducts.find(p=>p.id===mapping.productId);assert(product);assert.equal(product.relatedHref,guideUrl(topic));assert.equal(product.priceMinor,4900);assert.equal(product.currency,'USD');
 const html=render(topic,content.sources.filter(s=>topic.sourceIds.includes(s.id)));
 assert.equal((html.match(/aria-label="Share this article"/g)||[]).length,1,'Single share row');
 assert(!html.includes('Selected source populations'));assert(!html.includes('class="context-rail"'));
 const visible=html.replace(/&#x27;/g,"'").replace(/&amp;/g,'&').replace(/<!--.*?-->/g,'');
 assert(visible.includes('Explore the '+product.topic+' Guide'),'Pending CTA: '+topic.slug);
 assert(html.indexOf('class="article-share-rail"')<html.indexOf('<article class="research-content__center'),'mobile DOM order');
 assert(html.indexOf('class="related-reading"')>html.indexOf('</article>'),'related reading after body');
 for(const link of articleShareLinks(guideUrl(topic)+'?account=private&utm_source=test#safety',topic.title)){
  const url=new URL(link.href);assert(!decodeURIComponent(link.href).includes('private'));assert(!decodeURIComponent(link.href).includes('utm_'));
  if(link.key==='reddit')assert.equal(url.searchParams.get('title'),topic.title);
  if(link.key==='x')assert.equal(url.searchParams.get('text'),topic.title);
 }
}
assert.equal(canonicalArticleUrl('/drugs/metformin?secret=test#x'),'https://remaprx.com/drugs/metformin');
assert.throws(()=>canonicalArticleUrl('//evil.example/drugs/x'));
assert.deepEqual(guideOffer.launchProductIds,['SL-GUIDE-METFORMIN','SL-GUIDE-LONG-COVID','SL-GUIDE-ITRACONAZOLE-CANCER']);assert.equal(guideOffer.monthlyMinor,5900);assert(!('annualMinor' in guideOffer));assert.equal(guideOffer.enabled,false);
const color=hex=>hex.match(/\w\w/g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
const contrast=(color('FFC709')+.05)/(color('1736F5')+.05);assert(contrast>=4.5);
for(const p of guideProducts)assert(p.releaseState!=='released','This acceptance snapshot must not fabricate released guides');
console.log(`PASS: ${topics.length} explicit topic products, pending CTAs, single canonical sharing row, no account/tracking leakage, mobile DOM order, $49/$59 three-guide gate, ${contrast.toFixed(2)}:1 CTA contrast.`);
