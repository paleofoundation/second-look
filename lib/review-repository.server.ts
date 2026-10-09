import 'server-only';
import envelopes from '@/data/review-envelopes.json';
import type {ReviewEnvelope,ReviewRepository,ProtectedReview} from '@/lib/review-access';
export const reviewRepository:ReviewRepository={
 async getPublic(id){return Object.hasOwn(envelopes,id)?(envelopes as Record<string,ReviewEnvelope>)[id]:null},
 async readProtected(id){
  // This import is deliberately inside the post-authorization reader.
  const {default:records}=await import('@/data/private-reviews.json');
  return Object.hasOwn(records,id)?(records as unknown as Record<string,ProtectedReview>)[id]:null;
 }
};
