import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { contentPath } from "@/lib/content";
import { AUTHOR_BIOS } from "@/theme/authorsBios";
import { AuthorSocials } from "@/components/AuthorSocials";

// Author archive page: who the author is + everything they've worked on. Mirrors the
// original /author/<slug> page — hero (avatar + "Name, Role"), About (bio), then
// "Recent Posts" cards (date + title link + excerpt), most-recent first, paginated.
const AUTHORS: Record<string, { name: string; role?: string }> = {
  "kmfp84gmail-com": { name: "Karen Pendergrass", role: "Standards Team" },
  kimberly: { name: "Kimberly Eyer" },
  aleru: { name: "Divine Aleru", role: "Microbiome Medicine Research Coordinator" },
  giorgos: { name: "Giorgos Aristotelous" },
  "dr-umar": { name: "Dr. Umar" },
  "jonathan-pendergrass": { name: "Jonathan Pendergrass" },
};

const PAGE_SIZE = 24;

type Post = { type: string; slug: string; title: string; excerpt_html: string | null; modified_at: string | null };

const hrefFor = (type: string, slug: string): string => contentPath(type, slug);

async function authorPosts(name: string, page: number): Promise<{ posts: Post[]; total: number }> {
  const from = (page - 1) * PAGE_SIZE;
  const { data, count } = await supabase
    .from("content_items")
    .select("type,slug,title,excerpt_html,modified_at", { count: "exact" })
    .eq("status", "publish")
    .contains("meta->authors", JSON.stringify([{ name }]))
    .order("modified_at", { ascending: false, nullsFirst: false })
    .range(from, from + PAGE_SIZE - 1);
  return { posts: (data ?? []) as Post[], total: count ?? 0 };
}

export async function authorMetadata(slug: string): Promise<Metadata> {
  const a = AUTHORS[slug];
  if (!a) return {};
  return { title: a.name, alternates: { canonical: `/author/${slug}` } };
}

function Paginator({ slug, page, totalPages }: { slug: string; page: number; totalPages: number }) {
  if (totalPages <= 1) return null;
  const href = (p: number) => `/author/${slug}${p > 1 ? `?page=${p}` : ""}`;
  const set = new Set<number>([1, 2, totalPages - 1, totalPages, page - 1, page, page + 1]);
  const sorted = [...set].filter((n) => n >= 1 && n <= totalPages).sort((a, b) => a - b);
  const items: (number | "ellipsis")[] = [];
  let prev = 0;
  for (const n of sorted) {
    if (prev && n - prev > 1) items.push("ellipsis");
    items.push(n);
    prev = n;
  }
  return (
    <nav className="mbio-pagination" aria-label="Author pages">
      {page > 1 ? (
        <Link className="mbio-pagination__item prev" href={href(page - 1)}>‹ Prev</Link>
      ) : (
        <span className="mbio-pagination__item prev disabled">‹ Prev</span>
      )}
      {items.map((it, i) =>
        it === "ellipsis" ? (
          <span key={`e${i}`} className="mbio-pagination__ellipsis">…</span>
        ) : (
          <Link key={it} className={`mbio-pagination__item${it === page ? " current" : ""}`} href={href(it)}>
            {it}
          </Link>
        )
      )}
      {page < totalPages ? (
        <Link className="mbio-pagination__item next" href={href(page + 1)}>Next ›</Link>
      ) : (
        <span className="mbio-pagination__item next disabled">Next ›</span>
      )}
    </nav>
  );
}

export async function AuthorView({ slug, page = 1 }: { slug: string; page?: number }) {
  const author = AUTHORS[slug];
  if (!author) notFound();
  const bio = AUTHOR_BIOS[author.name];
  const avatar = bio?.avatar ? bio.avatar.replace(/&amp;/g, "&").replace(/s=\d+/, "s=256") : null;
  const cur = Math.max(1, page);
  const { posts, total } = await authorPosts(author.name, cur);
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="site-content">
      <main className="main">
        <div className="research-hero">
          <div className="research-hero__container">
            <div className="research-hero__simple">
              {avatar && (
                <img alt={author.name} src={avatar} className="avatar avatar-256 photo author-avatar" height={256} width={256} decoding="async" />
              )}
              <h1 className="research-hero__title">{author.role ? `${author.name}, ${author.role}` : author.name}</h1>
              <AuthorSocials bio={bio} />
            </div>
          </div>
        </div>

        <div className="research-content">
          <div className="research-content__center research-content__center--author">
            {bio?.bio && (
              <>
                <h3 className="rgbc-accent">About</h3>
                <p>{bio.bio}</p>
              </>
            )}
            <h3 className="rgbc-accent">Recent Posts</h3>
            <div>
              {total === 0 && <p>No published contributions yet.</p>}
              {posts.map((p) => (
                <article className="mbio-card" key={`${p.type}-${p.slug}`}>
                  <div className="mbio-card__border"></div>
                  {p.modified_at && <p className="mbio-card__date">{p.modified_at.slice(0, 10)}</p>}
                  <Link href={hrefFor(p.type, p.slug)} className="mbio-card__title">{p.title}</Link>
                  {p.excerpt_html && (
                    <div className="mbio-card__content">
                      <p>{p.excerpt_html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim()}</p>
                    </div>
                  )}
                </article>
              ))}
            </div>
            <Paginator slug={slug} page={cur} totalPages={totalPages} />
          </div>
        </div>
      </main>
    </div>
  );
}
