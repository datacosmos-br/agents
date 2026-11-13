---
name: dispatch-agent
description: "agent delegation, specialist selection, bounded work"
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","usage:on-demand"]'
---

# dispatch-agent

Delegate only when the current operator request or selected role authorizes it and a
bounded result gains from a specialist in the active client's current roster. A direct
bounded answer launches nothing, and free slots, an old fan-out order or a broad cleanup
request authorize nothing by themselves.

A handoff states one outcome: the objective, its repository, the exact paths the worker
may write, what it must leave alone, the acceptance it must show, and that it shares the
codebase and keeps others' changes. It says what must be true, never how
(`rules/law.md` 4), and grants no merge, publication or scope beyond the assignment.

Select one agent by the strongest material match and state why. Several run at once only
when each has its own owner and disjoint write paths; reads may run in parallel, and a
shared mutable resource (index, file family, cutover, environment) has one writer at a
time. Model, tier and provider come from the active runtime's current catalog, never from
a bundled roster, a fallback or a hardcoded name or price.

A worker's message, an empty output or a test result not tied to its exact revision proves
nothing: a result is accepted only after reading its diff and evidence and rerunning the
affected gates on the combined state. A stalled or failed worker reports its exact denial
or error, and the failing owner is corrected within the authorization; elapsed time never
justifies abandoning the task, switching checkouts, an unchanged retry or a raw-tool
substitute. A failed lane stays failed and is never reported as partial success.

The parent keeps the goal, the operator conversation, every sequenced effect (merge,
tracker closure) and closure itself; when dispatch is unavailable, it does the authorized
work itself.
