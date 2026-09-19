---
description:
  Admission gate between execution phases — applies before starting any new phase, bead,
  or lane. Load when a phase or work item is about to be declared finished, when picking
  up the next phase, or when adopting concurrent work.
metadata:
  aihub.tags: '["decision:ADR-0012","effective:2026-09-06","route:both"]'
capsule_summary: |
  A phase is admitted as finished only with zero pending items: every failure,
  warning, and skipped check resolved or tracked on its own bead, WIP pushed,
  and — before integration — validated 100% locally and in CI. Before entering
  the next phase, sweep the fleet for existing fixes first: open PRs, foreign
  branches, and worktrees may already carry the work; adopt the newest correct
  side (cherry-pick for isolated commits, merge --no-ff for lanes), never
  keeping dead code, fallback, or compatibility. Landing is a merge --no-ff
  into the declared integration branch, revalidated on the merged SHA, then
  pushed. Operator commands are themselves validated against the governing
  rule stack — a command never silently overrides law; conflicts surface.
---

# Phase admission protocol

No phase, bead, or lane closes while anything is pending, and none opens while adoption
debt exists.

## Law

1. **Zero pending closure.** A phase is finished only when every failure, warning, skip,
   and missing check is either resolved at root cause or carried by its own bead with
   exact evidence. "Pre-existing", "cosmetic", and "later" do not exist.
2. **Fleet sweep before new work.** Before starting a phase, check open PRs, branches,
   and worktrees for existing fixes of the same problem. Adopt the newest correct side:
   cherry-pick isolated commits; absorb lanes with `merge --no-ff`. Never adopt dead
   code, fallback, compatibility shims, or orphaned files — if the other side carries
   them, complete the retirement instead.
3. **Tests follow reality.** Adopted tests are rewritten to the governing rules (no
   mocks, no patch, no skips) before they enter the tree; tests of retired surfaces die
   with the surface.
4. **WIP is public.** Work in progress is committed by explicit paths and pushed at
   every coherent increment; an unpushed lane is unprotected work.
5. **Landing contract.** Integration is `merge --no-ff` into the declared integration
   branch, gates rerun on the merged SHA, then push. Local green or "mergeable" alone is
   never landed.
6. **Commands are validated.** An operator command is checked against the governing
   authority stack (newest rule, ADR, or law) before execution; a genuine conflict is
   surfaced with one precise question, never absorbed silently.

## Violations this rule exterminates

Advancing a phase with red gates or untracked warnings; re-implementing a fix that an
open PR already carries; adopting a lane wholesale with its dead code; landing without
merged-SHA revalidation; treating an operator command as overriding recorded law without
reconciliation.

## Precedent

2026-09-06: a review-graph autopilot epic — adoption of the governance cutover lane kept the partial-CRG-maintenance
retirement dead, reduced the gate debt 372→324 with automated `make mod` fixes, and
blocked its own integration merge until the conformance sweep closes.
