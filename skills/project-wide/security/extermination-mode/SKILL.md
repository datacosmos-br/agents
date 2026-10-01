---
name: extermination-mode
description: "zero residue, contract removal, consumer rewiring"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-01","usage:router"]'
---

# Extermination Mode

Use only after the operator has approved a complete cutover and identified the
superseded contract. This mode removes the old contract; it does not authorize deleting
data, repositories, branches, runtime state, or unrelated work.

1. Inventory the old owner, producers, consumers, loaders, fallbacks, aliases, tests,
   fixtures, templates, generated facades, documentation, and terms.
2. Classify tests by behavior:
   - delete tests whose sole purpose is enforcing the removed contract;
   - rewrite tests that protect behavior still required by the final contract;
   - preserve unrelated tests and concurrent WIP exactly.
   Work in the cleanup order of `rules/architecture/engineering-core.md`: steps 3–5
   below, with no heavy validation between them.
3. Delete exact tracked obsolete files with scoped patches. Regenerate managed indexes
   and artifacts through their canonical owner; do not hand-maintain a generated facade.
4. Rewire every useful consumer to the final SSOT in the same change; the landed
   cutover leaves no consumer on the removed owner. Use structural search/replace for
   mechanical migrations and review every match. Elide every field and call argument
   equal to a canonical typed default. Never add a compatibility alias, dual reader,
   fallback, or undeclared default-on-error behavior to make deletion easier.
5. Rewrite the classified tests to the real runtime behavior, then prove the cutover
   once, at the end, with zero-residue semantic searches, focused behavior tests,
   generation fixed point, static gates, and the repository's full gate. A failed gate
   means the extermination is incomplete, not that the gate or generator should be
   weakened.

Complete owner, consumer, approval, and concurrent-work preflight before the first
effect. Preserve the first gate or subprocess failure unchanged; a failed cutover
publishes nothing and runs no fallback path.

Stop when an apparent obsolete target still has a valid consumer, belongs to concurrent
work, or deletion would cross the operator-approved boundary.
