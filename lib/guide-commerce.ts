import { approvedGuideEdition, activeGuideMembership, type GuideEdition, type GuideProduct, type GuideRepository } from './guide-access';
import { ACCOUNT_PRIVATE_HEADERS, sameOriginMutation, type ReaderIdentity } from './profile-api';
import { verifyStripeEvent, type StripeEvent, type StripeGateway, type StripeObject } from './stripe-client';

export type CommerceProduct = GuideProduct & { priceMinor: number; currency: string };
export type CheckoutAttempt = { id: string; userId: string; requestKey: string; kind: 'guide' | 'membership'; productId: string | null; editionId: string | null; amount: number; currency: string; customerId: string; sessionId: string | null; sessionUrl: string | null; createdAt: string };
export type OrderProjection = { id: string; userId: string; productId: string; editionId: string; status: string; currency: string; amount: number; sessionId: string; paymentIntentId: string | null; chargeId: string | null; createdAt: string; updatedAt: string };
export type InvoiceProjection = { invoiceId: string; userId: string; subscriptionId: string; chargeId: string | null; paymentIntentId: string | null; status: string; paidThrough: string | null; updatedAt: string };
export type SubscriptionProjection = { userId: string; subscriptionId: string; customerId: string; state: string; cancelAtPeriodEnd: boolean };
export type CommerceProjection = { order?: OrderProjection; invoice?: InvoiceProjection; subscription?: SubscriptionProjection };
export interface CommerceRepository {
  readEditions(productId: string): Promise<GuideEdition[]>;
  customer(userId: string): Promise<string | null>;
  saveCustomer(userId: string, customerId: string): Promise<string>;
  userForCustomer(customerId: string): Promise<string | null>;
  attempt(userId: string, requestKey: string): Promise<CheckoutAttempt | null>;
  membershipCheckout(userId: string): Promise<CheckoutAttempt | null>;
  membershipSubscription(userId: string): Promise<string | null>;
  attemptById(id: string): Promise<CheckoutAttempt | null>;
  createAttempt(attempt: CheckoutAttempt): Promise<CheckoutAttempt>;
  attachSession(id: string, sessionId: string, url: string): Promise<void>;
  orderByCharge(chargeId: string): Promise<{ sessionId: string } | null>;
  invoiceByCharge(chargeId: string): Promise<{ invoiceId: string } | null>;
  acquireEventLock(owner: string, now: number): Promise<boolean>;
  releaseEventLock(owner: string): Promise<void>;
  hasEvent(id: string): Promise<boolean>;
  eventUser(id: string): Promise<string | null>;
  applyEvent(event: StripeEvent, projection: CommerceProjection, owner: string, now: Date): Promise<void>;
}
export type CommerceConfig = { enabled: boolean; mode: 'sandbox'; webhookSecret: string; origin: string };
export type CommerceDependencies = {
  getUser(): Promise<ReaderIdentity | null>; repository(): CommerceRepository; guides(): GuideRepository; stripe(): StripeGateway;
  config(): CommerceConfig; getProduct(id: string): CommerceProduct | undefined;
  offer: { enabled: boolean; monthlyMinor: number; currency: string; launchProductIds: string[]; launchMinimum: number };
  now?: () => Date; uuid?: () => string;
  reconcileLibrary?: (userId: string) => Promise<void>;
};
const object = (value: unknown): StripeObject => value && typeof value === 'object' ? value as StripeObject : { id: '' };
const id = (value: unknown): string => typeof value === 'string' ? value : typeof object(value).id === 'string' ? object(value).id : '';
const list = (value: unknown): StripeObject[] => Array.isArray(object(value).data) ? object(value).data as StripeObject[] : [];
const str = (value: unknown) => typeof value === 'string' ? value : '';
const iso = (seconds: unknown): string | null => typeof seconds === 'number' && Number.isSafeInteger(seconds) && seconds > 0 && seconds < 253402300799 ? new Date(seconds * 1000).toISOString() : null;
const resource = (prefix: string, value: string) => { if (!new RegExp(`^${prefix}_[A-Za-z0-9_]+$`).test(value)) throw new Error('Invalid provider resource.'); return value; };
const hostedUrl = (value: unknown, host: string): string => { const url = new URL(str(value)); if (url.protocol !== 'https:' || url.hostname !== host || url.username || url.password) throw new Error('Invalid hosted URL.'); return url.href; };
const metadataAttempt = (value: StripeObject) => str(object(value.metadata).remaprx_attempt);

