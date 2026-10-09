import 'server-only';
import { getReaderAccount } from '@/lib/profile-server';
import { evaluateReviewAccess, serializePublicPreview, type ReviewRepository } from '@/lib/review-access';
/** Integrator supplies a server-only repository. No private record is imported by this module's clients. */
export async function getReviewForRequest(repository: ReviewRepository, id: string) {
  const account = await getReaderAccount();
  if (account.error) {
    const envelope = await repository.getPublic(id);
    return envelope && envelope.preview.id === id
      ? { kind: 'unavailable' as const, preview: serializePublicPreview(envelope.preview), message: account.error }
      : { kind: 'not_found' as const };
  }
  return evaluateReviewAccess(repository, id, account.user, account.profile);
}
