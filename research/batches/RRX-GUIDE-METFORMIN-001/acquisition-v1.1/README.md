# Metformin source request 1.1

This is a prospective acquisition packet. The final ZIP may be labeled ready only after root GP PASS and byte/hash readback. No sources have been acquired or dispatched by preparing it.

To send after readiness: attach `RRX-GUIDE-METFORMIN-001-1.1-request.zip` to the acquisition worker, then paste `REQUEST.txt`. All essential plan/schema/question inputs are inside that archive. Raw existing papers are not included. The nested existing ACTIV-6/REVIVE packet is coordination input, excluded from these fourteen new assignments.

The worker returns an actual `RRX-GUIDE-METFORMIN-001-1.1-return.zip` attachment plus the filled receiving prompt described in `REVERSE-HANDOFF-INSTRUCTIONS.txt`. Download and attach that returned archive in the Drug Repurposing / RemapRx chat. Never use the synthetic example as evidence or claim that a future attachment already exists.

`validate.py` checks the request inputs and synthetic rejection probes. `prepare-package.py --manifest` prepares the source manifest; root GP must then match its hash before `--output` will package it. Neither command fetches, dispatches, approves scientific content or edits canonical records.
