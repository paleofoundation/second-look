/** Private library metadata. This module never contains or returns manuscript text. */
export type SavedGuideReason = 'manual' | 'interest' | 'purchase';
export type SavedGuide = { userId: string; productId: string; additionReason: SavedGuideReason; addedAt: string; lastViewedEditionId: string | null; removedAt: string | null };
type Row = { user_id: string; product_id: string; addition_reason: SavedGuideReason; added_at: string; last_viewed_edition_id: string | null; removed_at: string | null };
type Statement = { bind(...values: (string | number | null)[]): Statement; all<T>(): Promise<{ success: boolean; results: T[] }>; run(): Promise<unknown> };
export type GuideSavesDatabase = { prepare(sql: string): Statement };
export type GuideSaveCandidate = { productId: string; access: 'owned' | 'membership' };
export function createGuideSavesRepository(db: GuideSavesDatabase, now = () => new Date().toISOString()) {
  async function write(sql: string, ...values: (string | number | null)[]) {
    const result = await db.prepare(sql).bind(...values).run();
    if (result && typeof result === 'object' && 'success' in result && result.success === false) throw new Error('Guide library write failed');
  }
  async function read(userId: string): Promise<SavedGuide[]> {
    const result = await db.prepare('SELECT user_id, product_id, addition_reason, added_at, last_viewed_edition_id, removed_at FROM guide_saved_entries WHERE user_id = ? ORDER BY added_at DESC, product_id').bind(userId).all<Row>();
    if (!result.success || !Array.isArray(result.results)) throw new Error('Guide library unavailable');
    return result.results.filter(row => row.user_id === userId).map(row => ({ userId: row.user_id, productId: row.product_id, additionReason: row.addition_reason, addedAt: row.added_at, lastViewedEditionId: row.last_viewed_edition_id, removedAt: row.removed_at }));
  }
  return {
    read,
    /** Insert-only reconciliation is idempotent and cannot revive a removal tombstone. */
    async reconcile(userId: string, candidates: GuideSaveCandidate[], matchingProductIds: Set<string>, membershipActive: boolean) {
      const candidatesByProduct = new Map<string, SavedGuideReason>();
      for (const guide of candidates) {
        if (guide.access === 'owned') candidatesByProduct.set(guide.productId, 'purchase');
        else if (membershipActive && matchingProductIds.has(guide.productId) && !candidatesByProduct.has(guide.productId)) candidatesByProduct.set(guide.productId, 'interest');
      }
      for (const [productId, reason] of candidatesByProduct) await write('INSERT INTO guide_saved_entries (user_id, product_id, addition_reason, added_at) VALUES (?, ?, ?, ?) ON CONFLICT(user_id, product_id) DO NOTHING', userId, productId, reason, now());
      return read(userId);
    },
    async save(userId: string, productId: string) {
      await write(`INSERT INTO guide_saved_entries (user_id, product_id, addition_reason, added_at) VALUES (?, ?, 'manual', ?)
        ON CONFLICT(user_id, product_id) DO UPDATE SET addition_reason='manual', removed_at=NULL,
        added_at=CASE WHEN guide_saved_entries.removed_at IS NOT NULL THEN excluded.added_at ELSE guide_saved_entries.added_at END`, userId, productId, now());
    },
    async remove(userId: string, productId: string) {
      const at = now();
      await write(`INSERT INTO guide_saved_entries (user_id, product_id, addition_reason, added_at, removed_at) VALUES (?, ?, 'manual', ?, ?)
        ON CONFLICT(user_id, product_id) DO UPDATE SET removed_at=excluded.removed_at`, userId, productId, at, at);
    },
    async viewed(userId: string, productId: string, editionId: string) {
      // Reading a guide does not reverse a deliberate removal or silently save a new topic.
      await write('UPDATE guide_saved_entries SET last_viewed_edition_id = ? WHERE user_id = ? AND product_id = ? AND removed_at IS NULL', editionId, userId, productId);
    },
  };
}
export type GuideSavesRepository = ReturnType<typeof createGuideSavesRepository>;
