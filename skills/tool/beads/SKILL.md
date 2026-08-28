---
name: beads
description: 'beads, issue tracking, task workflow'
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:beads","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:beads","updates:manual","usage:router"]'
---

# Beads

Activate only when the repository selects Beads and the request concerns its
durable tracker. The active repository contract owns lifecycle and closure.

While the canonical tracker is suspended, do not invoke it, select an endpoint,
start an embedded database, recreate issues elsewhere, or claim tracker state.
Preserve execution evidence in the repository's declared manual ledger and keep
the issue and phase open.

After explicit restoration, preflight the repository identity, canonical
runtime, current issue revision, actor authority, operation scope, integration
state, and any non-derivable current-process credentials. Obtain the supported
interface from the restored runtime owner; never invent or retain commands,
flags, aliases, profiles, or routing.

Apply one authorized tracker operation against the current revision only after
all checks pass. The first runtime, conflict, authorization, or persistence
failure propagates unchanged. Do not retry, fall back, partially update, or
translate a failure into local evidence. Verify the durable post-state before
reporting it.
