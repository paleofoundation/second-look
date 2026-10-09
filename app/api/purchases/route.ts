import {getChatGPTUser} from '@/app/chatgpt-auth';
import {createGuideHandlers} from '@/lib/guide-access';
import {guideRepository} from '@/lib/guide-repository.server';
import {getGuideProduct} from '@/lib/guide-catalogue';
export const dynamic='force-dynamic';
const handlers=createGuideHandlers({getUser:getChatGPTUser,repository:guideRepository,getProduct:getGuideProduct});
export const GET=handlers.purchases;
