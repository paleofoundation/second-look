import sentenceMapData from '@/data/outcome-sentence-maps.json';
import {synthesisRows,isPrimarySource,type Guide,type Source,type SynthesisRow} from './content';
import {mechanismCitationIds} from './mechanisms';
import {buildUniversalArticlePlan,isRetiredArticleSection} from '@/components/shared-theme/universal-article';
import {createCitationOrder} from '@/components/shared-theme/citations';
import {describeEvidenceConfidence} from '@/components/shared-theme/evidence-confidence';
import {studyDesignsFor} from './evidence-presentation';
const sentenceMaps=sentenceMapData.rows as Record<string,{finding:{text:string;sources:string[]}[];magnitude:{text:string;sources:string[]}[]}>;
export function outcomeCitationOrder(rows:SynthesisRow[],sources:Source[]){return createCitationOrder([outcomeCitationIds(rows,sources),rows.flatMap(row=>row.sourceIds),sources.map(source=>source.id)],sources.map(source=>source.id));}
function outcomeCitationIds(rows:SynthesisRow[],sources:Source[]){const sorted=rows.toSorted((a,b)=>a.title.localeCompare(b.title));return [
 // The closed table shows every row's study designs. Drawer-only findings must
 // not preempt citations in a later visible row; opening a drawer never renumbers.
 ...sorted.flatMap(row=>studyDesignsFor(row,sources).flatMap(design=>design.sourceIds)),
 ...sorted.flatMap(row=>[
 ...(sentenceMaps[row.id]?.finding.flatMap(part=>part.sources)||row.finding.sources),
 ...(sentenceMaps[row.id]?.magnitude.flatMap(part=>part.sources)||row.sourceIds),
 ...(row.limitations[0]?.sources||[]),
 ...describeEvidenceConfidence({...row,limits:row.limitations.map(limit=>({text:limit.text,sourceIds:limit.sources})),background:!row.countsAsPrimaryEvidence,pending:row.coverage.pending},sources.map(source=>({...source,primary:isPrimarySource(source),quarantined:source.status==='Quarantined'}))).limitation.sourceIds
 ])];}

export function hasArticleEvidence(guide:Guide){return ['Drug','Condition','Evidence comparison'].includes(guide.type)||guide.type.includes('evidence answer')||!!guide.synthesisIds?.length;}

// The renderer and citation registry consume the same section groups.
export function articleSectionGroups(guide:Guide){
 const active=guide.sections.filter(section=>!isRetiredArticleSection(section));
 const evidence=hasArticleEvidence(guide)?active.filter(section=>section.label==='Evidence'):[];
 const before=active.filter(section=>!evidence.includes(section));
 return {first:before.slice(0,1),rest:before.slice(1),scoped:(guide.scopedSections||[]).filter(section=>!isRetiredArticleSection(section)),later:[] as Guide['sections'],evidence};
}
export function guideCitationOrder(guide:Guide,sources:Source[],additionalGroups:string[][]=[]){
 const isRecord=['Study','Background source','Glossary'].includes(guide.type);
 const rows=(guide.synthesisIds||[]).map(id=>synthesisRows.find(row=>row.id===id)).filter((row):row is SynthesisRow=>!!row);
 const {first,rest,scoped,later,evidence}=articleSectionGroups(guide);
 const sectionSources=(sections:Guide['sections'])=>sections.filter(section=>!isRetiredArticleSection(section)).flatMap(section=>[
  ...(section.sentences?section.sentences.flatMap(sentence=>sentence.sources):section.sources),
  ...(section.questions||[]).flatMap(question=>question.sentences?question.sentences.flatMap(sentence=>sentence.sources):question.sources)
 ]);
 if(guide.type==='Drug'||guide.type==='Condition'){
  const plan=buildUniversalArticlePlan({...guide,type:guide.type});
  const groups=plan.blocks.flatMap(block=>{
   const articleModule=block.module;
   return [sectionSources(articleModule.sections),
    articleModule.kind==='mechanisms'?mechanismCitationIds(guide):[],
    articleModule.kind==='faqs'?guide.faqs.flatMap(faq=>faq.sentences?faq.sentences.flatMap(sentence=>sentence.sources):faq.sources):[],
    sectionSources(articleModule.scoped?.sections||[]),
    articleModule.label==='Evidence'?outcomeCitationIds(rows,sources):[]];
  });
  return createCitationOrder([...groups,...additionalGroups,guide.sourceIds],sources.map(source=>source.id));
 }
 return createCitationOrder([sectionSources(first),mechanismCitationIds(guide),sectionSources(rest),sectionSources(scoped),!isRecord?guide.faqs.flatMap(faq=>faq.sentences?faq.sentences.flatMap(sentence=>sentence.sources):faq.sources):[],sectionSources(later),sectionSources(evidence),hasArticleEvidence(guide)?outcomeCitationIds(rows,sources):[],...additionalGroups,guide.sourceIds],sources.map(source=>source.id));
}
