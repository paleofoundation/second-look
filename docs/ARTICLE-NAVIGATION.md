# Article navigation and history — 11 October 2026

Later scope correction, October 12, 2026: [SL-RULE-011 / CONDITION-PAGES.md](CONDITION-PAGES.md) plans a condition-specific intervention roundup and replaces the forced pre-Evidence condition modules. The historical implementation/verification below remains a record of version 23. The shared Evidence → Research Feed → FAQs → Update History → References tail, icons, citations and history behavior remain applicable. This note does not claim the new condition structure has shipped.

Owner source: Examine sidebar screenshots supplied in the Drug Repurposing chat and the explicit request recorded as SL-RULE-004. Implemented on `codex/article-sidebar-history` and published as Sites version 23 after explicit owner approval; release details follow below. This presentation release does not establish scientific approval.

## Adopted behavior and source mapping

| Requirement | Source consulted | Destination and adaptation |
| --- | --- | --- |
| Small icons beside section labels | Owner screenshots; rendered `examine.com/conditions/endometriosis/`; Microbiome `src/components/SectionNav.tsx` | `components/shared-theme/section-icon.tsx`, `theme.tsx`, `theme.css`; local 22px outline SVGs, decorative accessible treatment, text links, visible focus, keyboard collapse and independently scrollable long desktop rail |
| Matching sidebar/body order | Examine screenshot and explicit owner FAQ correction | `universal-article.ts` owns Evidence → Research Feed → FAQs → Update History → References; earlier scientific modules retained. Record pages use Update History → Sources. `lib/citation-plan.ts` follows actual content order. |
| Canonical study summaries | Microbiome `docs/DESIGN-SYSTEM.md` Research Feed contract and `src/lib/researchFeedReveal.ts`; PepsAnon `components/peptide/research-catalog.tsx` and `guide-research.tsx` | `components/article.tsx`; native inline study disclosures with actual source summary, correction and limitation. Separate bibliography. Dedicated source route stays available. Existing Evidence drawer remains independent. |
| Real Update History | Microbiome `src/styles/theme-wp.css:265`, `_generator/pages/salmonella/build.mjs:241`, `src/components/ArticleView.tsx` | `update-history.tsx`/`.css` retain `mbio-update-history` / `mbio-card` timeline structure and use destination colors; semantic time/heading markup and div cards avoid nested article semantics. |
| Durable dated entries | Actual current presentation change | `data/article-updates.json`, `lib/update-history.ts`; one honest 2026-10-11 entry, scoped to 412 currently existing routes, newest-first selection, UTC-stable formatting, valid section links. No earlier history inferred from paper publication dates. |

Microbiome reference revision: `28ed85b6d510dfddf1720775b456771c7dc62763`. PepsAnon comparison tab remained available; its existing source was read without modification. Reference scientific content, colors, accounts and reviewer claims were not copied.

The feed's public summaries cite their source using the page's frozen first-appearance numbering. Expanded released reviews are fetched only from the existing authenticated, private/no-store `/api/reviews/:id` endpoint. A granted self-contained body renders all four canonical opening questions, mapped section citations and source locators with study-prefixed IDs. Cross-source reviews continue on their dedicated page to preserve citation order; opening a card does not renumber the article. No protected review is imported into a client component. Preview, pending and withdrawn states do not become full-review release claims.

Legacy `#research`, `#studies`, `#edition`, `#findings`, `#study-*`, `#source-ref-*` and numbered reference fragments remain functional. Update History replaces the misleading Updates link; source counts remain in the hero and correction notices remain attached to the relevant study and existing scientific prose.

## Verification

- `node scripts/check-article-navigation.mjs`: passes for 68 evidence-bearing articles, checking both rendered orders, decorative icons, canonical summaries, unique targets, compatibility fragments and scoped history. Synthetic authorized-body fixtures check all four openings, locators, frozen citations and no duplicate IDs across studies; unresolved/cross-source bodies are rejected for inline rendering.
- `node scripts/check-reader-sections.mjs --all-profiles`: passes for all 64 drug/condition profiles and 396 questions, including existing prose, fragments and first-appearance citations.
- `node scripts/check-evidence-section.mjs`: passes for 64 profiles plus four additional evidence guides, 124 rows and synthetic/empty cases.
- TypeScript, focused lint for the article/history/icon modules, content integrity, wiki-link checks, rule governance, build, and source/built-client privacy boundary checks pass. The shared `theme.tsx` file retains one pre-existing lint error at its unchanged search effect (`react-hooks/set-state-in-effect`, line 47) and six pre-existing image warnings; these are outside the sidebar changes. The build retains its existing advisory about a client chunk over 500 kB.
- `check-wiki-links.mjs`'s stale standalone table fixture was aligned to visible `studyDesigns` prose; drawer-only finding/magnitude text is no longer expected in closed-table SSR. No production table behavior changed for this test correction.
- Browser: 1280×900 desktop and 390×844 mobile verified; no horizontal page overflow at 390px; timeline date/title/type/summary visible; sidebar fragments focus their sections; keyboard collapse/reopen works; References opens its matching study; study-summary destination resolves; Evidence count opens the separate drawer and Escape restores focus to its trigger.
- Local anonymous review API returned HTTP 200 preview with private/no-store headers, without a protected body. A previously signed-in local test session had unavailable account storage and showed the retry path; signed-out reading was verified. No live released full review was available for a production authenticated-end-to-end assertion; full-body rendering used synthetic authorized fixtures without changing release records.

TypeScript now excludes `rules/`, `references/` and `research/prior-pilot/`: these are intentionally non-executable historical/reference source packets. Their integrity remains covered by governance hashing, rather than treating excerpt `.tsx` files as application compilation units.

## Rule synchronization and release state

Canonical One Match Rule v1.30, the installed skill and full ZIP export were synchronized and byte-verified (244 files). The repository's scoped rule/reference snapshot contains 162 files with master SHA-256 `7fae46e83e1da5e139b0ab2d11ca02292603c63a50f764c89819b0792bc2f330`. Governance verifies 236 rule/history/ingest records, preserving the frozen v1.1 baseline. Uploaded ChatGPT copies do not automatically refresh and were not represented as updated.

Automatic approval review initially rejected the Sites source workflow because it could export private repository contents to the external Sites service and publish them. Implementation and local verification continued without a workaround export or deployment. The owner subsequently answered “Approve source sync and publication” to the explicit request to synchronize the private source and publish these changes to the existing site.

Following that approval, source commit `29166f85abbb12a2ff53f0cd3b77dcfdc9615b95` was synchronized, packaged and published successfully on 2026-10-11 at 13:12:49 UTC. The native Sites deployment response confirmed success at https://second-look-evidence.kmfp.chatgpt.site. Existing public audience and scientific release gates were preserved.

- Project: `appgprj_6ac734459a508191a425263c7645a0be`.
- Sites version: 23, `appgprj_6ac734459a508191a425263c7645a0be~appgver_eb1b323817ac819188ffb080ba9cc118`.
- Deployment: `appgdep_6acb8b392c648191b4809d48feccb0af`, status `succeeded`.
- Packaged archive SHA-256: `8d681cde3db2f81a4ff4dd2ec679bcb0c282ecf90ecace21b3da05bb0b4df659`.

This post-release record is a local documentation follow-up; the deployed implementation is the exact source commit above. Native deployment success confirms publication, while reader behavior and access-boundary verification remain the bounded checks recorded in the Verification section.
