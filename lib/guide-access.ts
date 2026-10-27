import { guideManuscriptSchema } from './guide-manuscript';
import { ACCOUNT_PRIVATE_HEADERS, type ReaderIdentity } from './profile-api';

export type GuideProduct = { id: string; title: string; slug: string; releaseState: 'pending' | 'released' | 'withdrawn'; subscriptionIncluded: boolean; medicalReviewRequired?: boolean; marketingSha256?: string | null };
export type GuideOrder = { userId: string; productId: string; editionId: string; status: string; currency: string; totalMinor: number; createdAt: string; updatedAt: string };
export type GuideMembership = { userId: string; state: string; currentPeriodEnd: string | null; cancelAtPeriodEnd: boolean };
export type GuideEdition = {
  id: string; productId: string; version: string; releaseState: string;
  webAssetKey?: string | null; webSha256?: string | null; approvedWebSha256?: string | null; qualifiedApprovedWebSha256?: string | null; legalApprovedWebSha256?: string | null;
  updatedAt?: string | null; changeSummary?: string | null;
  pdfAssetKey: string | null; pdfSha256: string | null;
  summaryAssetKey: string | null; summarySha256: string | null;
  approvedVersion: string | null; approvedPdfSha256: string | null; approvedSummarySha256: string | null;
  humanEditorialApproved: boolean; approvedBy: string | null; approvedAt: string | null;
  qualifiedReviewRequired: boolean; qualifiedReviewApproved: boolean;
  qualifiedReviewedBy: string | null; qualifiedReviewerQualifications: string | null;
  qualifiedReviewerConflicts: string | null; qualifiedReviewedAt: string | null;
  marketingSha256: string | null; approvedMarketingSha256: string | null;
  qualifiedReviewScope: string | null; qualifiedReviewDecision: string | null;
  qualifiedApprovedVersion: string | null; qualifiedApprovedPdfSha256: string | null;
  qualifiedApprovedSummarySha256: string | null; qualifiedApprovedMarketingSha256: string | null;
  legalReviewApproved: boolean; legalReviewedBy: string | null; legalReviewerQualifications: string | null;
  legalReviewScope: string | null; legalReviewConflicts: string | null; legalJurisdiction: string | null;
  legalReviewedAt: string | null; legalReviewDecision: string | null; legalApprovedVersion: string | null;
  legalApprovedPdfSha256: string | null; legalApprovedSummarySha256: string | null; legalApprovedMarketingSha256: string | null;
};
export type GuideLibrary = { orders: GuideOrder[]; membership: GuideMembership | null; editions: GuideEdition[] };
export type GuideRepository = {
  readLibrary(userId: string, now: string): Promise<GuideLibrary>;
  readAsset(key: string): Promise<ArrayBuffer | null>;
};
export type GuideDependencies = {
  getUser: () => Promise<ReaderIdentity | null>;
  repository: () => GuideRepository;
  getProduct: (id: string) => GuideProduct | undefined;
  now?: () => Date;
};
const meaningful = (value: unknown): value is string => typeof value === 'string' && value.trim().length > 0 && !/^(pending|unknown|tbd|not reviewed)$/i.test(value.trim());
const validHash = (value: unknown): value is string => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const validKey = (value: unknown): value is string => meaningful(value) && value.length <= 512 && !/[\x00-\x1f]/.test(value) && !/^https?:/i.test(value) && !value.split('/').includes('..');
const instant = (value: string | null) => value && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value) ? Date.parse(value) : NaN;
const approvedDate = (value: string | null, now: Date) => Number.isFinite(instant(value)) && instant(value) <= now.getTime();

