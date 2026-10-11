import Link from "next/link";
import { notFound } from "next/navigation";
import { sectionBySegment, getItem, getWpHtml, allConditionLinks } from "@/lib/content";
import { canonicalItemPath, redirectIfUncanonicalSlug } from "@/lib/canonicalSlug";
import { WpRender } from "@/components/WpRender";
import { OrcidIcon } from "@/components/OrcidIcon";
import { Tooltips } from "@/components/Tooltips";
import { RightRail } from "@/components/RightRail";
import { autolinkConditions, autolinkEntities, buildConnections } from "@/lib/connections";
import { getLinkTargets } from "@/lib/linkTargets";
import { isLoggedIn } from "@/lib/supabase/server";
import { applyTextRules } from "@/lib/textRules";
import { getImageMeta } from "@/lib/imageMeta";
import { FavoriteStudyButton } from "@/components/FavoriteStudyButton";
import { ShareButton } from "@/components/ShareButton";
import { AUTHOR_BIOS } from "@/theme/authorsBios";
import { JsonLd } from "@/components/JsonLd";
import { buildJsonLd } from "@/lib/seo";

type Author = { name: string; orcid?: string | null; avatar?: string | null };
type Feed = {
  location?: string[];
  sample_site?: string[];
  species?: string[];
  paper_url?: string;
  conditions?: { label: string; href: string }[];
};

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Taxonomy metadata block (signature studies only).
function graphsHtml(feed: Feed): string {
  const fields: [string, string[] | undefined][] = [
    ["Location", feed.location],
    ["Sample Site", feed.sample_site],
    ["Species", feed.species],
  ];
  const present = fields.filter(([, v]) => Array.isArray(v) && v.length) as [string, string[]][];
  if (!present.length) return "";
  return (
    `<div class="research-feed__graphs">` +
    present
      .map(
        ([title, items]) =>
          `<div class="research-feed__graph"><div class="research-feed__graph-title">${esc(title)}</div>` +
          `<div class="research-feed__graph-items">` +
          items.map((i) => `<div class="research-feed__graph-item">${esc(i)}</div>`).join("") +
          `</div></div>`
      )
      .join("") +
    `</div>`
  );
}

