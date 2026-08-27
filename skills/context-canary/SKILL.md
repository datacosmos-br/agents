---
name: context-canary
description: context, canary, long, high-risk, sessions, detect, drift, compaction, loss, instruction
bundle: communication
scope: universal
license: MIT
metadata:
  version: 1.0.0
---

# Context Canary

A tiny repeated signal that reveals instruction drift, compaction loss, or context
rot early — before a real constraint is silently violated.

## Install

State the task contract once, then make this the first line of every response:

```text
**<name> · t<N> · ctx ok|ctx aging|ctx thin**
```

- Use the operator's name (ask if unknown). Increment `t<N>` each response.
- `ctx ok`: task anchored. `ctx aging`: long session, re-check facts.
  `ctx thin`: reconstructing from summaries/partial memory.
- Unsure of the count → emit `t?` and declare the canary tripped.

## Trip protocol

A trip = a missing/malformed line, a counter reset/skip/repeat, or self-declared
loss of the contract.

- **One miss:** resume, note the warning.
- **Two misses, counter discontinuity, or declared loss:**
  1. Stop trusting drift-prone chat state.
  2. Write/update a durable checkpoint (goal, decisions, files, verified evidence,
     next step) — a bead note or handoff.
  3. Re-read project instructions + the checkpoint before continuing.
  4. Re-verify recent "facts" against disk/bd before acting on them.

## Critical rules

- The canary never replaces evidence — it prompts re-grounding, not guessing.
- On any doubt after a trip, ASK the operator rather than proceed.
