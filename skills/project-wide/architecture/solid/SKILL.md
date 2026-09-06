---
name: solid
description: 'solid principles, responsibility boundaries, dependency direction'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","policy:atomic-effects","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:architecture","updates:manual","usage:router"]'
  version: 1.2.0
---

# SOLID

Enforce cohesive responsibilities, safe extension, substitutable contracts,
consumer-sized interfaces, and inward dependency direction with the same strict
evidence standard as `dry`.

Consume the current consumers retained by `yagni` and the authority map selected
by `ssot`. Emit only the responsibility, contract, and dependency boundary needed
for implementation; accept one recheck after `dry`. The global order is owned by
`search-first`. Read the
`SOLID remediation procedure` (skill file) for confirmed violations.

SOLID is not permission to add interfaces, inheritance, factories, plugins, or
layers speculatively. A small cohesive function with no architectural boundary
needs only inline `simplify`. Missing consumers, contracts, or runtime evidence
blocks redesign rather than authorizing pattern cargo cult.

Keep this owner language-neutral. When implementation evidence selects a
technology, framework, library, or project specialization, compose its child
skill after `$solid`; the child owns syntax and framework rules without copying
these decisions back here.
