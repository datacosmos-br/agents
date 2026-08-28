# SOLID remediation procedure

## Strict but non-ceremonial

A confirmed SOLID violation in the requested affected graph is a blocking design
defect when it makes behavior unsafe to change, couples policy to volatile I/O,
breaks substitutability, or forces consumers through unrelated responsibilities.
Correct it at the canonical owner in the same change. Never suppress, document
around, or preserve the violating path beside the replacement.

Strictness does not mean maximizing patterns. Interfaces, factories, strategies,
inheritance, dependency injection, and extension points have a cost. Add one only
when real current consumers and a stable contract prove it is smaller and safer
than direct code. The canonical `yagni` skill owns that necessity decision.

## Flow contract

The canonical sequence lives in `search-first`; do not reproduce it here. Consume
the current concept set from `yagni` and authority map from `ssot`. Output only the
minimal responsibility, behavioral-contract, interface, and dependency boundaries
needed by implementation and `dry`, then accept one post-rewiring check. SOLID
does not decide necessity, authority, structural consolidation, or local code
form.

## Establish behavioral contracts

Before restructuring, identify public inputs and outputs, preconditions,
postconditions, error types and causes, ordering, side effects, state transitions,
performance constraints, and security boundaries. Protect them with runtime,
characterization, or contract tests. A green unit test that bypasses the public
composition root is insufficient.

Map each module's current consumers and reasons to change. Trace construction and
dependency wiring. Use the `ssot` authority map: generated files are projections,
never owners; modify their generator input. If responsibility, variation,
authority, or substitutability cannot be observed, stop with the exact missing
evidence.

## Apply each principle from evidence

### SRP — one cohesive reason to change

Separate policy, persistence, transport, presentation, and orchestration when
their real change reasons and consumers differ. Size alone is not a violation.
A thin orchestrator may legitimately sequence several owners; it must not absorb
their rules or I/O details.

### OCP — extend a stable policy without editing its owner

Use an existing variation boundary when a second real implementation exists and
shares a stable behavioral contract. The composition root may select and inject
an implementation. Do not create a plugin system, registry, switch abstraction,
or future option for hypothetical variants.

### LSP — preserve the complete observable contract

Every implementation must accept the base preconditions, deliver its
postconditions, preserve documented errors and side effects, and avoid type-based
special cases in callers. Prove substitutability with the same contract suite. If
implementations cannot honor one contract, model distinct capabilities or use
composition instead of weakening the base.

### ISP — depend only on the capability a consumer uses

Shape interfaces from real consumer needs. Split broad contracts that force
no-op, stub, exception, or unused methods. Do not create one interface per class
when there is no substitution or boundary; the consumer-owned capability should
be the smallest stable behavior, not ceremonial indirection.

### DIP — policy owns abstractions, composition owns concretes

High-level policy depends on typed capabilities, not databases, HTTP clients,
providers, frameworks, filesystem APIs, or ambient globals. Construct concrete
implementations at the established composition root and inject them explicitly.
Never replace direct coupling with a service locator, global registry, dynamic
lookup, or untyped dependency bag.

## Atomic remediation

1. Add or strengthen public/contract tests that fail on the confirmed violation.
2. Introduce or reuse the smallest consumer-owned boundary.
3. Move each responsibility to the authority selected by `ssot` and inject
   dependencies at the existing composition root.
4. Rewire every current consumer atomically.
5. Apply `dry` to remove duplicated rules, obsolete branches, broad contracts,
   dead implementations, compatibility paths, fixtures, and documentation.
6. Recheck `yagni`, `ssot`, and `solid`, then apply `simplify` inline so the
   corrected design remains necessary, authoritative, explicit, and compact.
7. Delete the superseded design completely; never dual-read, dual-write, shim, or
   retain provider/type switches beside polymorphic dispatch.

## Verification

Run the real public runtime before general gates, after dependency rewiring, and
on the integrated result. Exercise every current implementation through one
contract suite, including causal errors and boundary cases. Run native unit,
integration, static, type, build, security, generation, and projection gates.

Search for concrete dependencies in policy, type/provider switches, oversized
interfaces, no-op methods, weakened contracts, duplicate responsibility owners,
and stale construction paths. Report the five-principle decision, owners and
consumers changed, contract/runtime evidence, YAGNI and SSOT rechecks, DRY
deletions, simplify outcome, and any blocker. Never claim SOLID from pattern names
alone.