/** Current provider objects, not the webhook snapshot, determine fulfillment. */
export class GuidePaymentReconciler {
  constructor(private readonly repo: CommerceRepository, private readonly stripe: StripeGateway, private readonly now: Date) {}
  private get(path: string, params: Record<string, string> = {}) { return this.stripe.request(path, params); }
  private async paymentState(paymentIntentId: string): Promise<{ status: string; chargeId: string | null }> {
    if (!paymentIntentId) return { status: 'pending', chargeId: null };
    const payment = await this.get(`/v1/payment_intents/${resource('pi', paymentIntentId)}`, { 'expand[]': 'latest_charge' });
    const charge = object(payment.latest_charge); const chargeId = id(payment.latest_charge) || null;
    if (payment.status !== 'succeeded') return { status: payment.status === 'canceled' || payment.status === 'requires_payment_method' ? 'failed' : 'pending', chargeId };
    if (!chargeId || !Object.hasOwn(charge, 'amount_refunded')) throw new Error('Payment charge unavailable.');
    if (typeof charge.amount_refunded === 'number' && charge.amount_refunded > 0) return { status: 'refunded', chargeId };
    if (charge.disputed === true) {
      const disputes = await this.get('/v1/disputes', { charge: chargeId, limit: '100' });
      if (disputes.has_more === true || !list(disputes).length || list(disputes).some(item => !['won', 'warning_closed'].includes(str(item.status)))) return { status: 'disputed', chargeId };
    }
    return { status: 'paid', chargeId };
  }
  async session(sessionId: string): Promise<CommerceProjection> {
    const session = await this.get(`/v1/checkout/sessions/${resource('cs', sessionId)}`);
    const attempt = await this.repo.attemptById(metadataAttempt(session));
    if (!attempt) return {}; // Unrelated Stripe activity cannot become a guide purchase.
    if ((attempt.sessionId && attempt.sessionId !== session.id) || id(session.customer) !== attempt.customerId || session.client_reference_id !== attempt.userId || session.currency !== attempt.currency.toLowerCase() || session.amount_total !== attempt.amount || session.mode !== (attempt.kind === 'guide' ? 'payment' : 'subscription')) throw new Error('Checkout identity or price mismatch.');
    if (attempt.kind === 'membership') return id(session.subscription) ? this.subscription(id(session.subscription)) : {};
    const paymentIntentId = id(session.payment_intent) || null;
    const payment = await this.paymentState(paymentIntentId ?? '');
    const status = session.status === 'expired' ? 'cancelled' : session.payment_status === 'paid' && session.status === 'complete' ? payment.status : payment.status === 'failed' ? 'failed' : 'pending';
    return { order: { id: attempt.id, userId: attempt.userId, productId: attempt.productId!, editionId: attempt.editionId!, status, currency: attempt.currency, amount: attempt.amount, sessionId: session.id, paymentIntentId, chargeId: payment.chargeId, createdAt: attempt.createdAt, updatedAt: this.now.toISOString() } };
  }
  async subscription(subscriptionId: string, invoiceId?: string): Promise<CommerceProjection> {
    const subscription = await this.get(`/v1/subscriptions/${resource('sub', subscriptionId)}`);
    const attempt = await this.repo.attemptById(metadataAttempt(subscription));
    if (!attempt || attempt.kind !== 'membership') return {};
    if (id(subscription.customer) !== attempt.customerId) throw new Error('Subscription identity mismatch.');
    const items = list(subscription.items);
    const price = object(items[0]?.price);
    if (items.length !== 1 || items[0].quantity !== 1 || price.unit_amount !== attempt.amount || price.currency !== attempt.currency.toLowerCase() || object(price.recurring).interval !== 'month' || object(price.recurring).interval_count !== 1) throw new Error('Subscription price mismatch.');
    let currentSubscription = subscription;
    const storedSubscriptionId = await this.repo.membershipSubscription(attempt.userId);
    if (storedSubscriptionId && storedSubscriptionId !== subscriptionId) {
      const stored = await this.get(`/v1/subscriptions/${resource('sub', storedSubscriptionId)}`);
      if (id(stored.customer) !== attempt.customerId || typeof stored.created !== 'number' || typeof subscription.created !== 'number') throw new Error('Subscription chronology unavailable.');
      if (stored.created > subscription.created) currentSubscription = stored;
    }
    // A late event for an old subscription can change its own invoice window,
    // but must not replace the current billing identity or cancellation state.
    const result: CommerceProjection = { subscription: { userId: attempt.userId, subscriptionId: currentSubscription.id, customerId: attempt.customerId, state: str(currentSubscription.status), cancelAtPeriodEnd: currentSubscription.cancel_at_period_end === true || currentSubscription.status === 'canceled' } };
    const targetInvoice = invoiceId || id(subscription.latest_invoice);
    if (!targetInvoice) return result;
    const invoice = await this.get(`/v1/invoices/${resource('in', targetInvoice)}`, { 'expand[]': 'payments' });
    const invoiceSubscription = id(object(object(invoice.parent).subscription_details).subscription);
    if (id(invoice.customer) !== attempt.customerId || invoiceSubscription !== subscriptionId || invoice.currency !== attempt.currency.toLowerCase()) throw new Error('Invoice identity mismatch.');
    const rows = list(invoice.lines);
    if (object(invoice.lines).has_more === true || rows.length !== 1 || rows[0].amount !== attempt.amount || rows[0].quantity !== 1) throw new Error('Unsupported membership invoice.');
    const paidThrough = iso(object(rows[0].period).end);
    const payments = list(invoice.payments);
    if (object(invoice.payments).has_more === true || payments.length > 1) throw new Error('Unsupported multiple invoice payments.');
    const paymentIntentId = id(object(payments[0]?.payment).payment_intent) || null;
    const payment = await this.paymentState(paymentIntentId ?? '');
    const status = invoice.status === 'paid' && invoice.amount_paid === attempt.amount && paidThrough ? payment.status : invoice.status === 'void' || invoice.status === 'uncollectible' ? 'failed' : 'pending';
    result.invoice = { invoiceId: invoice.id, userId: attempt.userId, subscriptionId, chargeId: payment.chargeId, paymentIntentId, status, paidThrough, updatedAt: this.now.toISOString() };
    return result;
  }
  async event(event: StripeEvent): Promise<CommerceProjection> {
    const eventObject = event.data.object;
    if (/^checkout\.session\.(completed|async_payment_succeeded|async_payment_failed|expired)$/.test(event.type)) return this.session(eventObject.id);
    if (/^customer\.subscription\.(created|updated|deleted)$/.test(event.type)) return this.subscription(eventObject.id);
    if (/^invoice\.(paid|payment_failed|voided|marked_uncollectible)$/.test(event.type)) {
      const invoice = await this.get(`/v1/invoices/${resource('in', eventObject.id)}`);
      const subscriptionId = id(object(object(invoice.parent).subscription_details).subscription);
      return subscriptionId ? this.subscription(subscriptionId, invoice.id) : {};
    }
    if (event.type === 'charge.refunded' || /^charge\.dispute\.(created|updated|closed|funds_withdrawn|funds_reinstated)$/.test(event.type) || /^refund\.(created|updated|failed)$/.test(event.type)) {
      const chargeId = event.type === 'charge.refunded' ? eventObject.id : id(eventObject.charge);
      if (!chargeId) return {};
      const order = await this.repo.orderByCharge(chargeId);
      if (order) return this.session(order.sessionId);
      const existing = await this.repo.invoiceByCharge(chargeId);
      if (existing) {
        const invoice = await this.get(`/v1/invoices/${resource('in', existing.invoiceId)}`);
        return this.subscription(id(object(object(invoice.parent).subscription_details).subscription), invoice.id);
      }
      // Out-of-order charge events may precede our invoice receipt. The later
      // invoice/session event retrieves the refunded/disputed charge itself.
    }
    return {};
  }
}

