import { redirect } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { SiteFooter } from '@/components/site-footer';
import { ReaderProfileForm } from '@/components/reader-profile-form';
import { getReaderAccount } from '@/lib/profile-server';
import { readerSignInPath, intakePath, safeRelativeReturnPath } from '@/lib/account-paths';
export const dynamic = 'force-dynamic';
export const metadata = { title: 'About you', robots: { index: false, follow: false } };
export default async function IntakePage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const query = await searchParams;
  const destination = safeRelativeReturnPath(query.returnTo);
  const account = await getReaderAccount();
  if (!account.user) redirect(readerSignInPath(destination));
  if (!account.error && account.profile) redirect(destination);
  return <><SiteHeader/><main id="main" className="wrap"><div className="page-intro"><h1>About you</h1><p>A short private intake before complete research reviews.</p></div>{account.error ? <div className="notice" role="alert"><p>{account.error}</p><a className="button" href={intakePath(destination)}>Retry loading your profile</a><p><a href={destination}>Return to the preview</a></p></div> : <ReaderProfileForm initialProfile={null} returnTo={destination} mode="intake"/>}</main><SiteFooter/></>;
}
