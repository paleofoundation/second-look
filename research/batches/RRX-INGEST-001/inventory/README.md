# RRX-INGEST-001 continuity inventory

This is a metadata and byte-continuity inventory, not a scientific ingest, review or release.

The app has 281 source records. The separate private research store has
2765 acquisition source records, 1990 report identities,
1930 assets and 570 draft results. These populations overlap and
must not be added together. No independent-study count is asserted.

The MOA archive has 1049 full-PDF entries and 223 prior-holding
cross-references. Its automatic tags do not prove eligibility. Existing targets may be screened;
additional names remain leads and do not create guides.

`source-records.jsonl` preserves separate origin records; `lineage.jsonl` gives exact source
file/pointer and record hashes. `return-appearances.jsonl` retains batch appearances without
counting duplicate appearances as new sources. `identity-groups.jsonl` proposes exact matching
candidates and conflicts; it never merges DOI reports. `bindings.jsonl` separates current editorial
usage and source-located private draft bindings from acquisition tags. No new findings are generated.

`source-locations.json` resolves logical roots, relative files and archive members with byte/hash
verification. Remap the four CLI roots on another host; host paths alone are not source identity.
Raw papers stay outside Git and public assets. Historical checkpoint receipts preserve their scope;
latest stored draft records do not imply acceptance into the current app or human scientific approval.

Run `python3 scripts/research_inventory.py` to regenerate, or add `--check` for a read-only
reproducibility comparison. The tool writes only this inventory directory. Missing expected inputs
or changed baseline counts are held explicitly. `summary.json` is the machine-readable status.
