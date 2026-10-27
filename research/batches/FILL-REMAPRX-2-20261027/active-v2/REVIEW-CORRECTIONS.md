# Source and rendered corrections

Root independent source review identified an important ACTIV-6 inconsistency: the discussion/conclusion uses decision-threshold language, but the Statistical Analysis section explicitly states that secondary endpoints were exploratory and no decision threshold was selected. The candidate and FR2-FLV-02 now follow that statistical-methods distinction. Health-care-use uncertainty includes no effect. The primary recovery efficacy threshold is not described as a dedicated secondary endpoint threshold.

The actual section check also caught an update-history link to the deliberately hidden Results module. The new explanatory paragraph now lives in visible Evidence, and new update events link only to rendered sections. The existing shared renderer is unchanged.

A first build attempt reached the framework configuration but failed because the copied dependency entry was an absolute symlink to the original read-only checkout. That local symlink was replaced with an isolated clone of the existing installed dependencies. No package, lockfile, runtime or source fix was introduced. Final checks follow the corrected isolated runtime.
