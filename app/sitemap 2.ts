import {content,guideUrl} from '@/lib/content';
export default function sitemap(){return ['', '/questions','/research','/glossary','/drugs','/conditions','/guides','/methods',...content.guides.map(guideUrl),...content.sources.map(s=>'/research/'+s.id),...content.glossary.map(t=>'/glossary/'+t.slug)].map(path=>({url:'https://second-look-evidence.kmfp.chatgpt.site'+path}))}
