-- Additive migration: v1 role intake and existing completion dates remain valid.
ALTER TABLE reader_profiles ADD COLUMN interests_json TEXT NOT NULL DEFAULT '[]';
--> statement-breakpoint
CREATE TABLE guide_saved_entries (
  user_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  addition_reason TEXT NOT NULL CHECK (addition_reason IN ('manual', 'interest', 'purchase')),
  added_at TEXT NOT NULL,
  last_viewed_edition_id TEXT,
  removed_at TEXT,
  PRIMARY KEY (user_id, product_id)
);
