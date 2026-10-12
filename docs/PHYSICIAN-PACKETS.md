# Physician packets: portal and document contract

Owner follow-up, October 12, 2026: implement condition-specific physician packets inside the paid-subscriber portal, with print/email delivery and a more professional, table-led structure. The owner permits leaving the specialist name and contact blank. No invented specialist, physician identity, credential, endorsement or contact is authorized. A real contributor may later be credited according to their actual qualifications and role; a byline is distinct from clinical approval.

This supersedes the earlier sample-only implementation scope. It does not change live prices, start billing, create clinical approval, or authorize sending a message during development. Existing commercial and scientific release requirements apply. Pricing continues to follow the separately adopted guide-commerce contract; this feature makes no pricing change. Earlier sample-price assumptions are historical only. A single-guide purchase does not grant the subscription-only packet tool.

## Document design

| Order | Physician's task | Presentation |
| --- | --- | --- |
| Clinical brief | Understand the question and applicability quickly | Short request, blank patient/context fields, sourced clinical context, intervention/population/implication table |
| Evidence detail | Inspect what each trial actually found | Two study blocks per page; population, design, comparison, primary endpoint, additional findings and limitations kept together |
| Consultation | Resolve safety and next steps | Safety table, three focused questions, action/person/date table |
| Sources and accountability | Verify claims and contributor identity | Numbered clickable citations, readable source URLs, source-access basis, evidence scope, edition/check date, blank credit/contact fields |

Use RemapRx ink and blue, restrained pale-blue table headers, whitespace, 8.3–11 pt table text, repeated page footers, U.S. Letter print rules and table headers. Preserve meaning in grayscale. Do not use efficacy icons, drug rankings, decorative artwork or fabricated evidence grades. This packet is a selected-source discussion aid, not a recommendation to delay or replace treatment.

## Member flow

`My guides → Physician packets → Condition → Generate packet → Preview → Print / Save PDF, Download PDF, or Email packet`.

The server checks the trusted Sites identity and the existing persisted guide-membership record for every catalog, document and PDF request. Only active, unexpired membership grants access; scheduled renewal cancellation preserves access through the paid-through instant. Browser flags, a reader role, an individual order, a supplied user ID or an expired membership never grant access. Responses are private/no-store.

No patient details are collected. Patient fields are blank in the output. The email panel supplies a copyable message and opens the member's email composer; the member must add the downloaded attachment and verified recipient. The application does not send email, automatically attach a PDF, publish a sharing link or imply that a message was delivered. The practice's patient portal can also be used.

## Exact-edition release contract

Private R2 object `physician-packets/catalogue.v1.json` contains an array matching `packetReleaseSchema`. Each entry names one current condition edition, immutable structured-JSON/PDF asset keys and SHA-256 hashes, and exact-edition editorial, qualified clinical and legal decisions with reviewer identity, qualifications, scope, conflicts and timestamps. Approvals bind both assets; changing either requires re-review. This retains the existing medical-product release boundary. Contributor credit in the content additionally requires recorded consent. No reviewer identity is collected from members.

`packetSchema` validates renderable structured content, source references and unique study/source identities. Full raw source captures and editorial production records are not sent to clients. Download verifies both the approved content and the PDF bytes. Pending/withdrawn/unapproved entries are not offered. Empty catalogs are an honest availability state. Unknown or unavailable conditions never generate improvised medical advice. No hosted approval records or billing records are inserted by this implementation.

## Reference and source mapping

Consulted Microbiome Medicine `ConditionsTable.tsx` and its design-system reference, PepsAnon `evidence-table.tsx`, and RemapRx's existing account, membership and source-citation paths. Adapted semantic table headers and source proximity to printable pages. Existing article drawers, grades, reading policy and research access remain unchanged.

The NSCLC layout fixture reuses the four source-checked reports and context from `second-look-navigation/research/batches/RRX-PHYSICIAN-NSCLC-001/` in the canonical workspace. This is a layout transformation of the existing sample, with no new literature acquisition, corpus import, certainty grade, clinical approval or completeness claim. Exact input hashes and claim IDs are recorded in the design handoff. The fixture is for local design/test artifacts only and must not enter the released R2 catalog or a public browser bundle.

## Verification and release

Verify access failures, account isolation, membership expiry, exact content/PDF hashes, approval/withdrawal changes, unknown conditions, injection/citation boundaries, retry states, mobile reading, every print page and email handoff wording. Tests use synthetic approval fixtures; they do not create real approval. A build is not paid-service launch or scientific acceptance. Record deployment and remaining product prerequisites separately in the implementation handoff.

## Earlier sample record (historical)

The following record is retained for provenance. Its sample-only limitation is superseded by the portal follow-up above; earlier pricing assumptions do not override later commercial requirements.

# Physician discussion packets

## Owner scope

October 12, 2026: provide paid subscribers with printable and emailable physician packets inside the logged-in portal, using firm, effective language to discuss relevant drug-repurposing evidence. The follow-up requests a non-small-cell lung cancer sample to inspect before implementing the feature. The $59/month and $39/guide figures remain planning assumptions. This sample does not authorize email delivery, account/data collection, payment changes or deployment.

## Sample implementation choices

Prepare a five-page U.S. Letter packet: patient cover note and clinical takeaway; two itraconazole summaries; two metformin trial summaries; numbered original-source references and coverage statement; patient/physician discussion worksheet. Supply an editable DOCX and a separate plain-text email template alongside the printable PDF. Use blank patient fields rather than invented medical facts. This is an illustrative selection, not the complete condition intervention roundup. No dosing regimen or automatic patient-specific treatment advice is generated.

The packet is explicitly a sample with independent clinical review pending. It supports documenting the physician's reasoning, clinical relevance and agreed next steps. It must not turn preliminary research into evidence that surgery can be omitted or postponed. Preserve favorable findings and null/harmful findings together, exact populations and comparators, endpoint hierarchy, source access limitations, stable source identities, and edition/check dates. No formal evidence grade or completed study appraisal is implied.

## Durable sources and deliverables

The prospective [sample research plan](../research/batches/RRX-PHYSICIAN-NSCLC-001/PLAN.md), schema, readiness, manuscript, claim/source records, source manifest, Q01-Q15 coverage and verification/handoff live in `research/batches/RRX-PHYSICIAN-NSCLC-001/`. Existing canonical data and concurrent calibration work are read-only inputs; no application evidence or review is imported or overwritten. Newly discovered candidates retain packet-local identities pending canonical reconciliation.

On this host, final files are under `/Users/kmfp/Documents/ChatGPT/Drug Repurposing/artifacts/physician-packet-nsclc/output/`. Web-query/source captures remain outside Git in the sibling `research/` directory, with hashes and access basis in the batch manifest. The builder and manuscript remain reproducible repository artifacts. Source links are supplied instead of redistributing copyrighted article PDFs.

## Acceptance and remaining work

Check every displayed number, source link and citation destination; render and visually inspect all five pages; verify selectable PDF text, page numbering and an editable DOCX. Record source verification separately from full study appraisal and qualified clinical approval. The static sample does not implement authentication, subscriptions, patient storage, secure links or actual email delivery. Those features and the existing clinical/commercial release checks remain future work.
