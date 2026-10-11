import Link from "next/link";
import type { ComponentProps } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ConditionsTable } from "@/components/ConditionsTable";
import { sectionBySegment, getItem, stripHost, getWpHtml, signatureMmaCount } from "@/lib/content";
import { canonicalItemPath, redirectIfUncanonicalSlug } from "@/lib/canonicalSlug";
import { WpRender } from "@/components/WpRender";
import { MicrobiomeSignature } from "@/components/MicrobiomeSignature";
import { Tooltips } from "@/components/Tooltips";
import { ContentAccordions } from "@/components/ContentAccordions";
import { AUTHOR_BIOS } from "@/theme/authorsBios";
import { linkifyClassifications } from "@/lib/classifications";
import { applyTextRules } from "@/lib/textRules";
import { getImageMeta } from "@/lib/imageMeta";
import { normSrc } from "@/lib/imageClassify";
import { StudyActions } from "@/components/StudyActions";
import { FollowButton } from "@/components/FollowButton";
import { ShareButton } from "@/components/ShareButton";
import { SectionNav, type NavGroup } from "@/components/SectionNav";
import { OrcidIcon } from "@/components/OrcidIcon";
import { PageSnapshot } from "@/components/PageSnapshot";
import { RightRail } from "@/components/RightRail";
import { JsonLd } from "@/components/JsonLd";
import { buildMetadata, buildJsonLd } from "@/lib/seo";
import { resolveConnections, autolinkEntities } from "@/lib/connections";
import { getLinkTargets } from "@/lib/linkTargets";

type Heading = { level: number; text: string; id: string };
type Author = { name: string; orcid?: string | null; avatar?: string | null };
type SigItem = { name: string; value: number; has_info?: boolean };

function tableOfContents(html: string): Heading[] {
  const out: Heading[] = [];
  const re = /<h([23])\b([^>]*)>([\s\S]*?)<\/h\1>/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html))) {
    const level = Number(m[1]);
    const text = m[3].replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
    if (!text) continue;
    const idm = /id="([^"]*)"/.exec(m[2] || "");
    const id = idm ? idm[1] : "h-" + text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    out.push({ level, text, id });
  }
  return out;
}

function referenceCount(html: string): number {
  const nums = new Set<string>();
  const re = /\[(\d{1,3})\]/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html))) nums.add(m[1]);
  return nums.size;
}

// The signature modal's "Studies" list = the page's referenced studies.
function extractStudies(html: string): { title: string; url: string }[] {
  const out: { title: string; url: string }[] = [];
  const seen = new Set<string>();
  const re = /rgbc-reference-tooltip__content[^>]*>([\s\S]*?)<\/div>/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html))) {
    const block = m[1];
    const titleM = /<a\s+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/.exec(block);
    if (!titleM) continue;
    const title = titleM[2].replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
    if (!title || seen.has(title)) continue;
    seen.add(title);
    const reviewM = /rgbc-reference-tooltip__btn[^>]*href="([^"]+)"/.exec(block);
    out.push({ title, url: reviewM ? (stripHost(reviewM[1]) || reviewM[1]) : titleM[1] });
  }
  return out;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// The original FAQ section was generated at runtime (never stored). Rebuild it
// from the page's own sections so the FAQs heading isn't empty.
function getFaqs(html: string, title: string): { q: string; a: string }[] {
  if (!/id="h-faqs"/.test(html)) return [];
  const qmap: [RegExp, string][] = [
    [/overview/i, `What is ${title}?`],
    [/associated conditions/i, `What conditions are associated with ${title}?`],
    [/causes/i, `What causes ${title}?`],
    [/symptoms/i, `What are the symptoms of ${title}?`],
    [/diagnos/i, `How is ${title} diagnosed?`],
    [/treatment|intervention/i, `What helps treat ${title}?`],
    [/prevent/i, `Can ${title} be prevented?`],
    [/risk/i, `What are the risk factors for ${title}?`],
  ];
  const faqs: { q: string; a: string }[] = [];
  const re = /<h([23])\b[^>]*>([\s\S]*?)<\/h\1>([\s\S]*?)(?=<h[23]\b|$)/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html))) {
    if (faqs.length >= 3) break;
    const heading = m[2].replace(/<[^>]+>/g, "").trim();
    if (!heading) continue;
    let q = "";
    for (const [rx, qq] of qmap) { if (rx.test(heading)) { q = qq; break; } }
    if (!q || faqs.some((f) => f.q === q)) continue;
    let a = "";
    const pre = /<p[^>]*>([\s\S]*?)<\/p>/gi;
    let pm: RegExpExecArray | null;
    while ((pm = pre.exec(m[3]))) {
      const t = pm[1].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
      if (t.length >= 40) { a = t; break; }
    }
    if (!a) continue;
    if (a.length > 700) a = a.slice(0, 700).replace(/\s+\S*$/, "") + "…";
    faqs.push({ q, a });
  }
  return faqs;
}

