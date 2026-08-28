---
name: simplify
description: 'Simplify each changed code unit inline when complete behavior is already implemented.'
license: MIT
metadata:
  aihub.tags: '["provenance:agents-owned","role:refactoring","updates:manual","usage:router"]'
  version: 2.1.0
---

# Simplify

Apply automatically while generating or changing code. Deliver the complete
requested behavior, then simplify each touched unit before moving to the next
one. Preserve contracts, errors, side effects, ordering, types, performance,
tests, and useful documentation.

Consume the necessary behavior, SSOT authority map, and any SOLID boundary already
selected by the global `search-first` flow. Use `dry` only when evidence reveals
cross-file semantic duplication, god patterns, dead ownership, or structural
waste. Simplify each edited unit inline and the final rewired graph once; never
restart discovery, elect an owner, redesign a boundary, or recurse.

Read the [inline simplification procedure](references/procedure.md) whenever code
is being generated, edited, or structurally remediated.

Compact code is cohesive and explicit, not code golf. Never omit required
behavior, weaken tests, hide failures, invent an abstraction, or trade readable
control flow for a line-count reduction. Generated files must be changed through
their canonical owner. Missing ownership, contract, or runtime evidence blocks
the edit loudly.

This always-on discipline does not expand task scope or authorization. It does
not independently redesign architecture, diagnose unrelated defects, or sweep
unchanged code.
