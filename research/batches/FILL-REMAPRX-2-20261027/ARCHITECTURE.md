# Canonical-path collision proof

Pinned source: d118d305b59cac5e54ca7f9e5aa55cea682d2cee.

- lib/content.ts:2 imports data/public-content.json. Lines 25 onward create canonicalContent and content.guides. Discovery entries are filtered when a canonical guide already has the same ID or route. All seven proposed pages already have canonical guide records.
- app/[...path]/page.tsx:81 resolves the requested guide from content.guides. Changing an unused discovery entry cannot change the existing page.
- scripts/parent_scope.py:7 names editorial/parent-guide-scopes.json as the maintained parent authority; apply_parent_scopes deliberately reapplies its guide fields and rejects unreconciled new source associations. A public-only patch would be unstable under regeneration.
- scripts/apply-reader-outcomes.py:186 writes canonical content, public content and parent scope alongside the evidence projections. Its existence does not authorize running the generator or editing forbidden files.
- lib/mechanisms.ts:1 imports data/public-mechanisms.json. That shared mechanism projection is also forbidden, so source-bound mechanism changes need an explicit scoped exception.
- AGENTS.md requires existing shared rendering and canonical data paths, and forbids historical corpus generators over current reviewed work. It also requires rule adoption in docs/PROJECT-RULES.md and docs/RULE-CHANGELOG.md, both forbidden in this order. The exact new requirement is therefore preserved here with contract propagation pending an explicit ownership ruling.

The conflict affects files, even though the seven guide identities do not overlap the 13 filled guide identities. Separate branches alone do not resolve a literal no-file-collision instruction. No forbidden file has been edited.
