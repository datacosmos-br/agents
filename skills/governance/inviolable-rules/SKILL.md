---
name: inviolable-rules
description: Mandatory universal governance for plan, edit, validate, merge, close.
bundle: governance
scope: universal
---

# Inviolable Rules

Universal only. Domain → project law. [references/gates.md](references/gates.md). `UNIVERSAL_CORE`.

## Start Gate

Read request, `UNIVERSAL_CORE`, project law, Bead, decisions · record intent; verify root/branch/worktree/paths/owners/WIP · confirm native validation commands · Bead claimed (Beads = SSOT; no competing plan; no hand-edit `.beads/`).

## Truth And Anti-Deception Gate

Done = command+cwd+exit+output+scope+blocker. Fake green = P0. No bypass; self-report ≠ proof.

## Role Gate

Orch: semantics, evidence, merge/close. Worker: 1 Bead/branch/worktree → push → PR. ≤5 lanes. See `beads-orchestrator`/`beads-worker`/`governance-audit`.

## Execution Gate

Make/CLI only (`make-check`). Fix forward; never stash/reset/force-push unknown WIP. Re-read; root-cause; adopt hunks. Warnings block. Full delivery or STOP+question.

## Incident Gate

Rules born from real outages: remote is ground truth; never mutate shared venv from a lane; no temporary fix; missing tool = RED.

## Complete Refactor Gate

Complete base → migrate all → delete superseded. No old+new.

## Tracker And Mirror Gate

Beads before GitHub; update Bead each state change; only orch mutates semantics.

## Continuous-Green / Green Checkpoint / Workspace And Test Laws / Evidence And Review / Session And Reporting

See [references/gates.md](references/gates.md). Procedure: `verification-loop`. `UNIVERSAL_CORE` P0.

## Stop Only For A Real Blocker

Destructive action, competing contracts, security/privacy, prod promotion, final release, authority conflict, material scope change. One Bead question; else continue.