export async function ResearchFeedView({ slug }: { slug: string }) {
  const section = sectionBySegment("research-feeds");
  if (!section) notFound();
  const item = await getItem(section.type, slug);
  if (!item) notFound();
  redirectIfUncanonicalSlug("research-feeds", slug, item.slug);
  const selfPath = canonicalItemPath("research-feeds", item.slug);

  const meta = (item.meta || {}) as Record<string, unknown>;
  const feed = (meta.feed || {}) as Feed;
  const conditions = Array.isArray(feed.conditions) ? feed.conditions : [];
  const condLinks = await allConditionLinks();

  const wpHtml = await getWpHtml(item.id);
  if (wpHtml) {
    // Universal rule: internally link the conditions this study discusses + surface them
    // (max 3, conditions-first) in the right-rail Connections.
    const { html: linkedHtml, linked } = autolinkConditions(wpHtml, condLinks);
    return (
      <WpRender
        item={item}
        html={linkedHtml}
        path={selfPath}
        type="research-feed"
        connectionsOverride={buildConnections(meta.connections, conditions, linked)}
        breadcrumbs={[
          { name: "Home", url: "/" },
          { name: "Research Feeds", url: "/research-feeds" },
          { name: item.title, url: selfPath },
        ]}
      />
    );
  }

  const authors: Author[] = (Array.isArray(meta.authors) ? (meta.authors as Author[]) : []).map((a) => ({
    ...a,
    avatar: (a.avatar || AUTHOR_BIOS[a.name]?.avatar || null)?.replace(/&amp;/g, "&") ?? null,
    orcid: a.orcid || AUTHOR_BIOS[a.name]?.orcid || null,
  }));
  const avatars = authors.filter((a) => a.avatar);
  const images = await getImageMeta();
  const loggedIn = await isLoggedIn();
  const linkedC = autolinkConditions(applyTextRules(graphsHtml(feed) + (item.content_html || ""), { images }), condLinks);
  const contentHtml = autolinkEntities(linkedC.html, await getLinkTargets(), selfPath).html;
  const linked = linkedC.linked;
  const connections = buildConnections(meta.connections, conditions, linked);
  const updated = item.modified_at ? item.modified_at.slice(0, 10) : null;
  const doi = feed.paper_url?.match(/doi\.org\/(.+)$/)?.[1];
  const jsonLd = buildJsonLd(item, {
    path: selfPath,
    type: "research-feed",
    authors,
    doi,
    breadcrumbs: [
      { name: "Home", url: "/" },
      { name: "Research Feeds", url: "/research-feeds" },
      { name: item.title, url: selfPath },
    ],
  });

  return (
    <div className="site-content flex">
      <JsonLd data={jsonLd} />
      <main className="main">
        <div className="research-hero ">
          <div className="research-hero__wrapper">
            <div className="research-hero__center">
              <p className="rgbc-breadcrumbs">
                <Link href="/">Home</Link> <Link href="/research-feeds">Research Feeds</Link> <span>{item.title}</span>
              </p>
              <div className="research-hero__center-content research-hero__center-content--fullwidth">
                <h1 className="research-hero__center-title">
                  {item.title}
                  {feed.paper_url && (
                    <a className="research-hero__external-link" href={feed.paper_url} target="_blank" rel="noreferrer">
                      Original paper
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                        <polyline points="15 3 21 3 21 9" />
                        <line x1="10" x2="21" y1="14" y2="3" />
                      </svg>
                    </a>
                  )}
                </h1>
              </div>

              {conditions.length > 0 && (
                <div className="research-hero__categories">
                  <div className="rgbc-content__details-categories">
                    <ul>
                      {conditions.map((c, i) => (
                        <li key={i}>
                          <a href={c.href}>{c.label}</a>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              <div className="research-hero__center-tags">
                <FavoriteStudyButton itemId={item.id} />
                <ShareButton />
              </div>
            </div>

            {authors.length > 0 && (
              <div className="research-hero__right">
                {avatars.length > 0 && (
                  <div className="research-hero__right-users">
                    <ul className="research-hero__tooltips-list research-hero__tooltips-list--an-image-as-link">
                      {avatars.map((a, i) => {
                        const ai = authors.indexOf(a);
                        return (
                          <li key={i}>
                            <span className="rgbc-tooltip" title={AUTHOR_BIOS[a.name] ? `.author-bio-${ai}` : undefined}>
                              <img alt={a.name} src={a.avatar as string} className="avatar avatar-96 photo" height={96} width={96} />
                            </span>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
                <div className="research-hero__right-meta">
                  <div className="research-hero__right-meta-item">
                    <p><span>Researched by:</span></p>
                    <div className="research-hero__right-meta-user">
                      <ul className="research-hero__tooltips-list ">
                        {authors.map((a, i) => (
                          <li key={i}>
                            <span className="rgbc-tooltip" title={AUTHOR_BIOS[a.name] ? `.author-bio-${i}` : undefined}>{a.name}</span>
                            {a.orcid && (<a className="orchid-id" target="_blank" rel="noreferrer" href={a.orcid} aria-label="ORCID iD"><OrcidIcon /></a>)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  {updated && (<div className="research-hero__right-meta-item"><p>Last Updated: {updated}</p></div>)}
                </div>
                {authors.map((a, i) => {
                  const b = AUTHOR_BIOS[a.name];
                  return b ? (
                    <div key={i} className={`tooltip author-bio-${i}`}>
                      <div className="tooltip__header">{a.name}</div>
                      <div className="tooltip__content">
                        {b.avatar && <img src={b.avatar} alt={a.name} className="avatar avatar-96 photo" />}
                        <p>{b.bio}</p>
                        {b.profile && <a href={b.profile}>Read More</a>}
                      </div>
                    </div>
                  ) : null;
                })}
              </div>
            )}
          </div>
        </div>

        <Tooltips />

        <div className="research-content">
          <div className="research-content__wrapper">
            <div className="research-content__left js-research-sidebar">
              <div className="research-content__left-menu">
                <div className="post-content__list post-sidebar">
                  <div className="post-content__item post-content__item--h2">
                    <span className="post-content__title">
                      <a className="post-content__link" href="/research-feeds">
                        <svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                          <rect width="8" height="4" x="8" y="2" rx="1" ry="1" />
                          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
                          <path d="M12 11h4" /><path d="M12 16h4" /><path d="M8 11h.01" /><path d="M8 16h.01" />
                        </svg>
                        Dashboard
                      </a>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="research-content__center entry-content" data-gated={loggedIn ? undefined : "research-feed"} dangerouslySetInnerHTML={{ __html: contentHtml }} />

            <RightRail connections={connections} />
          </div>
        </div>
      </main>
    </div>
  );
}
