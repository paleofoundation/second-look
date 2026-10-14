'use client';
import {FileText, Grid2X2, Info} from 'lucide-react';
import {Popover, PopoverTrigger, PopoverContent} from '@/components/ui/popover';
import type {PageSnapshotData} from '@/lib/page-snapshot';

export function PageSnapshot({snapshot, studiesHref}: {snapshot: PageSnapshotData; studiesHref: string}) {
 const peerLabel = snapshot.peerType === 'Drug' ? 'drug' : 'condition';
 return <section className="sl-page-snapshot" aria-label="Page Snapshot">
  <div className="sl-page-snapshot__header"><h2>Page Snapshot</h2>
   <Popover><PopoverTrigger asChild><button type="button" className="sl-page-snapshot__info" aria-label="How Page Snapshot is counted"><Info aria-hidden="true"/></button></PopoverTrigger>
    <PopoverContent className="snapshot-info" align="end" aria-label="About Page Snapshot">
     <p>Studies referenced counts primary research cited on this page, including human and laboratory studies. Reports with a recorded shared study identity count once. Reviews and other background references are excluded.</p>
     <p>These counts describe the research discussed, including mixed, negative or disputed findings. They do not measure effectiveness or evidence certainty.</p>
     {snapshot.peerType ? <p>Investigated {peerLabel}s covered on this page.{snapshot.peers.length ? <> Included: {snapshot.peers.map((peer, index) => <span key={peer.id}>{index ? ', ' : ''}<a href={peer.href}>{peer.title}</a></span>)}.</> : null}</p> : null}
    </PopoverContent>
   </Popover>
  </div>
  <a className="sl-page-snapshot__row" href={studiesHref}><FileText aria-hidden="true"/><span>{snapshot.studies} {snapshot.studies === 1 ? 'study' : 'studies'} referenced</span></a>
  {snapshot.peerType ? <div className="sl-page-snapshot__row"><Grid2X2 aria-hidden="true"/><span>{snapshot.peers.length} {peerLabel}{snapshot.peers.length === 1 ? '' : 's'} investigated</span></div> : null}
 </section>;
}
