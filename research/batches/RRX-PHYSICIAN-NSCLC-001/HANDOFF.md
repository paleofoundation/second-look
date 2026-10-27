# NSCLC physician packet sample handoff

Created October 12, 2026 for the owner's inspection. The five-page local PDF, editable DOCX and plain-text email template are complete. They model the requested subscriber experience; this is not an authenticated feature or a clinically approved release. Exact output paths and SHA-256 hashes are in `validation.json`.

## Contents and source scope

The packet contains a firm, collaborative patient cover letter; selected itraconazole and metformin study summaries; six numbered source references; and a discussion/next-steps worksheet. Patient fields are blank. It preserves the clinical context for surgery and distinguishes preliminary findings from evidence that would support a treatment change. No dosing prescription is generated.

Four primary reports are represented: two accessible abstracts and sections of two full reports. NCI guidance and the official itraconazole label supply context. Ten web-tool source/query captures are inventoried outside Git in `source-manifest.json`. These are tool-returned source text, not original downloaded report files. Full Q01-Q15 reviews, required companion inspection, comprehensive integrity review and qualified clinical approval remain incomplete. The separate candidate PMID 33559053 is a logged coverage lead, not an included report.

## Verification

- Candidate validation against the prospective packet schema passed with six unique source IDs and 14 uniquely identified source-bound claim blocks; no unresolved source references.
- The independent packet-audit agent checked the stored source captures against the manuscript's numbers, endpoints, populations, safety language and surgery applicability. It found no major numerical or endpoint errors. Its wording finding was resolved: grade 4 neutropenia is described as an event, without implying a formal serious-adverse-event classification. The bleeding event is described with its reported timing. This agent check is not independent qualified clinical approval.
- Additional NCI text was retrieved after the audit to directly substantiate the cover page's surgery and treatment-factor context; it is included in capture 10.
- All five rendered pages were visually inspected at page-image scale. Pages 2 and 3 were rechecked after source-fidelity edits, and page 1 after normalizing the condition title. No clipping, overlap, blank overflow page, split reference or missing footer was observed.
- The final PDF has five U.S. Letter pages, selectable text, page numbers, five section bookmarks, 17 internal citation links to the source page and six external links matching the source records. Exported page-content streams are identical to the inspected render. Link structure and destinations were checked programmatically; this is not an assertion of permanent remote URL availability.
- The DOCX remains editable; the matching email text supplies placeholders and identifies the attached sample edition. No email was sent.

`build_packet.py` reproduces the manuscript, claims, DOCX and email. Render the DOCX with the documents skill's `render_docx.py --emit_pdf`, inspect the page images, then run `finalize_packet.py` to create the bookmarked PDF and refresh the source/output fingerprints. The scripts use the bundled runtime. Research capture files must remain available for manifest reproduction.

## Completion dimensions

Sample manuscript, local exports, source-bound verification and visual QA: complete. Condition-wide literature coverage, full scientific appraisals, qualified clinical approval, authentication, payments, patient storage, secure sharing and subscriber release: not claimed. No canonical research data or application implementation was modified by this sample work. Concurrent changes in those areas belong to other work and were preserved.
