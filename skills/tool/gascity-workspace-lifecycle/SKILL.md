---
name: gascity-workspace-lifecycle
description: 'gas city, workspace lifecycle, runtime orchestration'
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:gascity","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:gascity","updates:manual","usage:on-demand"]'
---

# Gas City Workspace Lifecycle

Activate only for an explicitly Gas City-managed workspace decision. Derive all
placement and identity from the repository's Gas City owner rule and declared
city, rig, pinned Pack, agent, formula, provider, and physical workspace. Never
infer or locally recreate that configuration.

While runtime is suspended, validate supplied configuration statically and make
no workspace or runtime effect. A missing or conflicting declaration is the
first cause; do not invent a path, use a loose clone, worktree, temporary or
cross-repository location, translate another runtime's command, or substitute a
provider.

After explicit restoration, validate the complete placement graph, current
owner interface, authority, and non-derivable current-process credentials before
creation or dispatch. Apply one owner-selected workspace path atomically. The
first runtime, provider, filesystem, child, or publication failure propagates
unchanged; do not retry, retain a partial workspace, or fall back to another
path, provider, model, credential source, or compatibility interface.
