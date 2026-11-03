---
name: gc-change
description: "gas city, change lifecycle, runtime orchestration"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:gascity","effective:2026-08-30","route:agent","subject:gascity","supersedes:skill:gascity-change-lifecycle","usage:on-demand"]'
---

## Verification (mandatory)

Before acting on any bead, verify it under `rules/workflow/beads-traceability.md`.

# Gas City Change Lifecycle

Activate only when the workflow explicitly selects a Gas City-coordinated change
(`gc-city` skill); installation or detection is not selection. The city's own surfaces
own orchestration identity, dispatch, observation and placement, and
`rules/git/gitflow-branch-pr.md` owns landing and closure; never copy their commands or
semantics here.

While runtime is suspended, assess only statically from supplied configuration. Never
invoke, translate, simulate, or propose an orchestration command, nor create a city,
rig, Pack, agent, formula, run, session, workspace, branch, or tracker state.

After explicit restoration, preflight every identity and prerequisite the city
declares: runtime state, authority, non-derivable current-process credentials,
repository integration target, and complete landing evidence. Use only the current owner
interface and declared Beads store. The first dispatch, child,
observation, gate, publication, or integration failure propagates unchanged; no retry,
alternate provider/model/credential, compatibility syntax, partial landing, or inferred
closure. Cleanup preserves the first cause and removes partial orchestration residue.
