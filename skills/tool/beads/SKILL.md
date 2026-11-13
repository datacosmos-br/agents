---
name: beads
description: "beads, issue tracking, task workflow"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0038","detect:opt-in:beads","effective:2026-11-03","route:agent","subject:beads","supersedes:skill:beads-orchestrator","supersedes:skill:beads-reval","supersedes:skill:beads-worker","usage:router"]'
---

# Beads

Activate when the project or current operator explicitly selects an existing canonical
Beads route and the request concerns its durable tracker. The route may be
repository-local or a central store outside the checkout; `.beads/` alone selects
nothing, and without a selected route no `bd` or `gc` command runs.
`rules/workflow/beads-traceability.md` owns selection, the Available and Explicitly
suspended modes and closure evidence.

## Available

- Before a write, `bd context --json` and `bd ping --json`, run through the route's
  declared activation and working directory, prove the intended store. A project keeps
  its identity and database while inheriting the endpoint its runtime owner declares;
  no endpoint or ledger is chosen by inference.
- One authorized operation applies against the current revision. Its first runtime,
  conflict, authorization or persistence failure propagates unchanged, and the durable
  post-state is read back before it is reported.
- A bead exists before the first change in its scope, and every new red (test, gate or
  runtime defect) gets a bead the same turn with its failing site, best root-cause
  hypothesis and trigger.
- A bug bead never has an epic parent and task and feature beads sit under few
  canonical epics; a bead closes only as DONE, SUPERSEDED naming its survivor, or
  OBSOLETE, each with evidence, never while a child is open or another live lane holds
  it, and every duplicate scan is unbounded.
- Records written while tracking was suspended enter only through an
  operator-authorized import: converted to the canonical import schema, proven by a
  stdin dry run, imported through the supported owner, every identity verified and the
  source left unmodified. Dolt storage is never hand-edited, and newer live state is
  never overwritten.
- Each delivery checkpoint records the source revision, command, directory, exit,
  decisive output and next required proof on the item; it grants no commit, push, merge
  or runtime authority (`rules/git/gitflow-branch-pr.md`).

## Explicitly suspended

No tracker command runs, no endpoint is selected and no embedded database starts; no
issue, substitute tracker or ledger is created elsewhere. Evidence stays in separately
authorized Git, PR, review, check and CI surfaces, and tracker state and phase closure
stay unresolved.

## Roles

Each role adds its own procedure to the contract above; read the one that applies before
acting.

- Semantic graph or ownership decision by the designated tracker orchestrator:
  [orchestrator](references/orchestrator.md).
- Currently assigned implementation slice: [worker](references/worker.md).
- Explicitly requested revalidation of registered issues, including closed ones:
  [revalidation](references/revalidation.md).

Repetitive batch governance, the continuous cycle and store reorganization belong to
$wip-beads; Jira synchronization to $beads-jira.
