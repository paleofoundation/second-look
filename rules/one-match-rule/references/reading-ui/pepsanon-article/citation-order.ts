/** Deduplicate by source identity while preserving first citation order. */
export function referencesInOrder<T extends {url:string}>(citations:readonly T[]):T[] {
  return Array.from(new Map(citations.map(source=>[source.url,source])).values());
}
