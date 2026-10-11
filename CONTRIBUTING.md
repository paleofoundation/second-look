# Contributing to Second Look

Read [AGENTS.md](AGENTS.md), [project rules](docs/PROJECT-RULES.md), and the [collaborator handoff](docs/COLLABORATOR-HANDOFF.md). **Research contributors must read [Research ingestion](docs/RESEARCH-INGEST.md) before requesting files, extracting or importing evidence.**

Create a bounded branch from current `main` (default prefix `codex/` for agent work). Assign one integrator for a research batch, preserve concurrent changes and use a pull request for review. Include the changed claims/records and their exact sources, checks, unresolved gaps and next action. A new requirement belongs in the project contract and rule changelog immediately, even if implementation is unfinished. Update the ingestion plan/schema/checkpoint whenever that requirement changes research work.

Run `node scripts/check-governance.mjs` and relevant app/content checks. Document unexecuted or failing checks. CI checks repository integrity; it cannot infer undocumented instructions or certify scientific review. Keep source files, secrets, live accounts and private storage out of commits. This private repository contains internal research/editorial records and should not be made public without a separate review and explicit owner direction.

Merging or pushing code is not website deployment, human editorial approval, a completed research appraisal or permission to sell a guide. Follow the existing release workflow.
