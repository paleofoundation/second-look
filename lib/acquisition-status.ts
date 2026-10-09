import status from '@/data/acquisition-status.json';
export function acquisitionPageForPath(path:string){const normalized=path.startsWith('/')?path:'/'+path;return status.pages.find(p=>p.path===normalized)}
