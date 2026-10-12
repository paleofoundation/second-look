import 'server-only';
import {getChatGPTUser} from '@/app/chatgpt-auth';
import {createPacketHandlers} from './physician-packet-access';
import {packetRepository} from './physician-packet-repository.server';
export const packetHandlers=createPacketHandlers({getUser:getChatGPTUser,repository:packetRepository});
