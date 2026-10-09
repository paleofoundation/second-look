import status from '@/data/acquisition-status.json';
import {readerEvidenceStatus} from './reader-evidence-status';
export function acquisitionPageForPath(path:string){const normalized=path.startsWith('/')?path:'/'+path;const page=status.pages.find(p=>p.path===normalized);return page?{coverage_state:page.coverage_state,...readerEvidenceStatus(page.next_action)}:undefined}
