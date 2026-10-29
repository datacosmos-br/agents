---
description:
  No rushed work — preserve WIP, status, tracker items and authorized publication
capsule_summary: |
  Do not rush work to a completion claim. Preserve existing WIP and update status
  and tracker items at each boundary. Placement follows gascity, not a new lane
  inferred from a task. Git checkpointing and publication require their current
  authority; preservation is not landing or runtime delivery.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-10-29", "route:both"]'
---

# No rushed work: preserve WIP and report its actual state

Preserve work under `fix-forward-collaboration`; placement has one owner in
`rules/coordination/gascity.md`. The historical placement attribution in ADR-0021
does not establish a dedicated worktree or branch requirement.

1. Rushing to conclude is a defect: a grain ends when its cycle ends.
2. Retain existing tracked, staged and untracked contributions. Record and publish
   recoverable checkpoints through the Git owner when authorized; neither a new task
   nor a preservation obligation grants commit, push or checkout-changing authority.
   The branch/PR rule owns the distinction between completed working-branch checkpoints
   and explicitly authorized preservation refs; incomplete work is never published as
   a working-branch or PR checkpoint.
3. Status and tracker items are updated at every grain boundary — before starting the
   next piece, not "later".
4. Wip is preservation, not landing: the full landing cycle (PR to the integration
   branch; runtime when required) still applies before completion is claimed.

The 2026-10-29 reconciliation retains the 2026-10-24 no-incomplete-push intent.
Its older dedicated-placement and no-testing wording does not override the
current placement owner or the diagnosis required to restore a failing runtime.
