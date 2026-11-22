---
name: make-check
description: "native gates, root make verbs, runtime-first validation"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","usage:router"]'
---

# Make check

Activate when selecting or running a repository's validation; an ordinary writing request
starts no provisioning.

Read the repository instructions and root Makefile, then run its declared verbs directly,
never an underlying tool in their place. `rules/workflow/canonical-commands.md` owns the
verbs, deadlines, profiling, locks and test selection.

- `make setup` runs first in the project's declared commit and CI sequence; elsewhere it
  runs only when the environment is absent or fails its own check. A valid environment is
  reused, and lock changes belong to the upgrade verb.
- The changed behavior is shown through its real entry point first; the declared gates
  then run through the commit and push hooks and the integration CI, and an explicit gate
  run only diagnoses a red one.
- Record each run's command, directory, exit and decisive output for its scope.
  Compare native timing receipts for the same workload and verify behavior and coverage.

Check `$crg` consumers before declaring code dead. For a failure confirmed on the
integration tip, the finder records its SHA on the Bead and fixes it in the same cycle
through `rules/git/gitflow-branch-pr.md`.
