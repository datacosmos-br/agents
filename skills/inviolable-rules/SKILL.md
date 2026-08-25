---
name: inviolable-rules
description: "Mandatory universal governance for every plan, edit, validate, merge and close. USE FOR: truth-with-evidence gates, root-cause execution, Beads tracker discipline, Gas Town lane lifecycle (hook/sling/done/mq), role boundaries. DO NOT USE FOR: domain law and role procedures — their own skills own those."
license: MIT
metadata:
  bundle: governance
  scope: universal
---

# Inviolable Rules

Universal only. Domain → project law. [references/gates.md](references/gates.md) · [references/practices.md](references/practices.md) · `UNIVERSAL_CORE`.

## Start Gate

Read request, CORE, project law, Bead, decisions. Verify root/branch/worktree/owners/WIP. Bead claimed; never hand-edit `.beads/`.

## Truth And Anti-Deception Gate

Done = command+cwd+exit+output+scope+blocker. Fake green = P0. Self-report ≠ proof.

## Role Gate — Gas Town

Mayor dispatches (`gt sling`, convoys, `gt mountain`). Refinery owns merges (`gt mq`). Polecat finishes via `gt done --status COMPLETED|ESCALATED|DEFERRED`. Witness watches polecats; Deacon/dogs watch infra. ≤5 lanes per worker.

## Execution And Incident Gates

Make/CLI only (`governance/make`). Fix forward; never stash/reset/force-push unknown WIP. Warnings block. Remote is ground truth; no temporary fix; missing tool is RED.

## Complete Refactor Gate

Complete base → migrate all consumers → delete superseded. No old+new coexistence.

## Tracker And Mirror Gate

Beads before GitHub. Update Bead at every state change. Only orch mutates semantics.

## Green Checkpoint Gate

Short validated slices: commit explicit paths → push → land via merge queue (`gt done`; Refinery merges). `--pre-verified` only after rebase onto target. Procedure: `verification/loop`.

## Session Gate

Start: `gt prime` + `gt hook status`. Pause: `gt handoff -c`. Resume: `gt resume`. Blockers: `gt escalate`.

## Stop Only For A Real Blocker

Destructive action, security/privacy, prod promotion, authority conflict → one precise question. Else continue.
