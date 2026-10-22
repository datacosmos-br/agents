---
description:
  Internal projects enforce Clean Architecture, strict FLEXT facades, and explicit DI
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-09-29","route:project"]'
---

# Clean Architecture and DI for internal projects

Apply this rule to `internal` and `internal_flext` profiles. A `third_party_fork`
retains upstream architecture.

Compose `rules/architecture/engineering-core.md` for DDD, DRY, YAGNI, SSOT, KISS,
SOLID and business-change authorization throughout every phase. Within this internal
architecture, model bounded contexts, keep invariants with their domain owners and
express external capabilities through typed ports; the layer-specific contract follows.

Domain and application policy import no I/O, adapter, framework, process state, global
registry, or concrete service. They depend inward on precise typed ports. The public
`api.py` is the only composition root: it selects concrete edges once and injects them
through constructors or parameters. `cli.py` is a thin process adapter over that API.
Service locators, shared mutable containers, hidden singletons, import-time wiring,
string lookup, and auto-registration are violations. Create no empty layer or
speculative port.

The selected project's domain law owns its module shape, declarations, precise typing,
configuration boundary and size limits. Read those owners instead of copying their
values into this universal rule. Technology-specific validation follows the applicable
language and modeling rules.

For `internal_flext`, compose `flext-development` and resolve the exact branch-matched
local `flext-law` through its provider router. That domain owner defines facade MRO,
family layout, service bases, protocol ports, handler metadata, lazy exports and
configuration access. A missing or mismatched owner fails before effects. Do not resolve
a same-named law from another checkout or apply it to a third-party fork.

Correct each violation at the existing declaration, implementation or generator owner,
rewire its public consumers, prove runtime behavior and remove the superseded path.
Tests and documentation consume the final contract; they do not require compatibility
code to preserve an obsolete construction.
