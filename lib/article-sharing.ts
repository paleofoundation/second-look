/** Share only the public canonical route, never a visitor's query, fragment or account data. */
export function canonicalArticleUrl(path: string) {
  const route = path.split(/[?#]/, 1)[0];
  if (!/^\/(?:drugs|conditions|research|glossary|answers|comparisons|guides)\/[A-Za-z0-9._/-]+$/.test(route) || route.includes('..')) throw new Error('Invalid public article route');
  return new URL(route, 'https://remaprx.com').href;
}
export function articleShareLinks(path: string, title: string) {
  const url = canonicalArticleUrl(path), u = encodeURIComponent(url), t = encodeURIComponent(title);
  return [
    { key: 'x', label: 'Share on X / Twitter', href: `https://twitter.com/intent/tweet?url=${u}&text=${t}` },
    { key: 'reddit', label: 'Share on Reddit', href: `https://www.reddit.com/submit?url=${u}&title=${t}` },
    { key: 'linkedin', label: 'Share on LinkedIn', href: `https://www.linkedin.com/sharing/share-offsite/?url=${u}` },
    { key: 'email', label: 'Share by email', href: `mailto:?subject=${t}&body=${u}` },
  ];
}
