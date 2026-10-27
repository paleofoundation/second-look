# Guide commerce and protected delivery

Implementation record: October 12, 2026. This implements the owner's metformin-first product policy in a disabled, sandbox-only payment integration. No merchant account, sandbox key, webhook endpoint, transaction or clinical/legal approval was created by this work. Fixture checks are not payment-provider acceptance.

## Offers, identity and access

The authoritative catalog sets a topic purchase at $49 USD and monthly membership at $59 USD. Checkout additionally rejects different amounts and currencies. The request carries only `{kind:"guide",productId}` or `{kind:"membership"}` plus an `Idempotency-Key` UUID; the authenticated server supplies account, amount, edition, customer, return URLs and Stripe metadata. Unknown fields, cross-origin mutations, arbitrary return URLs and account parameters are rejected. The success page does not grant rights.

Membership checkout requires the enabled offer and approved editions for all configured launch products (Metformin, Long COVID and itraconazole), with a minimum of three. Each exact edition must have the human, qualified clinical and legal approvals required by its product. No unavailable product can reach checkout. Roles and interests confer no payment privileges.

A successfully paid order owns the **topic product**, including all future approved editions; its original edition remains in purchase history. Refunds remove that order's rights, disputes suspend them until the provider records a favorable closure, and independent valid orders remain effective. For this conservative initial policy, a partial refund also suspends the affected order/paid invoice; a reviewed partial-refund retention policy would need an explicit change before live launch.

Membership access comes from successful, unrefunded, undisputed invoice payments and their paid-through dates, never merely an `active` subscription label. Pending first payments grant no access. Cancellation, scheduled nonrenewal and a failed next invoice preserve previously paid access until its exact expiry. Refunding an older invoice does not erase a newer paid window. Expiry never removes separately purchased topic rights. Already downloaded files remain on the reader's device.

## Endpoints and private files

- `POST /api/checkout`: authenticated hosted Checkout creation; stable UUID request key makes retries return the existing session.
- `POST /api/billing/portal`: authenticated hosted portal for the server-bound Stripe customer; empty body required.
- `POST /api/stripe/webhook`: raw-body signature verification followed by authoritative provider reconciliation.
- `GET /api/guides/:editionId/reader`: entitled, approved, SHA-256-verified JSON manuscript only.
- `GET /api/guides/:editionId/download[?format=summary]`: entitled exact approved PDF or summary; hash and PDF signature verified.

All account and delivery responses use `Cache-Control: private, no-store, max-age=0`, account-aware `Vary` and `nosniff`. Paid assets are R2 object keys, not public/static URLs. `lib/guide-manuscript.ts` accepts plain structured text, tables, questions, citation IDs and HTTPS references; no manuscript HTML is executed. Its identity, edition and version must match the approval record. Unapproved/malformed/hash-mismatched or wrong-account content fails closed. The schema is public code; paid manuscript data is never imported into the client bundle.

Edition approval now includes `web_asset_key`, `web_sha256`, and exact human/clinical/legal approved web hashes alongside the PDF, summary and marketing hashes. Existing records are preserved with new fields null; they do not silently acquire new web approval. `updated_at` and `change_summary` feed private library edition notices.

## Provider event handling

`StripeClient` is an instance-scoped fetch client for Workers, pinned to **2026-09-30.endive**, the current version checked on October 12. It sends dynamic payment methods by omitting a method allowlist, uses hosted session URLs on Stripe's exact domains, and includes the supported `integration_identifier` parameter. The first release rejects live keys. There is no custom card form or card storage.

The webhook checks HMAC SHA-256 over the untouched body, all `v1` signatures, a five-minute timestamp tolerance and `livemode:false`. The configured endpoint must deliver **snapshot events** using the pinned API version. Subscribe to:

- `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed`, `checkout.session.expired`;
- `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`;
- `invoice.paid`, `invoice.payment_failed`, `invoice.voided`, `invoice.marked_uncollectible`;
- `charge.refunded`, `charge.dispute.created`, `charge.dispute.updated`, `charge.dispute.closed`, `charge.dispute.funds_withdrawn`, `charge.dispute.funds_reinstated`;
- `refund.created`, `refund.updated`, `refund.failed`.

Events re-fetch the current Checkout Session, PaymentIntent/latest charge, dispute, subscription or invoice instead of trusting event order. Checkout metadata is bound to a previously saved server attempt. PaymentIntent success and current charge state are required before fulfillment. Invoice parent/subscription identity, customer, amount, currency, quantity and monthly price are verified. Multi-line, discounted, prorated or multiple-payment invoices are outside this first offer and fail closed; configure the portal for payment-method updates and cancellation, with no plan/quantity changes or promotions. Tax handling is not silently enabled.

