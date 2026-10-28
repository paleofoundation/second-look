import raw from '@/data/outcome-summaries.json';
import type {SynthesisRow} from './content';

export type BenefitGrade='A'|'B'|'C'|'D'|'E'|'F';
export type OutcomeTrial={id:string;comparisonId?:string;sourceIds:string[];participants:number|null;participantBasis:string};
export type OutcomeEvidence={rctCount:number;participants:number|null;participantBasis:string;trialFamilyIds:string[];sourceIds:string[];trials:OutcomeTrial[]};
export type OutcomeSummary={
 id:string;synthesisIds:string[];drugId:string;conditionId:string;label:string;
 assessedOn?:string;
 purpose:'prevention'|'treatment'|'mechanistic'|'safety';
 grade:{value:BenefitGrade|null;label:string;rationale:string;sourceIds:string[]};
 effect:{label:string;detail:string;direction:'benefit'|'harm'|'mixed'|'uncertain'|'not_applicable';rationale:string};
 evidence:OutcomeEvidence;sourceIds:string[];aggregationNote:string;
};
export const outcomeSummaries=raw.records as OutcomeSummary[];
export const outcomeBenefitMethod=raw.method;
export const outcomeBenefitAssessmentDate=raw.assessedOn;
const bySynthesisId=new Map(outcomeSummaries.flatMap(summary=>summary.synthesisIds.map(id=>[id,summary] as const)));
export function outcomeSummaryFor(rowId:string){return bySynthesisId.get(rowId)}
/** Stable input order; merge only explicitly reviewed members, never by matching title. */
export function outcomeSummariesFor(rows:SynthesisRow[]):OutcomeSummary[]{
 const seen=new Set<string>();
 return rows.flatMap(row=>{const summary=bySynthesisId.get(row.id);if(!summary||seen.has(summary.id))return [];seen.add(summary.id);return [summary]});
}
/** A family shared by outcomes or companion reports contributes participants once. */
export function evidenceForSummaries(summaries:OutcomeSummary[]):OutcomeEvidence{
 if(summaries.length===1)return summaries[0].evidence;
 const byFamily=new Map<string,OutcomeTrial>();
 for(const trial of summaries.flatMap(summary=>summary.evidence.trials)){
  const previous=byFamily.get(trial.id);
  if(!previous){byFamily.set(trial.id,{...trial,sourceIds:[...trial.sourceIds]});continue;}
  const compatible=previous.participants===trial.participants&&previous.participantBasis===trial.participantBasis;
  byFamily.set(trial.id,{id:trial.id,sourceIds:[...new Set([...previous.sourceIds,...trial.sourceIds])],
   participants:compatible?trial.participants:null,
   participantBasis:compatible?trial.participantBasis:'Different reported populations for this trial cannot be added or substituted; see the outcome-specific study details.'});
 }
 const trials=[...byFamily.values()];
 const complete=trials.length>0&&trials.every(trial=>trial.participants!==null);
 return {rctCount:trials.length,participants:complete?trials.reduce((sum,trial)=>sum+(trial.participants??0),0):null,
 participantBasis:complete?'Participants in the included randomized comparisons, counted once per trial; see study details for enrollment and analysis populations.':trials.length?'A comparable participant total is not available for every included randomized comparison.':'No randomized clinical trial is represented in this selected evidence.',
 trialFamilyIds:trials.map(trial=>trial.id),sourceIds:[...new Set(summaries.flatMap(summary=>summary.evidence.sourceIds))],trials};
}
