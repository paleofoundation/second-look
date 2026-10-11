import type {ReactNode} from 'react';
import {content, guideUrl} from '@/lib/content';

type WikiEntity = {title: string; href: string; aliases?: readonly string[]};
export type WikiToken = {text: string; href?: string};
export type WikiTextRenderer = (text: string, linked?: Set<string>) => ReactNode;

// Aliases describe the same entity, never a broader disease or an efficacy claim.
// A spelling only becomes linkable when its canonical destination exists.
const routeAliases: Record<string, string[]> = {
  '/drugs/metformin': ['metformin hydrochloride'],
  '/drugs/sirolimus': ['rapamycin'],
  '/drugs/nirmatrelvir': ['nirmatrelvir', 'nirmatrelvir–ritonavir', 'nirmatrelvir/ritonavir', 'Paxlovid'],
  '/drugs/naltrexone': ['low-dose naltrexone'],
  '/drugs/valproic-acid': ['valproate'],
  '/conditions/long-covid': ['post-COVID-19 condition', 'post COVID condition', 'postacute sequelae of SARS-CoV-2 infection', 'PASC'],
  '/conditions/type-2-diabetes': ['type 2 diabetes mellitus', 'type II diabetes', 'T2DM', 'T2D'],
  '/conditions/parkinson-disease': ["Parkinson's disease", "Parkinson's", 'Parkinson disease'],
  '/conditions/alzheimer-disease': ["Alzheimer's disease", "Alzheimer's", 'Alzheimer disease'],
  '/conditions/crohn-disease': ["Crohn's disease", "Crohn's"],
  '/conditions/myalgic-encephalomyelitis-chronic-fatigue-syndrome': ['ME/CFS', 'myalgic encephalomyelitis', 'chronic fatigue syndrome'],
  '/conditions/amyotrophic-lateral-sclerosis': ['ALS'],
  '/conditions/multiple-sclerosis': ['MS'],
  '/conditions/non-small-cell-lung-cancer': ['non-small cell lung cancer', 'NSCLC'],
  '/conditions/basal-cell-carcinoma': ['basal cell carcinoma'],
  '/conditions/head-and-neck-squamous-cell-carcinoma': ['head-and-neck squamous cell carcinoma', 'HNSCC'],
  '/conditions/epithelial-ovarian-or-fallopian-tube-carcinoma': ['epithelial ovarian cancer', 'fallopian-tube carcinoma'],
  '/conditions/hepatocellular-carcinoma': ['HCC'],
  '/conditions/acute-myeloid-leukemia': ['acute myeloid leukaemia', 'AML'],
  '/conditions/chronic-myeloid-leukemia': ['chronic myeloid leukaemia', 'CML'],
  '/conditions/compulsive-sexual-behavior-disorder': ['compulsive sexual behaviour disorder', 'CSBD'],
  '/conditions/persistent-genital-arousal-disorder-genitopelvic-dysesthesia': ['persistent genital arousal disorder', 'genitopelvic dysesthesia', 'PGAD/GPD'],
  '/conditions/aging': ['aging and longevity'],
  '/glossary/off-label': ['off-label'],
  '/glossary/placebo': ['placebos'],
  '/glossary/confidence-interval': ['confidence intervals'],
  '/glossary/primary-outcome': ['primary outcomes'],
  '/glossary/study-family': ['study families'],
  '/glossary/randomization': ['randomisation'],
  '/glossary/relative-risk': ['risk ratio'],
  '/drug-repurposing': ['drug repositioning', 'medicine repurposing'],
};

const normalizeAlias = (value: string) => value.toLocaleLowerCase('en').replace(/[’‘]/g, "'")
  .replace(/[‐‑–—]/g, '-').replace(/\s+/g, ' ').trim();
