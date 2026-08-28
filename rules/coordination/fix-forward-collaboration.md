---
description: Preserve concurrent work and integrate every compatible contribution forward.
---

# Adopt the current state and collaborate by fix-forward

Treat every pre-existing, dirty, staged, committed, or concurrently arriving
change in the authorized repository as owned input, regardless of provenance or
age. Re-read a shared file before editing, attribute the intent of overlapping
hunks, and preserve every compatible contribution. The integration lane
continuously adopts compatible landed work from other lanes so the combined
result, not an isolated lane snapshot, is the delivery target. “Mine”, “theirs”,
“legacy”, and “pre-existing” never exempt a current defect from fix-forward.

Never stash, reset, restore, revert, rebase, force-push, roll back code or
history, or replace a shared file to remove work. Correct defects forward at
their canonical owner. Transaction rollback may undo only effects created by
the failing invocation; it never discards adopted current content.

A severe conflict exists only when two current intentions require incompatible
behavior or when preserving both would violate a higher authority. Stop before
the conflicting effect, present both intentions and their evidence, and ask the
operator one precise question. Ordinary overlap, divergence, a red gate, or
integration work is not severe: reconcile, validate, and continue forward.

Compose this invariant with [shared-file coordination](multiagent-edit-breadcrumb.md),
[operator precedence](operator-precedence.md),
[plan adoption](plan-topic-monopoly.md), and
[the destructive Git guard](../git/destructive-git-guard.md).
