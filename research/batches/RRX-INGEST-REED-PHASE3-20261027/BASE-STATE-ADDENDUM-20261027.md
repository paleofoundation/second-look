# External base state observation, October27 2026

After the original16:38 order and this runner branching at exact8aacc6b, PR11 was externally merged and its head advanced to f22edbfd. The first PR12 readback exposed the changed base. This runner paused additional pushes and performed one authorized read-only fetch; no branch, source packet or earlier approval was rewritten.

Both old8aacc6b and newf22edbfd have identical whole Git tree b1496e880cc2202c4aa016365bde2355cddf60ab. The new commit has parents8aacc6b and6e05f3b. Their file diff is empty and all1455 frozen hashes match. CONDUCTOR independently confirmed the same result and PR12 merge base8aacc6b, concluding that no integration/ref change is needed for the existing authorized work. Continue ordinary source/checkpoint work and serial plain HTTPS pushes on the same INGEST3 branch and PR12, with original8aacc6b ancestry preserved. This does not authorize merge/rebase/reset/retarget or PR11 mutation.

This addendum records observed remote history and the scope of the coordinator determination; original plan/readiness and earlier manifests remain immutable. Any further external tree change reopens the affected reconciliation. Source-specific independent audit and all scientific/human/release boundaries remain unchanged.
