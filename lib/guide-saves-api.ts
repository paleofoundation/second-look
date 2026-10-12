import { ACCOUNT_PRIVATE_HEADERS, sameOriginMutation, type ReaderIdentity } from './profile-api';
import { activeGuideMembership, guideLibraryView, type GuideRepository, type GuideProduct } from './guide-access';
import type { ProfileRepository } from './profile-repository';
import type { GuideSavesRepository, SavedGuideReason } from './guide-saves';
type Topic = { kind: 'drug' | 'condition'; slug: string; productId: string };
export type GuideSavesDependencies = {
  getUser: () => Promise<ReaderIdentity | null>; repository: () => GuideSavesRepository;
  guides: () => GuideRepository; profiles: () => ProfileRepository;
  getProduct: (id: string) => GuideProduct | undefined; topics: Topic[]; now?: () => Date;
};
export const GUIDE_ADDITION_REASONS: Record<SavedGuideReason, string> = {
  manual: 'Saved by you.', interest: 'Automatically saved because it matched your selected topics.', purchase: 'Added with your guide purchase.',
};
export function createGuideSavesHandlers(deps: GuideSavesDependencies) {
  const json = (body: unknown, status = 200) => Response.json(body, { status, headers: ACCOUNT_PRIVATE_HEADERS });
  const identity = async () => { try { return await deps.getUser(); } catch { return null; } };
  const now = () => deps.now?.() ?? new Date();
  async function snapshot(userId: string) {
    const at = now();
    const [library, profile] = await Promise.all([deps.guides().readLibrary(userId, at.toISOString()), deps.profiles().read(userId)]);
    const view = guideLibraryView(userId, library, deps.getProduct, at);
    const interests = new Set(profile?.interests ?? []);
    const matching = new Set(deps.topics.filter(topic => interests.has(`${topic.kind}:${topic.slug}`)).map(topic => topic.productId));
    const saved = await deps.repository().reconcile(userId, view.availableGuides, matching, activeGuideMembership(library.membership, userId, at));
    // Edition versions define progression; updating an older edition's metadata
    // must not make it the current edition. Dates only break version ties.
    const orderedEditions = [...view.availableGuides].sort((a, b) => b.version.localeCompare(a.version, 'en', { numeric: true }) || (b.updatedAt ?? '').localeCompare(a.updatedAt ?? '') || b.editionId.localeCompare(a.editionId));
    const savedGuides = saved.filter(entry => !entry.removedAt).flatMap(entry => {
      const product = deps.getProduct(entry.productId);
      if (!product) return [];
      const editions = orderedEditions.filter(guide => guide.productId === entry.productId);
      const current = editions[0] ?? null;
      return [{ productId: product.id, title: product.title, slug: product.slug, additionReason: entry.additionReason, reason: GUIDE_ADDITION_REASONS[entry.additionReason], addedAt: entry.addedAt, lastViewedEditionId: entry.lastViewedEditionId, currentEditionId: current?.editionId ?? null, badge: current ? !entry.lastViewedEditionId ? 'New' : entry.lastViewedEditionId !== current.editionId ? 'Updated' : null : null, current, editions }];
    });
    const availableToSave = orderedEditions.filter((guide, index) => orderedEditions.findIndex(candidate => candidate.productId === guide.productId) === index && !saved.some(entry => entry.productId === guide.productId && !entry.removedAt));
    return { ...view, savedGuides, availableToSave, explanation: 'Guides are saved in your account. Files download only when you choose Download. Removing a guide keeps it from being automatically added again.' };
  }
  async function mutation(request: Request, method: 'POST' | 'DELETE' | 'PATCH') {
    const user = await identity();
    if (!user) return json({ error: 'Sign in to manage your guide library.' }, 401);
    if (!sameOriginMutation(request)) return json({ error: 'Request origin rejected.' }, 403);
    if (new URL(request.url).search) return json({ error: 'Library changes use your signed-in account.' }, 400);
    if (!request.headers.get('content-type')?.startsWith('application/json')) return json({ error: 'Send a JSON guide selection.' }, 415);
    let input: { productId: string; editionId?: string };
    try {
      const raw = await request.text();
      if (raw.length > 1024) return json({ error: 'Guide selection is too large.' }, 413);
      const value: unknown = JSON.parse(raw);
      if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).some(key => !['productId', ...(method === 'PATCH' ? ['editionId'] : [])].includes(key))) throw new Error();
      input = value as typeof input;
      if (typeof input.productId !== 'string' || !deps.getProduct(input.productId) || (method === 'PATCH' && (typeof input.editionId !== 'string' || input.editionId.length > 128))) throw new Error();
    } catch { return json({ error: 'Choose a valid guide.' }, 400); }
    try {
      if (method === 'PATCH') {
        const at = now(); const library = await deps.guides().readLibrary(user.userId, at.toISOString());
        const view = guideLibraryView(user.userId, library, deps.getProduct, at);
        if (!view.availableGuides.some(guide => guide.productId === input.productId && guide.editionId === input.editionId)) return json({ error: 'This edition is not available for your account.' }, 403);
        await deps.repository().viewed(user.userId, input.productId, input.editionId!);
        return json({ viewed: true });
      }
      if (method === 'POST') await deps.repository().save(user.userId, input.productId);
      else await deps.repository().remove(user.userId, input.productId);
      return json(method === 'POST' ? { saved: true } : { removed: true });
    } catch { return json({ error: 'Your guide library could not be updated. Please retry.' }, 503); }
  }
  return {
    async GET(request: Request) {
      const user = await identity();
      if (!user) return json({ error: 'Sign in to view your guide library.' }, 401);
      const params = new URL(request.url).searchParams;
      if ([...params.keys()].some(key => key !== 'export') || params.getAll('export').length > 1 || (params.has('export') && params.get('export') !== '1')) return json({ error: 'Guide library requests use your signed-in account.' }, 400);
      try {
        const view = await snapshot(user.userId);
        if (params.get('export') === '1') return new Response(JSON.stringify({ format: 'remaprx-guide-library-v1', exportedAt: now().toISOString(), ...view }, null, 2), { headers: { ...ACCOUNT_PRIVATE_HEADERS, 'Content-Type': 'application/json', 'Content-Disposition': 'attachment; filename="remaprx-guide-library.json"' } });
        return json(view);
      } catch { return json({ error: 'Your guide library is temporarily unavailable. Please retry; no purchases have been changed.' }, 503); }
    },
    POST: (request: Request) => mutation(request, 'POST'),
    DELETE: (request: Request) => mutation(request, 'DELETE'),
    PATCH: (request: Request) => mutation(request, 'PATCH'),
  };
}
