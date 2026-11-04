-- Bind a commerce database to exactly one Stripe account and environment.
-- Never copy sandbox entitlements into a production database.
CREATE TABLE IF NOT EXISTS guide_commerce_environment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  stripe_account_id TEXT NOT NULL,
  mode TEXT NOT NULL CHECK (mode IN ('sandbox', 'live'))
);
