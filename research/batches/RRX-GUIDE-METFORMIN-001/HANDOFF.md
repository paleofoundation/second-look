# Metformin guide evidence checkpoint

**Current status after accepted acquisition v1.1:** twelve actual source assets are privately staged, including seven previously missing main reports. Scientific extraction/assessment and guide release remain held. Independent root byte/identity receipt acceptance passed (`direct-acquisition/root-acceptance.json`), with scientific claims still unapproved. Read `ACQUISITION-HANDOFF.md`, `coverage-after-acquisition.json` and `direct-acquisition/receipt.json` for the current acquired/missing dispositions and exact return. The material below is the preserved pre-acquisition reconciliation baseline; its statements about no new downloads and fifteen gaps describe that phase, not the current receipt.

## Preserved reconciliation baseline

October 12, 2026. The worker completed **metadata reconciliation and byte/hash inventory only**. No new source was requested or downloaded, no medical source was newly extracted, no scientific assessment was completed, and no public evidence or manuscript was changed. Root Mission Control records independent reconciliation acceptance in `readiness.json`; acquisition/extraction/guide release remains separate. The existing RRX-GAP-001 and CAL-T1 source-version operations were not modified or duplicated.

## Findings

The ledger covers 24/24 current metformin article references. It preserves 22 scholarly review obligations, including the narrative review and quarantined REVIVE, plus two official context sources. Seven have existing review envelopes; their existence is not review completion. This operation records zero new complete reviews, human approvals, syntheses or releases. It does not audit an absence of all possible prior assessment work; it preserves known partial records and the current handoff's unfinished scientific state.

Nine reference identities have local hash-verified asset matches or explicit identity leads, with twelve distinct hashes. **Seven references (ten hashes) match existing canonical IDs or exact DOI/PMID metadata; two (two hashes) are explicit title/URL identity leads requiring adjudication**: the acute COVID-OUT report and myeloma model report. No match is represented as fresh printed-source identity verification. Some include companions or multiple source versions, so neither nine nor twelve is an independent-study count. Fifteen references lack a matched local complete-source asset in the reconciled inventory; some have previously inspected indexed text or abstracts. A local PDF alone does not pass identity, completeness, extraction, numerical checks or appraisal.

There are also 271 D01-tagged origin records in the preserved acquisition metadata. These overlap and include sources outside this guide's declared question scope. `existing-metformin-leads.json` keeps them available for deduplicated screening; they are not 271 studies, accepted sources, or a demand ranking. Closing the guide requires relevant omitted evidence to be assessed or dispositioned; a 24-reference page is not a comprehensive metformin search.

## Highest-priority missing inputs

1. **COVID-OUT correction text:** PMID 37666258, linked to DOI 10.1016/S1473-3099(23)00299-2, with exact amended article and supplement/version trail. Original PDF, acute/viral companion material and trial protocol are already present. Reconcile the inconsistent absolute-incidence values and all affected figures/claims; do not choose a preferred value or simply remove the correction note.
2. **ACTIV-6 journal report and companions:** DOI 10.1093/cid/ciag335, full journal text, supplements, and relevant final protocol/SAP versions. The existing preprint is not the journal source. Reuse RRX-GAP-001 and preserve CAL-04/05's coordinated version hold; reuse existing registry/protocol and acute-report assets.
3. **REVIVE notice/republication:** notice DOI 10.7326/ANNALS-26-03050 / PMID 42832813, the actual corrected report identified there, supplements and change trail. Keep the original DOI 10.7326/ANNALS-25-03959 quarantined and outside benefit support. The existing RRX-GAP-001 is already the appropriate narrow request.
4. **Full originals/companions for the abstract/indexed-only gaps:** Korea established Long COVID, MET-PREVENT, MASTERS results, schizophrenia parent, NRG-LU001, ALMERA, MA.32 clinical/metabolic reports, pancreatic cancer, adenoma recurrence and short-term crypt-foci trial. Exact known DOI/PMID/PMC/publisher locations are in `MISSING-SOURCES.md` and the machine ledger.
5. **Exact current safety/formulation source versions:** reconcile the article's DailyMed setid against already held US IR/ER labels; verify current official labeling and dated FDA context. Do not request the held labels again or treat a prior retrieval date as current regulatory verification.

## Work still required on sources already present

| Held material | Next work before guide use |
|---|---|
| COVID-OUT original/acute/viral reports and protocol | Verify report versions/correction scope; coordinate overlapping participants; inspect full methods, attrition, endpoint changes, harms, figures/tables and supplements; one family, separate report reviews |
| STAMPEDE PDF and supplement | Full Q01–Q15 review and quantitative audit, analysis populations/subgroups, treatment context, metabolic versus cancer endpoints, safety and independent verification |
| CP016 Parkinson trial | Recheck all exact between-arm estimates, biomarker units and harms denominators; avoid within-arm significance as superiority; audit participant flow and applicable limitations |
| CP017 schizophrenia companion | Inspect actual supplementary format, exploratory tests/multiplicity and missing-data handling; reconcile parent trial/family, avoid counting it as replication or inferring mediation |
| Parkinson mechanism XML/PDF and myeloma PDF lead | Verify exact source identities/versions before merging; inspect biological versus technical replication, exposure, controls, figures and translation limits; do not infer human efficacy |
| CP018 narrative review | Full review of review methods/selection/applicability, source-located leads and overlap; distinguish historical context from later primary results |
| IR/ER labels and registry/protocol files | Exact product/version/jurisdiction and currentness; full safety mapping; companion interpretation without treating protocols/labels as efficacy studies |

Every cited scholarly source needs Q01–Q15 source/locator coverage and appropriate assessment. All guide-supporting numbers need independent source checks and consequential tables/figures need visual verification. Completed AI work remains separate from qualified human clinical, editorial and legal approval. The substantive manuscript remains held until metformin ingestion/assessment is complete; no placeholder manuscript is presented as a purchasable product.

## Portable packet and validation

`coverage-ledger.json`: all 24 reference identities, exact local hash/path observations, match basis, preserved integrity state, existing synthesis bindings and Q01–Q15 input gaps. `companion-and-safety-holdings.json`: ten additional held asset entries/roles to reuse. `source-access.json`: logical roots and remapping instructions. `input-manifest.json` pins actual metadata and frozen instruction snapshots; original first-inventory hashes and a real concurrent-document validation HOLD remain in `history/`. These files contain provenance, not raw papers or reader/account data.

Commands run from the canonical application root:

```text
python3 research/batches/RRX-GUIDE-METFORMIN-001/inventory.py
/tmp/remaprx-metformin-venv/bin/python research/batches/RRX-GUIDE-METFORMIN-001/validate.py
node scripts/check-governance.mjs
```

Results: inventory accounts for all 24 references; JSON Schema, source closure, Q IDs, saved observed hashes and pinned inputs pass; all four negative probes reject lost source coverage, duplicate Q IDs, invented completed assessment and wrong hash. A repeat inventory in temporary staging regenerated the four evidence-inventory outputs with **zero changed bytes**. Governance passes for 236 preserved rule/history/ingest files. Python validation uses jsonschema 4.26.0, the repository-pinned version, installed in a temporary isolated environment; the system and bundled Python lacked it. No application build or deployment is claimed by this metadata-only packet.

The root integrator may accept this reconciliation without approving scientific content. Next: continue the existing integrity returns, prepare exact source-bound extraction assignments for held material, acquire only verified remaining gaps, assess and independently audit the metformin scope, then author the versioned manuscript under `MANUSCRIPT-CONTRACT.md`. The three-guide commercial sequencing remains the owner's product contract; this research packet does not open sales.