/** Exact product/version/file approvals; this code cannot create an approval. */
export function approvedGuideEdition(product: GuideProduct | undefined, edition: GuideEdition, now: Date): boolean {
  if (!product || product.id !== edition.productId || product.releaseState !== 'released' || edition.releaseState !== 'released') return false;
  if (!meaningful(edition.version) || edition.approvedVersion !== edition.version || edition.humanEditorialApproved !== true || !meaningful(edition.approvedBy) || !approvedDate(edition.approvedAt, now)) return false;
  if (!validKey(edition.webAssetKey) || !validHash(edition.webSha256) || edition.approvedWebSha256 !== edition.webSha256) return false;
  if (!validKey(edition.pdfAssetKey) || !validHash(edition.pdfSha256) || edition.approvedPdfSha256 !== edition.pdfSha256) return false;
  if (!validKey(edition.summaryAssetKey) || !validHash(edition.summarySha256) || edition.approvedSummarySha256 !== edition.summarySha256) return false;
  if (typeof edition.qualifiedReviewRequired !== 'boolean') return false;
  // Unknown product classification is conservative; an edition cannot waive a
  // product-level clinical/legal requirement. Product marketing hashes are
  // generated from the catalogue and presentation inputs, outside this gate.
  const medicalReviewRequired = product.medicalReviewRequired !== false;
  if (medicalReviewRequired && (!validHash(product.marketingSha256) || edition.marketingSha256 !== product.marketingSha256 || edition.approvedMarketingSha256 !== product.marketingSha256)) return false;
  if (edition.qualifiedReviewRequired || medicalReviewRequired) {
    if (edition.qualifiedReviewApproved !== true || !meaningful(edition.qualifiedReviewedBy) || !meaningful(edition.qualifiedReviewerQualifications) || !meaningful(edition.qualifiedReviewerConflicts) || !approvedDate(edition.qualifiedReviewedAt, now) || !meaningful(edition.qualifiedReviewScope) || edition.qualifiedReviewDecision !== 'approved') return false;
    if (edition.qualifiedApprovedWebSha256 !== edition.webSha256 || edition.qualifiedApprovedVersion !== edition.version || edition.qualifiedApprovedPdfSha256 !== edition.pdfSha256 || edition.qualifiedApprovedSummarySha256 !== edition.summarySha256 || (medicalReviewRequired && edition.qualifiedApprovedMarketingSha256 !== product.marketingSha256)) return false;
  }
  if (medicalReviewRequired) {
    if (edition.legalReviewApproved !== true || !meaningful(edition.legalReviewedBy) || !meaningful(edition.legalReviewerQualifications) || !meaningful(edition.legalReviewScope) || !meaningful(edition.legalReviewConflicts) || !meaningful(edition.legalJurisdiction) || !approvedDate(edition.legalReviewedAt, now) || edition.legalReviewDecision !== 'approved') return false;
    if (edition.legalApprovedWebSha256 !== edition.webSha256 || edition.legalApprovedVersion !== edition.version || edition.legalApprovedPdfSha256 !== edition.pdfSha256 || edition.legalApprovedSummarySha256 !== edition.summarySha256 || edition.legalApprovedMarketingSha256 !== product.marketingSha256) return false;
  }
  return true;
}

export function activeGuideMembership(membership: GuideMembership | null, userId: string, now: Date): boolean {
  // Scheduled non-renewal leaves state active until the paid-through instant.
  // A terminated/cancelled/refunded state ends access immediately, regardless
  // of this renewal flag or a future period end.
  return !!membership && membership.userId === userId && membership.state === 'active' && instant(membership.currentPeriodEnd) > now.getTime();
}

/** Paid topic ownership remains independent of membership expiry/cancellation. */
export function guideEntitlement(userId: string, product: GuideProduct | undefined, edition: GuideEdition, library: GuideLibrary, now: Date): 'owned' | 'membership' | null {
  if (!approvedGuideEdition(product, edition, now)) return null;
  if (library.orders.some(order => order.userId === userId && order.productId === edition.productId && order.status === 'paid')) return 'owned';
  return product!.subscriptionIncluded && activeGuideMembership(library.membership, userId, now) ? 'membership' : null;
}

