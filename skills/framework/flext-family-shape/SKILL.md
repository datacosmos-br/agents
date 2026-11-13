---
name: flext-family-shape
description: "flext family shape, branch-matched declarations, semantic rewiring"
license: canonical flext law
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0038","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-11-03","route:project","subject:flext","usage:on-demand"]'
---

# Apply the selected family shape

Resolve branch-matched FLEXT law through $flext-development and read its current ADR-014
before a family migration. The project owns the family layout, facade composition and
exceptions; this skill does not restate them, and a third-party fork keeps its upstream
structure.

Read the live declarations, MRO and consumers through Rope, then use Rope's move, rename
and restructure directly. No candidate, preview, publication or journal layer sits between
Rope and the source, and no second refactoring engine is built.

The changed producer and every consumer it reaches are validated together through the
real entry point and the selected law's gates. Concurrent work is kept and fixed forward;
Git is the recovery, never an older snapshot or a private backup.
