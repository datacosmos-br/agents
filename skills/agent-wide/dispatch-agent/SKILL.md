---
name: dispatch-agent
description: 'agent delegation, specialist selection, bounded work'
metadata:
  aihub.tags: '["provenance:agents-owned","role:delegation","updates:manual","usage:on-demand"]'
---

# dispatch-agent

Use this skill when you need to delegate a task to the most appropriate
specialized agent exposed by the active client.

## How to use

1. Identify the user's intent / task.
2. Inspect the active client's available agents. If the client exposes no
   roster, stop without inventing an identity.
3. Choose the agent with the highest trigger overlap and confidence.
4. Invoke the chosen agent through the active client's native delegation API.
5. Hand off the task context and expected evidence through that native API.

## Rules

- Prefer specialized agents over the general `software-engineer`.
- Never use a bundled, cached, or hardcoded roster as a fallback.
- Model selection remains with the active runtime's canonical model owner; the
  roster must not invent tier, family, variant, or provider aliases.
- Always preserve project context (git branch, active plan, recent memory) when handing off.
- Return the delegation decision and confidence to the orchestrating caller.

## Example

Task: "Fix the failing test in tests/auth/test_login.py"
Recommended agent: `debugger`
Hand-off prompt: ask the available debugger agent to receive the failure,
identify its root cause, implement the correction, and return validation evidence.

## Project changes

Changing project code requires a declared Gas City city, rig, agent, formula,
run, and session plus the repository's native Git and PR contract. While Gas
City runtime is suspended, delegate only work that stays in the existing
checkout; never create a clone, worktree, run, session, or substitute lane.
