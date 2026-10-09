import { SiteHeader } from '@/components/site-header';
import { SiteFooter } from '@/components/site-footer';
import { ReaderProfileForm } from '@/components/reader-profile-form';
import { getReaderAccount } from '@/lib/profile-server';
import { profileView } from '@/lib/account-contract';
import { readerSignInPath } from '@/lib/account-paths';
import { chatGPTSignOutPath } from '@/app/chatgpt-auth';
export const dynamic = 'force-dynamic';
export const metadata = { title: 'Account / Profile', robots: { index: false, follow: false } };
export default async function ProfilePage() {
  const account = await getReaderAccount();
  return <><SiteHeader/><main id="main" className="wrap"><div className="page-intro"><h1>Account / Profile</h1><p>Your private reader roles and profile controls.</p></div>{!account.user ? <div className="empty"><p>Sign in to manage your reader profile.</p><a className="button accent" target="_top" href={readerSignInPath('/account/profile')}>Sign in with ChatGPT</a></div> : <><nav className="account-nav" aria-label="Your account"><a href="/account">Saved research</a><a href="/guides/library">My guides</a><a href="/account/profile" aria-current="page">Profile</a><a target="_top" href={chatGPTSignOutPath()}>Sign out</a></nav>{account.error ? <div role="alert" className="notice"><p>{account.error}</p><a className="button" href="/account/profile">Retry loading your profile</a></div> : <ReaderProfileForm initialProfile={account.profile ? profileView(account.profile) : null} returnTo="/account/profile" mode="settings"/>}</>}</main><SiteFooter/></>;
}
