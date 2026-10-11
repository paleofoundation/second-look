import { MicrobiomeSignature } from "@/components/MicrobiomeSignature";
import { Tooltips } from "@/components/Tooltips";
import { JsonLd } from "@/components/JsonLd";
import { WpInteractivity } from "@/components/WpInteractivity";
import { WpDiagram } from "@/components/WpDiagram";
import { ShareButton } from "@/components/ShareButton";
import { buildJsonLd } from "@/lib/seo";
import { getFaqs, injectFaqs } from "@/lib/faqs";
import { connectionsBlockHtml, autolinkEntities } from "@/lib/connections";
import { getLinkTargets } from "@/lib/linkTargets";
import { isLoggedIn } from "@/lib/supabase/server";
import { revealResearchFeedWalls } from "@/lib/researchFeedReveal";
import { AUTHOR_BIOS } from "@/theme/authorsBios";
import { linkifyClassifications } from "@/lib/classifications";
import { applyTextRules } from "@/lib/textRules";
import { stripHost, referenceCount, signatureMmaCount, type ContentItem } from "@/lib/content";
import { ORCID_SVG } from "@/components/OrcidIcon";
import { normSrc, type ImageMeta } from "@/lib/imageClassify";

type SigItem = { name: string; value: number; has_info?: boolean };

