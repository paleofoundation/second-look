import sentenceMapData from '@/data/outcome-sentence-maps.json';
import {synthesisRows,isPrimarySource,type Guide,type Source,type SynthesisRow} from './content';
import {mechanismContextsFor} from './mechanisms';
import {buildUniversalArticlePlan} from '@/components/shared-theme/universal-article';
import {createCitationOrder} from '@/components/shared-theme/citations';
import {describeEvidenceConfidence} from '@/components/shared-theme/evidence-confidence';
const sentenceMaps=sentenceMapData.rows as Record<string,{finding:{text:string;sources:string[]}[];magnitude:{text:string;sources:string[]}[]}>;
export function outcomeCitationOrder(rows:SynthesisRow[],sources:Source[]){return createCitationOrder([outcomeCitationIds(rows,sources),rows.flatMap(row=>row.sourceIds),sources.map(source=>source.id)],sources.map(source=>source.id));}
function outcomeCitationIds(rows:SynthesisRow[],sources:Source[]){return rows.toSorted((a,b)=>a.title.localeCompare(b.title)).flatMap(row=>[
 ...(sentenceMaps[row.id]?.finding.flatMap(part=>part.sources)||row.finding.sources),
 ...(sentenceMaps[row.id]?.magnitude.flatMap(part=>part.sources)||row.sourceIds),
 ...(row.limitations[0]?.sources||[]),
 ...describeEvidenceConfidence({...row,limits:row.limitations.map(limit=>({text:limit.text,sourceIds:limit.sources})),background:!row.countsAsPrimaryEvidence,pending:row.coverage.pending},sources.map(source=>({...source,primary:isPrimarySource(source),quarantined:source.status==='Quarantined'}))).limitation.sourceIds
 ]);}

// The renderer and citation registry consume the same section groups.
export function articleSectionGroups(guide:Guide){
 const later=guide.sections.filter(section=>section.label==='Connections'||(guide.type==='Drug'&&section.label==='Evidence'));
 const before=guide.sections.filter(section=>!later.includes(section));
 return {first:before.slice(0,1),rest:before.slice(1),scoped:guide.scopedSections||[],later};
}
export function guideCitationOrder(guide:Guide,sources:Source[],additionalGroups:string[][]=[]){
 const isRecord=['Study','Background source','Glossary'].includes(guide.type);
 const rows=(guide.synthesisIds||[]).map(id=>synthesisRows.find(row=>row.id===id)).filter((row):row is SynthesisRow=>!!row);
 const {first,rest,scoped,later}=articleSectionGroups(guide);
 const sectionSources=(sections:Guide['sections'])=>sections.flatMap(section=>section.sentences?section.sentences.flatMap(sentence=>sentence.sources):section.sources);
 if(guide.type==='Drug'||guide.type==='Condition'){
  const plan=buildUniversalArticlePlan({...guide,type:guide.type});
  const groups=plan.blocks.flatMap(block=>{
   if(block.kind==='findings')return [outcomeCitationIds(rows,sources)];
   const module=block.module;
   return [sectionSources(module.sections),
    module.kind==='mechanisms'?mechanismContextsFor(guide).flatMap(context=>context.sourceIds):[],
    module.kind==='faqs'?guide.faqs.flatMap(faq=>faq.sentences?faq.sentences.flatMap(sentence=>sentence.sources):faq.sources):[],
    sectionSources(module.scoped?.sections||[])];
  });
  return createCitationOrder([...groups,...additionalGroups,guide.sourceIds],sources.map(source=>source.id));
 }
 return createCitationOrder([sectionSources(first),mechanismContextsFor(guide).flatMap(context=>context.sourceIds),outcomeCitationIds(rows,sources),sectionSources(rest),sectionSources(scoped),!isRecord?guide.faqs.flatMap(faq=>faq.sentences?faq.sentences.flatMap(sentence=>sentence.sources):faq.sources):[],sectionSources(later),...additionalGroups,guide.sourceIds],sources.map(source=>source.id));
}
