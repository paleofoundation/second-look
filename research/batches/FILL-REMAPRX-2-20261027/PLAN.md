# FILL-REMAPRX-2: page selection and collision checkpoint

Date: October 27, 2026. Integrator: CONDUCTOR. Lane: 2. Base: d118d305b59cac5e54ca7f9e5aa55cea682d2cee. Branch: codex/fill-remaprx-2.

The 09:27 Elon order authorizes a next drug and condition fill batch, with a literal prohibition on editing any file changed in PRs 4 through 7 and any path under research/batches/RRX-INGEST-. This checkpoint inventories inputs and proposes questions. It does not extract new findings, assign grades, author clinical claims or fill pages.

## Proposed bounded batch

The order does not prescribe a page count. Propose the five thinnest eligible condition parents and the two thinnest eligible drug parents after removing the 13 guides changed in PRs 4 through 7, Vitiligo, guides using protected CP027/CP028 sources and azole mechanism work. Selection is reproducible from SELECTION.json. Its word counts are the supplied historical audit counts, not current live counts.

Conditions: type 2 diabetes, chronic myeloid leukemia, persistent genital arousal disorder/genitopelvic dysesthesia, acute myeloid leukemia and fibromyalgia. Drugs: fluvoxamine and sildenafil.

For each page, CLAIM-PLAN.json maps evidence coverage, exact mechanisms, human evidence and safety questions to current canonical source IDs. Before authoring, inspect the exact accessible source and bind each proposed sentence to a hash and stable locator. Use the unchanged five-domain method for each claim; do not derive a clinical benefit letter from a narrative confidence grade or study design. Preserve null, mixed, adverse and uncertain findings. Record search completion, access, extraction, appraisal, synthesis, Q01-Q15 review, human acceptance and release separately.

## Current permitted scope

Read-only metadata inventory and a new batch packet are permitted. Complete the full ingestion reading and exact prospective schema/readiness before any substantive extraction or import. This checkpoint is not GP Plan PASS for scientific extraction. No new retrieval, file request, clinical claim or numerical extraction has occurred. No raw paper is copied to Git or outputs.

The source-access inventory uses exact PMID/DOI metadata matches only, then hashes matching local assets without opening their content. Unmatched metadata is not evidence that a source is absent locally or that no human evidence exists. Historical inventory matches are not fresh scientific acceptance.

## Collision requiring a ruling

FORBIDDEN-PATHS.txt contains the union of every path touched by commits in PR3-base-to-PR7 history, not merely the net tree difference: 91 paths. All maintained canonical guide/public projections are included. The reserved RRX-INGEST prefix is separately forbidden. ARCHITECTURE.md provides the import and resolver proof. Editing discovery-pages or inserting an alternative adapter cannot legitimately override these existing canonical guides.

Preferred proposal for Elon: explicitly replace whole-file exclusion with guide-ID ownership for this named batch, allowing bounded edits to data/content.json, data/public-content.json and editorial/parent-guide-scopes.json for only the selected IDs. Permit data/public-mechanisms.json and data/article-updates.json only for selected IDs if required after source appraisal. Preserve all PR4-7 guide objects and all unrelated objects byte-equivalent, as well as lane 1 batch paths. Record the new rule in the project contract and changelog only if their currently forbidden paths are explicitly released. This proposal is not permission and has not been applied.

Alternative: keep whole-file exclusion and hold page implementation. The lane can deliver only this own-path planning packet; it cannot honestly report filled pages. Do not create a second renderer or silently change a generator to evade ownership.

## Verification and handoff

verify.py checks the pinned base, all 91 unchanged files, selected/held exclusions, source-ID references, no change outside this packet, no reserved-prefix edit, and output hashes. No app build or browser check is needed to prove a metadata-only checkpoint; neither is reported PASS. Page, scientific and release checks remain unperformed. No merge, deploy, publish, credential or production action is authorized.
