# Rule history

These files preserve the Second Look pilot's original requirements, classified
findings and rule adoption evidence. They are historical records, not current
release or scientific approval. Their original contents and status labels are
preserved byte for byte; [import-manifest.json](import-manifest.json) records the
source-relative names and checksums.

- [Frozen v1.1 baseline](../one-match-rule-baseline.md) and its
  [baseline record](../baseline-record.json) remain unchanged. The baseline
  SHA-256 is `01896e3c254f37483c226da52da0ef239b03eb7c762e5171675ae6dc302150d2`.
- [Pilot gap log](rule-gap-log.json) distinguishes missing or ambiguous rules
  from implementation defects, host limitations and ordinary unfinished work.
- [Owner interventions](owner-interventions.json) preserves additional scoped
  instructions and the actual historical implementation status.
- [Baseline versus revised rule](baseline-versus-revised-rule.json) and its
  [patch](baseline-versus-revised-rule.patch) describe the historical v1.1 to
  v1.2 adoption. The [sync report](rule-sync-report.json) is evidence for that
  adoption only.
- [Baseline versus proposed rule](baseline-versus-proposed-rule.json),
  [original proposal](canonical-rule-proposal.patch) and
  [proposed update-log entry](rule-update-log-proposal.txt) preserve the proposal
  stage without confusing it with a later accepted version.
- [Reader-value correction](reader-rule-correction.md) preserves the
  11 October request for substantive mechanisms, Benefits prose followed by
  scoped questions, and source-supported safety content. The document also
  distinguishes the completed bounded component edit from its proposed global
  rule wording. Its exact proposed wording is absent from the imported v1.29
  master; preserve the Second Look requirement in the project's current rules
  while tracking upstream reconciliation separately.

The adopted reusable rule is the separately pinned
[One Match Rule snapshot](../../rules/one-match-rule/ONE-MATCH-RULE.md), with
[its file manifest](../../rules/one-match-rule/snapshot-manifest.json). A later
snapshot must not replace the frozen baseline or rewrite these historical
records. Record new project requirements and findings in the current project
rules and change log, linking to the affected source, implementation and checks.

Historical local paths and task IDs identify provenance. They may not resolve
on another collaborator's machine. A link to a historical report does not
replace the actual inputs required to reproduce a research or release result.
