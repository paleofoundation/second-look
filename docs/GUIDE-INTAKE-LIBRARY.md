# Reader interests and guide library

Adopted October 12, 2026 from the owner's metformin-first guide implementation plan. The authoritative pricing, release sequence and release gates are in [TOPIC-GUIDES.md](TOPIC-GUIDES.md). This work extends existing account storage; it does not create scientific approval, payment, subscription or purchase records.

## Profile compatibility and privacy

`INTAKE_VERSION` remains 1. Existing valid role profiles, original completion dates, declined-role choices and eligibility for free released research reviews survive the additive migration. The former `clinician` role remains a valid selectable value; `physician` and `other_healthcare_professional` add more specific self-reported choices. These labels provide no professional verification or access privileges.

Optional interests are explicit `drug:slug` / `condition:slug` registry keys from the shared topic-guide mapping. They are not diagnoses. The form searches public topic labels locally; it does not collect credentials, medication histories, patient details or free-text health information. Skipping topics is allowed. The profile settings support changing, clearing, exporting and deleting interests. A legacy role-only save preserves existing interests. Profile deletion stops future interest-based additions but preserves guides, purchases, saved research and notes. No email enrollment is added.

Account identity is supplied exclusively by the existing sign-in provider. Profile and library responses are private and noncacheable. Mutation endpoints enforce same-origin JSON requests and reject client-supplied account identifiers.

## Saved guide behavior

`/api/library/guides` is separate from the existing saved-research and note API. Its GET reads the authenticated account's current entitlements, interests and saved-guide records, then idempotently reconciles them. Approved released purchased topics are added with reason `purchase`. Approved released membership guides matching selected interests are added with reason `interest`, only during active paid access. This reconciliation also picks up newly released matching guides when the reader next opens or refreshes the library. No manuscript/PDF bytes are fetched and no device download occurs during reconciliation.

The `guide_saved_entries` composite key is `(user_id, product_id)`. Each record holds the reason (`manual`, `interest`, `purchase`), addition date, last-viewed edition and optional removal date. A removed guide retains a tombstone so future reconciliation never silently restores it. An explicit manual save can restore it. Interests are not duplicated into library metadata; the reason explains that the guide matched selected topics without retaining a removed interest.

Removing an interest stops future automatic additions. It does not delete already saved guides. Expired membership preserves saved metadata but removes subscription-only web and download links. Purchases continue to grant access to future approved editions of the topic, subject to refund/dispute/withdrawal controls owned by the commerce system. Removing a purchased guide from saved guides does not remove purchase rights; it remains available to open or save again.

The account screen displays the current entitled edition, `New` before a first view, `Updated` when the last-viewed edition differs, an expandable `What changed` note and earlier approved editions. The protected reader mounts `GuideViewedMarker` only after the server has authorized and returned the exact edition. The PATCH API independently rechecks that account's edition entitlement before recording a view. The public article does not mark a guide as viewed.

Opening an eligible purchased or matching membership guide directly from an article first performs the same insert-only save reconciliation, so the view is recorded even before a first library visit. A removal tombstone remains removed. Reading an arbitrary membership topic that has not been saved or selected as an interest does not silently save it; last-view tracking begins when that topic is saved.

My guides shows `Manage billing` when the private response contains membership or purchase history. It sends an empty same-origin, credentialed POST to `/api/billing/portal`; the server chooses the customer from the authenticated account. The client redirects only to an HTTPS `billing.stripe.com` URL without credentials or a custom port. Expired login offers sign-in again; missing billing profiles, failed requests and malformed/untrusted destinations remain on the library screen with an error. No fallback opens checkout or assumes cancellation succeeded.

## Storage and verification

`drizzle/0012_guide_interests_library.sql` adds `reader_profiles.interests_json` with an empty-array default and the guide-library table. It does not rewrite existing profiles or orders. Register and apply this migration with the related commerce migration before exposing the new account endpoints in the hosted deployment. D1 data and reader exports remain outside Git.

`node scripts/check-guide-intake-library.mjs` passed on October 12, 2026 using a real in-memory SQLite database and the actual profile/library handlers. Coverage includes additive migration with an existing profile; completion-date preservation and repeat signup; new/declined roles; optional empty/valid/invalid interests; legacy client saves; export/delete; account isolation; origin/identifier rejection; insert-only automatic saves; manual removal and restoration; newly released guides; removed interests; edition badges/history; canceled renewal, expiry and permanent future-edition purchase access. Fixture approvals/payments exist only in the test process.

The check also verifies that changing metadata on an earlier edition does not replace the newer version as the current edition, and that unsaved topics open their current entitled edition. Repository TypeScript (`npx tsc --noEmit --pretty false`) and `git diff --check` passed after integration with the shared topic mapping and edition response fields.

Integration follow-up checks passed for a matching member opening the protected reader before visiting the library, preservation of a removed guide during that direct-reader path, and the billing client's empty authenticated request, valid redirect, expired sign-in, missing profile and hostile URL rejection. The private built client was also scanned for synthetic manuscript sentinels, guide storage keys, qualified-review fields and private profile/library table identifiers; none were present in the build inspected during the audit. A fresh production build remains required after the billing/view-tracking correction.

The two modified React components were checked against the React best-practices skill: hook order is stable, profile search derives from state, checkboxes/inputs have labels, controls are keyboard reachable, library data is fetched only from private endpoints, no private profile is stored in browser persistence, and the client bundle imports only the public topic registry. Browser account-flow verification and production migration/deployment results belong in the integrator's release receipt; this document does not claim a live subscription or payment test.

Reference consulted: the pinned Microbiome Medicine `role-intake.reference.tsx` and the existing site's reader-profile and saved-library components. This implementation preserves RemapRx's current authentication, optional interests and data-minimization contract rather than adopting the reference's extra personal/professional fields.
