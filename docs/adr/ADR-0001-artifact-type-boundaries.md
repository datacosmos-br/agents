# ADR-0001 — Preserve semantic artifact-type boundaries

- **Status:** Accepted
- **Date:** 2026-08-27
- **Scope:** Canonical skills, commands, agent profiles, and rules

## Context

Skills may activate from compact discovery metadata; commands are explicit parameterized
workflows; rules are standing constraints; agent profiles select roles. Treating them as
one generic prompt erases their distinct activation, input, size, and validation
contracts.

## Decision

Skills, commands, agents, and rules remain distinct canonical semantic types. Each has
one physical source grammar and one typed parser. A type correction is atomic: add the
correct owner, rewire every consumer, and remove the wrong owner without aliases or
coexistence. Provider representation and unsupported-type behavior belong to the AI Hub
consumer, not this bundle.

## Consequences

`GovernanceBundle` preserves the four inventories separately. Consumers adapt those
typed semantics without changing their canonical kind, while this package contains no
provider support matrix or rendering path.
