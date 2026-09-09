# ADR-0006 — Synthesize historical governance by behavior, not structure

- **Status:** Accepted
- **Date:** 2026-08-28
- **Scope:** External and historical governance evidence

## Context

Historical corpora mix useful behavior with generated projections, wrappers,
caches, provider assumptions, obsolete runtimes, and contradictory failure
semantics. Copying their structure would restore multiple owners.

## Decision

Treat external and historical artifacts as read-only evidence. Reduce a
candidate to its outcome, activation boundary, inputs, effects, failure
behavior, scope, current consumer, provenance, license, and material proof.
Place only distinct current behavior in the existing semantic owner selected by
ADR-0001 and `rules/architecture/governance-artifact-composition.md`.

Never import provider projections, caches, backups, archives, compatibility
facades, fixed tool quotas, private paths, updater runtimes, fallback, retry,
normalized failure, or copied generated output. Once adjudicated, the source
corpus is deleted; it is not retained as an archive.

## Consequences

The catalog grows only for a distinct recurring capability with a current
consumer. Existing owners receive a focused rule, procedure, or semantic task.
Inventory totals remain derived from the physical sources, never copied into an
acceptance test or registry.
