# Blue design and illustration verification

12 October 2026. Changes prepared in an isolated checkout opened from live Sites version 24, source `8d7424bd9dca50a68c224144749aaa04392e4eb1`. The active research checkout and separate reference repositories were preserved. This is presentation acceptance, not scientific approval.

## Completed local checks

- Palette rendered in the browser before the two images were generated: center `rgb(23,54,245)`, side panels `rgb(16,39,184)`, white/pale text and yellow accents.
- CSS parses, `git diff --check`, TypeScript, article-navigation checks for 68 articles, and evidence-section checks for 64 profiles plus four guides pass. Existing citation order, mechanism pilot, fragments and source panels remain intact.
- Production `npm run build` passes its grading, public-source, guide and asset gates. Standard Vite large-chunk warning remains; no build error.
- The route metadata change invalidated all eight conservative guide-marketing candidate hashes. The documented hash updater recorded new candidate hashes; no product copy, prices, scientific/clinical approval, offer flags or commercial release changed. Existing exact-edition gates remain required.
- Original 1254 × 1254 PNG masters retain alpha. WebP derivatives at 512/1024 retain alpha. Metformin is 17,254/41,788 bytes; Parkinson's is 35,682/84,170 bytes. Social PNGs are opaque 1200 × 630. Manifest hashes and file metadata agree.
- Browser checks cover home, Metformin and Parkinson's; 390px mobile, 1024px tablet and 1280px laptop topic layouts have no horizontal overflow. Art is visible, fully contained, and a 512px derivative is selected on narrow screens. The default wide viewport also renders the full left/center/right hero.
- Parkinson's rendered canonical URL, Open Graph image URL, image source and existing noindex/nofollow metadata match its registry. Explicit `/sitemap.xml` and the metadata sitemap share the RemapRx origin. Robots disallow is preserved.
- Metformin evidence drawer opens from the existing outcome control; Escape closes it and restores focus to the opener. The narrow Metformin page also selects its 512px image with no overflow.
- Governance integrity (236 preserved rule/history/ingest files) and built public-payload checks (30 payloads) pass.
- Independent source review found and prompted correction of the explicit sitemap's old hostname. No remaining concrete source issue was identified. Scientific data are unchanged; the two page histories gain a presentation-only entry.

## Release record

Final packaged build and publication are pending at the time this pre-release report is saved. Append the exact Sites version, commit, archive identity and deployment result after publication. The existing public audience, scientific/access/commercial gates and indexing hold must remain unchanged.

## Publication receipt

Sites version 25 deployed successfully on 12 October 2026 at 11:50:39 UTC (14:50:39 Asia/Nicosia). Source commit: `cee0a45a7ceb49e44fd23afbcbbfd0590cdff4f7`. Deployment: `appgdep_6accc97796248191834ac96f48266aac`. Archive SHA-256: `e50f3869da5cfb4e265d292aee5a60851f56b8278a32641b0c3adfb952edb1bd` (7,639,040 bytes, 170 files). Existing public audience preserved. Runtime source is the isolated Sites commit; this receipt is added after deployment in the collaborator repository. The design-only patch was applied to the existing collaborator checkout without replacing its concurrent mechanism/research changes. Native success confirms publication; custom-domain browser/HTTP checks follow.

## Published custom-domain checks

Live HTTPS browser loads on `remaprx.com/drugs/metformin` and `remaprx.com/conditions/parkinson-disease` confirmed the new blue hero, loaded topic art and canonical/image metadata. Both pages, all six image derivatives, sitemap and robots returned HTTP 200 using system certificate validation. PNG previews return `image/png`; Sites currently serves WebP bytes as `application/octet-stream`, although both browser hero images decode and render correctly. The registry correctly describes the actual WebP format. This hosting MIME behavior is recorded as a delivery limitation for future hosting refinement, not hidden as a verified image/webp HTTP header. Python’s separate local CA store was unavailable, so final HTTPS checks used curl with normal certificate validation; no certificate checks were bypassed.

Final screenshots and HTTP receipt are in the parent workspace `artifacts/remaprx-blue-design/`. The preview server and completed installer helper were stopped after publication. Existing noindex/nofollow and robots disallow remain: no search-indexing improvement is claimed before that separate release gate is lifted.

## Shared-checkout integration limit

After applying the design-only patch, governance passes and the diff is clean. A full TypeScript check in the concurrently active collaborator checkout also scans newly present `research/batches/RRX-INGEST-001/app-inputs/` snapshot files. Those incomplete copied modules report missing relative imports and resulting implicit-any errors. These research snapshot files are outside this design change and were not altered. The isolated published application passed TypeScript and both production builds; the shared-checkout research snapshot issue is not part of the deployed version.
