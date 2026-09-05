---
name: gc-agents
description: 'gas city agents, session lifecycle, pool capacity, drain restart, reconciliation'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:gc-agents","domain:gas-city","effective:2026-08-30","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","provenance:agents-owned","route:agent","route:project","technology:gas-city","updates:manual","usage:on-demand"]'
---
## Verification (mandatory)

Before acting on any bead, run the four-source cross-check defined in
`rules/coordination/beads-verification.md` (project law): the registered state
records, git history, measured reality, and the intent of the most recent
code. Declare the check and attach evidence — command, working directory,
exit code, decisive output — before closing. A bead whose premise the
current code retired is closed obsolete with evidence, never executed as
written.



# Agent Management

Agents are the workers in a Gas City workspace. Each runs in its own session (tmux pane, container, etc). Follow the complete
`router procedure` (skill file) and preserve its owners,
evidence contracts, failure propagation, and required output standard.

For session state, the controller reconciliation tick, the drain/restart
handshake, pool capacity keys, and claim identity, read
`references/lifecycle-reconciliation.md` (skill file) before diagnosing a session
that will not start, will not stop, restarts in a loop, or ignores a drain.

Managed availability is proven by `systemctl --user`, `gc order check`, supervisor
log, and Dolt runtime publication—not by a process census. Never send a signal to a
process inside a unit; ask the unit owner to stop or restart.
