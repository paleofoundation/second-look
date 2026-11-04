import {publicSitemapXml} from '@/lib/search-indexing';

export const dynamic = 'force-dynamic';

export function GET() {
  return new Response(publicSitemapXml(), {
    headers: {'Content-Type': 'application/xml; charset=utf-8', 'Cache-Control': 'public, max-age=300'},
  });
}
