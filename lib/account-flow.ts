import { hasCurrentIntake, type ReaderProfile } from './account-contract';
import { ACCOUNT_PRIVATE_HEADERS, type ReaderIdentity } from './profile-api';
import { readerSignInPath, intakePath, safeRelativeReturnPath } from './account-paths';
export type ReaderAccountState = { user: ReaderIdentity | null; profile: ReaderProfile | null; error: string | null };
export function createAccountContinueHandler(getAccount: () => Promise<ReaderAccountState>) {
  return async function GET(request: Request) {
    const destination = safeRelativeReturnPath(new URL(request.url).searchParams.get('returnTo'));
    const account = await getAccount();
    const redirectTo = !account.user ? readerSignInPath(destination)
      : account.error || !hasCurrentIntake(account.profile, account.user.userId) ? intakePath(destination) : destination;
    return new Response(null, { status: 303, headers: { ...ACCOUNT_PRIVATE_HEADERS, Location: new URL(redirectTo, request.url).href } });
  };
}
