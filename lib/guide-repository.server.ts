import 'server-only';
import { env } from 'cloudflare:workers';
import type { GuideEdition, GuideLibrary, GuideMembership, GuideOrder, GuideRepository } from './guide-access';
import { readCommerceIdentity, type CommerceEnvironment } from './guide-commerce-config';
import type { StripeMode } from './stripe-client';

type Statement = { bind(...values: unknown[]): Statement; all<T>(): Promise<{ success: boolean; results: T[] }> };
type Database = { prepare(sql: string): Statement };
type Bucket = { get(key: string): Promise<{ arrayBuffer(): Promise<ArrayBuffer> } | null> };
type OrderRecord = { user_id: string; product_id: string; edition_id: string; status: string; currency: string; total_minor: number; created_at: string; updated_at: string };
type MemberRecord = { user_id: string; state: string; current_period_end: string | null; cancel_at_period_end: number };
export type EditionRecord = { web_asset_key: string | null; web_sha256: string | null; approved_web_sha256: string | null; qualified_approved_web_sha256: string | null; legal_approved_web_sha256: string | null; updated_at: string | null; change_summary: string | null; id: string; product_id: string; version: string; release_state: string; pdf_asset_key: string | null; pdf_sha256: string | null; summary_asset_key: string | null; summary_sha256: string | null; approved_version: string | null; approved_pdf_sha256: string | null; approved_summary_sha256: string | null; human_editorial_approved: number; approved_by: string | null; approved_at: string | null; qualified_review_required: number; qualified_review_approved: number; qualified_reviewed_by: string | null; qualified_reviewer_qualifications: string | null; qualified_reviewer_conflicts: string | null; qualified_reviewed_at: string | null;
  marketing_sha256: string | null; approved_marketing_sha256: string | null;
  qualified_review_scope: string | null; qualified_review_decision: string | null;
  qualified_approved_version: string | null; qualified_approved_pdf_sha256: string | null;
  qualified_approved_summary_sha256: string | null; qualified_approved_marketing_sha256: string | null;
  legal_review_approved: number; legal_reviewed_by: string | null; legal_reviewer_qualifications: string | null;
  legal_review_scope: string | null; legal_review_conflicts: string | null; legal_jurisdiction: string | null;
  legal_reviewed_at: string | null; legal_review_decision: string | null; legal_approved_version: string | null;
  legal_approved_pdf_sha256: string | null; legal_approved_summary_sha256: string | null; legal_approved_marketing_sha256: string | null;
};

export function guideEditionFromRecord(row: EditionRecord): GuideEdition { return { webAssetKey: row.web_asset_key, webSha256: row.web_sha256, approvedWebSha256: row.approved_web_sha256, qualifiedApprovedWebSha256: row.qualified_approved_web_sha256, legalApprovedWebSha256: row.legal_approved_web_sha256, updatedAt: row.updated_at, changeSummary: row.change_summary, id: row.id, productId: row.product_id, version: row.version, releaseState: row.release_state, pdfAssetKey: row.pdf_asset_key, pdfSha256: row.pdf_sha256, summaryAssetKey: row.summary_asset_key, summarySha256: row.summary_sha256, approvedVersion: row.approved_version, approvedPdfSha256: row.approved_pdf_sha256, approvedSummarySha256: row.approved_summary_sha256, humanEditorialApproved: row.human_editorial_approved === 1, approvedBy: row.approved_by, approvedAt: row.approved_at, qualifiedReviewRequired: row.qualified_review_required !== 0, qualifiedReviewApproved: row.qualified_review_approved === 1, qualifiedReviewedBy: row.qualified_reviewed_by, qualifiedReviewerQualifications: row.qualified_reviewer_qualifications, qualifiedReviewerConflicts: row.qualified_reviewer_conflicts, qualifiedReviewedAt: row.qualified_reviewed_at,
        marketingSha256: row.marketing_sha256, approvedMarketingSha256: row.approved_marketing_sha256,
        qualifiedReviewScope: row.qualified_review_scope, qualifiedReviewDecision: row.qualified_review_decision,
        qualifiedApprovedVersion: row.qualified_approved_version, qualifiedApprovedPdfSha256: row.qualified_approved_pdf_sha256,
        qualifiedApprovedSummarySha256: row.qualified_approved_summary_sha256, qualifiedApprovedMarketingSha256: row.qualified_approved_marketing_sha256,
        legalReviewApproved: row.legal_review_approved === 1, legalReviewedBy: row.legal_reviewed_by, legalReviewerQualifications: row.legal_reviewer_qualifications,
        legalReviewScope: row.legal_review_scope, legalReviewConflicts: row.legal_review_conflicts, legalJurisdiction: row.legal_jurisdiction,
        legalReviewedAt: row.legal_reviewed_at, legalReviewDecision: row.legal_review_decision, legalApprovedVersion: row.legal_approved_version,
        legalApprovedPdfSha256: row.legal_approved_pdf_sha256, legalApprovedSummarySha256: row.legal_approved_summary_sha256, legalApprovedMarketingSha256: row.legal_approved_marketing_sha256 }; }

