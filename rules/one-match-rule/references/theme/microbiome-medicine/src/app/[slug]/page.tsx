import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getRootBySlug, getWpHtml, stripHost } from "@/lib/content";
import { ArticleView } from "@/components/ArticleView";
import { WpRender } from "@/components/WpRender";
import { buildMetadata } from "@/lib/seo";
import { canonicalItemPath, redirectIfUncanonicalSlug } from "@/lib/canonicalSlug";

export const revalidate = 3600;

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const item = await getRootBySlug(slug);
  if (!item) return {};
  const meta = (item.meta || {}) as Record<string, unknown>;
  const authors = Array.isArray(meta.authors) ? (meta.authors as { name: string; orcid?: string | null }[]) : [];
  const image = (typeof meta.hero_image === "string" ? meta.hero_image : null) || stripHost(item.featured_image_url);
  return buildMetadata(item, { path: canonicalItemPath("", item.slug), type: item.type, authors, image });
}

export default async function RootContentPage({ params }: Props) {
  const { slug } = await params;
  const item = await getRootBySlug(slug);
  if (!item) notFound();
  redirectIfUncanonicalSlug("", slug, item.slug);

  // Captured WordPress content (imported posts + static pages) renders verbatim via WpRender.
  // STOP pages and imported posts carry their full hero, "Did you know?", Update History, and
  // references in this captured HTML, so they must render here — the ArticleView post template
  // would drop that hero. type="post" preserves STOP detection + sidebar ordering.
  const wpHtml = await getWpHtml(item.id);
  if (wpHtml) {
    return (
      <WpRender
        item={item}
        html={wpHtml}
        path={canonicalItemPath("", item.slug)}
        type={item.type === "post" ? "post" : "page"}
        breadcrumbs={[
          { name: "Home", url: "/" },
          { name: item.title, url: canonicalItemPath("", item.slug) },
        ]}
      />
    );
  }

  // Blog posts without captured WordPress content use the full research template.
  if (item.type === "post") return <ArticleView segment="" slug={slug} />;

  // Fallback: clean, theme-styled article.
  return (
    <main className="site-content">
      <div className="entry-content" style={{ maxWidth: "65rem", margin: "0 auto", padding: "40px 20px 72px" }}>
        <h1 style={{ fontFamily: "var(--font-serif)", fontSize: "2.5rem", lineHeight: 1.15, marginBottom: "1rem" }}>{item.title}</h1>
        <hr style={{ border: 0, borderTop: "1px dashed #cbd5e1", margin: "1.5rem 0" }} />
        <div dangerouslySetInnerHTML={{ __html: item.content_html || "" }} />
      </div>
    </main>
  );
}
