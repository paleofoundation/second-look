import {publicSitemapPartXml} from '@/lib/search-indexing';

export const dynamic = 'force-dynamic';

export async function GET(_request: Request, context: {params: Promise<{part: string}>}) {
  const {part} = await context.params;
  const xml = publicSitemapPartXml(Number(part));
  if (!xml) return new Response('Not found', {status: 404, headers: {'Content-Type': 'text/plain; charset=utf-8'}});
  return new Response(xml, {
    headers: {'Content-Type': 'application/xml; charset=utf-8', 'Cache-Control': 'public, max-age=300'},
  });
}
