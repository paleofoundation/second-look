import {suitabilityCitationIds} from './treatment-suitability';
import sentenceMapData from '@/data/outcome-sentence-maps.json';
import {content,synthesisRows,isPrimarySource,type Guide,type Source,type SynthesisRow} from './content';
import {mechanismCitationIds,evidenceMechanismSourceIds} from './mechanisms';
import {buildUniversalArticlePlan,isRetiredArticleSection} from '@/components/shared-theme/universal-article';
import {createCitationOrder} from '@/components/shared-theme/citations';
import {describeEvidenceConfidence} from '@/components/shared-theme/evidence-confidence';
import {outcomeSummariesFor} from './outcome-summary';
const sentenceMaps=sentenceMapData.rows as Record<string,{finding:{text:string;sources:string[]}[];magnitude:{text:string;sources:string[]}[]}>;
function guideRows(guide:Guide){return (guide.synthesisIds||[]).map(id=>synthesisRows.find(row=>row.id===id)).filter((row):row is SynthesisRow=>!!row);}
/** Drawers reuse canonical mechanism sources even when the opposite guide did not cite them before. */
export function articleEvidenceSources(guide:Guide,sources:Source[]):Source[]{
 const rows=guideRows(guide);
 const ids=[...outcomeSummariesFor(rows).flatMap(summary=>summary.sourceIds),...evidenceMechanismSourceIds(rows)];
 const existing=new Set(sources.map(source=>source.id));
 return [...sources,...[...new Set(ids)].filter(id=>!existing.has(id)).map(id=>content.sources.find(source=>source.id===id)).filter((source):source is NonNullable<typeof source>=>!!source)];
}
function visibleOutcomeCitationIds(rows:SynthesisRow[],guide?:Guide){
 const summaries=outcomeSummariesFor(rows).toSorted((a,b)=>a.label.localeCompare(b.label));
 // The finder sorts labels before the table forms its condition/intervention
 // groups. Follow the resulting closed-table order, then freeze it for filtering.
 const groups=new Map<string,typeof summaries>();
 for(const summary of summaries){const key=guide?.type==='Condition'?summary.drugId:summary.conditionId;const group=groups.get(key)||[];group.push(summary);groups.set(key,group);}
 return [...groups.values()].flatMap(group=>group.flatMap(summary=>summary.sourceIds));
}
export function outcomeCitationOrder(rows:SynthesisRow[],sources:Source[]){return createCitationOrder([visibleOutcomeCitationIds(rows),outcomeDrawerCitationIds(rows,sources),rows.flatMap(row=>row.sourceIds),sources.map(source=>source.id)],sources.map(source=>source.id));}
function outcomeDrawerCitationIds(rows:SynthesisRow[],sources:Source[]){const sorted=rows.toSorted((a,b)=>a.title.localeCompare(b.title));return [
 ...sorted.flatMap(row=>[
 ...(sentenceMaps[row.id]?.finding.flatMap(part=>part.sources)||row.finding.sources),
 ...(sentenceMaps[row.id]?.magnitude.flatMap(part=>part.sources)||row.sourceIds),
 ...(row.limitations[0]?.sources||[]),
 ...describeEvidenceConfidence({...row,limits:row.limitations.map(limit=>({text:limit.text,sourceIds:limit.sources})),background:!row.countsAsPrimaryEvidence,pending:row.coverage.pending},sources.map(source=>({...source,primary:isPrimarySource(source),quarantined:source.status==='Quarantined'}))).limitation.sourceIds
 ]),
 ...evidenceMechanismSourceIds(sorted)];}

/** Drug Benefits questions move to FAQs unless already covered: an FAQ with the same id/question, or every cited source already represented by an Evidence outcome row. */
export function benefitQuestionPlan(guide:Guide,rows:SynthesisRow[]){const questions=guide.type==='Drug'?guide.sections.filter(section=>section.label==='Benefits').flatMap(section=>section.questions||[]):[];const evidenceIds=new Set(rows.flatMap(row=>row.sourceIds||[]));const norm=(text:string)=>text.toLowerCase().replace(/[^a-z0-9 ]/g,'').trim();const faqKeys=new Set(guide.faqs.flatMap(faq=>[faq.id||'',norm(faq.question)]));type BenefitQuestion=(typeof questions)[number];const moved:BenefitQuestion[]=[],dropped:BenefitQuestion[]=[];for(const question of questions){const covered=faqKeys.has(question.id)||faqKeys.has(norm(question.question))||(!!question.sources?.length&&question.sources.every(id=>evidenceIds.has(id)));(covered?dropped:moved).push(question)}return {moved,dropped}}

