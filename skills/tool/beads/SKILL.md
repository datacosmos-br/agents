---
name: beads
description: 'beads, issue tracking, task workflow'
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:beads","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:beads","updates:manual","usage:router"]'
---

# Beads

Activate only when the repository selects Beads and the request concerns its
durable tracker. The active repository contract owns lifecycle and closure.

Resolve Available versus Explicitly suspended from the active repository
contract; never infer availability from a binary, port, or old instruction.

## Available

Preflight the declared storage scope, repository identity, canonical runtime,
live endpoint, current issue revision, actor authority, operation scope,
integration state, and any non-derivable current-process credentials. Require
`bd context --json` and `bd ping --json` to prove the intended store before a
write. A project keeps its identity/database authority while inheriting a
managed endpoint declared by its runtime owner; do not select an alternate
endpoint or ledger by inference.

Historical records produced while tracking was suspended are immutable input
only for an operator-authorized reconciliation. Convert them to the canonical
Beads import schema, prove the conversion with a stdin dry run, import through
the supported owner, verify every resulting identity, and leave the source
unmodified. Never hand-edit Dolt storage, retain an alternate store, overwrite
newer live state, or use stale import authorization.

Apply one authorized tracker operation against the current revision only after
all checks pass. The first runtime, conflict, authorization, or persistence
failure propagates unchanged. Do not retry, fall back, partially update, or
translate a failure into local evidence. Verify the durable post-state before
reporting it.

## Explicitly suspended

Do not invoke the tracker, select an endpoint, start an embedded database,
recreate issues elsewhere, or claim tracker state. Create no substitute tracker
or ledger. Preserve evidence only in separately authorized Git, PR, review,
check, and CI surfaces; keep tracker state and phase closure unresolved.
