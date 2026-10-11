import { cache } from "react";
import { contentPath } from "./content";
import { supabase } from "./supabase";

// URL segment per content type (matches the app routes). research-feed/post/page are
// NOT link targets — they're articles, not canonical concept entities.
const TARGET_TYPES = [
  "condition",
  "definition",
  "intervention",
  "metal",
  "microbe",
  "supplement",
  "guide",
  "theory",
] as const;

export type LinkTarget = { title: string; href: string; type: string };

// Every canonical concept entity that other pages should link to at first mention.
// Loaded once per request (React cache()). ~80 rows, so an in-memory list is fine.
export const getLinkTargets = cache(async (): Promise<LinkTarget[]> => {
  try {
    const { data } = await supabase
      .from("content_items")
      .select("type,slug,title,status")
      .in("type", [...TARGET_TYPES])
      .eq("status", "publish");
    return ((data || []) as { type: string; slug: string; title: string }[])
      .filter((r) => r.title && r.slug)
      .map((r) => ({ title: r.title, href: contentPath(r.type, r.slug), type: r.type }));
  } catch {
    return [];
  }
});
