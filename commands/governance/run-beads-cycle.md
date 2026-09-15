---
name: run-beads-cycle
description: Execute the continuous bead governance cycle (collect, classify, align, unblock, title, deferred, validate) in bounded, reviewed batches.
argument-hint: "--mode <collect|classify|align|unblock|title|deferred|all> [--csv FILE] [--beads ID,...] [--limits N,...] [--apply] [--map FILE.json] [--json-report FILE.json]"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","route:project"]'
---

# Beads Cycle

Treat `$ARGUMENTS` as bounds for the cycle execution. Load the `beads-cycle` skill.
Resolve tracker authority before effects. A suspended tracker remains read-only
unless the current operator explicitly authorizes mutations to that exact store.

1. Regenerate or use provided CSV as source of truth (current open beads).
2. Execute requested `--mode` (default `all` runs full cycle in order).
3. Each mode runs dry-run by default; `--apply` mutates only after operator
   or coordinator agent approves the consolidated plan.
4. Batch size enforced by `--limits` (default >=25 per batch); cap 20 closes
   per batch via `bd batch`.
5. After each batch: `bd doctor --check=validate`, dedup gate, `bd orphans`.
6. Record every change via `bd note` with `WORKSPACE SYNC` evidence format.
7. Never mutate beads of active third-party lanes (§0.7 + claims ≤24h).
8. Close only with 3 legal reasons: `SUPERSEDED`, `OBSOLETE`, `DONE` with proof.

(End of file)
