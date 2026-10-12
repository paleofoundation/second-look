import {z} from 'zod';
const text=z.string().trim().min(1).max(2400);
const short=z.string().trim().min(1).max(180);
const slug=z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/).max(120);
const date=z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
const source=z.object({id:short,citation:text,url:z.string().url().refine(v=>v.startsWith('https://')),basis:short}).strict();
const statement=z.object({text,sourceIds:z.array(short).min(1).max(12)}).strict();
const study=z.object({id:short,intervention:short,title:short,population:text,design:text,comparison:text,primaryLabel:z.enum(['Primary outcome','Biological measurements']).optional(),primary:statement,additional:statement.optional(),limitations:statement,meaning:statement,sourceIds:z.array(short).min(1).max(12)}).strict();
export const packetSchema=z.object({
 schemaVersion:z.literal(1),condition:slug,title:short,edition:short,checkedOn:date,
 scope:text,summary:z.array(statement).min(1).max(4),studies:z.array(study).min(1).max(16),
 safety:z.array(statement.extend({label:short})).min(1).max(8),questions:z.array(text).min(1).max(6),sources:z.array(source).min(1).max(50),
 coverage:text,credit:z.object({name:short,credentials:short,role:short,contact:z.string().email().optional()}).strict().nullable(),
}).strict().superRefine((packet,ctx)=>{
 const ids=new Set(packet.sources.map(s=>s.id));
 if(ids.size!==packet.sources.length)ctx.addIssue({code:'custom',message:'Duplicate source identity'});
 if(new Set(packet.studies.map(s=>s.id)).size!==packet.studies.length)ctx.addIssue({code:'custom',message:'Duplicate study identity'});
 for(const group of [...packet.summary,...packet.safety,...packet.studies.flatMap(s=>[s,s.primary,s.limitations,s.meaning,...(s.additional?[s.additional]:[])])])
  if(group.sourceIds.some(id=>!ids.has(id)))ctx.addIssue({code:'custom',message:'Unresolved citation'});
});
export type PhysicianPacket=z.infer<typeof packetSchema>;
export type PacketChoice={condition:string;title:string;edition:string;checkedOn:string};
export type PacketCatalogue={access:'member'|'membership_required';packets:PacketChoice[];message:string};
export function packetEmail(packet:Pick<PhysicianPacket,'title'|'edition'>){return `Dear Dr. [name],\n\nCould we review the attached ${packet.title} evidence packet at my next appointment? I would appreciate your assessment of which studies apply to my situation, the important limitations and risks, and whether any further review or clinical trial inquiry is appropriate within my treatment timeline.\n\nIf an approach is unsuitable, please help me understand the specific reason and our next steps.\n\nThank you,\n[Your name]\n\nAttachment to add: ${packet.title} physician packet, edition ${packet.edition}.`;}
