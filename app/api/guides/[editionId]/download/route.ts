import {getChatGPTUser} from '@/app/chatgpt-auth';
import {createGuideHandlers} from '@/lib/guide-access';
import {guideRepository} from '@/lib/guide-repository.server';
import {getGuideProduct} from '@/lib/guide-catalogue';
export const dynamic='force-dynamic';
const handlers=createGuideHandlers({getUser:getChatGPTUser,repository:guideRepository,getProduct:getGuideProduct});
export async function GET(request:Request,{params}:{params:Promise<{editionId:string}>}){return handlers.download(request,(await params).editionId)}
