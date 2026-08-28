---
name: dry
description: 'Remove semantic duplication and god patterns when several owners repeat the same responsibility.'
license: MIT
metadata:
  aihub.tags: '["provenance:agents-owned","role:refactoring","updates:manual","usage:router"]'
  version: 1.1.0
---

# DRY

Aggressively reduce semantic duplication, dead code, needless work, oversized
units, and god objects or modules while preserving the complete public contract.
Every retained line and abstraction must serve a current behavior or invariant.

Use only for structural remediation proven by `search-first` and retained by the
`yagni` necessity gate across the affected call graph. Consume the unique authority
map selected by `ssot`; do not elect another owner. Respect the responsibility and
dependency boundaries selected by `solid`. Apply `simplify` inline to every
coherent unit changed by the remediation and once more to the final diff. Read the
[compact-code procedure](references/procedure.md).

Routine generation and local cleanup stay in `simplify`; they do not activate a
repository-wide DRY pass. A confirmed cross-file duplicate, god pattern, dead
owner, or measured repeated work crosses this boundary exactly once into `dry`.
Return the rewired graph for YAGNI, SSOT, and SOLID rechecks; `search-first` owns
the global order, so do not reproduce or restart it here.

Short code means a small, cohesive semantic surface, not dense code golf. Runtime
behavior, error propagation, security, types, observability, performance,
readability, tests, and useful documentation are non-negotiable. Tokei deltas are
evidence, never a quality score or an arbitrary line limit.

Do not activate for prose repetition, generated/vendor code, or a line-count-only
request with no behavioral baseline. Edit the canonical generator or owner, and
block when ownership, callers, or runtime proof cannot be established.
