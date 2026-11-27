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

- `make setup` provisions a lane and is never a commit-hook or CI row. `make check` is
  the single gate (ADR-0042, FLEXT ADR-037): outside CI it converges gen → fix → fmt,
  then runs the read-only gates; in CI it is verify-only. `gen`, `fix`, `fmt`, `lock`
  and `ci` are not public verbs. `make upg` is the only lock writer. The ordered cycle
  is owned by `rules/workflow/agent-delivery-doctrine.md`; outside it, an explicit gate
  run only diagnoses a red one.
- Record each run's command, directory, exit and decisive output for its scope.
  Compare native timing receipts for the same workload and verify behavior and coverage.

Check `$crg` consumers before declaring code dead. On a confirmed integration-tip red,
the finder fixes it this cycle via `rules/git/gitflow-branch-pr.md`. Record the full SHA
on the selected tracker when available, or in the PR otherwise.