The D1 adapter serializes payment reconciliation and Checkout creation with a two-minute fenced lock. Stripe requests time out after eight seconds. Lost locks cannot commit; event receipt and entitlement changes commit in one database batch. Duplicate event IDs return success without repeated fulfillment. Busy/failed reconciliation returns 503 for provider retry. Pending or existing nonterminal subscriptions are checked before another membership checkout. If Stripe created a session before a local attachment failure, the server recovers the prior attempt from Stripe’s customer sessions and resumes it. A late event for an older subscription cannot replace the newer billing identity or cancellation flag. This conservative lock is suitable for the initial low-volume release; move to a durable per-account queue before higher throughput, retaining the same fencing/idempotency guarantees.

The invoice ledger retains separate payment windows. A charge event arriving before its initial session/invoice event cannot grant access; later reconciliation sees the current refund/dispute. A recovered or out-of-order paid event likewise cannot revive refunded access. No webhook enrolls a reader in marketing or downloads a file to their device. After a verified order or subscription update commits, matching released topics are reconciled into the private library immediately. If library reconciliation fails, the webhook returns 503; its durable account-bound event receipt lets duplicate delivery retry the idempotent library step without repeating payment fulfillment. Newly released guides also reconcile on the next authenticated library read.

## Configuration and launch handoff

Apply the additive `drizzle/0011_guide_commerce.sql` migration, preserving existing profiles, orders and edition history. Configure an **isolated Stripe sandbox** through the host's secret mechanism, not Git or the browser:

| Name | Purpose |
|---|---|
| `STRIPE_SANDBOX_ID` | Explicit environment inventory identifier |
| `STRIPE_SANDBOX_KEY` | Prefer a restricted `rk_test_…` key scoped to the required customer/session/portal/read operations |
| `STRIPE_WEBHOOK_SECRET` | Sandbox endpoint signing secret |
| `GUIDE_CHECKOUT_SANDBOX_ENABLED` | Literal `true`, only on an isolated test deployment/database/bucket |
| `GUIDE_COMMERCE_ORIGIN` | HTTPS origin for the isolated test deployment; HTTP is accepted only for sandbox loopback hosts (`localhost`, `127.0.0.1`, `[::1]`) |

Use isolated synthetic products/editions and approval fixtures only in that test environment. Never mark production metformin or other guides approved to test billing. Test hosted successful, delayed, declined, refunded and disputed transactions, signed redelivery and cancellation/renewal with a Stripe test clock. Record actual provider IDs without secrets and verify account-library delivery before accepting this adapter against Stripe.

Live activation is deliberately unavailable in this code revision. It requires the actual merchant identity, tax jurisdiction/registrations and configuration, refund/consumer terms, support contacts, released clinical content, exact editorial/clinical/legal approvals, isolated provider acceptance results, reviewed live configuration and deployment verification. Do not reinterpret a successful build or synthetic test as fulfilling these dependencies.

## Verification

`node scripts/check-guide-commerce.mjs` passes with an in-memory SQLite database using the actual additive migrations and real HMAC signatures. It covers price/release/authentication gates; idempotent Checkout retries; failed, pending and successful payment states; duplicate/out-of-order events; refund/dispute reversal; renewal, cancellation and expiry; newer invoice protection after an older refund; future-edition ownership; account isolation; manuscript schema/citation closure; file hash verification; private response headers; lost-session recovery; preservation of newer subscription identity; immediate/retried library reconciliation; and same-origin loopback testing. `npx tsc --noEmit` also passed after implementation. No actual Stripe sandbox transaction has been executed; hosted UI, provider shapes and portal configuration remain acceptance work once an isolated environment is available.

Primary implementation references checked October 12: [fulfillment](https://docs.stripe.com/checkout/fulfillment), [webhook verification and ordering](https://docs.stripe.com/webhooks), [API version](https://docs.stripe.com/api/versioning), [Endive changes](https://docs.stripe.com/changelog/endive), [Checkout create](https://docs.stripe.com/api/checkout/sessions/create), [integration identifier](https://docs.stripe.com/changelog/dahlia/2026-03-25/adds-integration-identifier-parameter-to-checkout-sessions), [invoice payments](https://docs.stripe.com/api/invoice-payment/list), [subscription object](https://docs.stripe.com/api/subscriptions/object), and [dispute filtering](https://docs.stripe.com/api/disputes/list).
