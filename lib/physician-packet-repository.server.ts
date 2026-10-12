import 'server-only';
import {env} from 'cloudflare:workers';
import type {PacketRepository} from './physician-packet-access';
export function packetRepository():PacketRepository{
 const db=env.DB,bucket=env.BUCKET;
 if(!db||!bucket)throw new Error('Packet storage unavailable');
 return {
  async membership(userId){
   const row=await db.prepare('SELECT user_id,state,current_period_end,cancel_at_period_end FROM guide_memberships WHERE user_id = ?').bind(userId).first<{user_id:string;state:string;current_period_end:string|null;cancel_at_period_end:number}>();
   return row?{userId:row.user_id,state:row.state,currentPeriodEnd:row.current_period_end,cancelAtPeriodEnd:row.cancel_at_period_end===1}:null;
  },
  async releases(){
   const object=await bucket.get('physician-packets/catalogue.v1.json');if(!object)return [];
   if(object.size>300000)throw new Error('Invalid catalogue');
   const data:unknown=await object.json();if(!Array.isArray(data)||data.length>200)throw new Error('Invalid catalogue');return data;
  },
  async asset(key){const object=await bucket.get(key);if(!object||object.size>15000000)return null;return object.arrayBuffer();}
 };
}
