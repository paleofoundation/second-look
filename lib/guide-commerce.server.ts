import 'server-only';
import { env } from 'cloudflare:workers';
import { getChatGPTUser } from '@/app/chatgpt-auth';
import { getGuideProduct, guideOffer } from './guide-catalogue';
import { guideRepository } from './guide-repository.server';
import { createCommerceHandlers } from './guide-commerce';
import { createCommerceRepository } from './guide-commerce-repository.server';
import { StripeClient } from './stripe-client';
import { activeGuideMembership, guideLibraryView } from './guide-access';
import { readerProfiles } from './profile-server';
import { createGuideSavesRepository } from './guide-saves';
import { topicGuideMappings } from './topic-guides';
import { readCommerceConfiguration, type CommerceEnvironment } from './guide-commerce-config';

const configuration = () => readCommerceConfiguration(env as typeof env & CommerceEnvironment);
export const commerceHandlers = createCommerceHandlers({
  getUser: getChatGPTUser,
  repository: () => { if (!env.DB) throw new Error('Commerce storage unavailable.'); return createCommerceRepository(env.DB); },
  guides: guideRepository,
  stripe: () => { const config = configuration(); return new StripeClient(config.key, fetch, config); },
  config: () => { const {enabled, mode, accountId, webhookSecret, origin} = configuration(); return {enabled, mode, accountId, webhookSecret, origin}; },
  getProduct: getGuideProduct,
  offer: guideOffer as typeof guideOffer & { launchProductIds: string[] },
  reconcileLibrary: async userId => {
    if (!env.DB) throw new Error('Guide library storage unavailable.');
    const at = new Date();
    const [library, profile] = await Promise.all([guideRepository().readLibrary(userId, at.toISOString()), readerProfiles().read(userId)]);
    const view = guideLibraryView(userId, library, getGuideProduct, at);
    const interests = new Set(profile?.interests ?? []);
    const matching = new Set(topicGuideMappings.filter(topic => interests.has(`${topic.kind}:${topic.slug}`)).map(topic => topic.productId));
    await createGuideSavesRepository(env.DB).reconcile(userId, view.availableGuides, matching, activeGuideMembership(library.membership, userId, at));
  },
});
