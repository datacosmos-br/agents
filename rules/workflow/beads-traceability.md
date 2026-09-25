---
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:personal"]'
---

# Selected canonical tracker and Git preserve the execution record

Beads applies only when the repository contains its `.beads/` boundary, the project
authorizes it, and the workflow explicitly selects Beads. A repository without
`.beads/` selects neither Beads nor Gas City: do not invoke, locate, or probe `bd` or
`gc`, and do not create a replacement boundary. Installation or detection never selects
tracking or orchestration. Before effects in a selected repository, validate tracker
identity, authority, configuration, and runtime; the first defect ends the selected
workflow.

## Tracker mode is resolved, never assumed

Read the active repository instructions for the scope under work and resolve one mode
before any tracker action:

- **Unselected:** when the repository has no `.beads/` directory, perform no Beads or
  Gas City discovery, status, context, health, initialization, routing, or mutation.
  Continue through the repository's authorized non-tracker workflow; absence is not a
  tracker failure and creates no unresolved tracker closure requirement.
- **Available:** record and query execution state only through the declared tracker
  owner, verified through its documented interface. Never select an endpoint, database,
  or prefix by inference.
- **Explicitly suspended:** invoke no tracker command and create no alternate database,
  tracker, ledger, issue, or closure claim. Separately authorized Git, PR, review,
  checks, and CI preserve evidence; tracker state stays unresolved, so the phase cannot
  be `DONE`.

The `.beads/` boundary is the invariant selection prerequisite, not mutable runtime
state. Never restate Available or Explicitly suspended as a durable rule, and never
infer either from an installed binary, a reachable endpoint, a running process, or
another scope.

## Tracking capability and bead data are different subjects

Suspension governs Beads as the execution tracker of the current work. It does not
govern bead records that an authorized workflow owns as its own data — a migration,
import, export, or audit whose target store the operator declared. That workflow writes
only through its declared owner, at its declared endpoint, within its stated
authorization, and never becomes a substitute tracker for the work that performs it.

## Provenance is written, never inferred on read

A tool that writes records and later reads them back sees three populations it must
never conflate: what it imported from a source, what it authored itself to satisfy its
own contract, and what something else created directly in the destination. They are
indistinguishable by shape — a record the tool authored has no source and can never
carry source provenance, which is exactly what a record whose provenance was lost looks
like.

Write the class as a typed attribute at creation, and classify on read by that attribute
alone. Never infer it from a missing field, a title, a timestamp, or a count, and never
accept a claimed class without proving the marker is one the writer could have produced.
A record whose class cannot be established is a failure, not a default.

## Reconciliation preserves executable truth

When the operator selects backlog reconciliation, inspect the complete requested
population through explicit limits and mutate in batches of at most 20. Re-read each
bead immediately before its write and use its opaque revision when the backend exposes
one. A stale revision ends the batch.

Status follows current execution evidence. A claim requires a live owner, worktree,
branch, or process. Deferred work requires a current date or scope gate. A closed parent
cannot retain open children. Tasks belong to one feature; features stay small enough to
execute as short validated slices. Bugs remain at root, carry `bugfix`, and carry
`hotfix` only at P0 or P1. Labels encode these classes; prose explains the behavior and
evidence instead of repeating tags.

Weak commit subjects are discovery evidence only. Preserve published SHAs and derive
current summaries from the diff, integration reachability, merged PR, and live code.
Validate duplicates, cycles, parent state, and conventions before external sync. Record
the command, working directory, exit status, and remote result after every synced batch.
