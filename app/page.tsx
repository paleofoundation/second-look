import type {Metadata} from 'next';
import {ThemeHome} from '@/components/shared-theme/theme';
import {secondLookHome} from '@/lib/theme/config';
import {NOINDEX_ROBOTS} from '@/lib/search-indexing';
export const dynamic='force-dynamic';
export const metadata: Metadata = {
  alternates: {canonical: 'https://remaprx.com/'},
  robots: NOINDEX_ROBOTS,
};
export default function Home(){return <ThemeHome content={secondLookHome}/>}
