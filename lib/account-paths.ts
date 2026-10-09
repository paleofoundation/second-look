/** Routes shared by clients and server. Never import the server session into clients. */
export const DEFAULT_ACCOUNT_DESTINATION = '/guides/library';
const AUTH_PATHS = ['/signin-with-chatgpt', '/signout-with-chatgpt', '/callback', '/account/continue', '/account/intake'];
export function safeRelativeReturnPath(value: unknown, fallback = DEFAULT_ACCOUNT_DESTINATION): string {
  if (typeof value !== 'string' || value.length > 2048 || !value.startsWith('/') || value.startsWith('//')) return fallback;
  if (/[\\\u0000-\u0020\u007f]/.test(value)) return fallback;
  let url: URL;
  try {
    url = new URL(value, 'https://app.local');
    // Reject encoded slash/backslash/control bypasses, including repeated encodings.
    let decoded = url.pathname;
    for (let i = 0; i < 5; i++) {
      const next = decodeURIComponent(decoded);
      if (/[\\\u0000-\u0020\u007f]/.test(next) || next.startsWith('//')) return fallback;
      if (next === decoded) break;
      decoded = next;
    }
    if (AUTH_PATHS.some(path => decoded === path || decoded.startsWith(path + '/')) || decoded.startsWith('/api/')) return fallback;
  } catch { return fallback; }
  if (url.origin !== 'https://app.local') return fallback;
  return `${url.pathname}${url.search}${url.hash}`;
}
export function accountContinuePath(returnTo: unknown = DEFAULT_ACCOUNT_DESTINATION): string {
  return '/account/continue?returnTo=' + encodeURIComponent(safeRelativeReturnPath(returnTo));
}
export function readerSignInPath(returnTo: unknown = DEFAULT_ACCOUNT_DESTINATION): string {
  return '/signin-with-chatgpt?return_to=' + encodeURIComponent(accountContinuePath(returnTo));
}
export function intakePath(returnTo: unknown = DEFAULT_ACCOUNT_DESTINATION): string {
  return '/account/intake?returnTo=' + encodeURIComponent(safeRelativeReturnPath(returnTo));
}
