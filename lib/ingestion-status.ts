import status from '@/data/ingestion-status.json';
import {content,guideUrl,type Guide} from '@/lib/content';
import {readerEvidenceStatus} from './reader-evidence-status';
export const ingestedTopicPages=status.pages.map(page=>({topic_id:page.topic_id,title:page.title,path:page.path,aliases:page.aliases,notice:'Evidence incomplete. Independent review is not complete.',...readerEvidenceStatus(page.next_action)}));
export function ingestedTopicForPath(path:string){const normalized=path.startsWith('/')?path:'/'+path;return ingestedTopicPages.find(p=>p.path===normalized||p.aliases.includes(normalized))}
export function ingestionStatusGuide(page:typeof ingestedTopicPages[number],path:string):Guide{
 const prior=content.guides.find(g=>page.aliases.includes(guideUrl(g)));
 if(prior)return {...prior,slug:'/'+path};
 return {id:page.topic_id,slug:'/'+path,title:page.title,type:'Reader question',description:page.notice,topicIds:[page.topic_id],sections:[{id:'scope',label:'Question',title:'The question in this edition',paragraph:page.readerSummary,sources:[]},{id:'evidence-gaps',label:'Evidence gaps',title:'What is missing from the evidence',paragraph:page.readerNextStep,sources:[]},{id:'limits',label:'Limits',title:'What can be concluded?',paragraph:'The evidence currently summarized here does not establish a treatment benefit or a completed safety assessment.',sources:[]}],faqs:[{question:'Is there a completed evidence answer for this question?',answer:'An independently reviewed answer is not yet available. The evidence gaps above describe the limits of this page.',sources:[]},{question:'Does incomplete coverage mean that no relevant studies exist?',answer:'No. It describes the sources available here, not the absence of research.',sources:[]}],sourceIds:[],related:[]};
}