/** Private account history keeps edition metadata even when rights have ended. */
function orderDownloadDenial(order: GuideOrder, product: GuideProduct | undefined, edition: GuideEdition | undefined, available: boolean) {
  const unavailable = (code: string, reason: string) => ({ downloadUnavailableCode: code, downloadUnavailableReason: reason });
  if (order.status !== 'paid') {
    const reasons: Record<string, string> = { pending: 'Payment is pending; this order does not yet grant a download.', failed: 'Payment failed; this order does not grant a download.', refunded: 'This order was refunded and no longer grants a download.', disputed: 'This order is disputed; purchase access is unavailable.', cancelled: 'This order was canceled and does not grant a download.' };
    return unavailable(reasons[order.status] ? 'order_' + order.status : 'order_status_unverified', reasons[order.status] ?? 'The order status could not be verified; purchase access is unavailable.');
  }
  if (!product) return unavailable('product_unavailable', 'The guide catalog record is unavailable. Your purchase record has been retained.');
  if (!edition) return unavailable('edition_unavailable', 'The purchased edition record is unavailable. Your purchase record has been retained.');
  if (product.releaseState === 'withdrawn' || edition.releaseState === 'withdrawn') return unavailable('edition_withdrawn', 'This edition has been withdrawn from download. Your purchase record has been retained.');
  if (product.releaseState !== 'released' || edition.releaseState !== 'released') return unavailable('release_pending', 'This edition has not been released for download.');
  if (!available) return unavailable('approval_pending', 'The exact edition, full guide, summary and required reviews have not all been verified for download.');
  return { downloadUnavailableCode: null, downloadUnavailableReason: null };
}

export function guideLibraryView(userId: string, library: GuideLibrary, getProduct: GuideDependencies['getProduct'], now: Date) {
  const availableGuides = [...library.editions].sort((a, b) => b.version.localeCompare(a.version, 'en', { numeric: true }) || (b.updatedAt ?? '').localeCompare(a.updatedAt ?? '') || b.id.localeCompare(a.id)).flatMap(edition => {
    const product = getProduct(edition.productId);
    const access = guideEntitlement(userId, product, edition, library, now);
    if (!product || !access) return [];
    const downloadUrl = `/api/guides/${encodeURIComponent(edition.id)}/download`;
    return [{ productId: product.id, title: product.title, slug: product.slug, editionId: edition.id, version: edition.version, updatedAt: edition.updatedAt ?? null, changeSummary: edition.changeSummary ?? null, readerUrl: `/guides/read/${encodeURIComponent(edition.id)}`, access, downloadUrl, summaryDownloadUrl: edition.summaryAssetKey ? downloadUrl + '?format=summary' : null }];
  });
  const knownStatuses = ['paid', 'pending', 'failed', 'refunded', 'disputed', 'cancelled'];
  const purchases = library.orders.filter(order => order.userId === userId).map(order => {
    const product = getProduct(order.productId);
    const edition = library.editions.find(value => value.productId === order.productId && value.id === order.editionId);
    const available = availableGuides.find(edition => edition.productId === order.productId && edition.editionId === order.editionId);
    return { productId: product?.id ?? null, title: product?.title ?? 'Guide record unavailable', status: knownStatuses.includes(order.status) ? order.status : 'unknown', currency: /^[A-Z]{3}$/.test(order.currency) ? order.currency : null, totalMinor: Number.isSafeInteger(order.totalMinor) && order.totalMinor >= 0 ? order.totalMinor : null, createdAt: order.createdAt, updatedAt: order.updatedAt, editionVersion: edition && meaningful(edition.version) ? edition.version : null, downloadAvailable: order.status === 'paid' && !!available, ...orderDownloadDenial(order, product, edition, !!available) };
  });
  const member = library.membership?.userId === userId ? library.membership : null;
  const membership = member ? { state: member.state === 'active' && !activeGuideMembership(member, userId, now) ? 'expired' : ['active', 'inactive', 'cancelled', 'terminated', 'refunded', 'disputed', 'expired', 'past_due', 'pending'].includes(member.state) ? member.state : 'unknown', expiresAt: Number.isFinite(instant(member.currentPeriodEnd)) ? member.currentPeriodEnd : null, cancelAtPeriodEnd: member.cancelAtPeriodEnd === true } : null;
  return { commerce: 'not_launched' as const, purchases, membership, availableGuides, message: 'Sales and memberships have not launched. Purchased topics include future approved editions independently of membership; only released, approved files can be downloaded.' };
}

