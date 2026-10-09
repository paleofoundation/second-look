import { getReviewForRequest } from '@/lib/review-server';
import { reviewRepository } from '@/lib/review-repository.server';
import { ACCOUNT_PRIVATE_HEADERS } from '@/lib/profile-api';
export const dynamic = 'force-dynamic';
export async function GET(_request: Request, context: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await context.params;
    const result = await getReviewForRequest(reviewRepository, id);
    return Response.json(result, { status: result.kind === 'not_found' ? 404 : result.kind === 'unavailable' ? 503 : 200, headers: ACCOUNT_PRIVATE_HEADERS });
  } catch {
    return Response.json({ error: 'Research review temporarily unavailable. Please retry.' }, { status: 503, headers: ACCOUNT_PRIVATE_HEADERS });
  }
}