// The site must contain NO purple — the WP theme/markup carries purple accents
// (e.g. the paywall lock's #6e488c stroke + #d7cedf bg, inlined in the captured
// HTML). Map every purple to the brand red/pink at render time.
const PURPLE_TO_RED: [RegExp, string][] = [
  [/#6e488c/gi, "#cc3333"], [/#562e69/gi, "#a02727"], [/#5e3b76/gi, "#a02727"],
  [/#5f3b76/gi, "#a02727"], [/#2f1e4e/gi, "#1a1a2e"], [/#330968/gi, "#1a1a2e"],
  [/#7a00df/gi, "#cc3333"], [/#4721fb/gi, "#cc3333"], [/#ab1dfe/gi, "#cc3333"],
  [/#9b51e0/gi, "#cc3333"], [/#e2d9f3/gi, "#f7e6e6"], [/#dad0ec/gi, "#f7e6e6"],
  [/#d7cedf/gi, "#f7e6e6"], [/#e0dce5/gi, "#e3c9c9"], [/#efebf2/gi, "#f7e6e6"],
];
function dePurple(html: string): string {
  let out = html;
  for (const [re, red] of PURPLE_TO_RED) out = out.replace(re, red);
  return out;
}

// Rule (Karen, locked in): every conditions page's left sidebar lists its top-level
// sections in this canonical order — Overview, Microbiome Signature, Interventions,
// FAQs, Research Feed, Update History, References. The captured sidebar mirrors the
// authored section order, which drifted on a couple of migrated pages. This reorders
// the sidebar's top-level groups (each h2 item + its h3/h4 children) into the canonical
// order, leaving anchors + children intact. Sections not present are simply skipped;
// unknown sections keep their place. It is a no-op on already-correct pages.
// Canonical top-level sidebar order per page type (Karen's rules). Conditions:
// Overview, Microbiome Signature, Interventions, FAQs, Research Feed, Update History,
// References. Interventions: Overview (with Mechanism of Action as a subsection),
// Conditions, FAQs, Research Feed, Update History, References.
const SIDEBAR_ORDER: Record<string, (x: string) => number> = {
  condition: (x) =>
    x.includes("overview") ? 0 : x.includes("microbiome signature") ? 1 : x.startsWith("intervention") ? 2 :
    x.startsWith("faq") ? 3 : x.includes("research feed") ? 4 : x.includes("update history") ? 5 : x.includes("reference") ? 6 : -1,
  intervention: (x) =>
    x.includes("overview") ? 0 : x.startsWith("condition") ? 1 : x.startsWith("faq") ? 2 :
    x.includes("research feed") ? 3 : x.includes("update history") ? 4 : x.includes("reference") ? 5 : -1,
  // STOP (Suggested Termination of Practice) pages — their own post-type structure.
  stop: (x) =>
    x.includes("overview") ? 0 : x.includes("critical finding") ? 1 : x.startsWith("recommendation") ? 2 :
    x.startsWith("faq") ? 3 : x.includes("research feed") ? 4 : x.includes("update history") ? 5 : x.includes("reference") ? 6 : -1,
};
function reorderSidebar(html: string, type: string): string {
  const rankFn = SIDEBAR_ORDER[type];
  if (!rankFn) return html;
  const marker = 'post-content__list post-sidebar">';
  const s = html.indexOf(marker);
  if (s < 0) return html;
  const idx = s + marker.length;
  const itemRe = /^(\s*)<div class="post-content__item[^"]*">[\s\S]*?<\/div>/;
  const items: string[] = [];
  let rest = html.slice(idx);
  for (;;) {
    const m = rest.match(itemRe);
    if (!m) break;
    items.push(m[0]);
    rest = rest.slice(m[0].length);
  }
  if (!items.length) return html;
  const orig = items.join("");
  const isH2 = (it: string) => /post-content__item--h2/.test(it);
  const groups: string[][] = [];
  for (const it of items) {
    if (isH2(it) || !groups.length) groups.push([it]);
    else groups[groups.length - 1].push(it);
  }
  const label = (it: string) => {
    const m = it.match(/post-content__link[^>]*>([\s\S]*?)<\/a>/);
    return m ? m[1].replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim() : "";
  };
  const keyed = groups.map((g, i) => ({ g, i, r: rankFn(label(g[0]).toLowerCase()) }));
  let prev = -0.5; // keep unknown sections pinned after their preceding known section
  for (const k of keyed) {
    if (k.r >= 0) prev = k.r;
    else k.r = prev + 0.01;
  }
  const sorted = [...keyed].sort((a, b) => a.r - b.r || a.i - b.i);
  const newRegion = sorted.map((k) => k.g.join("")).join("");
  if (newRegion === orig) return html;
  return html.slice(0, idx) + newRegion + html.slice(idx + orig.length);
}

// The signature modal's "Studies" list = the microbiome-signature studies the
// original page lists inside the diagram modal (.modal--research-diagram__list),
// i.e. the research-feed signature studies for this condition.
function extractSignatureStudies(html: string): { title: string; url: string }[] {
  const out: { title: string; url: string }[] = [];
  const seen = new Set<string>();
  const listM = /<ul[^>]*class="modal--research-diagram__list"[^>]*>([\s\S]*?)<\/ul>/.exec(html);
  if (!listM) return out;
  const re = /<a\s+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(listM[1]))) {
    const url = stripHost(m[1]) || m[1];
    const title = m[2].replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
    if (title && !seen.has(url)) { seen.add(url); out.push({ title, url }); }
  }
  return out;
}

// Fallback for non-signature pages: the page's referenced studies.
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

// Authorless captured pages have no "Researched by" block in their hero. When meta
// credits an author (the site founder is the default for authorless research content),
// inject the same hero author markup the themed pages use — a visible photo row + the
// "Researched by" names + hover bios — so attribution (and a face) is shown at the top.
function researchedByHtml(authors: { name: string; orcid?: string | null; avatar?: string | null }[]): string {
  if (!authors.length) return "";
  const resolved = authors.map((a, i) => {
    const info = AUTHOR_BIOS[a.name];
    const avatar = (a.avatar || info?.avatar || "").replace(/&amp;|&/g, "&amp;"); // HTML entity form
    return { name: a.name, orcid: a.orcid || info?.orcid || null, avatar, bio: info?.bio || "", cls: `user-bio-auto-${i + 1}` };
  });
  const photos = resolved.filter((r) => r.avatar);
  const photoRow = photos.length
    ? `<div class="research-hero__right-users"><ul class="research-hero__tooltips-list research-hero__tooltips-list--an-image-as-link">${photos
        .map(
          (r) =>
            `<li><span class="rgbc-tooltip" data-options="position:left"${r.bio ? ` title=".${r.cls}"` : ""}><img alt="${r.name}" src="${r.avatar}" class="avatar avatar-96 photo" height="96" width="96" /></span></li>`
        )
        .join("")}</ul></div>`
    : "";
  const names = `<div class="research-hero__center-meta-item"><p><span>Researched by:</span></p><ul class="research-hero__tooltips-list">${resolved
    .map((r) => `<li><span>${r.name}</span>${r.orcid ? `<a class="orchid-id" target="_blank" href="${r.orcid}" aria-label="ORCID iD">${ORCID_SVG}</a>` : ""}</li>`)
    .join("")}</ul></div>`;
  const bios = resolved
    .filter((r) => r.bio)
    .map(
      (r) =>
        `<div class="tooltip ${r.cls}"><div class="tooltip__header">${r.name}</div><div class="tooltip__content"><p>${
          r.avatar ? `<img alt="User avatar" src="${r.avatar}" class="avatar avatar-96 photo" height="96" width="96" />` : ""
        }${r.bio}</p></div></div>`
    )
    .join("");
  return `<div class="research-hero__center-meta">${photoRow}${names}${bios}</div>`;
}

// Renders the captured WordPress content region verbatim (pixel-exact), injecting
// our generated FAQs and re-attaching the interactive pieces.
export async function WpRender({
  item,
  html,
  path,
  type,
  breadcrumbs,
  connectionsOverride,
  images,
}: {
  item: ContentItem;
  html: string;
  path: string;
  type: string;
  breadcrumbs: { name: string; url: string }[];
  connectionsOverride?: { label: string; href: string }[];
  images?: Map<string, ImageMeta>;
}) {
  const meta = (item.meta || {}) as Record<string, unknown>;
  const signature = meta.signature as { levels?: Record<string, SigItem[]> } | undefined;
  const hasSignature = !!signature?.levels;
  const authors = Array.isArray(meta.authors) ? (meta.authors as { name: string; orcid?: string | null }[]) : [];
  // STOP pages are their own post-type: they carry hand-authored FAQs baked into the
  // content, so skip the section-scraped auto-FAQ generation for them.
  const isStop = type === "post" && /^stop-/.test(item.slug);
  const faqs = isStop ? [] : getFaqs(html, item.title);
  // Inject the "Connections" list above the right-rail actions (Send feedback). A caller
  // override (e.g. research-feed conditions) wins, else the curated meta.connections.
  const connBlock = connectionsBlockHtml(html, path, connectionsOverride ?? meta.connections);
  const withConn = connBlock
    ? html.replace(/<div\b[^>]*\bresearch-content__right-actions\b[^>]*>/, (m) => connBlock + m)
    : html;
  // Author at the top of every page: inject the "Researched by" block (with a visible
  // author photo row) into captured heroes that lack one.
  const withAuthor =
    authors.length && !/Researched\s*by/i.test(withConn)
      ? withConn
          .replace(/research-hero__center-content--fullwidth/g, "research-hero__center-content")
          .replace(/(<h1\b[^>]*\bresearch-hero__center-title\b[^>]*>[\s\S]*?<\/h1>)/, (m) => m + researchedByHtml(authors))
      : withConn;
  let content = applyTextRules(dePurple(injectFaqs(linkifyClassifications(withAuthor), faqs)), { images });
  const sbType = isStop ? "stop" : type;
  if (SIDEBAR_ORDER[sbType]) content = reorderSidebar(content, sbType);
  // Remove the hero "Research feed" button — replaced by the Share button (ShareButton).
  content = content.replace(/<a class="research-hero__center-tag"[^>]*>[\s\S]*?researchfeed_white[\s\S]*?<\/a>/g, "");
  // Autolink the first mention of every concept entity in the body (sitewide rule).
  content = autolinkEntities(content, await getLinkTargets(), path).html;
  // Signed-in readers get the real Research Feed cards (excerpt + summary + Open/Link/Email)
  // in place of the "create a free account" teaser walls; logged-out readers keep the wall.
  const loggedIn = await isLoggedIn();
  if (loggedIn) content = await revealResearchFeedWalls(content);
  // Fill the Page Snapshot counts the way front.js used to (it's not loaded): References =
  // distinct [n] citations; Identified MMAs = signature taxa given their own sidebar.
  const refCount = referenceCount(content);
  const mmaCount = signatureMmaCount(meta);
  if (refCount) content = content.replace(/(<span class="js-count-references">)\s*(<\/span>)/g, `$1${refCount}$2`);
  if (mmaCount) content = content.replace(/(<span class="js-count-mmas">)\s*(<\/span>)/g, `$1${mmaCount}$2`);
  const sigStudies = extractSignatureStudies(content);
  const studies = sigStudies.length ? sigStudies : extractStudies(content);
  const heroSrc = (typeof meta.hero_image === "string" ? meta.hero_image : null) || stripHost(item.featured_image_url);
  const heroMeta = heroSrc && images ? images.get(normSrc(heroSrc)) : undefined;
  const jsonLd = buildJsonLd(item, {
    path,
    type,
    authors,
    image: heroSrc,
    imageAlt: heroMeta?.alt,
    imageCaption: heroMeta?.caption,
    imageWidth: heroMeta?.width,
    imageHeight: heroMeta?.height,
    faqs,
    breadcrumbs,
  });

  // Research-feed summaries get the cosmetic account-wall (AccessGate blurs + overlays
  // [data-gated]) — but ONLY for logged-out visitors, decided server-side (the client can't
  // read the httpOnly session cookie to unlock it). Signed-in readers get no gate at all.
  if (type === "research-feed" && !loggedIn) {
    content = content.replace(/(<div[^>]*\bresearch-content__center\b[^>]*)>/, '$1 data-gated="research-feed">');
  }

  // Right-rail "Join the Roundtable" CTA: relabel the captured /auth/signup link to "Join the Waitlist".
  content = content
    .replace(/Yes,\s*I want to\s*(<a href="\/auth\/signup)/i, "$1")
    .replace(/(<a href="\/auth\/signup\/"[^>]*>)[\s\S]*?(<\/a>)/, "$1Join the Waitlist$2 and help shape the future of microbiome medicine.");

  return (
    <>
      <div dangerouslySetInnerHTML={{ __html: content }} />
      {hasSignature && (
        <MicrobiomeSignature slug={item.slug} title={item.title} levels={signature!.levels!} studies={studies} />
      )}
      <Tooltips />
      <WpDiagram />
      <ShareButton />
      <WpInteractivity itemId={item.id} />
      <JsonLd data={jsonLd} />
    </>
  );
}