function injectFaqs(html: string, faqs: { q: string; a: string }[]): string {
  if (!faqs.length || !/id="h-faqs"/.test(html)) return html;
  const acc =
    `<div class="rgbc-faq-block">` +
    faqs.map((f) => `<details class="rgbc-faq-item"><summary><span class="rgbc-faq-icon"></span><span class="rgbc-faq-q">${escapeHtml(f.q)}</span></summary><div class="rgbc-faq-a"><strong>Quick answer:</strong> ${escapeHtml(f.a)}</div></details>`).join("") +
    `</div>`;
  return html.replace(/(<h2\b[^>]*id="h-faqs"[^>]*>)[\s\S]*?(<\/h2>)((?:\s*<p[^>]*>\s*<\/p>)*)/i, `$1FAQs$2${acc}`);
}

const SECTION_ICONS: Record<string, string> = {
  "h-overview": "overview.webp",
  "h-interventions": "research.webp",
  "h-faqs": "faq.webp",
  "rgbc-research-feed": "feed.webp",
  "rgbc-update-history": "updates.webp",
  "h-references": "references.webp",
  "rgbc-database": "database.webp",
};
function sectionIcon(id: string, text: string): string {
  if (SECTION_ICONS[id]) return SECTION_ICONS[id];
  const t = (id + " " + text).toLowerCase();
  if (/overview/.test(t)) return "overview.webp";
  if (/interven/.test(t)) return "research.webp";
  if (/faq/.test(t)) return "faq.webp";
  if (/research|feed/.test(t)) return "feed.webp";
  if (/update|history/.test(t)) return "updates.webp";
  if (/reference/.test(t)) return "references.webp";
  if (/signature|database|abundance/.test(t)) return "database.webp";
  return "overview.webp";
}
function buildNavGroups(toc: Heading[], hasSignature: boolean): NavGroup[] {
  const groups: NavGroup[] = [];
  for (const h of toc) {
    if (h.level === 2) groups.push({ id: h.id, text: h.text, icon: sectionIcon(h.id, h.text), children: [] });
    else if (groups.length) groups[groups.length - 1].children.push({ id: h.id, text: h.text });
  }
  if (hasSignature && !groups.some((g) => g.id === "rgbc-database")) {
    const sig: NavGroup = { id: "rgbc-database", text: "Microbiome Signature", icon: "database.webp", children: [], isSignature: true };
    groups.splice(groups.length > 1 ? 1 : groups.length, 0, sig);
  }
  return groups;
}

