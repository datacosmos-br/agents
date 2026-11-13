---
name: gc-dispatch
description: "gas city dispatch, sling routing, formula workflow, convoy orders"
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0038","detect:opt-in:gc-dispatch","effective:2026-11-03","route:agent","route:project","subject:gascity","usage:on-demand"]'
---

# Dispatching work

`gc sling` routes work to session configs; `gc sling --help`, `gc formula show`,
`gc convoy --help` and `gc order --help` own the grammar, and `-n/--dry-run` previews a
dispatch. Bead work follows `rules/workflow/beads-traceability.md`.

- Dispatched work is placed and prepared only by the city's formula; the dispatcher never
  pre-creates a competing lane or executor, and the repository keeps its own code, gates
  and Git integration.
- A multi-session config is a valid target: any eligible session claims the work, so no
  individual session is found or created first. A one-argument sling takes its target
  from the bead's rig `default_sling_target` in `city.toml`.
- A bead lives in the target agent's rig database (`gc bd create --rig <rig>`); sling's
  cross-rig guard blocks one from another database.
- Formulas come only from the packs the city imports (`gc import list`,
  `gc formula list`), never from memory; "not found in search paths" is a missing import,
  never a reason to hand-author the lifecycle. Every required variable is supplied before
  the sling, and a missing one stops it before any convoy or order exists.
- `-f <formula>` instantiates a formula and routes its root bead; `--on <formula>`
  attaches one to an existing bead. A v2 formula
  (`[requires] formula_compiler = ">=2.0.0"`) starts a workflow whose steps and handoff
  metadata persist as beads; a v1 formula instantiates a wisp. A formula that references
  `{{convoy_id}}` or drains needs a target convoy: `--on` creates its input convoy,
  `--no-convoy` never suppresses it, and a bare `-f` launch is rejected.
- A v2 workflow advances only through the control dispatcher (`core.control-dispatcher`),
  which executes its control beads; agents run only plain step beads, so open steps are
  checked at the dispatcher before any worker is nudged.
- Engineering work enters through the gascity pack's `implement` formula:
  `gc sling <rig>/gc.run-operator <bead> --on implement`, with push and PR off unless
  `--var push=true --var open_pr=true`. Its `do-work` step cuts the worktree from
  `origin/HEAD`, which must name the rig's integration lane.
- A polecat branch is cut from the first of `metadata.target` on the bead or its convoy,
  the bead rig's `default_branch`, the agent rig's, then `origin/HEAD`; `gc rig add`
  records `default_branch` once, so read it from `gc rig list --json`. Work that lands in
  a repository other than the rig's own is a plain bead handed to the coordinator.
- `gc convoy check` closes every fully resolved convoy city-wide, and `land` without
  `--dry-run`, `delete -f`, `delete-source --apply` and `reopen-source` all mutate:
  preview first. Epic beads are no longer containers; open epics move to convoys before
  convoy-only tooling is used.
