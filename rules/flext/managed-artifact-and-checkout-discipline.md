---
description: File-mutation infrastructure and rig checkout topology are single-owner facts, not per-consumer choices
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-12","route:personal"]'
---

<!-- Why: new file registering 2026-09-12 flext x ai-hub x agents operator rulings R20/R24; no existing owner covers managed-artifact mutation ownership or rig-checkout-tracks-integration-only -->

# Managed-artifact mutation and rig checkout discipline

Two invariants distilled from the 2026-09-12 toolchain/store operator rulings
(flext × ai-hub × agents). Both are single-owner facts, not implementation
choices a consumer may make on its own.

## File mutation has exactly one owner

flext-infra's managed-artifact machinery — codegen transaction, staging,
atomic journal, backup/validate/restore — is the sole owner of writing,
backing up, validating, and restoring generated files across the fleet. A
consumer, ai-hub included, calls that machinery; it never reimplements
transaction, staging, or rollback logic of its own for a file it does not
originate. A parallel implementation found in a consumer is exterminated and
rewired to the owner in the same change, never left to coexist as a
compatibility path.

## A rig's primary checkout tracks integration only

A project's primary (rig) checkout, and every submodule inside it, always
equals its remote integration branch; it is never the place where work
happens. Development happens in a worktree on its own lane — its own branch,
its own `.venv` reconstructed through the project's setup owner — and the
primary checkout receives only merged, fast-forwarded integration. A rig
found diverged from its integration branch is corrected by returning it to
that branch, never by continuing work in place.

See also: `shared-venv-guard.md` (rule file, `coordination/`) — the same
worktree-per-lane law applied to Python environments; `gitflow-branch-pr.md`
(rule file, `git/`) — lane creation and teardown ownership.
