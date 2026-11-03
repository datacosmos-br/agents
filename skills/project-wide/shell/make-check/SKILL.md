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

- `make setup` runs only when the environment is absent or fails its own check; a valid
  environment is reused, and lock changes belong to the upgrade verb.
- The changed behavior is shown through its real entry point first; then `make check`,
  any further declared gate verb and the test verb run, each invoked explicitly and never
  obtained as a side effect of another.
- Each run records command, directory, exit and decisive output; a focused run proves only
  its own scope.

Compose `$crg` when the change needs structural impact; a graph hit is not dead code until
its consumers are checked. A failure outside the authorized scope is reported with its
evidence, never repaired in passing.
