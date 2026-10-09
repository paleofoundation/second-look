'use client';
import { useState } from 'react';
import { READER_ROLES, type ReaderRole, type ProfileView } from '@/lib/account-contract';
import { readerSignInPath, safeRelativeReturnPath } from '@/lib/account-paths';
import '@/styles/reader-profile.css';

export function ReaderProfileForm({ initialProfile, returnTo, mode }: {
  initialProfile: ProfileView | null; returnTo: string; mode: 'intake' | 'settings';
}) {
  const [roles, setRoles] = useState<ReaderRole[]>(initialProfile?.roles ?? []);
  const [profile, setProfile] = useState(initialProfile);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [expired, setExpired] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const destination = safeRelativeReturnPath(returnTo);
  function toggle(role: ReaderRole) {
    setMessage('');
    setRoles(current => current.includes(role) ? current.filter(value => value !== role)
      : role === 'prefer_not_to_say' ? [role] : [...current.filter(value => value !== 'prefer_not_to_say'), role]);
  }
  async function save(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError(''); setMessage(''); setExpired(false);
    try {
      const response = await fetch('/api/profile', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ roles }), cache: 'no-store' });
      const data = await response.json() as { profile?: ProfileView; error?: string };
      if (!response.ok || !data.profile) {
        setExpired(response.status === 401);
        setError(data.error || 'Your roles could not be saved. Please retry.'); return;
      }
      // Only confirmed server persistence unlocks the next route. No localStorage completion flag.
      setProfile(data.profile); setRoles(data.profile.roles);
      if (mode === 'intake') window.location.assign(destination);
      else setMessage('Your reader profile has been saved.');
    } catch { setError('Connection failed. Your selection is preserved; please retry.'); }
    finally { setBusy(false); }
  }
  async function remove() {
    if (!confirmDelete) return;
    setBusy(true); setError(''); setMessage(''); setExpired(false);
    try {
      const response = await fetch('/api/profile', { method: 'DELETE', cache: 'no-store' });
      const data = await response.json() as { deleted?: boolean; error?: string };
      if (!response.ok || data.deleted !== true) { setExpired(response.status === 401); setError(data.error || 'Your profile could not be removed. Please retry.'); return; }
      setProfile(null); setRoles([]); setConfirmDelete(false);
      setMessage('Reader profile removed. Your saved research and notes are unchanged. Complete this short intake again before opening a released full review.');
    } catch { setError('Connection failed. Please retry removing your profile.'); }
    finally { setBusy(false); }
  }
  return <div className="reader-profile auth"><div className="auth__wrapper"><div className="auth__content">
    <form className="auth-form auth-form--signup" onSubmit={save}>
      <h2 className="auth-form__title">How will you use this research?</h2>
      <p id="role-purpose">Tell us which roles describe you so we can understand our readers and improve the reading experience. Select all that apply, or choose Prefer not to say. All readers see the same findings and limitations.</p>
      <p className="small">These are private, self-reported roles, not verified credentials or marketing consent. Every released full research review is free after sign-in and this intake. Pending reviews stay pending. Please do not provide patient details or medical history.</p>
      <fieldset disabled={busy} aria-describedby="role-purpose"><legend className="sr-only">Reader roles</legend><div className="role-selection">{READER_ROLES.map(option => <label className="reader-role" key={option.value}><input type="checkbox" name="roles" value={option.value} checked={roles.includes(option.value)} onChange={() => toggle(option.value)}/><span>{option.label}</span></label>)}</div></fieldset>
      {error ? <p className="field__errors" role="alert">{error}</p> : null}
      {expired ? <p><a target="_top" href={readerSignInPath(mode === 'settings' ? '/account/profile' : destination)}>Sign in again, then retry</a></p> : null}
      <div className="auth-form__row"><button className="button accent" disabled={busy || roles.length === 0} type="submit">{busy ? 'Saving…' : mode === 'intake' ? 'Save and continue' : 'Save profile'}</button></div>
      {message ? <p className="auth-form__success" role="status">{message}</p> : null}
      <p className="small">You can change or remove these roles in <a href="/account/profile">Account / Profile</a>. Your name and email are managed by the sign-in provider; we do not ask for them again.</p>
    </form>
    {mode === 'settings' ? <div className="profile-controls">
      <h2>Control your profile</h2><a className="button ghost" href="/api/profile?export=1">Export reader profile</a>
      {profile ? <><p className="small">Removing the role profile does not delete your sign-in account, saved research, notes or corrections. It removes intake eligibility until you complete this form again.</p><label className="reader-role"><input type="checkbox" checked={confirmDelete} onChange={event => setConfirmDelete(event.target.checked)} disabled={busy}/><span>Remove my private reader-role profile</span></label><button className="button ghost" type="button" disabled={busy || !confirmDelete} onClick={remove}>Remove profile</button></> : <p className="small">No current reader profile is stored.</p>}
    </div> : <p className="small profile-controls"><a href={destination}>Return to the preview without completing intake</a></p>}
  </div></div></div>;
}
