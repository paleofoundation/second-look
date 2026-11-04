# Metformin-first guide infrastructure — implementation receipt

October 12, 2026. Contract: [TOPIC-GUIDES.md](TOPIC-GUIDES.md). This is an infrastructure release, not a sale-ready Metformin edition. Scientific source reconciliation and approvals remain separate.

## Delivered

- Shared article sharing/guide rail, canonical social compose links, copy feedback, 44px targets and visible keyboard focus. Yellow/blue CTA contrast 4.66:1. Pending, released and entitled CTA states use one product mapping. Article populations remain in study details; the evidence drawer, author and Page Snapshot remain available. At 991px and below, the offer follows the hero and related reading follows the article.
- Explicit mappings for all 64 drug/condition profiles and truthful own-topic product pages. All topic products are $49 USD once. The $59/month membership is disabled until Metformin, Long COVID and itraconazole are released. No unavailable product can reach checkout; no annual or physician offer.
- Optional self-reported roles and searchable private interests, profile migration without changing intake eligibility, editing/export/removal, and account-scoped library saves. Matching guides are reconciled after verified payment and library refresh; removals are retained as tombstones. New/Updated states compare last-viewed and current editions, with edition change notes and history. Files download only on request.
- Topic-level permanent purchase rights, private web reader and download endpoints, exact manuscript/file/marketing approval hashes, server-authorized storage reads, hosted Checkout/portal endpoints and signed webhook handling. Delayed/duplicate/out-of-order events, renewals, cancellation, refunds/disputes and expiry have local lifecycle coverage. Missing runtime configuration fails closed.
- Versioned manuscript schema and reusable PDF renderer adapter produce web, full PDF, selected sample and printable summary outputs from one source. Synthetic renderer tests establish consistency, link/bookmark destinations, deterministic hashes and output isolation. Every synthetic PDF page was visually inspected. The engine is currently **private-draft-only and untagged**; final commercial/accessibility acceptance is outstanding.

Implementation details: [GUIDE-COMMERCE.md](GUIDE-COMMERCE.md), [GUIDE-INTAKE-LIBRARY.md](GUIDE-INTAKE-LIBRARY.md), [GUIDE-RENDERER.md](GUIDE-RENDERER.md).

## Verification

Passed governance, content, wiki links, reader coverage, article navigation/citations, all-profile reader/evidence sections, evidence grading, Page Snapshot, topic mappings/sharing, TypeScript, production build, and whitespace checks. The built public-boundary checker passed 33 payloads. The fresh local D1 migration chain applied successfully, including existing-schema compatibility fixtures.

Real SQLite/handler tests cover legacy profiles and free-review eligibility, repeat signup, optional interests, account isolation, export, matching saves, manual removal, direct-reader last-viewed tracking, update badges and expiry. Commerce tests use verified-signature/provider-state fixtures and cover successful/pending/failed/refunded/disputed/duplicate payments, renewals, cancellation, paid-through access, permanent purchase updates and checkout recovery. These are local lifecycle tests, **not a completed hosted Stripe sandbox payment**.

The production Worker ran locally on October 12. `scripts/check-guide-http-boundary.mjs` checks five public/shell pages and eight anonymous API boundaries. Protected APIs return only an error with `private, no-store, max-age=0`; unsigned webhooks fail verification. No paid manuscript or real guide files have been uploaded or placed in public bundles.

Browser verification covered 1280px desktop, 390px mobile and 320px narrow mobile: no horizontal article overflow; correct share destinations; 44px share targets; the offer before article content on mobile; related reading after content; keyboard focus and guide navigation; pending product states; optional physician/Metformin intake, persistence, interest removal and library empty state. Evidence outcome/study drawers still select the expected sources and Escape returns focus to the opener. An old development browser tab stopped following anchors; a fresh tab verified ordinary native-link navigation without a code workaround.

## Source and publication

