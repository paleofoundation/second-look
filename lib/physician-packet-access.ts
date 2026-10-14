import {z} from 'zod';
import {activeGuideMembership,type GuideMembership} from './guide-access';
import {ACCOUNT_PRIVATE_HEADERS,type ReaderIdentity} from './profile-api';
import {packetSchema,type PhysicianPacket} from './physician-packet-contract';
const hash=z.string().regex(/^[a-f0-9]{64}$/);
const key=z.string().min(1).max(300).refine(v=>v.startsWith('physician-packets/')&&!v.includes('..')&&!/[\x00-\x1f]/.test(v));
const identified=z.string().trim().min(2).refine(v=>!/^(pending|unknown|tbd|placeholder|not reviewed)$/i.test(v));
const approval=z.object({name:identified,qualifications:identified,scope:z.string().trim().min(5),conflicts:z.string().trim().min(2),decision:z.literal('approved'),at:z.string().datetime(),edition:z.string(),bodySha256:hash,pdfSha256:hash}).strict();
export const packetReleaseSchema=z.object({condition:z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/).max(120),title:z.string().min(1).max(180),edition:z.string().min(1).max(80),checkedOn:z.string().regex(/^\d{4}-\d{2}-\d{2}$/),state:z.enum(['pending','released','withdrawn']),bodyKey:key,pdfKey:key,bodySha256:hash,pdfSha256:hash,editorial:approval.nullable(),clinical:approval.nullable(),legal:approval.nullable(),creditConsent:z.boolean()}).strict();
export type PacketRelease=z.infer<typeof packetReleaseSchema>;
export type PacketRepository={membership(userId:string):Promise<GuideMembership|null>;releases():Promise<unknown[]>;asset(key:string):Promise<ArrayBuffer|null>};
export type PacketDependencies={getUser:()=>Promise<ReaderIdentity|null>;repository:()=>PacketRepository;now?:()=>Date};
export function releasedPacket(value:unknown,at:Date):PacketRelease|null{
 const parsed=packetReleaseSchema.safeParse(value);if(!parsed.success)return null;
 const p=parsed.data;if(p.state!=='released'||!Number.isFinite(Date.parse(p.checkedOn))||Date.parse(p.checkedOn)>at.getTime())return null;
 if(![p.editorial,p.clinical,p.legal].every(a=>a&&Date.parse(a.at)<=at.getTime()&&a.edition===p.edition&&a.bodySha256===p.bodySha256&&a.pdfSha256===p.pdfSha256))return null;
 return p;
}
async function digest(bytes:ArrayBuffer){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(b=>b.toString(16).padStart(2,'0')).join('');}
export function createPacketHandlers(deps:PacketDependencies){
 const json=(body:unknown,status=200)=>Response.json(body,{status,headers:ACCOUNT_PRIVATE_HEADERS});
 async function authorize(){
  const user=await deps.getUser();if(!user)return {error:json({error:'Sign in to open physician packets.'},401)};
  const at=deps.now?.()??new Date();const repo=deps.repository();
  if(!activeGuideMembership(await repo.membership(user.userId),user.userId,at))return {error:json({access:'membership_required',packets:[],message:'Physician packets are included with an active paid membership. Memberships have not launched yet.'},403)};
  return {repo,at};
 }
 async function releases(repo:PacketRepository,at:Date){
  const entries=(await repo.releases()).map(x=>releasedPacket(x,at)).filter((x):x is PacketRelease=>x!==null);
  const ids=entries.map(e=>e.condition);if(new Set(ids).size!==ids.length)throw new Error('Duplicate condition release');return entries;
 }
 async function verifiedBody(repo:PacketRepository,release:PacketRelease):Promise<PhysicianPacket>{
  const bytes=await repo.asset(release.bodyKey);if(!bytes||bytes.byteLength>300000||await digest(bytes)!==release.bodySha256)throw new Error('Body integrity');
  const p=packetSchema.parse(JSON.parse(new TextDecoder().decode(bytes)));
  if(p.condition!==release.condition||p.edition!==release.edition||p.title!==release.title||p.checkedOn!==release.checkedOn||p.credit&&!release.creditConsent)throw new Error('Edition identity');return p;
 }
 return {
  async catalogue(request:Request){
   try{const auth=await authorize();if(auth.error)return auth.error;if(new URL(request.url).search)return json({error:'Account parameters are not accepted.'},400);
    const entries=await releases(auth.repo!,auth.at!);
    return json({access:'member',packets:entries.map(({condition,title,edition,checkedOn})=>({condition,title,edition,checkedOn})),message:entries.length?'Choose a condition to prepare a physician discussion packet.':'No reviewed packet editions are available yet. Please check back for condition coverage.'});
   }catch{return json({error:'Physician packets could not load. Please retry.'},503);}
  },
  async packet(request:Request,condition:string,format:'json'|'pdf'='json'){
   try{const auth=await authorize();if(auth.error)return auth.error;
    if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(condition)||condition.length>120||new URL(request.url).search)return json({error:'Choose a valid condition.'},400);
    const release=(await releases(auth.repo!,auth.at!)).find(p=>p.condition===condition);
    if(!release)return json({error:'A reviewed packet is not available for this condition.'},404);
    const packet=await verifiedBody(auth.repo!,release);
    if(format==='json')return json({packet});
    const bytes=await auth.repo!.asset(release.pdfKey);
    if(!bytes||bytes.byteLength>15000000||await digest(bytes)!==release.pdfSha256||new TextDecoder().decode(bytes.slice(0,5))!=='%PDF-')throw new Error('PDF integrity');
    return new Response(bytes,{headers:{...ACCOUNT_PRIVATE_HEADERS,'Content-Type':'application/pdf','Content-Disposition':`attachment; filename="${condition}-physician-packet.pdf"`,'Content-Security-Policy':'sandbox'}});
   }catch{return json({error:'This packet could not be verified. Please retry later.'},503);}
  }
 };
}
