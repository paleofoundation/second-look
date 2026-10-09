import { profileView } from './account-contract';
import { ProfileInputError, type ProfileRepository } from './profile-repository';
export const ACCOUNT_PRIVATE_HEADERS = {
  'Cache-Control': 'private, no-store, max-age=0',
  'Vary': 'Cookie, oai-authenticated-user-id, oai-authenticated-user-email',
  'X-Content-Type-Options': 'nosniff',
};
export type ReaderIdentity = { userId: string };
export type ProfileDependencies = { getUser: () => Promise<ReaderIdentity | null>; repository: () => ProfileRepository };
export function sameOriginMutation(request: Request): boolean {
  const origin = request.headers.get('origin');
  return Boolean(origin && origin === new URL(request.url).origin && request.headers.get('sec-fetch-site') !== 'cross-site');
}
export function createProfileHandlers(deps: ProfileDependencies) {
  const json = (body: unknown, status = 200) => Response.json(body, { status, headers: ACCOUNT_PRIVATE_HEADERS });
  async function identity() { try { return await deps.getUser(); } catch { return null; } }
  return {
    async GET(request: Request) {
      const user = await identity();
      if (!user) return json({ error: 'Sign in to view your reader profile.' }, 401);
      const url = new URL(request.url);
      if ([...url.searchParams.keys()].some(key => key !== 'export')) return json({ error: 'Profile requests always use your signed-in account.' }, 400);
      try {
        const profile = await deps.repository().read(user.userId);
        const view = profile ? profileView(profile) : null;
        if (url.searchParams.get('export') === '1') return new Response(JSON.stringify({ format: 'second-look-reader-profile-v1', exportedAt: new Date().toISOString(), profile: view }, null, 2), { headers: { ...ACCOUNT_PRIVATE_HEADERS, 'Content-Type': 'application/json', 'Content-Disposition': 'attachment; filename="second-look-reader-profile.json"' } });
        return json({ profile: view });
      } catch { return json({ error: 'Your reader profile could not load. Please retry.' }, 503); }
    },
    async PUT(request: Request) {
      const user = await identity();
      if (!user) return json({ error: 'Sign in to update your reader profile.' }, 401);
      if (!sameOriginMutation(request)) return json({ error: 'Request origin rejected.' }, 403);
      if (!request.headers.get('content-type')?.startsWith('application/json')) return json({ error: 'Send a JSON role selection.' }, 415);
      let input: unknown;
      try {
        const raw = await request.text();
        if (raw.length > 2048) return json({ error: 'Role selection is too large.' }, 413);
        input = JSON.parse(raw);
      } catch { return json({ error: 'Invalid role selection. Please choose again.' }, 400); }
      try { return json({ profile: profileView(await deps.repository().save(user.userId, input)) }); }
      catch (error) {
        if (error instanceof ProfileInputError) return json({ error: error.message }, 400);
        return json({ error: 'Your roles were not confirmed saved. Your selection is still here; retry to continue.' }, 503);
      }
    },
    async DELETE(request: Request) {
      const user = await identity();
      if (!user) return json({ error: 'Sign in to remove your reader profile.' }, 401);
      if (!sameOriginMutation(request)) return json({ error: 'Request origin rejected.' }, 403);
      if (new URL(request.url).search) return json({ error: 'Profile deletion always uses your signed-in account.' }, 400);
      // No user ID is accepted, in the URL or body.
      try { if ((await request.text()).trim()) return json({ error: 'Do not send an account identifier.' }, 400); }
      catch { return json({ error: 'Invalid deletion request.' }, 400); }
      try { await deps.repository().remove(user.userId); return json({ deleted: true }); }
      catch { return json({ error: 'Your profile could not be removed. Please retry.' }, 503); }
    },
  };
}
