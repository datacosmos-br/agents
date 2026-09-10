---
name: beads-organization
description: 'beads organization, reconciliation, adjudication, hierarchy repair'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-organization","effective:2026-09-10","route:agent","subject:beads","usage:router"]'
---

# Beads Organization

Activate when continuously reconciling a selected Beads store against current
integration, workspace, runtime, plan, documentation, code, or external-tracker
evidence. Read the `complete procedure` (skill file) before any tracker write.

## Safety Contract

- Resolve the canonical tracker, configured integration branch, and current Gas
  City state before effects. A suspended store remains read-only unless the
  operator explicitly authorizes mutations to that exact store.
- Inventory through `bd` with an explicit limit. Use `--limit 0` only for an
  explicitly requested complete population.
- Use `scripts/reconcile-inventory.sh --limit <n> --integration <ref>` with
  either `--dry-run` or `--output <file.csv>`. `--beads` may be repeated or hold
  comma-separated IDs. The script queries `bd` and Git read-only, records
  integration/worktree context, and never authorizes a tracker mutation.
- Treat every CSV row as an unreviewed candidate. A write requires explicit
  reviewed input identifying the bead, intended change, and supporting current
  evidence. Re-read that bead immediately before applying the reviewed change.
- Apply no more than 20 reviewed mutations per batch. The first stale read,
  failed precondition, command failure, warning, or graph defect stops the batch.
- Never rewrite published Git history to improve weak subjects. Preserve the SHA
  and record a factual capability summary derived from its diff and integration
  reachability.

## Reconciliation Rules

1. Adjudicate by scope, owner, dependencies, and delivery evidence, never by
   title similarity. Similarity reports candidates, not duplicate truth.
2. Status follows live execution. Release claims only when owner, process,
   branch, and worktree evidence proves there is no executor. Deferred work
   needs a current date or scope gate; age alone changes nothing.
3. Tasks have one feature parent. Keep features small enough for short validated
   slices. Bugs remain at root with `bugfix`; `hotfix` belongs only to P0/P1 bugs.
4. Before closing a parent, re-parent or close every open child. Valid closure
   reasons begin with `SUPERSEDED:`, `OBSOLETE:`, or `DONE:` and name the proof.
5. Preserve legitimate workflow records whose metadata proves distinct spec,
   step, or control roles. Record the adjudication rather than closing them.
6. Run duplicate, cycle, parent-state, orphan, and convention gates before any
   authorized external sync. Start every next batch from a fresh inventory.

Report the exact command, working directory, exit status, decisive output,
reviewed IDs, and remote result for each applied batch. Never claim reconciliation
from a dry-run, generated CSV, stale snapshot, partial batch, or local-only state.

## Wave Protocol

- Analysis is delegated to bounded read-only subagent waves; only the
  coordinator applies reviewed mutation batches. Every worker returns one fixed
  row contract: `id, action, target, labels_add, labels_remove, status,
  evidence (<=15 words), exact command/SHA`, plus an explicit `undecided` list
  when evidence is insufficient.
- Each worker gets a precise row or file scope and disjoint file sets from its
  peers. Workers extract evidence through bounded searches (grep with context,
  line ranges) — never whole multi-thousand-line logs; a worker that exceeds
  its context budget fails its wave and is re-scoped, not retried unchanged.
- Gate each batch: before, `bd graph check --json`; after, `bd count
  --by-status --json`, `bd find-duplicates --limit 20 --json`, and
  `bd orphans --json`. Start every batch from a fresh read of its exact targets.
- `bd create/update/close --json` emits a JSON list, not an object; parse
  accordingly.
- Coordinator edits on a shared working tree are clobberable by concurrent
  lanes: scope every worker to disjoint paths, commit by explicit paths only,
  and re-verify shared-file edits immediately before each commit.
- When reconciliation touches generated-config floors, a committed SSOT
  contract (constraint caps, "do not lift" decrees) outranks an uncommitted
  mechanical rewrite. Restore the contract, revalidate, and file a defect bead
  against the tool that emitted the violation with a `discovered-from` link.
