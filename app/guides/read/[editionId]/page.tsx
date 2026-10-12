import {notFound} from 'next/navigation';
import {GuideReader} from '@/components/guide-reader';
export const metadata={title:'Your guide | RemapRx',robots:{index:false,follow:false}};
export default async function GuideReaderPage({params}:{params:Promise<{editionId:string}>}) {
 const {editionId}=await params;
 if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(editionId))notFound();
 return <main id="main" className="guide-reader-page"><GuideReader editionId={editionId}/></main>;
}
