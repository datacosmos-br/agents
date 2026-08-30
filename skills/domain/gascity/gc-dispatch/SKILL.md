---
name: gc-dispatch
description: 'gas city dispatch, sling routing, formula workflow, convoy orders'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in", "detect:opt-in:gc-dispatch", "domain:gas-city", "policy:atomic-effects", "policy:causal-subprocess", "policy:fail-loud", "policy:no-fallback", "policy:preflight-before-effects", "policy:strict-execution", "provenance:agents-owned", "route:agent", "technology:gas-city", "updates:manual", "usage:on-demand"]'
---

# Dispatching Work

`gc sling` routes work to session configs. **Multi-session configs are valid targets** — sling to the config and any eligible session can claim the work. You do NOT need to find or create an individual session first. Follow the complete
`router procedure` (skill file) and preserve its owners,
evidence contracts, failure propagation, and required output standard.
