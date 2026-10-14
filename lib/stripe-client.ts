/** Small fetch-based Stripe client for the Workers runtime; no global API keys. */
export const STRIPE_API_VERSION = '2026-09-30.endive';
export type StripeObject = { id: string; [key: string]: unknown };
export interface StripeGateway { request(path: string, params?: Record<string, string>, method?: 'GET' | 'POST', idempotencyKey?: string): Promise<StripeObject>; }
export class StripeClient implements StripeGateway {
  constructor(private readonly key: string, private readonly fetcher: typeof fetch = fetch) {
    // This first release deliberately cannot issue live Stripe requests.
    if (!/^(rk|sk)_test_/.test(key)) throw new Error('An isolated Stripe sandbox key is required.');
  }
  async request(path: string, params: Record<string, string> = {}, method: 'GET' | 'POST' = 'GET', idempotencyKey?: string): Promise<StripeObject> {
    if (!/^\/v1\/[a-z_]+(?:\/[A-Za-z0-9_]+)*$/.test(path)) throw new Error('Invalid Stripe resource.');
    const encoded = new URLSearchParams(params);
    const response = await this.fetcher(`https://api.stripe.com${path}${method === 'GET' && encoded.size ? '?' + encoded : ''}`, {
      method, headers: { Authorization: `Bearer ${this.key}`, 'Stripe-Version': STRIPE_API_VERSION, ...(method === 'POST' ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}), ...(idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : {}) },
      ...(method === 'POST' ? { body: encoded } : {}), signal: AbortSignal.timeout(8000),
    });
    if (!response.ok) throw new Error(`Stripe request failed (${response.status}).`);
    const body = await response.json() as StripeObject;
    if (!body || typeof body !== 'object' || body.livemode === true) throw new Error('Unexpected Stripe environment.');
    return body;
  }
}

export type StripeEvent = { id: string; type: string; created: number; livemode: boolean; data: { object: StripeObject } };
export async function verifyStripeEvent(raw: string, header: string | null, secret: string, now: Date): Promise<StripeEvent> {
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
  if (!/^evt_[A-Za-z0-9]+$/.test(event.id) || typeof event.type !== 'string' || !Number.isSafeInteger(event.created) || event.livemode !== false || typeof event.data?.object?.id !== 'string') throw new Error('Invalid sandbox event.');
  return event;
}
