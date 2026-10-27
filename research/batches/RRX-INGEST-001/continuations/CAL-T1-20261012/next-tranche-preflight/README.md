# Remaining tranche preflight

This isolated return is metadata-only planning for CAL01–06 and CAL08 after CAL07. It preserves the original assignments and all holds; it does not modify CAL07's frozen source plan, validator, schemas or source map.

`metadata-inventory.json` records 11 source-file references across seven packets, including the same held PDF under two separate identities. It verifies actual hashes/media, physical PDF counts, streamed ZIP-member identities/counts and PASTIS HTML section/figure/link attributes. No scientific body text or figure interpretation was extracted. `inventory.py` reproduces this scope; five synthetic tests check unsafe archive paths, duplicates/case collisions, links, unsupported types, size/ratio bounds and attribute-only HTML inventory.

`eligibility-summary.json` and per-packet `eligibility.json` separate three conditionally eligible packets from four held packets. CAL01 has a 9-page main report and three unmaterialized PDFs of 7, 29 and 56 pages. CAL02 has 22+44 pages. CAL03 has 8+30 pages and two WebP assets whose earlier unsupported-format holds need prospective resolution. CAL04/05 preserve the shared 34-page preprint identity conflict. CAL06 preserves quarantine with no eligible assigned full text. CAL08 lacks four referenced JPEGs and DOCX supporting information; no full-review assignment is fabricated for its unsupported missing companion.

`CAL-01`, `CAL-02` and `CAL-03` contain schema-valid prospective assignment candidates. They are not passed plans. CAL01's three members remain pending until private safe materialization and receipt. `source-locations.prospective.json` contains remappable local roots, verified file references and archive-member lineage; it does not overwrite any current source map. `archive-members.prospective.json` and `ZIP-MEMBER-CONTRACT-DRAFT.md` define the proposed preparation boundary. `CLINICAL-APPRAISAL-DRAFT.md` supplies distinct trial/crossover and observational questions without pretending any source has been appraised.

`plan.proposed.json` is deliberately marked draft, names preserved holds and has no GP receipt. The integrator must accept CAL07, finalize source preparation/identity/integrity scope, adopt the design-specific method, pin current controls and record a fresh GP before substantive authoring. Missing protocol/registry/integrity checks discovered later remain explicit gaps. An existing byte-perfect packet is not a claim that every relevant source has been acquired or that source coverage is complete.

`bibliographic-identity.proposed.json` adds a central front-matter title/DOI/PMID/version reconciliation stage for CAL01–03 before scientific fan-out. It preserves historical IDs and explicitly marks front-matter verification unperformed. Separate, prospective exact-identifier Europe PMC/Crossref acquisitions after CAL07 must supply the actual dated Q13 metadata assets. No current notice/version check is inferred from closed-packet metadata; no remote lookup was performed in this preflight.

Reproduce metadata without source extraction:

```sh
python3 research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/next-tranche-preflight/inventory.py --root .
python3 -m unittest discover -s research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/next-tranche-preflight -p test_inventory.py -q
python3 research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/next-tranche-preflight/prepare-drafts.py
```

`pdfinfo` supplies physical page counts; Python/jsonschema dependencies match the existing ingestion environment. Raw papers and archive members remain external private dependencies. The metadata source inspection and scope claims should receive independent review before adoption.
