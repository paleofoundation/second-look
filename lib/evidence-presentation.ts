import type {Source,SynthesisRow} from './content';

/** Keep the compact table and its citation traversal on the same source-backed design labels. */
export function studyDesignsFor(row:SynthesisRow,sources:Source[]) {
 const designs=new Map<string,string[]>();
 for(const sourceId of [...new Set(row.sourceIds)]) {
  const source=sources.find(item=>item.id===sourceId);
  if(!source)continue;
  const labels=[...new Set(row.effects.filter(effect=>effect.sourceId===sourceId)
   .map(effect=>effect.design?.trim()).filter((label):label is string=>!!label))];
  if(!labels.length&&source.design?.trim())labels.push(source.design.trim());
  for(const text of labels)designs.set(text,[...new Set([...(designs.get(text)||[]),sourceId])]);
 }
 if(!designs.size&&row.evidenceBase.trim())designs.set(row.evidenceBase.trim(),row.sourceIds.filter(id=>sources.some(source=>source.id===id)));
 return [...designs].map(([text,sourceIds])=>({text,sourceIds}));
}