export function createGuideRepository(db: Database, bucket?: Bucket, identity?: {accountId: string; mode: StripeMode} | null): GuideRepository {
  async function query<T>(sql: string, ...values: unknown[]): Promise<T[]> { const result = await db.prepare(sql).bind(...values).all<T>(); if (!result.success || !Array.isArray(result.results)) throw new Error('Guide storage read failed'); return result.results; }
  async function verifyEnvironment() {
    if (identity === undefined) return true; // Standalone test repositories can omit deployment identity.
    if (identity) {
      const [binding] = await query<{stripe_account_id:string;mode:string}>('SELECT stripe_account_id,mode FROM guide_commerce_environment WHERE id=1');
      if (binding) {
        if (binding.stripe_account_id !== identity.accountId || binding.mode !== identity.mode) throw new Error('Guide storage does not match the configured Stripe environment.');
        return true;
      }
    }
    // Before commerce setup, an empty library remains usable. Never read or
    // reinterpret existing entitlements without a verified environment binding.
    const [existing] = await query<{present:number}>('SELECT EXISTS(SELECT 1 FROM guide_orders) OR EXISTS(SELECT 1 FROM guide_memberships) AS present');
    if (existing?.present) throw new Error('Existing guide entitlements require a configured Stripe environment.');
    return false;
  }
  return {
    async readLibrary(userId: string, now: string): Promise<GuideLibrary> {
      if (!userId) throw new Error('A signed-in account is required');
      if (!await verifyEnvironment()) return {orders:[],membership:null,editions:[]};
      const [orderRows, memberRows, editionRows] = await Promise.all([
        query<OrderRecord>('SELECT user_id, product_id, edition_id, status, currency, total_minor, created_at, updated_at FROM guide_orders WHERE user_id = ? ORDER BY updated_at DESC', userId),
        query<MemberRecord>('SELECT user_id, state, current_period_end, cancel_at_period_end FROM guide_memberships WHERE user_id = ?', userId),
        query<EditionRecord>(`SELECT e.* FROM guide_editions e WHERE
          EXISTS (SELECT 1 FROM guide_orders o WHERE o.user_id = ? AND o.product_id = e.product_id)
          OR (e.release_state = 'released' AND EXISTS (SELECT 1 FROM guide_memberships m WHERE m.user_id = ? AND m.state = 'active' AND m.current_period_end > ?))`, userId, userId, now),
      ]);
      const orders: GuideOrder[] = orderRows.filter(row => row.user_id === userId).map(row => ({ userId: row.user_id, productId: row.product_id, editionId: row.edition_id, status: row.status, currency: row.currency, totalMinor: row.total_minor, createdAt: row.created_at, updatedAt: row.updated_at }));
      const member = memberRows.find(row => row.user_id === userId);
      const membership: GuideMembership | null = member ? { userId: member.user_id, state: member.state, currentPeriodEnd: member.current_period_end, cancelAtPeriodEnd: member.cancel_at_period_end === 1 } : null;
      const editions = editionRows.map(guideEditionFromRecord);
      return { orders, membership, editions };
    },
    async readAsset(key: string) { if (!await verifyEnvironment() || !bucket) throw new Error('Private guide storage unavailable'); const object = await bucket.get(key); return object ? object.arrayBuffer() : null; },
  };
}

export function guideRepository(): GuideRepository {
  if (!env.DB) throw new Error('Guide database unavailable');
  const configuration = env as typeof env & CommerceEnvironment;
  return createGuideRepository(env.DB, env.BUCKET, configuration.STRIPE_ACCOUNT_ID ? readCommerceIdentity(configuration) : null);
}
