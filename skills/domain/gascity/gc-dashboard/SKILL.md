---
name: gc-dashboard
description: "gas city dashboard, api server, web ui, realtime monitoring"
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:gc-dashboard","effective:2026-08-30","route:agent","route:project","subject:gascity","usage:on-demand"]'
---

## Verification (mandatory)

Before acting on any bead, verify it under `rules/workflow/beads-traceability.md`.

# Dashboard

The dashboard is a web UI compiled into the `gc` binary for monitoring convoys, agents,
mail, rigs, sessions, and events in real time. Follow the complete `router procedure`
(skill file) and preserve its owners, evidence contracts, failure propagation, and
required output standard.
