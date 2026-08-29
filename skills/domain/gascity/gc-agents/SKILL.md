---
name: gc-agents
description: 'gas city agents, session management, pool lifecycle, runtime drain'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in", "detect:opt-in:gc-agents", "domain:gas-city", "policy:atomic-effects", "policy:causal-subprocess", "policy:fail-loud", "policy:no-fallback", "policy:preflight-before-effects", "policy:strict-execution", "provenance:agents-owned", "route:agent", "technology:gas-city", "updates:manual", "usage:on-demand"]'
---

# Agent Management

Agents are the workers in a Gas City workspace. Each runs in its own session (tmux pane, container, etc). Follow the complete
[router procedure](references/router-procedure.md) and preserve its owners,
evidence contracts, failure propagation, and required output standard.
