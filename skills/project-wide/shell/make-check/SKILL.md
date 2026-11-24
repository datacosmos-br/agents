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
- The changed behavior is shown through its real, installed entry point first; only then
  run `fix`, `fmt`, `check` and `tests`, never the opposite
  (`rules/workflow/agent-delivery-doctrine.md`). The declared gates also run through the
  commit and push hooks and the integration CI, and an explicit gate run only diagnoses a
  red one.
- Record each run's command, directory, exit and decisive output for its scope.
  Compare native timing receipts for the same workload and verify behavior and coverage.

Check `$crg` consumers before declaring code dead. On a confirmed integration-tip red,
the finder fixes it this cycle via `rules/git/gitflow-branch-pr.md`. Record the full SHA
on the selected tracker when available, or in the PR otherwise.
