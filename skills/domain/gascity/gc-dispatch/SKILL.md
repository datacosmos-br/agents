name: gc-dispatch
description: 'gas city dispatch, sling routing, formula workflow, convoy orders'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in", "detect:opt-in:gc-dispatch", "domain:gas-city", "policy:atomic-effects", "policy:causal-subprocess", "policy:fail-loud", "policy:no-fallback", "policy:preflight-before-effects", "policy:strict-execution", "provenance:agents-owned", "route:agent", "technology:gas-city", "updates:manual", "usage:on-demand"]'
---
## Verification (mandatory)

Before acting on any bead, run the four-source cross-check defined in
`rules/coordination/beads-verification.md` (project law): registered manual
ledgers, git history, measured reality, and the intent of the most recent
code. Declare the check and attach evidence — command, working directory,
exit code, decisive output — before closing. A bead whose premise the
current code retired is closed obsolete with evidence, never executed as
written.



# Dispatching Work

`gc sling` routes work to session configs. **Multi-session configs are valid targets** — sling to the config and any eligible session can claim the work. You do NOT need to find or create an individual session first. Follow the complete
`router procedure` (skill file) and preserve its owners,
evidence contracts, failure propagation, and required output standard.
