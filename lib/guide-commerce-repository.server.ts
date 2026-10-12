import 'server-only';
import type { CheckoutAttempt, CommerceProjection, CommerceRepository } from './guide-commerce';
import { guideEditionFromRecord, type EditionRecord } from './guide-repository.server';
import type { StripeEvent } from './stripe-client';
type Result<T> = { success: boolean; results?: T[] };
type Statement = { bind(...values: unknown[]): Statement; all<T>(): Promise<Result<T>> };
export type CommerceDatabase = { prepare(sql: string): Statement; batch(statements: Statement[]): Promise<Result<unknown>[]> };
type AttemptRow = { id: string; user_id: string; request_key: string; kind: 'guide' | 'membership'; product_id: string | null; edition_id: string | null; amount: number; currency: string; customer_id: string; session_id: string | null; session_url: string | null; created_at: string };
const attemptFromRow = (row: AttemptRow): CheckoutAttempt => ({ id: row.id, userId: row.user_id, requestKey: row.request_key, kind: row.kind, productId: row.product_id, editionId: row.edition_id, amount: row.amount, currency: row.currency, customerId: row.customer_id, sessionId: row.session_id, sessionUrl: row.session_url, createdAt: row.created_at });
export function createCommerceRepository(db: CommerceDatabase): CommerceRepository {
  const statement = (sql: string, ...values: unknown[]) => db.prepare(sql).bind(...values);
  async function query<T>(sql: string, ...values: unknown[]): Promise<T[]> { const result = await statement(sql, ...values).all<T>(); if (!result.success) throw new Error('Commerce storage unavailable.'); return result.results ?? []; }
  async function first<T>(sql: string, ...values: unknown[]): Promise<T | null> { return (await query<T>(sql, ...values))[0] ?? null; }
  return {
    async readEditions(productId) { return (await query<EditionRecord>('SELECT * FROM guide_editions WHERE product_id = ?', productId)).map(guideEditionFromRecord); },
    async customer(userId) { return (await first<{ stripe_customer_id: string }>('SELECT stripe_customer_id FROM guide_customers WHERE user_id = ?', userId))?.stripe_customer_id ?? null; },
    async saveCustomer(userId, customerId) {
      await query('INSERT INTO guide_customers(user_id, stripe_customer_id) VALUES (?, ?) ON CONFLICT(user_id) DO NOTHING', userId, customerId);
      const row = await first<{ stripe_customer_id: string }>('SELECT stripe_customer_id FROM guide_customers WHERE user_id = ?', userId);
      if (!row) throw new Error('Customer association unavailable.'); return row.stripe_customer_id;
    },
    async userForCustomer(customerId) { return (await first<{ user_id: string }>('SELECT user_id FROM guide_customers WHERE stripe_customer_id = ?', customerId))?.user_id ?? null; },
    async attempt(userId, key) { const row = await first<AttemptRow>('SELECT * FROM guide_checkout_attempts WHERE user_id = ? AND request_key = ?', userId, key); return row ? attemptFromRow(row) : null; },
    async membershipCheckout(userId) { const row = await first<AttemptRow>("SELECT * FROM guide_checkout_attempts WHERE user_id=? AND kind='membership' ORDER BY created_at DESC LIMIT 1", userId); return row ? attemptFromRow(row) : null; },
    async membershipSubscription(userId) { return (await first<{ stripe_subscription_id: string }>('SELECT stripe_subscription_id FROM guide_memberships WHERE user_id=?', userId))?.stripe_subscription_id ?? null; },
    async attemptById(id) { const row = await first<AttemptRow>('SELECT * FROM guide_checkout_attempts WHERE id = ?', id); return row ? attemptFromRow(row) : null; },
    async createAttempt(attempt) {
      await query('INSERT INTO guide_checkout_attempts(id,user_id,request_key,kind,product_id,edition_id,amount,currency,customer_id,created_at) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(user_id,request_key) DO NOTHING', attempt.id, attempt.userId, attempt.requestKey, attempt.kind, attempt.productId, attempt.editionId, attempt.amount, attempt.currency, attempt.customerId, attempt.createdAt);
      const row = await first<AttemptRow>('SELECT * FROM guide_checkout_attempts WHERE user_id=? AND request_key=?', attempt.userId, attempt.requestKey);
      if (!row || row.kind !== attempt.kind || row.product_id !== attempt.productId) throw new Error('Checkout request conflict.'); return attemptFromRow(row);
    },
    async attachSession(id, sessionId, url) { await query('UPDATE guide_checkout_attempts SET session_id=?,session_url=? WHERE id=? AND (session_id IS NULL OR session_id=?)', sessionId, url, id, sessionId); },
    async orderByCharge(chargeId) { const row = await first<{ stripe_session_id: string }>('SELECT stripe_session_id FROM guide_orders WHERE charge_id=?', chargeId); return row ? { sessionId: row.stripe_session_id } : null; },
    async invoiceByCharge(chargeId) { const row = await first<{ invoice_id: string }>('SELECT invoice_id FROM guide_invoice_payments WHERE charge_id=?', chargeId); return row ? { invoiceId: row.invoice_id } : null; },
    async acquireEventLock(owner, now) { return (await query("INSERT INTO guide_commerce_locks(name,owner,expires_at) VALUES('stripe',?,?) ON CONFLICT(name) DO UPDATE SET owner=excluded.owner,expires_at=excluded.expires_at WHERE guide_commerce_locks.expires_at < ? RETURNING owner", owner, now + 120000, now)).length === 1; },
    async releaseEventLock(owner) { await query("DELETE FROM guide_commerce_locks WHERE name='stripe' AND owner=?", owner); },
    async hasEvent(id) { return !!await first('SELECT id FROM guide_stripe_events WHERE id=?', id); },
    async applyEvent(event: StripeEvent, projection: CommerceProjection, owner: string, now: Date) {
      const statements: Statement[] = [];
      const fence = "EXISTS(SELECT 1 FROM guide_commerce_locks WHERE name='stripe' AND owner=? AND expires_at>?)";
      const end = [owner, now.getTime()];
      if (projection.order) {
        const o = projection.order;
        statements.push(statement(`INSERT INTO guide_orders(id,user_id,product_id,edition_id,status,currency,total_minor,created_at,updated_at,stripe_session_id,payment_intent_id,charge_id) SELECT ?,?,?,?,?,?,?,?,?,?,?,? WHERE ${fence} ON CONFLICT(id) DO UPDATE SET status=excluded.status,updated_at=excluded.updated_at,payment_intent_id=excluded.payment_intent_id,charge_id=excluded.charge_id`, o.id,o.userId,o.productId,o.editionId,o.status,o.currency,o.amount,o.createdAt,o.updatedAt,o.sessionId,o.paymentIntentId,o.chargeId,...end));
      }
      if (projection.invoice) {
        const i = projection.invoice;
        statements.push(statement(`INSERT INTO guide_invoice_payments(invoice_id,user_id,subscription_id,charge_id,payment_intent_id,status,paid_through,updated_at) SELECT ?,?,?,?,?,?,?,? WHERE ${fence} ON CONFLICT(invoice_id) DO UPDATE SET charge_id=excluded.charge_id,payment_intent_id=excluded.payment_intent_id,status=excluded.status,paid_through=excluded.paid_through,updated_at=excluded.updated_at`, i.invoiceId,i.userId,i.subscriptionId,i.chargeId,i.paymentIntentId,i.status,i.paidThrough,i.updatedAt,...end));
      }
      if (projection.subscription) {
        const m = projection.subscription;
        // Paid invoice windows, rather than subscription.status, grant access.
        // A failed renewal/cancellation cannot erase an already-paid window.
        const paidEnd = "(SELECT MAX(paid_through) FROM guide_invoice_payments WHERE user_id=? AND status='paid')";
        statements.push(statement(`INSERT INTO guide_memberships(user_id,state,current_period_end,cancel_at_period_end,stripe_subscription_id,stripe_customer_id) SELECT ?,CASE WHEN ${paidEnd}>? THEN 'active' ELSE ? END,${paidEnd},?,?,? WHERE ${fence} ON CONFLICT(user_id) DO UPDATE SET state=excluded.state,current_period_end=excluded.current_period_end,cancel_at_period_end=excluded.cancel_at_period_end,stripe_subscription_id=excluded.stripe_subscription_id,stripe_customer_id=excluded.stripe_customer_id`, m.userId,m.userId,now.toISOString(),projection.invoice?.status === 'refunded' ? 'refunded' : projection.invoice?.status === 'disputed' ? 'disputed' : m.state === 'past_due' ? 'past_due' : m.state === 'canceled' ? 'cancelled' : 'pending',m.userId,Number(m.cancelAtPeriodEnd),m.subscriptionId,m.customerId,...end));
      }
      statements.push(statement(`INSERT INTO guide_stripe_events(id,type,processed_at) SELECT ?,?,? WHERE ${fence} ON CONFLICT(id) DO NOTHING`, event.id,event.type,now.toISOString(),...end));
      const results = await db.batch(statements);
      if (results.some(result => !result.success) || !await first('SELECT id FROM guide_stripe_events WHERE id=?', event.id)) throw new Error('Payment transaction was not committed.');
    },
  };
}
