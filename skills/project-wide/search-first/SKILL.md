---
name: search-first
description: 'owner discovery, reusable code, architecture research'
license: MIT
metadata:
  aihub.tags: '["provenance:agents-owned","role:discovery","updates:manual","usage:router"]'
  version: 1.2.0
---

# Search First

Research the active project before the first technical design or implementation
edit. Resolve the project contract, architecture, canonical owner, equivalent
code, pinned dependencies, current consumers, runtime, and native gates.

Apply automatically to features, fixes, refactors, integrations, dependency or
configuration changes, and new abstractions. Read the
[search and decision procedure](references/procedure.md).

Produce one reusable evidence packet. Pass it through `yagni` to remove scope with
no current requirement, consumer, and runtime path, then through `ssot` to select
one writable authority and classify every projection. Apply `solid` only when the
surviving change affects design boundaries. During implementation, apply
`simplify` inline to each cohesive edit. Invoke `dry` only for proven structural
waste inside the authorized graph; reuse the packet instead of recursively
restarting search. Recheck YAGNI, SSOT, and SOLID after structural remediation,
apply one final `simplify`, then prove the public runtime and native gates.

Do not activate for pure summarization, translation, formatting, or non-technical
questions. Do not rerun discovery while its owner, scope, dependency set, and
consumer evidence remain current. Missing or contradictory project evidence is a
loud blocker, never permission to invent architecture or duplicate code.
