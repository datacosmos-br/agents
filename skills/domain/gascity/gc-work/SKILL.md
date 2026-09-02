---
name: gc-work
description: 'gas city work, bead lifecycle, claim close, hook ready'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:gc-work","domain:gas-city","effective:2026-08-30","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","provenance:agents-owned","route:agent","route:project","technology:gas-city","updates:manual","usage:on-demand"]'
---
## Verification (mandatory)

Before acting on any bead, run the four-source cross-check defined in
`rules/coordination/beads-verification.md` (project law): the registered state
records, git history, measured reality, and the intent of the most recent
code. Declare the check and attach evidence — command, working directory,
exit code, decisive output — before closing. A bead whose premise the
current code retired is closed obsolete with evidence, never executed as
written.



# Work Items (Beads)

Everything in Gas City is a bead — tasks, messages, molecules, convoys. The `gc bd` CLI is the primary interface for bead CRUD. Follow the complete
`router procedure` (skill file) and preserve its owners,
evidence contracts, failure propagation, and required output standard.
