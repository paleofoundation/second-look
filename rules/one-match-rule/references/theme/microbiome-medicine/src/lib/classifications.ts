// Intervention "Classification" values that have their own definition page. The
// interventions table's Classification cells link to these. Extend this map as the
// matching definition pages are created (e.g. Herbal, Pharmaceutical, Diet, Supplement,
// Biophysical Interventions do not exist as definitions yet).
const CLASSIFICATION_LINKS: Record<string, string> = {
  "Drug Repurposing": "/definition/drug-repurposing",
  Prebiotics: "/definition/prebiotics",
  Prebiotic: "/definition/prebiotics",
  Postbiotics: "/definition/postbiotics",
  "Fecal Microbiota Transplantation": "/definition/fecal-microbiota-transplantation-fmt",
};

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

// Link a table's Classification cells — a <td> whose entire text is a known
// classification — to that classification's definition page. Safe by construction:
// it only rewrites a cell that equals the term (not the same word inside prose or
// in the Intervention/Status columns), and skips cells that already contain a link.
export function linkifyClassifications(html: string): string {
  if (!html) return html;
  let out = html;
  for (const [term, href] of Object.entries(CLASSIFICATION_LINKS)) {
    const re = new RegExp(`(<td\\b[^>]*>)\\s*(${escapeRe(term)})\\s*(</td>)`, "g");
    out = out.replace(re, `$1<a href="${href}">$2</a>$3`);
  }
  return out;
}
