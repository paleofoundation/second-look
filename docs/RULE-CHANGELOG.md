# Second Look rule changelog

Record requirements when adopted, even if implementation is pending. Keep history append-only; describe supersession explicitly. Each entry needs source/date, scope, requirement, affected contracts, implementation/verification/release status and unresolved work.

## 2026-10-12 — SL-RULE-PHYSICIAN-PORTAL: table-led member packets

Source: owner request to build condition-specific physician packets into the paid-subscriber portal, organize the material with tables and support printing/emailing; follow-up permits leaving specialist name/contact blank. Scope: member feature, document redesign and owner-inspectable NSCLC sample. Supersedes sample-only implementation scope. Contract: `docs/PHYSICIAN-PACKETS.md`.

Implementation: private membership/edition checks, condition selection, structured preview, print styling, verified PDF download and member-controlled email draft. The owner does not require a physician signature; no specialist credentials are invented. Credit remains separate from the existing qualified clinical and commercial release gates. Local verification and deployment are recorded in `docs/PHYSICIAN-PACKET-IMPLEMENTATION.md`; live billing, real approvals and sending messages remain outside this development operation.

## 2026-10-12 — SL-RULE-TOPIC-GUIDES: sharing, permanent topic guides and private member library

Source: owner's explicit “PLEASE IMPLEMENT THIS PLAN” request, Metformin-first guides, sharing sidebar, and member library. Scope and acceptance: `docs/TOPIC-GUIDES.md`. Adopted prices are $49 once per topic (future approved editions included) and $59/month; membership follows three substantive releases in order Metformin, Long COVID, itraconazole. No first-release annual plan or physician edition. Supersedes prior catalogue prices, edition-only rights, and the persistent Entity/Scope/population rail. Preserve evidence panels, author/Page Snapshot, public safety and free authenticated reviews.

Implementation includes canonical sharing and truthful mapped product offers; optional self-reported role/interests intake; private automatic library saves with removal/update semantics; protected versioned manuscripts; server-authorized Stripe Checkout/portal/webhooks; and a metformin source-gap reconciliation before substantive guide authoring. Research and human clinical/legal approval cannot be replaced by interface completion or payment fixtures. Status at adoption: implementation in progress in an isolated checkout of published source `b0a05596eb665f479bddb9f7517d1a8253f0877f`; no paid guide or live commerce released. Exact verification, deployment and unresolved external inputs will be recorded in `GUIDE-IMPLEMENTATION.md`. The pinned upstream/reference projects remain unchanged; reusable rule synchronization is pending.
