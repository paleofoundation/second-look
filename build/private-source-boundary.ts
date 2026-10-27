import type {Plugin} from 'vite';
import {posix} from 'node:path';

// HTTP requests only: internal server imports remain available, and public
// /research/<paper> routes must not be confused with private research files.
export function isPrivateSourceRequest(path: string): boolean {
  return /(?:^|\/)(?:private-[^/]+|content\.json|reader-evidence\.json|ingested-topic-pages\.json|acquisition-pages\.json|review-repository\.server\.[^/]+)$/i.test(path)
    || /(?:^|\/)research\/(?:batches|corpus)(?:\/|$)/i.test(path)
    || /(?:^|\/)work\/research-ingest(?:\/|$)/i.test(path)
    || /(?:^|\/)\.research-ingest(?:\/|$)/i.test(path);
}

export function privateSourceBoundary(): Plugin {
  return {
    name: 'second-look-private-source-boundary', apply: 'serve', enforce: 'pre',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        let path = (req.url || '').split('?')[0];
        try {
          for (let i = 0; i < 8; i++) {
            const decoded = decodeURIComponent(path);
            if (decoded === path) break;
            path = decoded;
          }
          if (/%[0-9a-f]{2}/i.test(path)) throw new Error('Unresolved encoding');
        } catch {
          res.statusCode = 400; res.end('Bad path'); return;
        }
        path = posix.normalize(path.replaceAll('\\', '/').split(/[?#]/)[0]).replace(/\/$/, '');
        if (isPrivateSourceRequest(path)) {
          res.statusCode = 404;
          res.setHeader('Cache-Control', 'no-store');
          res.end('Not found');
          return;
        }
        next();
      });
    },
  };
}
