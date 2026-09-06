---
name: beads-organization
description: 'beads organization, deduplication, feature hierarchy, jira alignment'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-organization","effective:2026-09-02","policy:atomic-effects","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:beads","updates:manual","usage:router"]'
---

# Beads Organization

Activate when organizing beads into features, deduplicating, or aligning with
an external tracker.

## Canonical Hierarchy

- **Feature** (macro épico): top-level work domain; at most 2 open child
  tasks. Labels: `priority:P<N>` and `domain:<area>`.
- **Task**: closeable work under one feature; must have a parent.
- **Bug**: stays at root; labels `bugfix`; `hotfix` on P0/P1 only; never a
  Jira subtask.
- **Epic**: superseded by features; close with `SUPERSEDED` once reorganized.

## Deduplication Gate (mandatory before any external push)

1. `bd find-duplicates --status open --limit 30 --json`.
2. Resolve any pair above 0.5 first: keep the more recent bead, close the
   older with a `SUPERSEDED: deduplicado com <new-id>` reason — unless
   metadata proves a legitimate spec/step/control triad.
3. Re-run the gate; only then execute any external sync.

## Limits

Max 20 issues created per invocation; larger batches need `--dry-run` plus
operator review. Orphan query and zero-residue checklist:
`references/procedure.md`.

## Closure Rules

Every `bd close` carries a descriptive `--reason`: `SUPERSEDED:`,
`OBSOLETE:`, or `DONE:` with an explanation.

## External References

Set `--external-ref` right after creation; a bead closed with its external
issue open (or the reverse) fails the next sync audit.

## Orphan Children

After closing a parent, re-parent or close every open child. Exit: zero open
children with a closed parent.