export function createCommerceHandlers(deps: CommerceDependencies) {
  const json = (value: unknown, status = 200) => Response.json(value, { status, headers: ACCOUNT_PRIVATE_HEADERS });
  const now = () => deps.now?.() ?? new Date();
  const uuid = () => deps.uuid?.() ?? crypto.randomUUID();
  const user = async () => { try { return await deps.getUser(); } catch { return null; } };
  const settings = () => {
    const config = deps.config(); const origin = new URL(config.origin);
    const secureOrLoopback = origin.protocol === 'https:' || origin.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(origin.hostname);
    if (!config.enabled || config.mode !== 'sandbox' || !secureOrLoopback || origin.origin !== config.origin) throw new Error('Checkout not configured.');
    return config;
  };
  return {
    async checkout(request: Request) {
      const identity = await user(); if (!identity) return json({ error: 'Sign in to get a guide.' }, 401);
      if (!sameOriginMutation(request)) return json({ error: 'Request origin rejected.' }, 403);
      if (new URL(request.url).search || !request.headers.get('content-type')?.startsWith('application/json')) return json({ error: 'Send a guide selection as JSON.' }, 400);
      const requestKey = request.headers.get('idempotency-key') ?? '';
      if (!/^[a-f0-9-]{36}$/i.test(requestKey)) return json({ error: 'A valid checkout request key is required.' }, 400);
      let input: { kind?: unknown; productId?: unknown };
      try { const raw = await request.text(); if (raw.length > 1024) return json({ error: 'Checkout selection is too large.' }, 413); input = JSON.parse(raw); if (!input || Array.isArray(input) || Object.keys(input).some(key => !['kind', 'productId'].includes(key))) throw new Error(); } catch { return json({ error: 'Choose a valid guide offer.' }, 400); }
      if (!['guide', 'membership'].includes(String(input.kind)) || (input.kind === 'membership' && input.productId !== undefined) || (input.kind === 'guide' && typeof input.productId !== 'string')) return json({ error: 'Choose a valid guide offer.' }, 400);
      let checkoutRepo: CommerceRepository | undefined; let lockOwner: string | undefined;
      try {
        const config = settings(); const at = now(); const repo = deps.repository(); const stripe = deps.stripe();
        checkoutRepo = repo; const owner = uuid();
        if (!await repo.acquireEventLock(owner, at.getTime())) return json({ error: 'Checkout is busy. Please retry.' }, 503);
        lockOwner = owner;
        const library = await deps.guides().readLibrary(identity.userId, at.toISOString());
        let product: CommerceProduct | undefined; let edition: GuideEdition | undefined;
        if (input.kind === 'guide') {
          product = deps.getProduct(input.productId as string);
          if (!product || product.priceMinor !== 4900 || product.currency !== 'USD') return json({ error: 'This guide is not available for checkout.' }, 409);
          edition = (await repo.readEditions(product.id)).filter(item => approvedGuideEdition(product, item, at)).sort((a, b) => b.version.localeCompare(a.version, 'en', { numeric: true }) || (b.updatedAt ?? '').localeCompare(a.updatedAt ?? ''))[0];
          if (!edition) return json({ error: 'This guide is in development and is not available for purchase.' }, 409);
          if (library.orders.some(order => order.userId === identity.userId && order.productId === product!.id && order.status === 'paid') || product.subscriptionIncluded && activeGuideMembership(library.membership, identity.userId, at)) return json({ error: 'This guide is already available in your library.', libraryUrl: '/guides/library' }, 409);
        } else {
          if (!deps.offer.enabled || deps.offer.monthlyMinor !== 5900 || deps.offer.currency !== 'USD' || deps.offer.launchProductIds.length < 3 || new Set(deps.offer.launchProductIds).size < 3 || deps.offer.launchMinimum < 3) return json({ error: 'Membership opens after the first three topic guides are released.' }, 409);
          for (const productId of deps.offer.launchProductIds) if (!(await repo.readEditions(productId)).some(item => approvedGuideEdition(deps.getProduct(productId), item, at))) return json({ error: 'Membership is not yet available.' }, 409);
          if (activeGuideMembership(library.membership, identity.userId, at)) return json({ error: 'You already have an active membership. Manage it in billing.', libraryUrl: '/guides/library' }, 409);
        }
        let existing = await repo.attempt(identity.userId, requestKey);
        if (existing && (existing.kind !== input.kind || existing.productId !== (product?.id ?? null))) return json({ error: 'This request key was already used for another offer.' }, 409);
        if (existing?.sessionUrl) return json({ url: hostedUrl(existing.sessionUrl, 'checkout.stripe.com') });
        if (input.kind === 'membership' && !existing) {
          const subscriptionId = await repo.membershipSubscription(identity.userId);
          if (subscriptionId) {
            const subscription = await stripe.request(`/v1/subscriptions/${resource('sub', subscriptionId)}`);
            if (!['canceled', 'incomplete_expired'].includes(str(subscription.status))) return json({ error: 'This account already has a membership billing record. Use billing to manage or complete it.' }, 409);
          }
          const previous = await repo.membershipCheckout(identity.userId);
          let previousSessionId = previous?.sessionId;
          if (previous && !previousSessionId) {
            // A provider success followed by a local crash must not create a
            // second subscription after the browser generates a new key.
            const sessions = await stripe.request('/v1/checkout/sessions', { customer: previous.customerId, limit: '100' });
            const recovered = list(sessions).find(session => metadataAttempt(session) === previous.id);
            if (recovered) {
              previousSessionId = recovered.id;
              if (recovered.url) await repo.attachSession(previous.id, recovered.id, hostedUrl(recovered.url, 'checkout.stripe.com'));
            } else {
              if (sessions.has_more === true) throw new Error('Checkout recovery needs a complete provider history.');
              existing = previous;
            }
          }
          if (previousSessionId) {
            const session = await stripe.request(`/v1/checkout/sessions/${resource('cs', previousSessionId)}`);
            if (session.status === 'open' && session.url) return json({ url: hostedUrl(session.url, 'checkout.stripe.com') });
            if (session.status !== 'expired') {
              const subscription = id(session.subscription) ? await stripe.request(`/v1/subscriptions/${resource('sub', id(session.subscription))}`) : null;
              if (!subscription || !['canceled', 'incomplete_expired'].includes(str(subscription.status))) return json({ error: 'A membership checkout or payment is already in progress. Return to your existing checkout or manage billing.' }, 409);
            }
          }
        }
        let customer = await repo.customer(identity.userId);
        if (!customer) {
          const customerObject = await stripe.request('/v1/customers', { 'metadata[remaprx_account]': identity.userId }, 'POST', `remaprx-customer-${identity.userId}`);
          customer = await repo.saveCustomer(identity.userId, resource('cus', customerObject.id));
        }
        existing ??= await repo.createAttempt({ id: uuid(), userId: identity.userId, requestKey, kind: input.kind as 'guide' | 'membership', productId: product?.id ?? null, editionId: edition?.id ?? null, amount: product?.priceMinor ?? deps.offer.monthlyMinor, currency: 'USD', customerId: customer, sessionId: null, sessionUrl: null, createdAt: at.toISOString() });
        const params: Record<string, string> = {
          mode: existing.kind === 'guide' ? 'payment' : 'subscription', customer: existing.customerId, client_reference_id: identity.userId,
          success_url: config.origin + '/guides/library?checkout=returned', cancel_url: config.origin + '/guides/library?checkout=canceled',
          'metadata[remaprx_attempt]': existing.id, 'line_items[0][quantity]': '1', 'line_items[0][price_data][currency]': 'usd',
          'line_items[0][price_data][unit_amount]': String(existing.amount), 'line_items[0][price_data][product_data][name]': product?.title ?? 'RemapRx membership',
          integration_identifier: 'remaprx_guides_qnvdmtrp',
        };
        if (existing.kind === 'membership') { params['line_items[0][price_data][recurring][interval]'] = 'month'; params['subscription_data[metadata][remaprx_attempt]'] = existing.id; }
        const session = await stripe.request('/v1/checkout/sessions', params, 'POST', 'remaprx-checkout-' + existing.id);
        const url = hostedUrl(session.url, 'checkout.stripe.com');
        await repo.attachSession(existing.id, session.id, url);
        return json({ url });
      } catch { return json({ error: 'Checkout is not available yet. No guide access has been changed.' }, 503); }
      finally { if (checkoutRepo && lockOwner) await checkoutRepo.releaseEventLock(lockOwner).catch(() => {}); }
    },
    async portal(request: Request) {
      const identity = await user(); if (!identity) return json({ error: 'Sign in to manage billing.' }, 401);
      if (!sameOriginMutation(request)) return json({ error: 'Request origin rejected.' }, 403);
      if (new URL(request.url).search || (await request.text()).trim()) return json({ error: 'Billing always uses your signed-in account.' }, 400);
      try {
        const config = settings(); const customer = await deps.repository().customer(identity.userId);
        if (!customer) return json({ error: 'This account does not have a billing profile yet.' }, 404);
        const session = await deps.stripe().request('/v1/billing_portal/sessions', { customer, return_url: config.origin + '/guides/library' }, 'POST');
        return json({ url: hostedUrl(session.url, 'billing.stripe.com') });
      } catch { return json({ error: 'Billing is temporarily unavailable. Please retry.' }, 503); }
    },
    async webhook(request: Request) {
      let event: StripeEvent; const at = now();
      try { const config = settings(); event = await verifyStripeEvent(await request.text(), request.headers.get('stripe-signature'), config.webhookSecret, at); } catch { return json({ error: 'Webhook verification failed.' }, 400); }
      let repo: CommerceRepository | undefined; const owner = uuid(); let locked = false;
      try {
        repo = deps.repository();
        locked = await repo.acquireEventLock(owner, at.getTime());
        if (!locked) return json({ error: 'Reconciliation is busy; retry this event.' }, 503);
        if (await repo.hasEvent(event.id)) {
          const userId = await repo.eventUser(event.id);
          if (userId) await deps.reconcileLibrary?.(userId);
          return json({ received: true, duplicate: true });
        }
        const projection = await new GuidePaymentReconciler(repo, deps.stripe(), at).event(event);
        await repo.applyEvent(event, projection, owner, now());
        const userId = projection.order?.userId ?? projection.subscription?.userId;
        if (userId) await deps.reconcileLibrary?.(userId);
        return json({ received: true });
      } catch { return json({ error: 'Payment reconciliation was not confirmed. Retry this event.' }, 503); }
      finally { if (locked && repo) await repo.releaseEventLock(owner).catch(() => {}); }
    },
  };
}
