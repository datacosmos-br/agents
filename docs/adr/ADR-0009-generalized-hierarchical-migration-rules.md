# ADR-0009: Generalized hierarchical structural-migration rules

## Status

Accepted — 2026-09-05

## Context

The `make mod` / `make mod-check` surface accumulated one narrow ast-grep rule per
historical defect shape (24 rules, most matching single literal keys of legacy
evaluation schemas). Per-key catalogs scale linearly with history, duplicate one law
across many files, and do not travel across projects, so importing projects could not
receive the migration law of the projects they import.

## Decision

1. Rules are generalized laws, not defect catalogs: one rule per FLEXT principle (single
   ownership, zero residue, fail-loud completeness, declared public fixtures), with file
   scoping expressed in the rule.
2. Rules are layered: `ast-grep-rules/universal/` in the governance home for
   context-free patterns, framework layers in the framework law surfaces, and project
   overlays in project trees. Children strengthen; never re-allow.
3. Rules propagate through project imports via canonical governance delivery: importing
   projects receive imported layers through their rig's delivered `.agents` tree and
   reference them from their migration config; consumer copies are generated projections
   with standardized headers.

## Consequences

The evaluation-suite rule corpus consolidated from 24 files to 7 (one generalized
owner-policy rule plus hygiene, outcome, and fixture rules). New legacy key shapes are
covered by the generalized rule without new files. Projects across the fleet receive the
universal layer through delivery instead of copying it.

## Approval

Operator directive, 2026-09-05: structural-migration rules must be maximally generalized
under standard FLEXT rules, hierarchically defined, and carried to importing projects.
