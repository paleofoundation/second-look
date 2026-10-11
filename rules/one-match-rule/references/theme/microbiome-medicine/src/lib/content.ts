import { cache } from "react";
import { supabase } from "./supabase";
import { asciiSlug, slugLookupVariants, slugSearchToken, slugsEquivalent } from "./slugs";

export type ListItem = {
  id: number;
  slug: string;
  title: string;
  excerpt_html: string | null;
  featured_image_url: string | null;
};

export type ContentItem = ListItem & {
  type: string;
  content_html: string | null;
  seo_title: string | null;
  seo_description: string | null;
  published_at: string | null;
  modified_at: string | null;
  meta: Record<string, unknown>;
};

export type Section = { segment: string; type: string; label: string; nav: string; blurb: string };

// Maps URL segment -> content type. Preserves the original WordPress URL structure.
export const SECTIONS: Section[] = [
  { segment: "microbes", type: "microbe", label: "Microbes", nav: "Microbes", blurb: "Bacteria, fungi, and other organisms of the human microbiome." },
  { segment: "conditions", type: "condition", label: "Conditions", nav: "Conditions", blurb: "Diseases and conditions linked to microbiome signatures." },
  { segment: "interventions", type: "intervention", label: "Interventions", nav: "Interventions", blurb: "Therapies, treatments, and modulators of the microbiome." },
  { segment: "definition", type: "definition", label: "Definitions", nav: "Definitions", blurb: "Key terms and concepts in microbiome medicine." },
  { segment: "metals", type: "metal", label: "Metals", nav: "Metals", blurb: "Heavy metals and their interactions with the microbiome." },
  { segment: "supplement", type: "supplement", label: "Supplements", nav: "Supplements", blurb: "Supplements studied for microbiome effects." },
  { segment: "guide", type: "guide", label: "Guides and Resources", nav: "Guides", blurb: "In-depth guides and reference resources." },
  { segment: "research-feeds", type: "research-feed", label: "Research Feeds", nav: "Research", blurb: "Curated summaries of microbiome research." },
  { segment: "theories-hypotheses", type: "theory", label: "Novel Theories and Hypotheses", nav: "Theories", blurb: "Emerging theories and hypotheses." },
];

// Routed types that are not in the public header/footer nav (SECTIONS). Adding
// them here restores /validation/:slug without inventing a nav item.
export const EXTRA_SECTIONS: Section[] = [
  {
    segment: "validation",
    type: "validation",
    label: "Validation",
    nav: "Validation",
    blurb: "Microbiome-targeted intervention validation reports.",
  },
];

export const sectionBySegment = (segment: string): Section | undefined =>
  SECTIONS.find((s) => s.segment === segment) ?? EXTRA_SECTIONS.find((s) => s.segment === segment);

export const segmentForType = (type: string): string =>
  SECTIONS.find((s) => s.type === type)?.segment ??
  EXTRA_SECTIONS.find((s) => s.type === type)?.segment ??
  type;

export const INDEXABLE_TYPES = new Set<string>([
  "post",
  "page",
  ...SECTIONS.map((s) => s.type),
  ...EXTRA_SECTIONS.map((s) => s.type),
]);

export function contentPath(type: string, slug: string): string {
  const s = asciiSlug(slug) || slug;
  if (type === "post" || type === "page") return `/${s}`;
  return `/${segmentForType(type)}/${s}`;
}

// Verbatim captured WordPress content region for a page (pixel-exact rendering).
export const getWpHtml = cache(async (id: number): Promise<string | null> => {
  try {
    const { data } = await supabase.from("wp_render").select("html").eq("id", id).maybeSingle();
    return (data?.html as string | undefined) ?? null;
  } catch {
    return null;
  }
});

// Internal-link/image URLs were already made root-relative on import; this also
// covers any absolute featured-image URLs still pointing at the old host.
export const stripHost = (url: string | null | undefined): string | null =>
  ((url || "").replace(/^https?:\/\/(www\.)?microbiomemedicine\.com/i, "") || null);

export const listByType = cache(
  async (type: string, page = 1, pageSize = 48) => {
    const from = (page - 1) * pageSize;
    try {
      const { data, count } = await supabase
        .from("content_items")
        .select("id,slug,title,excerpt_html,featured_image_url", { count: "exact" })
        .eq("type", type)
        .eq("status", "publish")
        .order("title")
        .range(from, from + pageSize - 1);
      return { items: (data ?? []) as ListItem[], total: count ?? 0, page, pageSize };
    } catch {
      return { items: [] as ListItem[], total: 0, page, pageSize };
    }
  }
);