export function createGuideHandlers(deps: GuideDependencies) {
  const json = (body: unknown, status = 200) => Response.json(body, { status, headers: ACCOUNT_PRIVATE_HEADERS });
  const now = () => deps.now?.() ?? new Date();
  const identity = async () => { try { return await deps.getUser(); } catch { return null; } };
  return {
    async purchases(request: Request) {
      const user = await identity();
      if (!user) return json({ error: 'Sign in to view My guides.' }, 401);
      if (new URL(request.url).search) return json({ error: 'Guide requests use your signed-in account; no account parameters are accepted.' }, 400);
      try { const at = now(); const library = await deps.repository().readLibrary(user.userId, at.toISOString()); return json(guideLibraryView(user.userId, library, deps.getProduct, at)); }
      catch { return json({ error: 'Your guide library is temporarily unavailable. Please retry; no purchases have been changed.' }, 503); }
    },
    async reader(request: Request, editionId: string) {
      const user = await identity();
      if (!user) return json({ error: 'Sign in to read your guide.' }, 401);
      if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(editionId) || new URL(request.url).search) return json({ error: 'Choose a valid guide edition.' }, 400);
      try {
        const at = now(); const repository = deps.repository(); const library = await repository.readLibrary(user.userId, at.toISOString());
        const edition = library.editions.find(value => value.id === editionId);
        const product = edition ? deps.getProduct(edition.productId) : undefined;
        const access = edition && guideEntitlement(user.userId, product, edition, library, at);
        if (!edition || !product || !access) return json({ error: 'This edition is not available for this account, or its release is still pending.' }, 403);
        const bytes = edition.webAssetKey ? await repository.readAsset(edition.webAssetKey) : null;
        if (!bytes || bytes.byteLength > 4_000_000) return json({ error: 'The approved guide is temporarily unavailable.' }, 503);
        const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(byte => byte.toString(16).padStart(2, '0')).join('');
        if (hash !== edition.webSha256) return json({ error: 'The guide could not be verified against its approved edition.' }, 503);
        const parsed = guideManuscriptSchema.safeParse(JSON.parse(new TextDecoder().decode(bytes)));
        if (!parsed.success || parsed.data.productId !== product.id || parsed.data.editionId !== edition.id || parsed.data.version !== edition.version) return json({ error: 'The approved guide format could not be verified.' }, 503);
        return json({ manuscript: parsed.data, access });
      } catch { return json({ error: 'Your guide is temporarily unavailable. Please retry.' }, 503); }
    },
    async download(request: Request, editionId: string) {
      const user = await identity();
      if (!user) return json({ error: 'Sign in to download your guide.' }, 401);
      const params = new URL(request.url).searchParams;
      if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(editionId) || [...params.keys()].some(key => key !== 'format') || params.getAll('format').length > 1 || (params.has('format') && params.get('format') !== 'summary')) return json({ error: 'Choose a valid guide download.' }, 400);
      try {
        const at = now(); const repository = deps.repository(); const library = await repository.readLibrary(user.userId, at.toISOString());
        const edition = library.editions.find(value => value.id === editionId);
        const product = edition ? deps.getProduct(edition.productId) : undefined;
        if (!edition || !product || !guideEntitlement(user.userId, product, edition, library, at)) return json({ error: 'This edition is not available for this account, or its release is still pending.' }, 403);
        const summary = params.get('format') === 'summary';
        const key = summary ? edition.summaryAssetKey : edition.pdfAssetKey;
        const expectedHash = summary ? edition.summarySha256 : edition.pdfSha256;
        if (!key || !expectedHash) return json({ error: 'This edition does not have that download.' }, 404);
        const bytes = await repository.readAsset(key);
        if (!bytes) return json({ error: 'The approved file is temporarily unavailable. Please retry.' }, 503);
        const actualHash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(byte => byte.toString(16).padStart(2, '0')).join('');
        if (actualHash !== expectedHash || new TextDecoder().decode(bytes.slice(0, 5)) !== '%PDF-') return json({ error: 'This file could not be verified against the reviewed edition. Download is unavailable.' }, 503);
        const safeName = `${product.slug}-${edition.version}${summary ? '-summary' : ''}`.replace(/[^a-zA-Z0-9._-]/g, '-').slice(0, 160);
        return new Response(bytes, { headers: { ...ACCOUNT_PRIVATE_HEADERS, 'Content-Type': 'application/pdf', 'Content-Disposition': `attachment; filename="${safeName}.pdf"`, 'Content-Length': String(bytes.byteLength), 'Content-Security-Policy': 'sandbox' } });
      } catch { return json({ error: 'Your guide download is temporarily unavailable. Please retry.' }, 503); }
    },
  };
}
