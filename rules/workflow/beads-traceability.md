---
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:personal"]'
---

# Selected canonical tracker and Git preserve the execution record

Beads applies only when the project or current operator explicitly selects its
canonical workflow and route. That route may belong to the repository or to an
existing central store outside the checkout. A local `.beads/` directory is not an
authorization by itself; its absence does not revoke an explicit central-store
selection. Installation or detection never selects tracking or orchestration.
Before effects in a selected workflow, validate tracker
identity, authority, configuration, and runtime; the first defect ends the selected
workflow.

## Tracker mode is resolved, never assumed

Read the active repository instructions for the scope under work and resolve one mode
before any tracker action:

- **Route absent:** when neither the project nor the operator selects an existing
  canonical route, perform no Beads or
  Gas City discovery, status, context, health, initialization, routing, or mutation.
  Continue through the repository's authorized non-tracker workflow; absence is not a
  tracker failure and creates no unresolved tracker closure requirement.
- **Workflow unselected:** when `.beads/` exists but the project or current workflow does
  not select Beads, perform no tracker discovery, status, context, health,
  initialization, routing, or mutation. The boundary alone grants no tracker action.
- **Available:** record and query execution state only through the declared tracker
  owner, verified through its documented interface. Never select an endpoint, database,
  or prefix by inference.
- **Explicitly suspended:** invoke no tracker command and create no alternate database,
  tracker, ledger, issue, or closure claim. Separately authorized Git, PR, review,
  checks, and CI preserve evidence; tracker state stays unresolved, so the phase cannot
  be `DONE`.

Explicit selection of the canonical route is the prerequisite. Do not create a local
boundary, initialize another database or copy server state to satisfy it. Never
restate Available or Explicitly suspended as a durable rule, and never
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

Plan reconciliation transfers valid pending work to canonical Beads before source
retirement; it does not authorize implementing historical proposals. Use the
`plan-reconciliation` skill for the single-plan transfer and retirement proof.

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

## AI Hub owns the versioned Beads-to-TODO view

Where this Beads projection is selected, AI Hub automatically generates and maintains
`TODO.md` for workspace roots, members and standalone projects. Beads alone owns work
state; no independent checklist, hand-edited projection or Markdown-to-Beads input path
is permitted. Each versioned view contains only its own project's nonterminal issues
across issue types, including active, blocked and deferred work. A root never aggregates
members. Terminal issues remain in Beads history; terminality comes from the selected
tracker's native lifecycle contract, not a guessed status list.

Ownership is one explicit issue metadata entry referencing AI Hub's canonical project
identity. Its key and schema belong to AI Hub's typed owner; verify the native metadata
round-trip before migration and preserve unrelated entries. Ledger identity, redirects,
folder names, issue prefixes and free text do not establish project ownership. Do not
invent a native Beads field or repurpose Jira's `external_ref`.

Before publication, enumerate and validate every nonterminal issue in the canonical
source, not merely ready issues or one destination's subset. Unknown, missing or
ambiguous attribution blocks every destination fed by that source, with exact blocking
issue IDs. Independent validated sources are not blocked by association. Initial
migration excludes terminal history; reopening requires valid ownership. Authorized
tracker clients own attribution writes; the renderer never silently repairs issue state.

AI Hub's existing maintenance and publication owners must provide automatic convergence,
complete snapshots, deterministic changed-byte views and destination precondition
checks. Failed reads, incomplete enumeration or attribution, concurrent manual edits
and failed publication never become an empty, partial or fresh-success view. Preserve
existing bytes and causal diagnostics without a fallback store. Adopting handwritten
content first requires complete semantic transfer and per-item receipts under the
plan-reconciliation source contract; never overwrite unaccounted or changed bytes.
The 2026-10-23T21:26:27Z operator correction selects Git history for recovery of old
TODO versions/data, not a parallel backup/archive store or separate TODO backup writer.
Unique untracked/uncommitted content stays in place until accounted for; Git history
does not recover those bytes. No automatic commits are permitted for preservation.
This correction changes no CAS publication safety requirement. Unrelated private plan
evidence and attachments retain their approved protected-evidence contract.

`TODO.md` is versioned, not ignored. Automatic updates may change the shared worktree
but never stage, commit or push; first generation is not Git publication. Source
alignment describes the required contract, not evidence of implemented or activated
automation. Real AI Hub runtime and distribution receipts are separate prerequisites
before relying on the projection for plan retirement.
