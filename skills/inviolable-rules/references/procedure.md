# Inviolable Rules

Universal only. Domain → project law. [references/gates.md](../references/gates.md). `UNIVERSAL_CORE`.

## Start Gate

1. Read request, `UNIVERSAL_CORE`, project law, Bead, decisions.
2. Record intent; verify root/branch/worktree/paths/owners/consumers/WIP.
3. Confirm native validation commands.
4. Bead claimed. Beads = SSOT. No competing plan; no hand-edit `.beads/`.

## Truth And Anti-Deception Gate

Done = command+cwd+exit+output+scope+blocker. Fake green = P0. No bypass; self-report ≠ proof.

## Role Gate

Orch: semantics, evidence, merge/rollout/close. Worker: 1 Bead/branch/worktree → push → PR. ≤5 lanes. See `beads/orchestrator`/`beads/worker`/`beads/audit`.

## Execution Gate

Make/CLI only (`governance/make`). Fix forward; never stash/reset/force-push unknown WIP. Re-read; root-cause; adopt hunks. Warnings block. Full delivery or STOP+question. See [references/gates.md](../references/gates.md).

## Incident Gate

Rules born from outages that ALREADY happened: remote is ground truth; never mutate the shared venv from a lane; no temporary fix; a missing tool is RED, never green. Detail: [references/gates.md](../references/gates.md).

## Complete Refactor Gate

Complete base → migrate all → delete superseded. No old+new. See [references/gates.md](../references/gates.md).

## Tracker And Mirror Gate

Beads before GitHub; sync. Update Bead each state change. Only orch mutates semantics.

## Continuous-Green Gate

See [references/gates.md](../references/gates.md). Procedure: `verification/loop`.

## Green Checkpoint Gate

See [references/gates.md](../references/gates.md).

## Workspace And Test Laws

See [references/gates.md](../references/gates.md). `UNIVERSAL_CORE` P0. Workspace
identity and placement follow `rules/gascity.md`. While runtime is suspended,
create no workspace. No loose clone, manual worktree, symlink, cross-repository
reference, or project/build/checkpoint staging in `/tmp`.

## Evidence And Review Gate

See [references/gates.md](../references/gates.md).

## Session And Reporting Gate

See [references/gates.md](../references/gates.md).

## Stop Only For A Real Blocker

Stop for destructive action, competing contracts, security/privacy, `main`/prod promotion, final release, authority conflict, material scope change. One Bead question; else continue.
