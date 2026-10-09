/** Pure citation presentation helpers. Build one order from the complete page's
 * canonical reading sequence, then reuse it when filtering or opening panels.
 * These helpers never infer claim support or mutate scientific source data. */
export type CitationGroups = ReadonlyArray<ReadonlyArray<string>>;

/** Known sources receive contiguous numbers at their first logical appearance. */
export function createCitationOrder(groups: CitationGroups, availableIds: Iterable<string>): string[] {
  const available = new Set(availableIds);
  const seen = new Set<string>();
  const order: string[] = [];
  for (const group of groups) for (const id of group) {
    if (available.has(id) && !seen.has(id)) { seen.add(id); order.push(id); }
  }
  return order;
}

/** Collect missing identities for validation; never silently claim they exist. */
export function unknownCitationIds(groups: CitationGroups, availableIds: Iterable<string>): string[] {
  const available = new Set(availableIds);
  return [...new Set(groups.flat().filter(id => !available.has(id)))];
}

/** Repeated and out-of-order input IDs produce one ascending group. */
export function orderCitationGroup(ids: ReadonlyArray<string>, order: ReadonlyArray<string>): string[] {
  const requested = new Set(ids);
  return [...new Set(order)].filter(id => requested.has(id));
}

/** An absent identity is missing, never citation zero. */
export function citationNumber(id: string, order: ReadonlyArray<string>): number | null {
  const index = order.indexOf(id);
  return index < 0 ? null : index + 1;
}

/** Remove whitespace before a superscript without changing source wording or
 * punctuation. Render the returned text, then the superscript, then a separate
 * inter-sentence space. A fragment remains a fragment: any missing sentence
 * punctuation must be resolved by the host explicitly, not silently invented.
 * hasCitations is accepted for the shared prose/table call shape.
 */
export function normalizeCitationSentence(text: string, _hasCitations = true): string {
  return text.trimEnd();
}

/** Stable fragment survives display-number changes; hosts retain ref-N aliases. */
export function sourceReferenceId(sourceId: string): string {
  return `source-ref-${encodeURIComponent(sourceId)}`;
}
