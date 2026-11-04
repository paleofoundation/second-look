import type {Metadata} from 'next';
import {NOINDEX_ROBOTS} from '@/lib/search-indexing';

export const metadata: Metadata = {
  title: 'Page not found',
  description: 'This address is not in the RemapRx library.',
  alternates: {canonical: 'https://remaprx.com/'},
  robots: NOINDEX_ROBOTS,
};

export default function NotFound(){return <main className="narrow"><a className="wordmark" href="/">RemapRx</a><h1 style={{marginTop:60}}>This page is not in the library.</h1><p>The address may have changed, or this question may still be in the research queue.</p><a className="button" href="/search">Search the library</a></main>}
