---
description: An approved plan owns its topic
metadata:
  aihub.tags: '["decision:ADR-0025","effective:2026-09-22","route:both"]'
---

# An approved plan owns its topic

At plan start or update, reconcile every correlated owner, WIP, branch, commit, and PR
within the authorized repository. Preserve and adopt useful work into the existing
change branch under `fix-forward collaboration` (rule file). Destroy, stash, or revert
nothing.

When required work has not reached the integration branch, adopt it into the owned
branch by reviewed non-FF merge. Preserve attribution and revalidate the integrated
result.

Keep repository scope within the operator's authorization. Every manual task uses a
dedicated native Git worktree and branch per `rules/coordination/gascity.md`; never
implement in the primary/default checkout. Do not invoke suspended orchestration or a
suspended tracker. Orchestration suspension alone leaves an independently selected and
available canonical Beads service usable. If the tracker is suspended, create no
substitute tracker or ledger and preserve evidence only in separately authorized
Git/PR/CI.

A diagnosis that ends in a verified-healthy service is complete, not a mandate to
improve it. When a service functions in the current session — including through a scoped
override such as an environment variable — continue the declared plan; do not rewrite
its persisted configuration in pursuit of a cleaner state. Persisted-configuration
change is scope expansion and requires a current defect or an explicit operator
instruction. Diagnosis is not reconfiguration.

## Operator-declared repository monopoly

The operator may name one session the sole holder of listed repositories. While the
declaration stands, no other actor edits, merges, or realigns branches there. The holder
assumes every pending WIP, branch, worktree, PR, and bead in them: it records each tip
SHA, adopts aligned work into the integration lane by fix-forward, and closes superseded
work with evidence. The monopoly waives no law — dedicated worktree, four-source bead,
PR, `merge --no-ff`, no rebase, no database reset. A bead closure in a shared tracker
still routes through its curation owner (`tracker-curation-routing`), and a lane whose
claim is under 24 hours old (`beads-canonical-epics`) is adopted only after `[coord]`
mail to its owner, unless the operator's declaration names it. Effects outside the held repositories
still require `[coord]` mail. The declaration lives in the current operator order and the
city `AGENTS.md`; a later session never inherits it by assumption.

## Corpus reconciliation

A reconciliation cycle selects one evidenced newest plan and retains it through its
integration proof before another plan begins. Within that plan, evaluate projects one at
a time from dependency owners to consumers, using the configured graph. Read the
complete plan and its attached material before adjudicating its meaning. Automatic
collection and ordering do not decide implementation, supersession, deletion, or tracker
closure.

The selected tracker alone owns execution status; a generated source inventory is not a
second ledger.
Versioned documents own the reviewed plan content, and any home copy is a configured
projection. Follow the `plan-reconciliation` skill for procedure; the distribution and
integration owners remain unchanged.
