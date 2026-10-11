# Code and behavior references

Established at the user's request on 2026-10-11 for the Drug Repurposing site.

## Microbiome Medicine

- Repository: https://github.com/paleofoundation/microbiomemedicine
- Local checkout: `/Users/kmfp/Documents/ChatGPT/Drug Repurposing/references/microbiomemedicine`
- Shallow clone of `main`, commit `28ed85b6d510dfddf1720775b456771c7dc62763` at retrieval.
- Live site: https://microbiomemedicine.com/
- Read `AGENTS.md` and `docs/DESIGN-SYSTEM.md` in that checkout for its canonical component references. The design documentation identifies `/conditions/endometriosis` as its most developed condition-page reference.

Useful source paths relative to the checkout:

| Behavior | Source |
| --- | --- |
| Header and search | `src/components/SiteHeader.tsx`, `src/components/HeaderSearch.tsx`, `src/components/SearchAutocomplete.tsx` |
| Article layout and section navigation | `src/components/ArticleView.tsx`, `src/components/SectionNav.tsx`, `src/components/WpRender.tsx` |
| Research feed expansion | `src/components/ContentAccordions.tsx`, `src/components/ResearchFeedView.tsx`, `src/lib/researchFeedReveal.ts` |
| Condition evidence and study drawer | `src/components/ConditionsTable.tsx`, `src/components/StudyDrawer.tsx` |
| Internal linking | `src/lib/linkTargets.ts`, `src/lib/slugs.ts` |
| Visual styles | `src/styles/theme-wp.css`, `src/app/globals.css` |
| Update History timeline | `src/styles/theme-wp.css` (`.mbio-update-history`, `.mbio-card`), `_generator/pages/salmonella/build.mjs` (dated entry markup), `src/components/ArticleView.tsx` (updates icon mapping) |

The clone contains source code, not a provisioned copy of the site's external database. No dependencies or database credentials were installed for this reference checkout.

## PepsAnon

- Existing source: `/Users/kmfp/Documents/ChatGPT/Pepsanon.com/site-study-records`
- Build: https://pepsanon.com/ (also recorded locally as https://peptide-evidence.kmfp.chatgpt.site)
- Source HEAD when inspected: `e8c88effdf3aad26ebe805c72cbda361c78a4092`, with preexisting uncommitted changes. This is not a claim that source HEAD equals the deployed build.
- PepsAnon was opened in this chat's browser as a persistent reference tab. No local PepsAnon server was started.

Useful source paths relative to the PepsAnon source:

| Behavior | Source |
| --- | --- |
| Navigation and shell | `components/peptide/header.tsx`, `components/peptide/shell.tsx`, `lib/navigation.ts` |
| Guide pages and prose | `app/peptides/[slug]/page.tsx`, `app/stacks/[slug]/page.tsx`, `components/peptide/canonical-prose.tsx` |
| Study disclosures | `docs/canonical-research.md`, `components/peptide/guide-research.tsx`, `components/peptide/research-catalog.tsx` |
| Evidence table and right sidebar | `components/peptide/evidence-table.tsx`, `components/peptide/research-panel.tsx` |
| Citations and fragment reveals | `components/peptide/citations.tsx`, `components/peptide/cited-text.tsx`, `components/peptide/reveal-anchor.tsx` |
| Contextual internal links | `lib/guide-links.ts`, `lib/prose-links.ts`, `lib/guide-graph.ts` |

PepsAnon's Evidence section begins with prose and ends with an Outcome and study design / Grade / Evidence table. Its outcome and evidence-count buttons open a right-side study-information panel. The separate Research catalogue uses inline study disclosures and reveals enclosing disclosures when following fragment links. These are distinct interactions; preserve the table's drawer behavior when adapting Evidence.

Use each implementation to understand the relevant interaction, then adapt it to Drug Repurposing's current requirements and content.

The owner's 11 October Examine sidebar screenshots and [live endometriosis page](https://examine.com/conditions/endometriosis/) establish the small outline icons and Evidence / Research Feed / FAQs / Update History / References ordering for this correction. They do not authorize copying scientific content or replacing the site's existing scientific modules, branding or account policy. Source-to-destination adaptations are recorded in `docs/ARTICLE-NAVIGATION.md`.

## Portable collaborator access

The local paths above are provenance from the original host. In a fresh clone, use `rules/one-match-rule/references/theme/`, `references/reading-ui/` and `references/research-reviews/` under that same rule package for bundled source excerpts, styles, manifests and theme archives. Read each packet README and its readiness limits. A snapshot does not prove source parity.

Microbiome Medicine can be checked out separately with `git clone https://github.com/paleofoundation/microbiomemedicine.git references/microbiomemedicine`; inspect the recorded reference revision and its instructions before comparisons. The original workspace may already have this checkout in its parent `references/` directory. Keep that checkout ignored. PepsAnon has no configured Git remote in the inspected checkout; use the packaged extracts and live reference, and request missing exact source from the integrator if a change needs more. Do not claim the complete PepsAnon source is included here.
