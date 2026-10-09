import { sqliteTable, text, integer, primaryKey, index } from 'drizzle-orm/sqlite-core';
export const savedItems=sqliteTable('saved_items',{userId:text('user_id').notNull(),itemId:text('item_id').notNull(),note:text('note').notNull().default(''),updatedAt:text('updated_at').notNull() },t=>[primaryKey({columns:[t.userId,t.itemId]})]);
export const corrections=sqliteTable('corrections',{id:text('id').primaryKey(),userId:text('user_id').notNull(),page:text('page').notNull(),message:text('message').notNull(),createdAt:text('created_at').notNull()});

export const readerProfiles = sqliteTable('reader_profiles', {
  userId: text('user_id').primaryKey(),
  intakeVersion: integer('intake_version').notNull(),
  rolesJson: text('roles_json').notNull(),
  intakeState: text('intake_state').notNull(),
  completedAt: text('completed_at').notNull(),
  updatedAt: text('updated_at').notNull(),
});

// Commerce remains unlaunched. These tables are empty until an authorized,
// verified fulfillment/review process records genuine orders and editions.
export const guideOrders = sqliteTable('guide_orders', {
  id: text('id').primaryKey(),
  userId: text('user_id').notNull(),
  productId: text('product_id').notNull(),
  editionId: text('edition_id').notNull(),
  status: text('status').notNull().default('pending'),
  currency: text('currency').notNull(),
  totalMinor: integer('total_minor').notNull(),
  createdAt: text('created_at').notNull(),
  updatedAt: text('updated_at').notNull(),
}, table => [
  index('idx_guide_orders_user_updated').on(table.userId, table.updatedAt),
  index('idx_guide_orders_user_product_edition').on(table.userId, table.productId, table.editionId),
]);

export const guideMemberships = sqliteTable('guide_memberships', {
  userId: text('user_id').primaryKey(),
  state: text('state').notNull().default('inactive'),
  currentPeriodEnd: text('current_period_end'),
  cancelAtPeriodEnd: integer('cancel_at_period_end', { mode: 'boolean' }).notNull().default(false),
});

export const guideEditions = sqliteTable('guide_editions', {
  id: text('id').primaryKey(),
  productId: text('product_id').notNull(),
  version: text('version').notNull(),
  releaseState: text('release_state').notNull().default('pending'),
  pdfAssetKey: text('pdf_asset_key'),
  pdfSha256: text('pdf_sha256'),
  summaryAssetKey: text('summary_asset_key'),
  summarySha256: text('summary_sha256'),
  approvedVersion: text('approved_version'),
  approvedPdfSha256: text('approved_pdf_sha256'),
  approvedSummarySha256: text('approved_summary_sha256'),
  humanEditorialApproved: integer('human_editorial_approved', { mode: 'boolean' }).notNull().default(false),
  approvedBy: text('approved_by'),
  approvedAt: text('approved_at'),
  qualifiedReviewRequired: integer('qualified_review_required', { mode: 'boolean' }).notNull().default(true),
  qualifiedReviewApproved: integer('qualified_review_approved', { mode: 'boolean' }).notNull().default(false),
  qualifiedReviewedBy: text('qualified_reviewed_by'),
  qualifiedReviewerQualifications: text('qualified_reviewer_qualifications'),
  qualifiedReviewerConflicts: text('qualified_reviewer_conflicts'),
  qualifiedReviewedAt: text('qualified_reviewed_at'),
  marketingSha256: text('marketing_sha256'),
  approvedMarketingSha256: text('approved_marketing_sha256'),
  qualifiedReviewScope: text('qualified_review_scope'),
  qualifiedReviewDecision: text('qualified_review_decision'),
  qualifiedApprovedVersion: text('qualified_approved_version'),
  qualifiedApprovedPdfSha256: text('qualified_approved_pdf_sha256'),
  qualifiedApprovedSummarySha256: text('qualified_approved_summary_sha256'),
  qualifiedApprovedMarketingSha256: text('qualified_approved_marketing_sha256'),
  legalReviewApproved: integer('legal_review_approved', { mode: 'boolean' }).notNull().default(false),
  legalReviewedBy: text('legal_reviewed_by'),
  legalReviewerQualifications: text('legal_reviewer_qualifications'),
  legalReviewScope: text('legal_review_scope'),
  legalReviewConflicts: text('legal_review_conflicts'),
  legalJurisdiction: text('legal_jurisdiction'),
  legalReviewedAt: text('legal_reviewed_at'),
  legalReviewDecision: text('legal_review_decision'),
  legalApprovedVersion: text('legal_approved_version'),
  legalApprovedPdfSha256: text('legal_approved_pdf_sha256'),
  legalApprovedSummarySha256: text('legal_approved_summary_sha256'),
  legalApprovedMarketingSha256: text('legal_approved_marketing_sha256'),
});
