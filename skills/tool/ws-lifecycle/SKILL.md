---
name: ws-lifecycle
description: "gas city, workspace lifecycle, runtime orchestration"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:gascity","effective:2026-08-30","route:agent","subject:gascity","supersedes:skill:gascity-workspace-lifecycle","usage:on-demand"]'
---

## Verification (mandatory)

Before bead effects, apply the four-source cross-check in
`rules/coordination/beads-verification.md`. Record command, working directory, exit
code, and decisive output. Close a retired premise as obsolete with evidence; never
execute it.

# Gas City Workspace Lifecycle

Activate only when the project authorizes Gas City and the workflow explicitly selects a
Gas City-managed workspace decision. Installation or detection is not selection. Derive
all placement and identity from the repository's Gas City owner rule and declared city,
rig, pinned Pack, agent, formula, provider, store, and physical workspace. Beads
requirements exist only when the project also selects Beads. Never infer or locally
recreate configuration.

While runtime is suspended, validate supplied configuration statically and make no
workspace or runtime effect. A missing or conflicting declaration is the first cause; do
not invent a path, use a loose clone, worktree, temporary or cross-repository location,
translate another runtime's command, or substitute a provider.

Before effects read `execution modes`; never mix modes or use `make work`.

After explicit restoration, validate the complete placement graph, current owner
interface, authority, and non-derivable current-process credentials before creation or
dispatch. Apply one owner-selected workspace path atomically. The first runtime,
provider, filesystem, child, or publication failure propagates unchanged; do not retry,
retain a partial workspace, or fall back to another path, provider, model, credential
source, or compatibility interface.
