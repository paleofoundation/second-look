import {packetHandlers} from '@/lib/physician-packet-server';
export const dynamic='force-dynamic';
export async function GET(request:Request,{params}:{params:Promise<{condition:string}>}){return packetHandlers.packet(request,(await params).condition,'pdf');}