Work was isolated from the canonical repository's concurrent research changes. It incorporates published Sites version 35, source `70c19536f84d40153053cb4607a752dbad901c15`, including the approved RemapRx identity and native navigation changes. The project remains public with its existing indexing and scientific release gates. A bounded source sync preserves unrelated canonical work.

Sites **version 36** published from `c12df71db701d5f8ba180a35f326b1adde64c33b`. Deployment `appgdep_6acceff26e3c81918332236af1fbbc1d` succeeded October 12, 2026 at 14:34:53 UTC. Archive SHA-256 `c0f60ac1e593e5e0db27e420c7721d7e53774239c971f6e986fae2c5c5e16ae5` (448 files). Live verification on https://remaprx.com passed all 13 public/private HTTP probes at 14:35 UTC. The live browser verified the Metformin CTA and pending product state, desktop rail and 390px mobile offer. Screenshots are preserved in the canonical repository under `artifacts/guide-library/`. No guide or membership was activated.

The canonical source sync passed governance and application TypeScript checks. Archived partial TypeScript copies under `research/batches/**/app-inputs/**` initially caused unrelated missing-module errors; these immutable handoff snapshots are now excluded from the application compiler, alongside the existing reference/prior-pilot exclusions. Their files were preserved. `docs/GUIDE-SOURCE-SYNC.json` records the bounded implementation sync.

The direct Metformin acquisition return contains 12 verified source assets, including seven newly held main reports, the MASTERS corrigendum and two MA.32 metabolic supplements. Root independently accepted its schema, byte hashes, report identities/media and archive on October 12. All 165 scientific question inputs remain unextracted; four main reports, the COVID-OUT correction body, specified companions and version checks remain missing. The exact current continuation is the canonical `research/batches/RRX-GUIDE-METFORMIN-001/ACQUISITION-HANDOFF.md`.

## Outstanding release requirements

1. Complete Metformin ingestion, extraction and scientific assessment, including corrections, study-family overlap, missing source material and the existing ACTIV-6/REVIVE intake. The canonical packet is `research/batches/RRX-GUIDE-METFORMIN-001/`; its gap ledger and missing-source handoff are the authority, not the public article's apparent completeness.
2. Write the substantive consumer manuscript only after evidence assessment; generate and inspect every page of its real web/PDF/sample/summary edition, verify citations and approve the exact final assets. No substantive Metformin paid manuscript or real release approvals were fabricated.
3. Connect the owner's isolated Stripe sandbox, configure its test credentials/webhook/prices and perform actual hosted Checkout/portal tests. The owner confirmed they will connect a sandbox; only a live account was exposed during implementation, and it was not modified or charged.
4. Complete merchant/tax/refund/support details, final accessible PDF/release support, and genuine editorial, clinical and legal release records before live individual sales. Long COVID and itraconazole follow; membership stays disabled until all three substantive guides pass.

Concurrent Sites version 37 (`11b907ced9b7f8d720756cccef3d49a9fb693446`, deployment `appgdep_6accf19ca79c819181dfda79d8b9bc65`) subsequently published the separate physician-packet workspace and retained this guide infrastructure. Its application changes were preserved. The follow-up source merge restores all prior append-only changelog entries alongside that new contract and the version-36 receipt; it makes no additional application behavior change.

## November 4, 2026 continuation

The earlier October acquisition counts above are historical. The current Metformin candidate is `2026.11.04-candidate.1`, with a 15-chapter manuscript, 30 cited references and web/full-PDF/sample/summary outputs stored outside the application checkout. `research/batches/RRX-METFORMIN-COMPLETE-20261103/README.md` is the current handoff. It records the 33-source disposition ledger, actual correction/replacement work, 24 source assessments, remaining access gaps and independent approvals still required.

The host PDF adapter now keeps individual bibliography entries and worksheet prompts together at page breaks. The vendored renderer is unchanged, and the manifest also records the host Python adapter hash. Full manuscript and raw source files remain outside Git and deployment artifacts. No guide has been deployed, put on sale or marked human-approved by this continuation.