const routePath = (value: string) => value.split(/[?#]/, 1)[0].replace(/\/+$/, '') || '/';
const escapePattern = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const aliasPattern = (value: string) => escapePattern(value).replace(/'/g, "['’‘]")
  .replace(/-/g, '[-‐‑–—]').replace(/ /g, '\\s+');

/** Ambiguous aliases are omitted instead of silently choosing an unrelated page. */
export function createWikiRegistry(entities: readonly WikiEntity[]) {
  const destinations = new Map<string, Set<string>>();
  const spellings = new Map<string, Set<string>>();
  for (const entity of entities) {
    if (!/^\/(?!\/)/.test(entity.href)) continue;
    for (const name of [entity.title, ...(entity.aliases || []), ...(routeAliases[entity.href] || [])]) {
      const alias = normalizeAlias(name);
      if (!alias) continue;
      const targets = destinations.get(alias) || new Set<string>();
      targets.add(entity.href);
      destinations.set(alias, targets);
      const originals = spellings.get(alias) || new Set<string>();
      originals.add(name);
      spellings.set(alias, originals);
    }
  }
  const aliases = new Map([...destinations].filter(([, targets]) => targets.size === 1)
    .map(([alias, targets]) => [alias, [...targets][0]]));
  const acronyms = new Map([...spellings].filter(([, names]) =>
    [...names].every(name => /^[A-Z][A-Z0-9]*(?:\/[A-Z0-9]+)*$/.test(name))));
  const patterns = [...aliases.keys()].sort((a, b) => b.length - a.length || a.localeCompare(b)).map(aliasPattern);
  // Unicode letters and digits prevent substring matches, including non-English words.
  const pattern = patterns.length ? new RegExp(`(?<![\\p{L}\\p{N}_])(?:${patterns.join('|')})(?![\\p{L}\\p{N}_])`, 'giu') : null;
  return {aliases, pattern, acronyms};
}

export const wikiRegistry = createWikiRegistry([
  ...content.guides.filter(guide => ['Drug', 'Condition'].includes(guide.type) || guideUrl(guide) === '/drug-repurposing')
    .map(guide => ({title: guide.title, href: guideUrl(guide), aliases: guide.aliases})),
  ...content.glossary.map(term => ({title: term.title, href: '/glossary/' + term.slug, aliases: term.aliases})),
]);

/** Text only: callers keep existing anchors, headings, citations and source titles intact. */
export function wikiTokens(text: string, currentPath = '', linked = new Set<string>(), registry = wikiRegistry): WikiToken[] {
  if (!registry.pattern) return [{text}];
  // Never create a link inside a literal URL, email address, Markdown link or code span.
  const protectedRanges = [...text.matchAll(/https?:\/\/[^\s<>]+|www\.[^\s<>]+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\[[^\]]*\]\([^)]*\)|`[^`]*`/gi)]
    .map(match => [match.index!, match.index! + match[0].length]);
  const tokens: WikiToken[] = [];
  let end = 0;
  // matchAll clones the regular expression; no mutable shared lastIndex across renders.
  for (const match of text.matchAll(registry.pattern)) {
    const start = match.index!;
    const alias = normalizeAlias(match[0]);
    const href = registry.aliases.get(alias);
    // Acronyms retain case so units such as "ms" cannot become disease links.
    if (registry.acronyms.has(alias) && !registry.acronyms.get(alias)!.has(match[0])) continue;
    if (!href || routePath(href) === routePath(currentPath) || linked.has(href)
      || protectedRanges.some(([from, to]) => start < to && start + match[0].length > from)) continue;
    if (start > end) tokens.push({text: text.slice(end, start)});
    tokens.push({text: match[0], href});
    linked.add(href);
    end = start + match[0].length;
  }
  if (end < text.length) tokens.push({text: text.slice(end)});
  return tokens;
}

export function wikiText(text: string, currentPath = '', linked?: Set<string>): ReactNode {
  return wikiTokens(text, currentPath, linked).map((token, index) => token.href
    ? <a key={index} href={token.href} className="wiki-link">{token.text}</a>
    : token.text);
}

/** Each invocation starts a paragraph; an explicit set shares links across its sentences. */
export function wikiTextRenderer(currentPath = ''): WikiTextRenderer {
  return (text, linked) => wikiText(text, currentPath, linked);
}
