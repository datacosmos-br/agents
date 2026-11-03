---
name: gc-work
description: "gas city work, bead lifecycle, claim close, hook ready"
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:gc-work","effective:2026-08-30","route:agent","route:project","subject:gascity","usage:on-demand"]'
---

## Verification (mandatory)

Before acting on any bead, verify it under `rules/workflow/beads-traceability.md`.

# Work Items (Beads)

Everything in Gas City is a bead — tasks, messages, molecules, convoys. The `gc bd` CLI
is the primary interface for bead CRUD. Follow the complete `router procedure` (skill
file) and preserve its owners, evidence contracts, failure propagation, and required
output standard.
