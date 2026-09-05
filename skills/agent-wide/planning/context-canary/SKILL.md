---
name: context-canary
description: 'context drift, session continuity, compaction recovery'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","policy:atomic-effects","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","provenance:agents-owned","role:continuity","updates:manual","usage:on-demand"]'
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

- **Any miss, counter discontinuity, or declared loss:**
  1. Stop trusting drift-prone chat state.
  2. Validate the checkpoint owner and complete content. When the selected
     canonical tracker is available, publish one durable checkpoint atomically
     (goal, decisions, files, verified evidence, next step). While it is
     explicitly suspended, publish no substitute tracker or ledger and re-anchor
     from the approved plan, canonical files, and authorized Git/PR/CI evidence.
  3. Re-read project instructions + the checkpoint before continuing.
  4. Re-verify recent facts against canonical files and the declared tracker
     surface before acting on them.

## Critical rules

- The canary never replaces evidence — it prompts re-grounding, not guessing.
- Missing identity, counter, checkpoint owner, or evidence blocks further work;
  ask the operator rather than fabricate state or continue with partial memory.
