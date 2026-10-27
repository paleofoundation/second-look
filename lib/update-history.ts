import history from '@/data/article-updates.json';
import createdDates from '@/data/page-created-dates.json';

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

// Rule (one-match-rule reading-ui/article-navigation; DESIGN-SYSTEM): Update History
// lists only material changes to the page's content, never processes. Evidence,
// correction and new-page events are material; presentation events are kept only
// when they add or expand substantive content, and never when they concern
// design, imagery, navigation or pipeline/process work.
const PROCESS_PATTERN = /illustration|palette|image|icon|navigation|sidebar|reading order|layout|theme|design|reorganiz|easier to|ingest|pipeline|checkpoint|validat|render|handoff|internal review|rule version|build|deploy/i;
const MATERIAL_PRESENTATION = /^(expanded|added|new section|safety|correction)/i;
export function isMaterialUpdate(entry: ArticleUpdate): boolean {
  if (entry.changeType !== 'presentation') return !PROCESS_PATTERN.test(entry.title);
  return MATERIAL_PRESENTATION.test(entry.title) && !PROCESS_PATTERN.test(entry.title);
}

export function articleUpdatesForPath(pagePath: string): ArticleUpdate[] {
  const normalized = pagePath.split(/[?#]/, 1)[0].replace(/\/+$/, '') || '/';
  return articleUpdates
    .filter(entry => entry.pagePaths.includes(normalized) && isMaterialUpdate(entry))
    .toSorted((a, b) => b.date.localeCompare(a.date) || b.id.localeCompare(a.id));
}

export function articleUpdateDate(date: string): string {
  return new Intl.DateTimeFormat('en-US', {
    day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
  }).format(new Date(`${date}T12:00:00Z`));
}

/** First git commit that introduced the page (precomputed by scripts/build-page-created-dates.mjs). */
export function pageCreatedDate(pagePath: string): string | undefined {
  const normalized = pagePath.split(/[?#]/, 1)[0].replace(/\/+$/, '') || '/';
  return (createdDates.dates as Record<string, string>)[normalized];
}
