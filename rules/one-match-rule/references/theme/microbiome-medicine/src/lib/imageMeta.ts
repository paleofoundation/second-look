import { cache } from "react";
import { supabase } from "./supabase";
import { normSrc, type ImageMeta } from "./imageClassify";

// Load the AI-generated alt/caption + intrinsic dimensions for every unique image src
// once per request (React cache() dedupes across the page's components). The table is
// tiny (~300 unique content/hero srcs — avatars/icons are decorative and not stored),
// so an in-memory Map keyed by normSrc is the right shape. The render transform
// (normalizeImages in textRules.ts) looks images up here and injects alt/caption/dims.
export const getImageMeta = cache(async (): Promise<Map<string, ImageMeta>> => {
  const m = new Map<string, ImageMeta>();
  try {
    const { data } = await supabase
      .from("image_meta")
      .select("src,kind,alt,caption,width,height");
    for (const r of (data || []) as {
      src: string;
      kind: ImageMeta["kind"];
      alt: string | null;
      caption: string | null;
      width: number | null;
      height: number | null;
    }[]) {
      m.set(normSrc(r.src), { kind: r.kind, alt: r.alt, caption: r.caption, width: r.width, height: r.height });
    }
  } catch {
    // Missing table or a transient DB error must not 5xx the article page.
  }
  return m;
});
