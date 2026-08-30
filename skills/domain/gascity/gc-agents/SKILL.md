---
name: gc-agents
description: 'gas city agents, session management, pool lifecycle, runtime drain'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:gc-agents","domain:gas-city","effective:2026-08-30","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","provenance:agents-owned","route:agent","technology:gas-city","updates:manual","usage:on-demand"]'
---
## Verification (mandatory)

Before acting on any bead, run the four-source cross-check in
`rules/coordination/beads-verification.md` (project law) and attach the
evidence it requires.

# Agent Management

Agents are the workers in a Gas City workspace. Each runs in its own session (tmux pane, container, etc). Follow the complete
`router procedure` (skill file) and preserve its owners,
evidence contracts, failure propagation, and required output standard.