export async function ArticleView({ segment, slug }: { segment: string; slug: string }) {
  const section = sectionBySegment(segment) ?? { segment: "", type: "post", label: "Blog", nav: "Blog", blurb: "" };
  const item = await getItem(section.type, slug);
  if (!item) notFound();
  redirectIfUncanonicalSlug(section.type === "post" ? "" : segment, slug, item.slug);

  const images = await getImageMeta();
  const wpHtml = await getWpHtml(item.id);
  if (wpHtml) {
    const wpPath = canonicalItemPath(section.type === "post" ? "" : segment, item.slug);
    return (
      <WpRender
        item={item}
        html={wpHtml}
        path={wpPath}
        type={section.type}
        images={images}
        breadcrumbs={[
          { name: "Home", url: "/" },
          { name: section.label, url: section.type === "post" ? "/" : `/${segment}` },
          { name: item.title, url: wpPath },
        ]}
      />
    );
  }

  const meta = (item.meta || {}) as Record<string, unknown>;
  const html = item.content_html || "";
  // Generated pages (taxon/condition) bake a real .rgbc-faq-block with authored, taxon-specific
  // FAQs. Only auto-build FAQs for pages that LACK one (older migrated pages with an empty FAQ
  // section). Auto-building over a real block duplicated it and re-escaped entities + citations
  // into plain text (e.g. &ldquo; shown literally, [1] no longer a superscript link).
  const faqs = html.includes("rgbc-faq-block") ? [] : getFaqs(html, item.title);
  let contentHtml = applyTextRules(linkifyClassifications(injectFaqs(html, faqs)), { images });
  const excerptHtml = applyTextRules(item.excerpt_html || "", { images });
  const toc = tableOfContents(html);
  const refs = referenceCount(html);
  // Identified MMAs = microbes given their own sidebar in the signature (has_info), NOT studies.
  const mmas = signatureMmaCount(meta) || null;
  // Resolve each author's photo from AUTHOR_BIOS when meta omits one, so every page
  // shows a face at the top (e.g. generated pages credited to the founder).
  const authors: Author[] = (Array.isArray(meta.authors) ? (meta.authors as Author[]) : []).map((a) => ({
    ...a,
    avatar: (a.avatar || AUTHOR_BIOS[a.name]?.avatar || null)?.replace(/&amp;/g, "&") ?? null,
    orcid: a.orcid || AUTHOR_BIOS[a.name]?.orcid || null,
  }));
  const didYouKnow = typeof meta.did_you_know === "string" ? applyTextRules(meta.did_you_know.replace(/^Did you know\??\s*/i, "")) : null;
  const signature = meta.signature as { levels?: Record<string, SigItem[]>; studies?: { title: string; url: string }[] } | undefined;
  const hasSignature = !!signature?.levels;
  // Per-type hero features (from auditing each post type's real page).
  const showInterventions = section.type === "condition";
  const showResearchFeed = ["condition", "microbe", "intervention", "definition", "metal", "guide", "post"].includes(section.type);
  const showStudyActions = ["theory", "research-feed"].includes(section.type);
  // Dedicated left-panel illustration (separate from the featured image).
  const heroImg = typeof meta.hero_image === "string" ? meta.hero_image : null;
  const img = heroImg || stripHost(item.featured_image_url);
  const heroMeta = img ? images.get(normSrc(img)) : undefined;
  const updated = item.modified_at ? item.modified_at.slice(0, 10) : null;
  const avatars = authors.filter((a) => a.avatar);
  const selfPath = canonicalItemPath(section.type === "post" ? "" : segment, item.slug);
  // Autolink the first mention of every concept entity (metals, definitions, microbes,
  // interventions, conditions…) in the body — sitewide internal-linking rule.
  contentHtml = autolinkEntities(contentHtml, await getLinkTargets(), selfPath).html;
  // Taxon pages ship a structured meta.conditions + a <!--CONDITIONS_TABLE--> marker where the
  // interactive Conditions table mounts. Split the body there and slot the component in; every
  // other page (no marker) renders exactly as before.
  const condMarker = "<!--CONDITIONS_TABLE-->";
  const condData = meta.conditions as ComponentProps<typeof ConditionsTable>["data"] | undefined;
  const hasCond = !!condData && contentHtml.includes(condMarker);
  const [condBefore, condAfter] = hasCond ? contentHtml.split(condMarker) : ["", ""];
  const connections = resolveConnections(meta.connections, html, selfPath);
  const jsonLd = buildJsonLd(item, {
    path: selfPath,
    type: section.type,
    authors,
    image: img,
    imageAlt: heroMeta?.alt,
    imageCaption: heroMeta?.caption,
    imageWidth: heroMeta?.width,
    imageHeight: heroMeta?.height,
    faqs,
    breadcrumbs: [
      { name: "Home", url: "/" },
      { name: section.label, url: section.type === "post" ? "/" : `/${segment}` },
      { name: item.title, url: selfPath },
    ],
  });

  return (
    <div className="site-content flex">
      <JsonLd data={jsonLd} />
      <main className="main">
        <div className="research-hero ">
          <div className="research-hero__wrapper">
            <div className="research-hero__left">
              {section.type === "post" ? (
                <div className="research-hero__left-content" dangerouslySetInnerHTML={{ __html: excerptHtml }} />
              ) : (
                <>
                  {img && (
                    <img
                      src={img}
                      alt={heroMeta?.alt || item.title}
                      className="research-hero__left-image"
                      width={heroMeta?.width || undefined}
                      height={heroMeta?.height || undefined}
                      sizes="(max-width: 768px) 100vw, 150px"
                      decoding="async"
                      fetchPriority="high"
                    />
                  )}
                  {didYouKnow && (
                    <div className="research-hero__left-content">
                      <p><strong>Did you know?</strong><br />{didYouKnow}</p>
                    </div>
                  )}
                </>
              )}
            </div>

            <div className="research-hero__center">
              <nav className="breadcrumb">
                <ol className="breadcrumb__wrapper">
                  <li className="breadcrumb__item"><Link className="breadcrumb__link" href="/">Home</Link></li>
                  <li className="breadcrumb__item"><Link className="breadcrumb__link" href={section.type === "post" ? "/" : `/${segment}`}>{section.label}</Link></li>
                  <li className="breadcrumb__item"><Link className="breadcrumb__link" href={selfPath}>{item.title}</Link></li>
                  <li className="breadcrumb__item"><span className="breadcrumb_last"><span className="badge">✓ Evidence based</span></span></li>
                </ol>
              </nav>

              <div className="research-hero__center-content ">
                <h1 className="research-hero__center-title">{item.title}</h1>
                {item.excerpt_html && (
                  <div className="research-hero__center-text" dangerouslySetInnerHTML={{ __html: excerptHtml }} />
                )}
              </div>

              <div className="research-hero__categories"></div>

              {(hasSignature || showInterventions || showResearchFeed) && (
                <div className="research-hero__center-tags">
                  {hasSignature && (
                    <button type="button" data-modal-id="research-diagram-modal" className="research-hero__center-tag" style={{ cursor: "pointer", border: "none", font: "inherit" }}>
                      <img src="/wp-content/themes/rgbcode/static_media/examinedatabase_white.webp" alt="" width={18} height={18} /> Microbiome Signature
                    </button>
                  )}
                  {showInterventions && (
                    <a className="research-hero__center-tag" href="#h-interventions">
                      <img src="/wp-content/themes/rgbcode/static_media/research.webp" alt="" width={18} height={18} /> Interventions
                    </a>
                  )}
                  {showResearchFeed && <FollowButton itemId={item.id} />}
                  <ShareButton />
                </div>
              )}
              {showStudyActions && (
                <StudyActions
                  itemId={item.id}
                  title={item.title}
                  authors={authors.map((a) => a.name)}
                  year={updated ? updated.slice(0, 4) : undefined}
                  url={`https://microbiomemedicine.com${selfPath}`}
                />
              )}
            </div>

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
                {authors.length > 0 && (
                  <div className="research-hero__right-meta-item">
                    <p><span>Researched by:</span></p>
                    <div className="research-hero__right-meta-user">
                      <ul className="research-hero__tooltips-list ">
                        {authors.map((a, i) => (
                          <li key={i}>
                            <span>{a.name}</span>
                            {a.orcid && (<a className="orchid-id" target="_blank" rel="noreferrer" href={a.orcid} aria-label="ORCID iD"><OrcidIcon /></a>)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
                {updated && (<div className="research-hero__right-meta-item"><p>Last Updated: {updated}</p></div>)}
              </div>
              {(refs > 0 || mmas || condData) && <PageSnapshot refs={refs} mmas={mmas} stats={condData?.summary} />}
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
          </div>
        </div>

        {hasSignature && (
          <MicrobiomeSignature
            slug={slug}
            title={item.title}
            levels={signature!.levels!}
            studies={Array.isArray(signature!.studies) && signature!.studies!.length ? signature!.studies! : extractStudies(html)}
          />
        )}
        <Tooltips />
        <ContentAccordions />

        <div className="research-content">
          <div className="research-content__wrapper">
            <SectionNav groups={buildNavGroups(toc, hasSignature)} />

            {hasCond ? (
              <div className="research-content__center entry-content">
                <div dangerouslySetInnerHTML={{ __html: condBefore }} />
                <ConditionsTable data={condData!} />
                {condAfter && <div dangerouslySetInnerHTML={{ __html: condAfter }} />}
              </div>
            ) : (
              <div className="research-content__center entry-content" dangerouslySetInnerHTML={{ __html: contentHtml }} />
            )}

            <RightRail connections={connections} />
          </div>
        </div>
      </main>
    </div>
  );
}

export async function articleMetadata(segment: string, slug: string): Promise<Metadata> {
  const section = sectionBySegment(segment) ?? { segment: "", type: "post", label: "Blog", nav: "Blog", blurb: "" };
  const item = await getItem(section.type, slug);
  if (!item) return {};
  const meta = (item.meta || {}) as Record<string, unknown>;
  const authors = Array.isArray(meta.authors) ? (meta.authors as { name: string; orcid?: string | null }[]) : [];
  const image = (typeof meta.hero_image === "string" ? meta.hero_image : null) || stripHost(item.featured_image_url);
  const path = canonicalItemPath(section.type === "post" ? "" : segment, item.slug);
  return buildMetadata(item, { path, type: section.type, authors, image });
}
