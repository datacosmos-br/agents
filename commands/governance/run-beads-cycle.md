---
name: run-beads-cycle
description:
  Execute the continuous bead governance cycle (collect, classify, align, unblock,
  title, deferred, validate) in bounded, reviewed batches.
argument-hint:
  "--mode <collect|classify|align|unblock|title|deferred|all> [--csv FILE] [--beads
  ID,...] [--limits N,...] [--apply] [--map FILE.json] [--json-report FILE.json]"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","route:agent"]'
---

# Beads Cycle

Treat `$ARGUMENTS` as bounds for the cycle execution and run the `beads-cycle` skill,
which owns the order, batch limits, gates and closure reasons. Resolve tracker
authority before effects. A suspended tracker remains read-only unless the current
operator explicitly authorizes mutations to that exact store. `--mode` defaults to
`all` and `--limits` to at least 25 per batch; each mode is a dry run, and `--apply` mutates only after the operator or the
coordinator agent approves the consolidated plan.
