---
description:
  Changing a surface that many repositories receive. Load before editing a projected
  rule, skill, command, instruction file, or ignore entry in a consumer repository.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-19","route:both"]'
---

# A projected surface reaches a repository only through the distributor's landing verb

A projected surface has one writable authority and many destinations. Editing it in a
destination is not a small fix: the same edit is owed to every other destination, on
every branch, forever, and the next regeneration silently discards it. Hundreds of
repositories multiply one manual edit into work that is redone until someone stops
doing it and the fleet diverges.

So the edit goes to the authority, and the distributor's landing verb carries it:
lane, projection, residue removal, untracking, the destination's own native gates,
checkpoint, pull request, merge commit, and lane retirement after an ancestry proof.
A step the verb does not cover is a gap in the verb, fixed there before the change
lands — never a manual step performed once by hand.

- Opening a worktree, deleting a file, editing configuration, or opening a pull request
  by hand in a consumer repository, in order to apply a projection, is a process defect.
- The verb is idempotent and resumable: a second run over an unchanged fleet has no
  effect, and a re-run completes whatever was left pending.
- One destination's red gate is recorded and does not stop the others. The fleet
  finishes; the divergence ledger names what did not.
- Everything the verb needs is derived: the integration base is read from the forge, the
  tracker identity from the project's own registration, the untrack list from the
  generated ignore file, and residue only from a retired owner's own receipt. A
  destination declares an override only where no derivation exists.

Composes with `generators not projections` (rule file), which owns the
authority-and-regeneration contract, and `gitflow branch and pull request` (rule file),
which owns the landing cycle the verb executes.
