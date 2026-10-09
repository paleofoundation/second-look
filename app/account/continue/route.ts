import { getReaderAccount } from '@/lib/profile-server';
import { createAccountContinueHandler } from '@/lib/account-flow';
export const dynamic = 'force-dynamic';
export const GET = createAccountContinueHandler(getReaderAccount);