export function hasArticleEvidence(guide:Guide){return ['Drug','Condition','Evidence comparison'].includes(guide.type)||guide.type.includes('evidence answer')||!!guide.synthesisIds?.length;}

// The renderer and citation registry consume the same section groups.
export function articleSectionGroups(guide:Guide){
 const active=guide.sections.filter(section=>!isRetiredArticleSection(section));
 const evidence=['Study','Background source','Glossary'].includes(guide.type)?[]:active.filter(section=>section.label==='Evidence');
 const before=active.filter(section=>!evidence.includes(section));
 return {first:before.slice(0,1),rest:before.slice(1),scoped:(guide.scopedSections||[]).filter(section=>!isRetiredArticleSection(section)),later:[] as Guide['sections'],evidence};
}
export function guideCitationOrder(guide:Guide,sources:Source[],additionalGroups:string[][]=[]){
 sources=articleEvidenceSources(guide,sources);
 const isRecord=['Study','Background source','Glossary'].includes(guide.type);
 const feedSourceIds=sources.filter(isPrimarySource).map(source=>source.id);
 const rows=guideRows(guide);
 const {first,rest,scoped,later,evidence}=articleSectionGroups(guide);
 const sectionSources=(sections:Guide['sections'])=>sections.filter(section=>!isRetiredArticleSection(section)).flatMap(section=>[
  ...(section.sentences?section.sentences.flatMap(sentence=>sentence.sources):section.sources),
  ...(section.questions||[]).flatMap(question=>question.sentences?question.sentences.flatMap(sentence=>sentence.sources):question.sources)
 ]);
 if(guide.type==='Drug'||guide.type==='Condition'){
  const plan=buildUniversalArticlePlan({...guide,type:guide.type});
  // Drug Benefits renders inside Overview (summary) and FAQs (uncovered questions).
  const benefitSections=guide.type==='Drug'?plan.modules.find(item=>item.label==='Benefits')?.sections||[]:[];
  const movedQuestions=guide.type==='Drug'?benefitQuestionPlan(guide,rows).moved:[];
  const groups=plan.blocks.flatMap(block=>{
   const articleModule=block.module;
   if(guide.type==='Drug'&&articleModule.label==='Benefits')return [];
   return [sectionSources(articleModule.sections),
    articleModule.label==='Overview'?sectionSources(benefitSections.map(section=>({...section,questions:[]}))):[],
    ((guide.type==='Drug'&&articleModule.label==='Contraindications')||(guide.type==='Condition'&&articleModule.label==='Safety'))?suitabilityCitationIds(guide.slug):[],
    articleModule.kind==='mechanisms'?mechanismCitationIds(guide,'evidence'):[],
    articleModule.kind==='faqs'?guide.faqs.flatMap(faq=>faq.sentences?faq.sentences.flatMap(sentence=>sentence.sources):faq.sources):[],
    articleModule.kind==='faqs'?movedQuestions.flatMap(question=>question.sentences?question.sentences.flatMap(sentence=>sentence.sources):question.sources||[]):[],
    sectionSources(articleModule.scoped?.sections||[]),
    articleModule.label==='Evidence'?visibleOutcomeCitationIds(rows,guide):[],
    ...(articleModule.kind==='research'?[...additionalGroups,feedSourceIds]:[])];
  });
  // Sources cited only inside a drawer follow the complete article's visible
  // citation sequence. Opening, filtering or closing it never renumbers the page.
  return createCitationOrder([...groups,outcomeDrawerCitationIds(rows,sources),guide.sourceIds],sources.map(source=>source.id));
 }
 return createCitationOrder([sectionSources(first),mechanismCitationIds(guide),sectionSources(rest),sectionSources(scoped),sectionSources(later),sectionSources(evidence),hasArticleEvidence(guide)?visibleOutcomeCitationIds(rows,guide):[],...additionalGroups,!isRecord?feedSourceIds:[],!isRecord?guide.faqs.flatMap(faq=>faq.sentences?faq.sentences.flatMap(sentence=>sentence.sources):faq.sources):[],hasArticleEvidence(guide)?outcomeDrawerCitationIds(rows,sources):[],guide.sourceIds],sources.map(source=>source.id));
}