export type FeedItem = { slug: string; title: string; excerpt_html: string | null; modified_at: string | null };

// All research-feed items (for the category-grouped view); pages past the 1000-row cap.
export const listAllResearchFeeds = cache(async (): Promise<FeedItem[]> => {
  const out: FeedItem[] = [];
  try {
    for (let from = 0; from < 4000; from += 1000) {
      const { data } = await supabase
        .from("content_items")
        .select("slug,title,excerpt_html,modified_at")
        .eq("type", "research-feed")
        .eq("status", "publish")
        .range(from, from + 999);
      if (!data || data.length === 0) break;
      out.push(...(data as FeedItem[]));
      if (data.length < 1000) break;
    }
  } catch {
    return out;
  }
  return out;
});

async function fetchPublishedBySlug(type: string | null, slug: string): Promise<ContentItem | null> {
  try {
    let q = supabase.from("content_items").select("*").eq("slug", slug).eq("status", "publish");
    q = type ? q.eq("type", type) : q.in("type", ["post", "page"]);
    const { data } = await q.order("type").limit(1).maybeSingle();
    return (data as ContentItem | null) ?? null;
  } catch {
    return null;
  }
}

async function fetchPublishedBySlugToken(type: string | null, slug: string): Promise<ContentItem | null> {
  const token = slugSearchToken(slug);
  if (!token) return null;
  try {
    let q = supabase.from("content_items").select("*").eq("status", "publish").ilike("slug", `%${token}%`).limit(25);
    q = type ? q.eq("type", type) : q.in("type", ["post", "page"]);
    const { data } = await q;
    const rows = (data ?? []) as ContentItem[];
    return rows.find((r) => slugsEquivalent(r.slug, slug)) ?? null;
  } catch {
    return null;
  }
}

export const getItem = cache(async (type: string, slug: string) => {
  for (const candidate of slugLookupVariants(slug)) {
    const hit = await fetchPublishedBySlug(type, candidate);
    if (hit) return hit;
  }
  return fetchPublishedBySlugToken(type, slug);
});

export const getRootBySlug = cache(async (slug: string) => {
  for (const candidate of slugLookupVariants(slug)) {
    const hit = await fetchPublishedBySlug(null, candidate);
    if (hit) return hit;
  }
  return fetchPublishedBySlugToken(null, slug);
});

// "Identified MMAs" = the microbes important enough to be given their own sidebar
// (detail panel) in the microbiome signature — i.e. has_info:true across the signature
// levels. That is exactly how the original site counted them; clicking the count opens
// the signature modal.
export function signatureMmaCount(meta: Record<string, unknown> | null | undefined): number {
  const levels = (meta?.signature as { levels?: Record<string, { has_info?: boolean }[]> } | undefined)?.levels;
  if (!levels) return 0;
  let n = 0;
  for (const arr of Object.values(levels)) if (Array.isArray(arr)) for (const t of arr) if (t?.has_info) n++;
  return n;
}

// A page's reference count = the distinct [n] citation markers in its body.
export function referenceCount(html: string): number {
  const nums = new Set<string>();
  const re = /\[(\d{1,3})\]/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html || ""))) nums.add(m[1]);
  return nums.size;
}

// All published condition pages as {title, href} — for internally linking condition
// mentions in research-feed bodies + populating the Connections sidebar.
export const allConditionLinks = cache(async (): Promise<{ title: string; href: string }[]> => {
  try {
    const { data } = await supabase
      .from("content_items")
      .select("slug,title")
      .eq("type", "condition")
      .eq("status", "publish");
    return (data ?? []).map((c) => ({
      title: String((c as { title: string }).title).trim(),
      href: contentPath("condition", (c as { slug: string }).slug),
    }));
  } catch {
    return [];
  }
});

export const sampleByType = cache(async (type: string, limit = 6) => {
  try {
    const { data } = await supabase
      .from("content_items")
      .select("id,slug,title,excerpt_html,featured_image_url")
      .eq("type", type)
      .eq("status", "publish")
      .order("title")
      .limit(limit);
    return (data ?? []) as ListItem[];
  } catch {
    return [];
  }
});
