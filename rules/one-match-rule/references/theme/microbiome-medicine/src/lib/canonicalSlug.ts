import { permanentRedirect } from "next/navigation";
import { asciiSlug } from "./slugs";

export function canonicalItemPath(segment: string, storedSlug: string): string {
  const s = asciiSlug(storedSlug) || storedSlug;
  return segment ? `/${segment}/${s}` : `/${s}`;
}

/** 308 to the ASCII slug when the request still has unicode / encoded WP form. */
export function redirectIfUncanonicalSlug(segment: string, requestSlug: string, storedSlug: string): void {
  const canon = asciiSlug(storedSlug) || storedSlug;
  if (requestSlug !== canon) permanentRedirect(canonicalItemPath(segment, storedSlug));
}
