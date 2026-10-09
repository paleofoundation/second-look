import 'server-only';
import { getChatGPTUser } from '@/app/chatgpt-auth';
import { libraryDb } from '@/lib/library';
import { createProfileRepository } from '@/lib/profile-repository';
/** Server-only integration module. Never import this module from a client component. */
export function readerProfiles() { return createProfileRepository(libraryDb()); }
export async function getReaderAccount() {
  const user = await getChatGPTUser();
  if (!user) return { user: null, profile: null, error: null };
  try { return { user, profile: await readerProfiles().read(user.userId), error: null }; }
  catch { return { user, profile: null, error: 'Your reader profile is temporarily unavailable. Please retry.' }; }
}
