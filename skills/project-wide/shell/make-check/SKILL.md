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

- Reuse a valid environment. Provision an absent or invalid environment through
  `make setup`, and leave version changes to the upgrade verb.
- Show the changed behavior through its real entry point. Native commit and push hooks
  and integration CI run the declared checks. Diagnose red results with the owning
  verb and follow `rules/git/gitflow-branch-pr.md`.
- Each run records command, directory, exit and decisive output; a focused run proves only
  its own scope.

Compose `$crg` when the change needs structural impact; a graph hit is not dead code until
its consumers are checked. A failure outside the authorized scope is reported with its
evidence, never repaired in passing.
