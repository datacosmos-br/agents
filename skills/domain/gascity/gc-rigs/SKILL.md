---
name: gc-rigs
description: 'gas city rigs, rig registration, bead scoping, suspend resume'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in", "detect:opt-in:gc-rigs", "domain:gas-city", "policy:atomic-effects", "policy:causal-subprocess", "policy:fail-loud", "policy:no-fallback", "policy:preflight-before-effects", "policy:strict-execution", "provenance:agents-owned", "route:agent", "technology:gas-city", "updates:manual", "usage:on-demand"]'
---

# Rig Management

A rig is a project directory registered with the city. Agents can be scoped to rigs via the `dir` field. Follow the complete
[router procedure](references/router-procedure.md) and preserve its owners,
evidence contracts, failure propagation, and required output standard.
