import {content,guideUrl} from '@/lib/content';
import {REMAPRX_ORIGIN} from '@/lib/hero-art';
export default function sitemap(){return ['', '/questions','/research','/glossary','/drugs','/conditions','/guides','/methods',...content.guides.map(guideUrl),...content.sources.map(s=>'/research/'+s.id),...content.glossary.map(t=>'/glossary/'+t.slug)].map(path=>({url:REMAPRX_ORIGIN+path}))}
