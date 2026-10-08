import { env } from 'cloudflare:workers';
export function libraryDb(){if(!env.DB) throw new Error('Storage unavailable');return env.DB;}
export const privateHeaders={'Cache-Control':'private, no-store','Vary':'Cookie, oai-authenticated-user-id','X-Content-Type-Options':'nosniff'};
export function safeMutation(request:Request){const origin=request.headers.get('origin');return !!origin&&origin===new URL(request.url).origin;}
