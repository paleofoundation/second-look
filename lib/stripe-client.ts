/** Small fetch-based Stripe client for the Workers runtime; no global API keys. */
export const STRIPE_API_VERSION = '2026-09-30.endive';
export type StripeMode = 'sandbox' | 'live';
export type StripeObject = { id: string; [key: string]: unknown };
export interface StripeGateway { request(path: string, params?: Record<string, string>, method?: 'GET' | 'POST', idempotencyKey?: string): Promise<StripeObject>; }
export class StripeClient implements StripeGateway {
  private accountVerification?: Promise<void>;
  constructor(private readonly key: string, private readonly fetcher: typeof fetch = fetch, private readonly environment: { mode: StripeMode; accountId?: string } = { mode: 'sandbox' }) {
    const prefix = environment.mode === 'live' ? /^(rk|sk)_live_/ : /^(rk|sk)_test_/;
    if (!['sandbox', 'live'].includes(environment.mode) || !prefix.test(key)) throw new Error('Stripe key does not match the configured environment.');
    if ((environment.mode === 'live' || environment.accountId) && !/^acct_[A-Za-z0-9]+$/.test(environment.accountId ?? '')) throw new Error('A Stripe account identity is required.');
  }
  async request(path: string, params: Record<string, string> = {}, method: 'GET' | 'POST' = 'GET', idempotencyKey?: string): Promise<StripeObject> {
    if (this.environment.accountId) {
      this.accountVerification ??= this.send('/v1/account').then(account => {
        if (account.id !== this.environment.accountId) throw new Error('Stripe account does not match the configured merchant.');
      });
      await this.accountVerification;
    }
    return this.send(path, params, method, idempotencyKey);
  }
  private async send(path: string, params: Record<string, string> = {}, method: 'GET' | 'POST' = 'GET', idempotencyKey?: string): Promise<StripeObject> {
    if (!/^\/v1\/[a-z_]+(?:\/[A-Za-z0-9_]+)*$/.test(path)) throw new Error('Invalid Stripe resource.');
    const encoded = new URLSearchParams(params);
    const response = await this.fetcher(`https://api.stripe.com${path}${method === 'GET' && encoded.size ? '?' + encoded : ''}`, {
      method, headers: { Authorization: `Bearer ${this.key}`, 'Stripe-Version': STRIPE_API_VERSION, ...(method === 'POST' ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}), ...(idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : {}) },
      ...(method === 'POST' ? { body: encoded } : {}), signal: AbortSignal.timeout(8000),
    });
    if (!response.ok) throw new Error(`Stripe request failed (${response.status}).`);
    const body = await response.json() as StripeObject;
    if (!body || typeof body !== 'object') throw new Error('Unexpected Stripe response.');
    // Lists and expanded payment objects must agree with the request's mode too.
    const inspect = (value: unknown): void => {
      if (!value || typeof value !== 'object') return;
      if ('livemode' in value && value.livemode !== (this.environment.mode === 'live')) throw new Error('Unexpected Stripe environment.');
      for (const nested of Object.values(value)) inspect(nested);
    };
    inspect(body);
    return body;
  }
}

export type StripeEvent = { id: string; type: string; created: number; livemode: boolean; data: { object: StripeObject } };
export async function verifyStripeEvent(raw: string, header: string | null, secret: string, now: Date, mode: StripeMode = 'sandbox'): Promise<StripeEvent> {
  if (!secret.startsWith('whsec_') || !header || raw.length > 1_000_000) throw new Error('Invalid webhook.');
  const parts = header.split(',').map(part => part.trim().split('='));
  const times = parts.filter(([key]) => key === 't');
  const timestamp = times.length === 1 && /^\d+$/.test(times[0][1]) ? Number(times[0][1]) : NaN;
  if (!Number.isSafeInteger(timestamp) || Math.abs(now.getTime() / 1000 - timestamp) > 300) throw new Error('Expired webhook.');
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['verify']);
  const payload = new TextEncoder().encode(`${timestamp}.${raw}`);
  let verified = false;
  for (const [kind, value] of parts) if (kind === 'v1' && /^[a-f0-9]{64}$/.test(value)) {
    const bytes = Uint8Array.from(value.match(/../g)!, hex => parseInt(hex, 16));
    if (await crypto.subtle.verify('HMAC', key, bytes, payload)) verified = true;
  }
  if (!verified) throw new Error('Invalid webhook signature.');
  const event = JSON.parse(raw) as StripeEvent;
  if (!['sandbox', 'live'].includes(mode) || !/^evt_[A-Za-z0-9]+$/.test(event.id) || typeof event.type !== 'string' || !Number.isSafeInteger(event.created) || event.livemode !== (mode === 'live') || typeof event.data?.object?.id !== 'string') throw new Error('Invalid Stripe event environment or identity.');
  return event;
}
