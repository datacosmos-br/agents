---
name: advance
description:
  Rebuild the work order from current evidence, close the active phase,
  and start the next authorized phase when closure is proved.
argument-hint: "<optional focus, plan path, bead, or project path>"
metadata:
  aihub.tags: '["decision:ADR-0020","effective:2026-09-10","route:agent"]'
---

# Advance — review, repair, and advance the active phase

Use `$ARGUMENTS` to locate the plan, bead, or project. Run `session-preflight`;
when the plan is a formal handoff, use `plan-handoff` as directed by preflight.
Read the current authority and branch-matched owning skills before acting.

## Rebuild the work order

Use the approved plan, selected tracker, Git and PR state, and measured gate and
runtime evidence. State the objective, current phase, scope, owners, adopted work,
integration target, first unproved gate, and exact next action in at most ten lines.
Before changing an asset, use `search-first` across affected repositories, libraries,
and declared tools to find the capability, its owner, and its consumers. Route shared
governance to `agents`, FLEXT contracts to the branch-matched `flext-law` and owning
ADRs, and governance delivery and installed proof to AI Hub.

## Repair the active phase

Challenge dependencies, domain ownership, behavior, performance, and recovery.
Adopt overlapping work through `fix-forward`. Reproduce failed gates, correct their
cause and any conflicting guidance at the owning source, and rerun the same public
entry point. Update consumers and retire obsolete paths in the same slice. Use the
project's [canonical commands](../../rules/workflow/canonical-commands.md) and declared
test population. Record causal lessons on the selected bead, or in authorized PR
evidence while tracking is unavailable. Preserve the cursor through `focus-recovery`.

## Admit the next phase

Apply `sprint-closure`: resolve review, prove checks on the exact PR head, integrate
through the declared lane, and record fresh gate and runtime evidence on the merged
revision. Close the selected tracker work when its contract is satisfied. Finish the
active slice before opening the next PR in the plan.

State `READY` with the closure evidence and start the next authorized step. Otherwise
state `BLOCKED` for the phase transition, name the first missing proof, its owner and
the exact next command, and continue independent work.
