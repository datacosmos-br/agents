---
name: dispatch-agent
description: dispatch, agent, selecting, delegating, work, specialized, local, roster
---

# dispatch-agent

Use this skill when you need to delegate a task to the most appropriate
specialized agent exposed by the active client or bundled catalog.

## How to use

1. Identify the user's intent / task.
2. Inspect the active client's available agents; when unavailable, use the
   bundled `agents.json` catalog.
3. Optionally run the bundled `dispatch.py '<task>'` from this skill directory.
4. Choose the agent with the highest trigger overlap and confidence.
5. Invoke the chosen agent through the active client's native delegation API.
6. Hand off to that agent by emitting its system prompt plus the task context.

## Rules

- Prefer specialized agents over the general `software-engineer`.
- Use the model preference from the manifest when available.
- Always preserve project context (git branch, active plan, recent memory) when handing off.
- Log the delegation decision.

## Example

Task: "Fix the failing test in tests/auth/test_login.py"
Recommended agent: `debugger`
Hand-off prompt: ask the available debugger agent to receive the failure,
identify its root cause, implement the correction, and return validation evidence.

## Project lanes

If the task requires changing project code, attach it to a verified Bead and
let Gas Town create the ephemeral lane:

```bash
gt sling <bead-id> <rig>
```

For persistent operator work use `gt crew add <name> --rig <rig>`. Never create
a raw clone or manual worktree.
