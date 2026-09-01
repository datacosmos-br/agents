---
description: Publishing work — creating a branch, commit, push, or opening a PR. Load when the user asks to commit, push, land, publish, open a pull request, or before any git push.
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-29","route:personal"]'
---

# Branch and PR — integration by merge commit

Work on a change branch of the authorized repository, never directly on `main`
or the integration branch. Creating a clone, worktree, workspace, or alternate
checkout is a scope expansion the operator must state explicitly; while
orchestration is suspended it is prohibited.

- The repository owns Git branches, native gates, pull requests, and landing.
- Integration base comes from the repository's own law or configuration; read it
  there for the repository under work. Never hardcode a branch name in universal
  guidance, assume one from another repository, or reuse the base of a sibling
  project.
- One git root per PR; never mix two repositories in one commit or PR.
- **Clean-round checkpoint:** after every complete applicable local validation
  round that is green and covers material tracked changes, immediately stage
  explicit scoped paths, create a conventional checkpoint commit, and push the
  change branch. Open or update its PR, require remote gates and review, and
  merge that persisted checkpoint into integration by merge commit before
  starting the next implementation unit. Revalidate the exact integration merge
  SHA, then start the next unit from that current integration state. A red or
  incomplete round produces no green checkpoint. Never create an empty commit
  merely because remote CI completed: that would recursively start another CI
  round without a material state change. Pre-commit/pre-push/CI may repeat their
  declared matrix; `verification-loop` owns the manual RED→GREEN evidence.
- If integration advanced or diverged, merge `origin/<integration>` into the
  change branch with `--no-ff`, resolve by preserving valid concurrent work,
  and revalidate. After that clean combined round, checkpoint and push the merge
  before continuing. Never rebase or force-push an authorized branch.
- Open/update the PR against integration, resolve every conversation, obtain
  approval, require green checks, and merge by merge commit. Revalidate the
  exact merge SHA on integration.
- A failed check, actionable review finding, missing approval, or temporarily
  non-mergeable state keeps this landing cycle active. Fix, push, and rerun every
  actionable item; solicit or request help for independent approval only after
  the technical surface is green. Never switch task, phase, or repository merely
  by reporting the open PR state.
- Independent review is mandatory and never self-granted. When the operator
  states that no independent reviewer exists and authorizes an administrative
  merge, that authorization covers the human approval row only: green checks,
  resolved conversations, merge-commit strategy, and revalidation of the exact
  merge SHA stay mandatory, and the closure record names the approval as
  operator-authorized instead of satisfied.
- Promotion to `main` waits for explicit operator approval.

A phase is `DONE` only after the approved PR is merged into integration and the
canonical tracker item is closed with evidence. Resolve the tracker mode from
the repository's own instructions; while it is explicitly suspended, closure
stays open and no phase may be reported `DONE`.
