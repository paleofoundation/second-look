import status from '@/data/ingestion-status.json';
import {content,guideUrl,type Guide} from '@/lib/content';
export const ingestedTopicPages=status.pages;
export function ingestedTopicForPath(path:string){const normalized=path.startsWith('/')?path:'/'+path;return ingestedTopicPages.find(p=>p.path===normalized||p.aliases.includes(normalized))}
export function ingestionStatusGuide(page:typeof ingestedTopicPages[number],path:string):Guide{
 const prior=content.guides.find(g=>page.aliases.includes(guideUrl(g)));
 if(prior)return {...prior,slug:'/'+path};
 return {id:page.topic_id,slug:'/'+path,title:page.title,type:'Reader question',description:'Evidence incomplete. Verification and independent review are pending.',topicIds:[page.topic_id],sections:[{id:'scope',label:'Question',title:'The question in this edition',paragraph:page.notice,sources:[]},{id:'next-action',label:'Next action',title:'What needs to happen next',paragraph:page.next_action,sources:[]},{id:'limits',label:'Limits',title:'Current evidence boundary',paragraph:'Newly ingested records remain pending verification, pending human review and draft. Their result values are withheld from this preview. No topic verdict has been issued.',sources:[]}],faqs:[{question:'Is there a completed evidence answer for this question?',answer:'No completed or approved synthesis is available for this question in this edition. The next action above records the work still required.',sources:[]},{question:'Does incomplete coverage mean that no relevant studies exist?',answer:'No. It describes the coverage of this bounded corpus, not the absence of research. Acquisition, mapping and appraisal gaps must be resolved separately.',sources:[]}],sourceIds:[],related:[]};
}
