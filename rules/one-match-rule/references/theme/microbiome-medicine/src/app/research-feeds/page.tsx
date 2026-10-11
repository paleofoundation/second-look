import type { Metadata } from "next";
import { listAllResearchFeeds, type FeedItem } from "@/lib/content";
import { asciiSlug } from "@/lib/slugs";
import { RF_CATEGORY_ORDER, RF_CATEGORIES } from "@/theme/researchFeedCategories";
import { ArchiveView } from "@/components/ArchiveView";

export const revalidate = 3600;
export const metadata: Metadata = {
  title: "Research Feeds",
  description: "Curated summaries of microbiome research.",
  alternates: { canonical: "/research-feeds" },
};

type Props = { searchParams: Promise<{ mode?: string }> };

function fmtDate(d?: string | null) {
  if (!d) return "";
  return new Date(d).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function excerptText(html?: string | null) {
  if (!html) return "";
  const t = html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  return t.length > 200 ? t.slice(0, 200).replace(/\s+\S*$/, "") + "…" : t;
}

export default async function Page({ searchParams }: Props) {
  const { mode } = await searchParams;
  // "Feed View" — the A–Z index.
  if (mode === "list") return <ArchiveView segment="research-feeds" page={1} />;

  // "Category View" — feeds grouped into topic accordions (matches ?mode=category).
  const feeds = await listAllResearchFeeds();
  const bySlug = new Map(feeds.map((f) => [f.slug, f]));

  return (
    <div className="site-content">
      <main className="main">
        <div className="rgbc-hero">
          <div className="rgbc-hero__wrapper">
            <div className="rgbc-hero__center">
              <div className="rgbc-hero__content">
                <p className="rgbc-breadcrumbs"><a href="/">Home</a> <span>Research Feeds</span></p>
                <h1>Research Feeds</h1>
                <div className="rgbc-hero__excerpt"><p>Curated summaries of microbiome research, grouped by topic.</p></div>
              </div>
            </div>
          </div>
        </div>

        <section className="rgbc-content">
          <div className="rgbc-content__wrapper">
            <div className="rgbc-content__main">
              <div className="rgbc-content__layout-switch" style={{ display: "flex", gap: "1rem", justifyContent: "flex-end", marginBottom: "1rem" }}>
                <strong style={{ color: "var(--color-primary)" }}>Category View</strong>
                <a href="/research-feeds?mode=list">Feed View</a>
              </div>

              {RF_CATEGORY_ORDER.map((cat) => {
                const items = (RF_CATEGORIES[cat] || [])
                  .map((s) => bySlug.get(s))
                  .filter((f): f is FeedItem => Boolean(f));
                if (!items.length) return null;
                return (
                  <details className="rgbc-content__details" key={cat}>
                    <summary className="rgbc-content__details-summary">
                      <div className="rgbc-content__summary-header">
                        <span className="rgbc-content__details-marker">▸</span>
                        <h2 className="rgbc-content__details-heading">
                          {cat} <small style={{ color: "rgba(80,80,80,.7)", fontWeight: 400 }}>({items.length})</small>
                        </h2>
                      </div>
                    </summary>
                    <div className="rgbc-content__details-content rgbc-content__details-content--grid">
                      {items.map((f) => (
                        <a key={f.slug} href={`/research-feeds/${asciiSlug(f.slug) || f.slug}`}>
                          <p>{f.title}</p>
                          <div className="rgbc-content__details-meta">
                            <small className="rgbc-content__details-date">{fmtDate(f.modified_at)}</small>
                          </div>
                          <div className="rgbc-content__details-excerpt">{excerptText(f.excerpt_html)}</div>
                        </a>
                      ))}
                    </div>
                  </details>
                );
              })}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
