---
description: Apply the mandatory engineering decision and delivery sequence.
---

# Engineering core

For every implementation, use this order:

1. Search the repository, declared owners, dependencies, and current canonical
   documentation before designing anything.
2. Remove scope with no current requirement or consumer (YAGNI).
3. Elect one writable authority and classify every other copy as a generated
   projection (SSOT).
4. Apply SOLID only where a real responsibility, substitution, interface, or
   dependency boundary is under change.
5. Implement through the owner and simplify inline without weakening behavior.
6. Remove proven semantic duplication and god components, then recheck YAGNI,
   SSOT, and SOLID.
7. Simplify once more, exercise real runtime behavior, run every native gate,
   and complete the approved landing cycle before changing phase.

Hardcoded environment facts, caught or normalized failure, hidden failover,
retry, operational defaults, compatibility, partial execution, keyring, and
success without decisive evidence are runtime-critical defects. Exterminate
them at their owner. The first exception escapes the owning CLI with its raw
traceback and causal chain.

Compose this sequence with [generalized ownership](generalized-abstraction.md),
[strict execution](../runtime/strict-execution.md),
[runtime evidence](../workflow/runtime-is-reality.md),
[storage isolation](../storage.md),
[security closure](../security/scanner-closure.md), and
[landing discipline](../git/gitflow-branch-pr.md).
