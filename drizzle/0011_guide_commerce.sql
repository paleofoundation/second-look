ALTER TABLE guide_editions ADD web_asset_key text;
--> statement-breakpoint
ALTER TABLE guide_editions ADD web_sha256 text;
--> statement-breakpoint
ALTER TABLE guide_editions ADD approved_web_sha256 text;
--> statement-breakpoint
ALTER TABLE guide_editions ADD qualified_approved_web_sha256 text;
--> statement-breakpoint
ALTER TABLE guide_editions ADD legal_approved_web_sha256 text;
--> statement-breakpoint
ALTER TABLE guide_editions ADD updated_at text;
--> statement-breakpoint
ALTER TABLE guide_editions ADD change_summary text;
--> statement-breakpoint
ALTER TABLE guide_orders ADD stripe_session_id text;
--> statement-breakpoint
ALTER TABLE guide_orders ADD payment_intent_id text;
--> statement-breakpoint
ALTER TABLE guide_orders ADD charge_id text;
--> statement-breakpoint
CREATE UNIQUE INDEX idx_guide_orders_session ON guide_orders(stripe_session_id);
--> statement-breakpoint
CREATE INDEX idx_guide_orders_charge ON guide_orders(charge_id);
--> statement-breakpoint
ALTER TABLE guide_memberships ADD stripe_subscription_id text;
--> statement-breakpoint
ALTER TABLE guide_memberships ADD stripe_customer_id text;
--> statement-breakpoint
CREATE TABLE guide_customers (user_id text PRIMARY KEY NOT NULL, stripe_customer_id text NOT NULL UNIQUE);
--> statement-breakpoint
CREATE TABLE guide_checkout_attempts (
  id text PRIMARY KEY NOT NULL, user_id text NOT NULL, request_key text NOT NULL,
  kind text NOT NULL CHECK(kind IN ('guide','membership')), product_id text, edition_id text,
  amount integer NOT NULL, currency text NOT NULL, customer_id text NOT NULL,
  session_id text UNIQUE, session_url text, created_at text NOT NULL,
  UNIQUE(user_id, request_key)
);
--> statement-breakpoint
CREATE TABLE guide_invoice_payments (
  invoice_id text PRIMARY KEY NOT NULL, user_id text NOT NULL, subscription_id text NOT NULL,
  charge_id text, payment_intent_id text, status text NOT NULL, paid_through text, updated_at text NOT NULL
);
--> statement-breakpoint
CREATE INDEX idx_guide_invoice_charge ON guide_invoice_payments(charge_id);
--> statement-breakpoint
CREATE INDEX idx_guide_invoice_user ON guide_invoice_payments(user_id, status, paid_through);
--> statement-breakpoint
CREATE TABLE guide_stripe_events (id text PRIMARY KEY NOT NULL, type text NOT NULL, processed_at text NOT NULL);
--> statement-breakpoint
CREATE TABLE guide_commerce_locks (name text PRIMARY KEY NOT NULL, owner text NOT NULL, expires_at integer NOT NULL);
