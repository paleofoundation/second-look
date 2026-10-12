import history from '@/data/article-updates.json';

export type ArticleUpdate = {
  id: string;
  date: string;
  title: string;
  changeType: 'presentation' | 'evidence' | 'correction' | 'new-page';
  summary: string;
  pagePaths: string[];
  affectedSections?: {id: string; label: string}[];
  references?: {href: string; label: string}[];
  reviewedBy?: string;
};

// This public ledger contains reader-facing changes only. Its explicit route list
// prevents a later article from inheriting a change that predates its creation.
export const articleUpdates = history.entries as ArticleUpdate[];

export function articleUpdatesForPath(pagePath: string): ArticleUpdate[] {
  const normalized = pagePath.split(/[?#]/, 1)[0].replace(/\/+$/, '') || '/';
  return articleUpdates
    .filter(entry => entry.pagePaths.includes(normalized))
    .toSorted((a, b) => b.date.localeCompare(a.date) || b.id.localeCompare(a.id));
}

export function articleUpdateDate(date: string): string {
  return new Intl.DateTimeFormat('en-US', {
    day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
  }).format(new Date(`${date}T12:00:00Z`));
}
