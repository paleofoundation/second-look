import 'server-only';
import { env } from 'cloudflare:workers';
import { getChatGPTUser } from '@/app/chatgpt-auth';
import { getGuideProduct, guideOffer } from './guide-catalogue';
import { guideRepository } from './guide-repository.server';
import { createCommerceHandlers } from './guide-commerce';
import { createCommerceRepository } from './guide-commerce-repository.server';
import { StripeClient } from './stripe-client';

type CommerceEnvironment = { STRIPE_SANDBOX_KEY?: string; STRIPE_WEBHOOK_SECRET?: string; GUIDE_CHECKOUT_SANDBOX_ENABLED?: string; GUIDE_COMMERCE_ORIGIN?: string; STRIPE_SANDBOX_ID?: string };
const configuration = () => {
  const config = env as typeof env & CommerceEnvironment;
  if (config.GUIDE_CHECKOUT_SANDBOX_ENABLED !== 'true' || !config.STRIPE_SANDBOX_ID || !config.STRIPE_SANDBOX_KEY || !config.STRIPE_WEBHOOK_SECRET) throw new Error('An isolated sandbox is not configured.');
  return config;
};
export const commerceHandlers = createCommerceHandlers({
  getUser: getChatGPTUser,
  repository: () => { if (!env.DB) throw new Error('Commerce storage unavailable.'); return createCommerceRepository(env.DB); },
  guides: guideRepository,
  stripe: () => new StripeClient(configuration().STRIPE_SANDBOX_KEY!),
  config: () => ({ enabled: true, mode: 'sandbox', webhookSecret: configuration().STRIPE_WEBHOOK_SECRET!, origin: configuration().GUIDE_COMMERCE_ORIGIN ?? 'https://remaprx.com' }),
  getProduct: getGuideProduct,
  offer: guideOffer as typeof guideOffer & { launchProductIds: string[] },
});
