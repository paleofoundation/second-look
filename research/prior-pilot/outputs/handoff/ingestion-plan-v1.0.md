# Second Look ingestion plan · v1.0

Plan ID: `SL-INGEST-1.0`. Created 2026-10-08T06:51:18.683276+00:00. The authoritative executable record is [ingestion-plan-v1.0.json](ingestion-plan-v1.0.json). Its readiness and exact hash are recorded separately in [Mission Control](../mission-control.json).

This plan was created after the initial pilot extracted evidence and imported it into the site. Earlier scoping/full prompts were handed back as artifacts, but no Grokbot job was dispatched. This is retrospective adoption; it does not satisfy the new sequencing requirement for work that already happened. The [sequence audit](../governance/ingestion-sequence-audit.json) preserves that distinction. The frozen v1.1 rule and existing evidence remain unchanged.

## Scope and delivery

Cover all 36 stable DR questions through the declared 8 October 2026 cutoff. Keep PRIMARY original studies separate from CONTEXT definitions, reviews, regulation and discussion demand. Preserve exact drug, condition stage, population, route/formulation, comparator, outcome and follow-up. Include null, adverse, contrary and unpublished evidence; log actual database queries, screening, access limits and update searches. A later cutoff requires a versioned scope change.

Return schema 1.0.0 `corpus.json` with `synthetic=false`, the entity JSONL exports, coverage, source manifest, identity map, exceptions, receipt, validation and completion report. The bundled schema hash is `32953789f4b96f19d7f7f44394f930aa33dceb33245478cde2fcab2c28cc5a70`. The JSON plan lists exact required files, manifest fields, missingness values and input hashes. Preserve immutable lawful source bytes under PRIMARY/CONTEXT in private storage; partial snapshots, abstracts and challenge pages cannot become full-text/PDF claims.

## Ownership and batch order

Mission Control owns accepted merges and site publication. Grokbot acquires only after an explicit dispatch. The evidence worker extracts bounded assigned batches; the audit worker independently checks them. Human scientific reviewers remain unassigned. Every batch uses its own incoming directory; workers return candidate patches and cannot overwrite accepted evidence or the site.

| Batch | Work | Dependency |
|---|---|---|
| B00 | Retrospective pilot reconciliation — DR001, DR002, DR003, DR004 | Existing pilot only |
| B01 | Source integrity and safety repair — DR001, DR002, DR003, DR004, DR013, DR014, DR016 | B00 |
| B02 | Established illness trial completion — DR002, DR003, DR004, DR017, DR018 | B01 integrity triage |
| B03 | Remaining Long COVID and process coverage — DR001, DR002, DR003, DR004, DR005, DR009, DR010, DR011, DR012, DR013, DR014, DR015, DR016, DR017, DR018, DR020, DR021 | B00, P0, varied calibration before scale |
| B04 | Oncology questions — DR006, DR007, DR008, DR019, DR022 | B00, P0, varied calibration before scale |
| B05 | Naltrexone and pramipexole — DR023, DR024, DR025, DR026, DR027, DR028, DR029, DR030, DR031 | B00, P0, varied calibration before scale |
| B06 | Rapamycin and acarbose — DR032, DR033, DR034, DR035, DR036 | B00, P0, varied calibration before scale |

B01 takes priority because correction/retraction and safety uncertainty affect existing pages. B02 completes established-illness reports. B03–B06 organize broader acquisition; they are not active jobs. The JSON plan assigns all 36 topic IDs and exact current report/claim/page relationships.

## Extraction, verification and recovery

First hash and classify the received files, reconcile IDs/versions and persist a batch receipt. Before extraction, record the eligible list, worker, plan/schema hash and start time. Extract every eligible full text or record an explicit pending/failure state, with located outcomes, arms, denominators, uncertainty, harms, missingness and Q01–Q15 reviews. Use a varied 20–30-document calibration before broad scaling where that many eligible documents exist; the existing three-review pilot is a documented smaller calibration, not a substitute for full coverage.

