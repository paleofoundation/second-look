# Physician packet implementation — October 12, 2026

## Implemented scope

The member portal at `/account/physician-packets` has condition selection, structured preview, print styling, verified PDF download and an email drafting panel. Account navigation and My guides link to it. Every catalogue, JSON and PDF request independently checks the trusted signed-in identity and an active, unexpired membership. Individual guide ownership is insufficient. Private R2 entries must carry exact-edition editorial, qualified clinical and legal approvals; no real release records were created. Name, qualifications and contact fields remain blank in the sample.

The existing NSCLC sample was reorganized as a five-page document: clinical brief; two study-detail pages; safety/consultation worksheet; sources/accountability. Seven semantic tables appear in the browser preview. The printable PDF has five bookmarks, 33 link annotations and selectable text on every page. It uses embedded Arial, pale blue table headings and numbered citations. All five PDF pages were rendered and visually inspected. The current PDF SHA-256 is `5b9164a12fb94749200081b355b7e19fb61696d77334fa7eb9f245faf1f05bc9`.

Owner artifact on this host: `../artifacts/physician-packet-nsclc-v2/output/remaprx-nsclc-physician-packet-v2.pdf`. Source-input hashes are in `PHYSICIAN-PACKET-DESIGN-INPUTS.json`. The fixture reuses the prior sourced sample; no new literature search or scientific appraisal is represented. It is excluded from production client imports and has no hosted release entry.

## Verification evidence

- `node scripts/check-physician-packets.mjs`: 32 authorization, expiry, approval, privacy and integrity response assertions; five-page rendering, seven tables, citation closure, HTML escaping and email contract checks passed.
- TypeScript with `--noEmit --incremental false` passed.
- Governance (236 preserved rule/history/ingest files) and public-reader boundary checks passed. Full Sites build passed; final packaging repeats the build after incorporating Sites version 35.
- Actual local Vinext application: sign-in redirects through existing account flow; a signed-in nonmember sees membership required; a temporary synthetic membership reaches the honest empty catalogue. Existing local migrations 0001/0002/0003 were applied; the temporary membership was removed. Production membership and approval data were not altered.
- Browser design harness: condition selection renders the sample; desktop and 390 px mobile views inspected. Mobile document width equals viewport width (390 px), with the summary table scrolling inside its container. Email panel exposes the draft and explains manual PDF attachment; no message was sent. Download action produced the five-page PDF.
- Native browser print invocation could not be conclusively observed in the in-app browser. The downloadable PDF's print layout was verified independently; browser-specific print-dialog acceptance remains a manual check. Future approved editions need their own visual pagination acceptance.

## Source and release boundaries

Implementation began from Sites version 34 (`a4dc664fd2644d9c4d46d6846d9a546bdf4b8c4c`) in an isolated checkout. Version 35 (`70c19536f84d40153053cb4607a752dbad901c15`) was incorporated to retain concurrently published identity copy. The later guide infrastructure source (`c12df71db701d5f8ba180a35f326b1adde64c33b`) was also merged after a normal push rejected the outdated source. Merge resolutions retained the new guide library and catalogue, added the packet link, kept both changelog entries, and regenerated candidate marketing hashes without creating approvals. The canonical GitHub checkout contains unrelated in-progress work and is not the publication source for this operation.

The portal interface is prepared for publication to the existing public site with member-only packet APIs. No paid service, real packet edition or clinical approval is released by the interface build. Remaining product prerequisites: reviewed condition editions and exact approved assets in private storage, the separately governed paid-membership launch, and any real contributor's identity/consent before adding a byline. An unsigned packet does not need a fabricated specialist credit.

Deployment receipt is recorded separately after the native Sites publish returns. No production patient data, email delivery or public sharing links are introduced.
