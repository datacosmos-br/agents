---
name: beads
description: 'beads, issue tracking, task workflow'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads","effective:2026-08-29","route:agent","subject:beads","usage:router"]'
---

# Beads

Activate only when the repository selects Beads and the request concerns its
durable tracker. The active repository contract owns lifecycle and closure.

Resolve Available versus Explicitly suspended from the active repository
contract; never infer availability from a binary, port, or old instruction.

## Available

Preflight the declared storage scope, repository identity, canonical runtime,
live endpoint, current issue revision, actor authority, operation scope,
integration state, and non-derivable process credentials. Require
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

## Mutation coupling delta (evidence 2026-09-11, plan `docs/plans/2026-09-11-flext-conformance-sweep.md`)

- A bead must exist BEFORE the first repo-state mutation of its scope: file
  write, shell effect on the tree, or history rewrite. Git is the mirror; Beads
  is the execution truth — a change that exists only in git does not exist for
  the fleet's coordination views.
- Every newly discovered red (test failure, gate failure, runtime defect) gets
  a bead in the SAME turn it is observed, carrying the failing site, the best
  current root-cause hypothesis, and the observable trigger. Classifying a
  red as "pre-existing" without a bead is abandonment of the root cause, not
  scoping.
- Closure requires the four-evidence pattern: recorded state, git history,
  measured reality, integrated code.

## Explicitly suspended

Do not invoke the tracker, select an endpoint, start an embedded database,
recreate issues elsewhere, or claim tracker state. Create no substitute tracker
or ledger. Preserve evidence only in separately authorized Git, PR, review,
check, and CI surfaces; keep tracker state and phase closure unresolved.
