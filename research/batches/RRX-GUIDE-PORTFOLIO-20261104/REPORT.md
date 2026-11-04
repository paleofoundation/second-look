# Every-topic guide requirement and commerce preparation

Owner instruction, November 4, 2026: every drug and condition page needs its own guide available for purchase. The owner selected Microbiome Signatures LLC as seller. This is a catalogue, completion-policy and commerce-code operation, not a new scientific extraction batch. No source acquisition, study grading or manuscript approval was performed here.

Baseline: `8f7f831fa8a406d725266ab2262c9e897d08134a`, containing the completed private Metformin candidate. Work branch: `codex/all-topic-guides-20261104`. The canonical checkout has concurrent work and is not overwritten or merged by this operation.

## Actual coverage

The first count of 66 confused catalogue products with parent pages. The real runtime registry contains **64 parents: 32 drugs and 32 conditions**. Each has one distinct mapped topic guide. The other two products are general reading guides. Both current checkouts have the same 64 mappings. The generated [portfolio](../../../docs/GUIDE-PORTFOLIO.md) lists every required topic and will change with the runtime registry; 64 is not a fixed limit.

There is one registered substantive manuscript candidate, Metformin, and zero catalogue releases. The other 63 topic manuscripts are not registered. Metformin's private asset manifest links to its actual web/PDF/sample/summary files and retains its source limitations and pending clinical/editorial/legal approvals. No placeholder or product listing counts as finished work. No reference-count cap is introduced.

## Implemented

- Durable universal-guide requirement and seller selection in the project and topic-guide contracts and rule changelog.
- Runtime topic-to-product checks now run during production builds. They check every actual parent and correct product link, unique mapping and product routes, prices and state-appropriate CTAs. Synthetic released/pending/withdrawn cases replace the obsolete requirement that every product stay pending. Membership counts follow released launch products.
- A generated per-topic inventory with manifest registration, stale-inventory checking and an explicit `--require-released` check that currently reports incompleteness. Passing structural checks never certifies manuscript, scientific or live-sale completion.
- Explicit live/sandbox configuration with separate keys/signing secrets, matching event/response mode and verified merchant account identity. A new additive database binding prevents switching an existing payment database between accounts/modes. Protected library and asset reads enforce the same boundary; empty unconfigured libraries remain usable.
- Removed stale global “all in development” copy and the hardcoded “not launched” library message. The pending purchase label uses the product's actual status, including Metformin's “In review.” Candidate marketing hashes were refreshed after presentation changes; all other product fields and release states are identical to baseline.

The Stripe planner selected hosted Checkout. Read-only connected-account discovery and product-name search were performed after the owner's account selection. No matching RemapRx/guide products were returned. No Stripe objects, secrets, charges, registrations, webhooks, portal settings or production services were changed.

## Verification

Passed against this patch:

- `node scripts/check-guide-commerce.mjs` and `node scripts/check-guide-commerce.mjs --live-fixtures`: full synthetic payment, refund/dispute, renewal/cancellation, expiry, idempotency and permanent-topic lifecycle in SQLite, plus account/key/event mismatch, nested response mode, legacy database and protected read isolation.
- `node scripts/check-guide-intake-library.mjs`: private interests, account isolation, saved-library behavior, updates, cancellation/expiry and ownership.
- `node scripts/check-topic-guides.mjs`: all 64 actual topic pages and three synthetic availability states.
- `node scripts/guide-portfolio.mjs --check`: current manifest and topic inventory.
- TypeScript with `--noEmit --incremental false` and production build.
- ESLint on the seven changed commerce, access and repository TypeScript modules.
- `node scripts/verify-reader-boundary.mjs`: 10 projections, 19,986 fields and 36 built payloads.
- `node scripts/check-guide-http-boundary.mjs http://127.0.0.1:8796`: 13 built-site page/access checks, including correct product status and anonymous checkout/download rejection. The loopback listener required sandbox escalation; the authorized local check succeeded.
- Governance: 236 preserved rule/history files. Whitespace checks passed. Catalogue comparison verifies that only 66 candidate marketing hashes changed.
- Negative completion check: `--require-released` correctly exits with failure for all 64 unreleased topic guides instead of reporting catalogue coverage as completion.

Actual HTTP results are in `http-verification.json`. No provider transaction, complete browser payment flow, clinical review or production deployment is claimed. The initially attempted nonexistent `check-guide-access.mjs` was a command-selection error; access behavior is covered by the existing commerce, intake/library and HTTP suites above.

References consulted: the project's `references/README.md`, PepsAnon guide research and Microbiome Medicine ArticleView source. No navigation/layout structure or scientific content changed. TypeSafe guidance places these deterministic decisions in code rather than model judgments.

## Remaining work

1. Complete the other 63 substantive topic manuscripts under their appropriate source and assessment plans. Long COVID and itraconazole retain first-wave priority. Condition guides must cover the intervention landscape; do not substitute a drug guide.
2. Finish each candidate's real source/review obligations and record exact-edition approval. Existing Metformin source limits and reviewer status remain in its candidate manifest.
3. Verify merchant charge readiness, applicable tax configuration, consumer/refund/support terms, and a real isolated Stripe sandbox. Provision scoped secrets and snapshot webhooks privately, apply additive migrations, and run provider acceptance. Do not promote test entitlements into production.
4. Integrate this reviewed branch with the current application version, publish the checked build, upload approved private assets and activate each released guide's purchase flow. Verify real hosted checkout and protected delivery before claiming that topic is available for purchase.

The user requirement remains incomplete until every required topic is actually purchasable. This packet completes its software preparation and tracking, not the 63 outstanding manuscripts or live activation.
