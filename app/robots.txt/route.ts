import {robotsTxtForHost} from '@/lib/search-indexing';

export const dynamic = 'force-dynamic';

export function GET(request: Request) {
  const host = request.headers.get('host');
  return new Response(robotsTxtForHost(host), {
    headers: {'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'public, max-age=300'},
  });
}
