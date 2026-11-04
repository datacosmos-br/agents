---
description: Internal projects enforce inward dependencies and explicit typed DI
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-11-02","route:project"]'
---

# Clean Architecture and DI for internal projects

Apply this rule to `internal` and `internal_flext` profiles. A `third_party_fork`
retains upstream architecture.

Compose `rules/architecture/engineering-core.md` for DDD, DRY, YAGNI, SSOT, KISS,
SOLID and business-change authorization throughout every phase. Within this internal
architecture, model bounded contexts, keep invariants with their domain owners and
express external capabilities through typed ports; the layer-specific contract follows.

Domain and application policy import no I/O, adapter, framework, process state, global
registry, or concrete service. They depend inward on precise typed ports. Compose
concrete edges once at the project's declared executable boundary and inject them
through constructors or parameters. Process adapters delegate to application policy.
Service locators, shared mutable containers, hidden singletons, import-time wiring,
string lookup, and auto-registration are violations. Create no empty layer or
speculative port.

Adapter internals own library identities and native integrations; application ports,
payloads and orchestration name capabilities, without exposing implementation-library
names. Native integration and duplicate-analysis removal follow
`rules/workflow/declared-tool-ownership.md`.

The selected project's domain law owns its module shape, declarations, precise typing,
composition-root location, configuration boundary and size limits. Read those owners
instead of copying their values into this universal rule. Technology-specific validation
follows the applicable language and modeling rules.

For `internal_flext`, compose `flext-development` and resolve the exact branch-matched
local `flext-law` through its provider router. That domain owner defines facade MRO,
family layout, service bases, protocol ports, handler metadata, lazy exports and
configuration access. A missing or mismatched owner fails before effects. Do not resolve
a same-named law from another checkout or apply it to a third-party fork.

The domain's current protocol-only annotation amendment and model/service projection
own the distinction between typed contracts and executable model construction.
Resolve ADR-028 Decision 15 and ADR-018's model/service projection in that same
branch-matched source. Preserve concrete payload validation and JSON Schema through
its native schema owner; a DI capability check is not payload admission. This rule
routes to those owners and declares no parallel projection or typing exception.

Correct each violation at the existing declaration, implementation or generator owner,
rewire its public consumers, prove runtime behavior and remove the superseded path.
Tests and documentation consume the final contract; they do not require compatibility
code to preserve an obsolete construction; a rewire spanning waves follows
the `zero residue` rule's "Deprecated-signature window" section.
