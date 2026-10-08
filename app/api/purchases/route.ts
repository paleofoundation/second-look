import {getChatGPTUser} from '@/app/chatgpt-auth';
import {privateHeaders} from '@/lib/library';
export const dynamic='force-dynamic';
export async function GET(){if(!await getChatGPTUser())return Response.json({error:'Sign in to view guides.'},{status:401,headers:privateHeaders});return Response.json({commerce:'not_launched',purchases:[],message:'No guides are sold yet. Paid editions will appear here after a verified purchase when sales launch.'},{headers:privateHeaders});}
