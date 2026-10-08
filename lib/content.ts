import raw from '@/data/content.json';
import rawTopics from '@/data/topics.json';
export type Source={id:string;title:string;url:string;doi?:string;year?:number;design?:string;population?:string;n?:number|null;access?:string;preview:string;review?:Record<string,string>;reviewSentences?:Record<string,{text:string;sources:string[]}[]>;locators?:unknown;status?:string;correction?:string;sourceType?:string;authors?:string[]};
export type Section={id:string;label:string;title:string;paragraph:string;sources:string[];sentences?:{text:string;sources:string[]}[]};
export type Guide={id:string;slug:string;title:string;type:string;description:string;topicIds:string[];sections:Section[];faqs:{question:string;answer:string;sources:string[];sentences?:{text:string;sources:string[]}[]}[];sourceIds:string[];related:string[]};
export type Term={slug:string;title:string;meaning:string;context:string;examples:string;sources:string[]};
export const content=raw as unknown as {sources:Source[];guides:Guide[];glossary:Term[]};
export const topics=rawTopics as unknown as {id:string;question:string;sourceLinks?:string[];status?:string;related?:string;category?:string}[];
export function sourceById(id:string){return content.sources.find(x=>x.id===id)}
export function guideUrl(g:Guide){return g.slug.startsWith('/')?g.slug:`/answers/${g.slug}`}
export function allItems(){return [...content.guides.map(g=>({id:g.id,title:g.title,url:guideUrl(g),type:g.type,description:g.description,aliases:g.topicIds.join(' ')})),...content.sources.filter(s=>s.sourceType!=='context').map(s=>({id:s.id,title:s.title,url:`/research/${s.id}`,type:s.sourceType==='context'?'Context':'Study',description:s.preview,aliases:s.doi||''})),...content.glossary.map(t=>({id:`term-${t.slug}`,title:t.title,url:`/glossary/${t.slug}`,type:'Glossary',description:t.meaning,aliases:''})),...topics.map(t=>({id:t.id,title:t.question,url:`/questions#${t.id}`,type:'Question',description:'Community question · evidence coverage varies',aliases:t.category||''}))]}
