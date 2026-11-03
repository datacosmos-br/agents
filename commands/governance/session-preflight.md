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
Follow `rules/coordination/inter-session-mail.md` and the operator's current scope.
This preflight inspects and reports; claims, adoption, lane creation and announcements
are later, explicit effects.

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
6. Identify the active approved plan and every instruction, document, skill, rule and
   command the planned change would contradict (`rules/law.md` item 12); report each
   before implementation.
7. For an authorized transaction, identify the owner that makes its effect complete or
   absent (`rules/law.md` item 8) and report a missing one instead of inventing a
   substitute. The agreed specification stands (`rules/law.md`); a faster validation
   route keeps its declared population and acceptance evidence.

Run only discovered public commands under `rules/workflow/canonical-commands.md`.
Return one evidence-bearing result per inspection, its scope and the first causal
failure. A missing inspection is unresolved, not a pass. Do not use skip switches to
omit required ownership or coordination evidence.
