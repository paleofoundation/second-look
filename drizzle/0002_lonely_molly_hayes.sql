CREATE TABLE `guide_editions` (
	`id` text PRIMARY KEY NOT NULL,
	`product_id` text NOT NULL,
	`version` text NOT NULL,
	`release_state` text DEFAULT 'pending' NOT NULL,
	`pdf_asset_key` text,
	`pdf_sha256` text,
	`summary_asset_key` text,
	`summary_sha256` text,
	`approved_version` text,
	`approved_pdf_sha256` text,
	`approved_summary_sha256` text,
	`human_editorial_approved` integer DEFAULT false NOT NULL,
	`approved_by` text,
	`approved_at` text,
	`qualified_review_required` integer DEFAULT true NOT NULL,
	`qualified_review_approved` integer DEFAULT false NOT NULL,
	`qualified_reviewed_by` text,
	`qualified_reviewer_qualifications` text,
	`qualified_reviewer_conflicts` text,
	`qualified_reviewed_at` text,
	`marketing_sha256` text,
	`approved_marketing_sha256` text,
	`qualified_review_scope` text,
	`qualified_review_decision` text,
	`qualified_approved_version` text,
	`qualified_approved_pdf_sha256` text,
	`qualified_approved_summary_sha256` text,
	`qualified_approved_marketing_sha256` text,
	`legal_review_approved` integer DEFAULT false NOT NULL,
	`legal_reviewed_by` text,
	`legal_reviewer_qualifications` text,
	`legal_review_scope` text,
	`legal_review_conflicts` text,
	`legal_jurisdiction` text,
	`legal_reviewed_at` text,
	`legal_review_decision` text,
	`legal_approved_version` text,
	`legal_approved_pdf_sha256` text,
	`legal_approved_summary_sha256` text,
	`legal_approved_marketing_sha256` text
);
--> statement-breakpoint
CREATE TABLE `guide_memberships` (
	`user_id` text PRIMARY KEY NOT NULL,
	`state` text DEFAULT 'inactive' NOT NULL,
	`current_period_end` text
);
--> statement-breakpoint
CREATE TABLE `guide_orders` (
	`id` text PRIMARY KEY NOT NULL,
	`user_id` text NOT NULL,
	`product_id` text NOT NULL,
	`edition_id` text NOT NULL,
	`status` text DEFAULT 'pending' NOT NULL,
	`currency` text NOT NULL,
	`total_minor` integer NOT NULL,
	`created_at` text NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `idx_guide_orders_user_updated` ON `guide_orders` (`user_id`,`updated_at`);--> statement-breakpoint
CREATE INDEX `idx_guide_orders_user_product_edition` ON `guide_orders` (`user_id`,`product_id`,`edition_id`);