Validate all schema/graph/hash requirements. Independently inspect every launch-supporting paper, identity conflict and surprising result; audit at least a recorded random 10% of remaining full-text extractions and expand the affected batch after a material error. Formal appraisal and human approval remain distinct from automated validation. Current numeric test fixtures cover selected calibration effects, not every future result.

Log each exception with source, stage, evidence, owner, attempt and next action. Allow an initial lawful retrieval and at most two alternate official/repository/format attempts, honoring transient retry instructions. Then retain a visible pending/access gap. Preserve corrupt/OCR failures separately; never guess numeric cells. Quarantine identity conflicts and retracted supportive claims. A schema change pauses dependent work until the schema, plan, fixtures and migration tests are versioned. Roll back the affected evidence/claims/pages together while preserving unrelated changes.

## Mapping and completion

The path is DR question → report/study/result → located claim → review and sentence citations → guide/FAQ/Research → tested private preview → human release gate. DR001 maps to G-MET-PREVENT, DR002 to G-MET-TREAT and DR003 to G-NMV-TREAT; DR004 has no accepted benefit claim. The metformin profile, long COVID overview and comparison inherit only accepted relevant claims. Other questions retain acquisition-pending states until evidence supports a real answer. Every import proposes a record and page diff and proves unchanged-input idempotence before the integrator merges.

A completed batch reconciles every received file and every accepted, duplicate, context, excluded, quarantined, unreadable or pending disposition. Track reports, independent families, PDFs, extractions, reviews, mapped claims and pages separately. Topic completion requires the declared search coverage and explicit disposition of all in-scope records; an unfinished source/search/appraisal remains INCOMPLETE. Technical private deployment is not scientific or public release.

## Required gates

1. **P0:** Persist this version, validate its input hashes, reconcile prior sequence, and record READY with the exact digest in Mission Control. No additional owner approval is required.
2. **P1:** Before any file-request handoff or dispatch, including scoping, check P0 and attach this plan, schema, topic scope, identity snapshot and readiness receipt. Log the actual handoff/dispatch separately. Internally drafting a prompt is not dispatch.
3. **P2:** Before extraction, additionally require a hashed receipt, source/identity/media triage, eligible list and assigned worker.
4. **P3:** Before import, additionally require candidate validation, exception disposition, record/page diffs, independent check, idempotence evidence and fresh accepted-base hashes. Mission Control alone merges.
5. **P4:** Keep source completeness, appraisal, human approval and production release gates separate.

The next authorized step is plan-gated B01 acquisition handoff. Creating this plan does not launch Grokbot or perform another extraction/import.

## Workload and portable return

Three full review drafts exist, but no reliable separate per-document timing was captured. File timestamps and parallel work cannot supply review throughput, so no document-per-hour or complete-corpus ETA is claimed. The next calibration must log active minutes by source/stage, media/design and rework; estimate subsequent batches only from those measured results. The 36 questions are not a paper-count estimate.

External workers receive the attached acquisition ZIP and return a ZIP attachment to Mission Control. Bundled relative paths are portable inputs; the Mac staging directory belongs to the integrator and is not assumed accessible to Grokbot.

## Schema compatibility and candidate validation

The existing canonical schema does not have a modeling paper type. Preserve modeling originals and metadata in the separate typed staging inventory; extraction/import for that class stays HOLD until a tested schema/plan revision. Do not force a modeling record into a clinical or engineering class. Registry/protocol metadata may be related CONTEXT, excluded from study counts; unsupported registry outcomes need a schema revision. Unreadable files remain an operational exception, with paper metadata/access state only where known. Never fabricate required bibliographic fields.

The existing full-pilot validator requires four calibration result IDs, so it is not a standalone batch validator. The candidate wrapper explicitly rejects synthetic evidence and runs the same structural/graph/hash checks with those four fixed assertions disabled. Test compatible fixtures before P2; run the normal fixed regression checks on a merged scratch graph before P3. An accepted-corpus import remains a separate, gated mutation with diff and repeat-import evidence.
