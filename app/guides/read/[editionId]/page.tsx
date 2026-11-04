import type {Metadata} from 'next';
import {notFound} from 'next/navigation';
import {GuideReader} from '@/components/guide-reader';
import {NOINDEX_ROBOTS} from '@/lib/search-indexing';
export async function generateMetadata({params}:{params:Promise<{editionId:string}>}): Promise<Metadata> {
 const {editionId}=await params;
 return {title:'Your guide',description:'A private guide edition for a signed-in reader. This is not medical advice.',alternates:{canonical:`https://remaprx.com/guides/read/${encodeURIComponent(editionId)}`},robots:NOINDEX_ROBOTS};
}
export default async function GuideReaderPage({params}:{params:Promise<{editionId:string}>}) {
 const {editionId}=await params;
 if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(editionId))notFound();
 return <main id="main" className="guide-reader-page"><GuideReader editionId={editionId}/></main>;
}
