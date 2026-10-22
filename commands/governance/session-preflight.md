---
name: session-preflight
description:
  Run the session startup preflight covering runtime-lock verification, tracker identity, and the adoption sweep.
argument-hint: "<optional repository paths>"
metadata:
  aihub.tags: '["decision:ADR-0028","effective:2026-09-27","route:project"]'
---

# Session preflight

Resolve each requested repository from `$ARGUMENTS`; otherwise use the active project.
Follow `rules/coordination/session-startup-census.md` and the current operator's
placement and scope authorization. This preflight inspects and reports; claims,
adoption, lane creation and announcements are explicit subsequent effects.

1. Read the selected tracker route from its owner and prove the intended identity
   through its declared context command when that capability is selected. Installation
   or a directory alone never selects a tracker. Keep unavailable orchestration and
   separately available tracking distinct.
2. Establish source, physical environment, lock and consumed dependency identities
   through the project's native provenance operation. A mismatch invalidates dependent
   receipts. Setup reconciles declared locks; dependency advancement uses its separate
   owner. Reuse a currently valid environment rather than reinstalling it per gate.
3. Inspect the integration tip, open PRs, existing branches, worktrees and recorded
   ownership. Preserve relevant WIP and identify an adoption path before creating a
   competing lane. Do not infer abandonment from one old signal.
4. Resolve the coordinator and selected communication channel through their canonical
   rules. Read current claims and conflicts. Report any missing declaration before the
   first coordinated effect; do not resume suspended orchestration.
5. Identify unpublished owned commits and incomplete prior units. Reconcile them through
   their existing lane and tracker before accumulating another independent unit.

Run only discovered public commands under `rules/workflow/canonical-commands.md`.
Return one evidence-bearing result per inspection, its scope and the first causal
failure. A missing inspection is unresolved, not a pass. Do not use skip switches to
omit required ownership or coordination evidence.
