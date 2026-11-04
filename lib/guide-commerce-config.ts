import type { StripeMode } from './stripe-client';

export type CommerceEnvironment = {
  GUIDE_COMMERCE_MODE?: string;
  GUIDE_COMMERCE_ORIGIN?: string;
  STRIPE_ACCOUNT_ID?: string;
  GUIDE_CHECKOUT_LIVE_ENABLED?: string;
  STRIPE_LIVE_KEY?: string;
  STRIPE_LIVE_WEBHOOK_SECRET?: string;
  GUIDE_CHECKOUT_SANDBOX_ENABLED?: string;
  STRIPE_SANDBOX_ID?: string;
  STRIPE_SANDBOX_KEY?: string;
  STRIPE_WEBHOOK_SECRET?: string;
};

/** Explicit deployment configuration; content approvals are checked separately. */
export function readCommerceIdentity(env: CommerceEnvironment) {
  const mode = env.GUIDE_COMMERCE_MODE ?? 'sandbox';
  if (mode !== 'live' && mode !== 'sandbox') throw new Error('Unknown commerce mode.');
  const accountId = env.STRIPE_ACCOUNT_ID;
  if (!/^acct_[A-Za-z0-9]+$/.test(accountId ?? '')) throw new Error('Stripe account identity is required.');
  return {mode: mode as StripeMode, accountId: accountId!};
}

export function readCommerceConfiguration(env: CommerceEnvironment) {
  const {mode, accountId} = readCommerceIdentity(env);
  const live = mode === 'live';
  const enabled = live ? env.GUIDE_CHECKOUT_LIVE_ENABLED : env.GUIDE_CHECKOUT_SANDBOX_ENABLED;
  const key = live ? env.STRIPE_LIVE_KEY : env.STRIPE_SANDBOX_KEY;
  const webhookSecret = live ? env.STRIPE_LIVE_WEBHOOK_SECRET : env.STRIPE_WEBHOOK_SECRET;
  const origin = env.GUIDE_COMMERCE_ORIGIN ?? 'https://remaprx.com';
  const url = new URL(origin);
  const secure = url.protocol === 'https:' || (!live && url.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname));
  if (enabled !== 'true' || !/^acct_[A-Za-z0-9]+$/.test(accountId ?? '') || !key || !(live ? /^(rk|sk)_live_/ : /^(rk|sk)_test_/).test(key) || !webhookSecret?.startsWith('whsec_') || (!live && !env.STRIPE_SANDBOX_ID) || !secure || url.origin !== origin) throw new Error('Commerce configuration is incomplete or inconsistent.');
  if (live && env.GUIDE_CHECKOUT_SANDBOX_ENABLED === 'true') throw new Error('Live and sandbox checkout cannot share a deployment.');
  return { enabled: true, mode, accountId, key, webhookSecret, origin };
}
