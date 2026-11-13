---
name: gc-rigs
description: "gas city rigs, rig registration, bead scoping, suspend resume"
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:gc-rigs","effective:2026-08-30","route:agent","route:project","subject:gascity","usage:on-demand"]'
---

## Verification (mandatory)

Before acting on any bead, verify it under `rules/workflow/beads-traceability.md`.

# Rig Management

A rig is a project directory registered with the city. Agents can be scoped to rigs via
the `dir` field. Follow the complete `router procedure` (skill file) and preserve its
owners, evidence contracts, failure propagation, and required output standard.
