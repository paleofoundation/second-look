# Private source access

Raw originals are external dependencies of this application repository. The
CAL07 source registry is `source-locations.json`; its logical `CAL_T1_RAW` root
currently resolves to the sibling `private-research/RRX-INGEST-001/CAL-T1-20261012`
directory in the parent workspace. The parent workspace is also a Git checkout,
so its local `.gitignore` explicitly excludes `/private-research/`. No raw file
from this root is tracked. Preserve that exclusion when working here.

For another machine, transfer the lawful source files through a private,
receiver-accessible channel, preserve relative paths, and edit a local copy of
the source map's root binding. Keep this copy and originals outside Git, or in
an explicitly ignored raw-source directory. Do not copy papers, response pages,
session material or failed-download diagnostics into the application or public
assets. Metadata receipts and short source-bound review evidence are separate
from the originals.

Verify a received CAL07 asset from the application root:

```sh
python3 -m scripts.research_ingest resolve \
  --source-map LOCAL_SOURCE_LOCATIONS.json \
  --source-id MECH-D07-HEDGEHOG-2010
```

The full-review validator also accepts `--source-map LOCAL_SOURCE_LOCATIONS.json`.
It checks the receiving files against the immutable assignment hashes and byte
counts and records the local map hash. A successful local source check does not
prove access for another collaborator, and a URL alone is not a delivered file.

The CAL07 registry contains the NIH manuscript, seven original JPEG figures, the
ten-page publisher supplement and two dated exact-identifier metadata responses.
The acquisition receipts preserve failed publisher/PMC alternatives separately;
those response pages are not scientific sources. The publisher supplement's
actual verified article PII is `S153561081000070X`. The different PII listed in the
initial prospective alternatives was not used and must not be adopted as an
identity alias.

Later packets use separately finalized source-map versions, preserving CAL07's
frozen registry. ZIP members retain the parent archive and member hashes as well
as individual readable-file identities. Preparing or receiving those files does
not claim that they have been read, verified scientifically or released.
