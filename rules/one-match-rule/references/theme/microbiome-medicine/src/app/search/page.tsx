import type { Metadata } from "next";
import { supabase } from "@/lib/supabase";
import { contentPath } from "@/lib/content";
import { NOINDEX_ROBOTS } from "@/lib/seo";

export const dynamic = "force-dynamic";
export const metadata: Metadata = {
  title: "Search",
  robots: NOINDEX_ROBOTS,
  alternates: { canonical: "/search" },
};

type Props = { searchParams: Promise<{ q?: string; s?: string }> };
type Item = { type?: string; slug: string; title: string; excerpt_html?: string | null };

function pathFor(type: string, slug: string): string {
  return contentPath(type, slug);
}

// Badge label per content type (matches the original search results page).
const TYPE_LABEL: Record<string, string> = {
  "research-feed": "Research Feed",
  definition: "Definitions",
  condition: "Conditions",
  microbe: "Microbe",
  metal: "Metal",
  intervention: "Interventions",
  supplement: "Supplements",
  guide: "Guides",
  theory: "Theories",
  post: "Article",
  page: "Page",
};

const plain = (html: string | null | undefined): string =>
  (html || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();

// The explore directory shown when the header search opens with no query.
const DIRECTORY: { type: string; seg: string; label: string }[] = [
  { type: "condition", seg: "conditions", label: "Conditions" },
  { type: "definition", seg: "definition", label: "Definitions" },
  { type: "microbe", seg: "microbes", label: "Microbes" },
  { type: "intervention", seg: "interventions", label: "Interventions" },
  { type: "metal", seg: "metals", label: "Metals" },
  { type: "supplement", seg: "supplement", label: "Supplements" },
  { type: "guide", seg: "guide", label: "Guides and Resources" },
  { type: "theory", seg: "theories-hypotheses", label: "Theories and Hypotheses" },
];

async function sample(type: string): Promise<Item[]> {
  try {
    const { data } = await supabase
      .from("content_items")
      .select("slug,title")
      .eq("type", type)
      .eq("status", "publish")
      .order("title")
      .limit(12);
    return (data as Item[]) || [];
  } catch {
    return [];
  }
}

const Magnifier = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none" viewBox="0 0 24 24">
    <path fill="#fff" fillRule="evenodd" d="M15.66 15.66a1.5 1.5 0 0 1 2.12 0l5.78 5.78a1.5 1.5 0 0 1-2.12 2.12l-5.78-5.77a1.5 1.5 0 0 1 0-2.13Z" clipRule="evenodd" />
    <path fill="#fff" fillRule="evenodd" d="M9.75 18a8.25 8.25 0 1 0 0-16.5 8.25 8.25 0 0 0 0 16.5Zm9.75-8.25a9.75 9.75 0 1 1-19.5 0 9.75 9.75 0 0 1 19.5 0Z" clipRule="evenodd" />
  </svg>
);

function SearchForm({ q }: { q: string }) {
  return (
    <form className="rgbc-search__form rgbc-searchresults__form" action="/search" method="get">
      <input
        name="q"
        type="search"
        defaultValue={q}
        className="rgbc-search__input field field--lg"
        placeholder="What do you want to learn about?"
        autoFocus
      />
      <button className="rgbc-search__submit btn btn--lg" type="submit" aria-label="Search">
        <Magnifier />
      </button>
    </form>
  );
}

export default async function SearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const q = (sp.q || sp.s || "").trim();

  // Full-text search across page bodies (title + content + excerpt) — every page that
  // mentions the term, exactly like the original WordPress ?s= results.
  let results: Item[] = [];
  if (q) {
    try {
      const { data } = await supabase
        .from("content_items")
        .select("type,slug,title,excerpt_html")
        .eq("status", "publish")
        .textSearch("search_tsv", q, { type: "websearch", config: "english" })
        .limit(100);
      results = (data as Item[]) || [];
    } catch {
      results = [];
    }
  }

  if (q) {
    return (
      <div className="site-content">
        <main className="main">
          <div className="research-hero">
            <div className="research-hero__container rgbc-searchhero">
              <nav className="breadcrumb">
                <ol className="breadcrumb__wrapper">
                  <li className="breadcrumb__item"><a className="breadcrumb__link" href="/">Home</a></li>
                  <li className="breadcrumb__item"><span className="breadcrumb_last">You searched for {q}</span></li>
                </ol>
              </nav>
              <h1 className="research-hero__title">Search Results for: {q}</h1>
              <SearchForm q={q} />
            </div>
          </div>

          <div className="rgbc-searchresults">
            {results.length === 0 ? (
              <p className="rgbc-searchresults__empty">No results found for “{q}”.</p>
            ) : (
              results.map((it, i) => (
                <article className="rgbc-searchresult" key={i}>
                  <div className="rgbc-searchresult__head">
                    <a className="rgbc-searchresult__title" href={pathFor(it.type as string, it.slug)}>{it.title}</a>
                    <span className="rgbc-searchresult__type">{TYPE_LABEL[it.type as string] || it.type}</span>
                  </div>
                  {plain(it.excerpt_html) && <p className="rgbc-searchresult__excerpt">{plain(it.excerpt_html)}</p>}
                </article>
              ))
            )}
          </div>
        </main>
      </div>
    );
  }

  const sections = await Promise.all(DIRECTORY.map(async (d) => ({ ...d, items: await sample(d.type) })));
  return (
    <div className="site-content flex">
      <main className="main">
        <div className="rgbc-explore">
          <form className="rgbc-search__form rgbc-explore__form" action="/search" method="get">
            <input name="q" type="search" className="rgbc-search__input field field--lg" placeholder="What do you want to learn about?" autoFocus />
            <button className="rgbc-search__submit btn btn--lg" type="submit" aria-label="Search"><Magnifier /></button>
          </form>
          <div className="rgbc-explore__grid">
            {sections.map((s) => (
              <section key={s.type} className="rgbc-explore__section">
                <div className="rgbc-explore__head">
                  <h2 className="rgbc-explore__title">{s.label}</h2>
                  <a className="rgbc-explore__viewall" href={`/${s.seg}`}>View All →</a>
                </div>
                <ul className="rgbc-explore__list">
                  {s.items.map((it, i) => (
                    <li key={i}><a href={pathFor(s.type, it.slug)}>{it.title}</a></li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
