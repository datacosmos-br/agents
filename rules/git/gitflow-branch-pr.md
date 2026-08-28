---
description: Publishing work — creating a branch, commit, push, or opening a PR. Load when the user asks to commit, push, land, publish, open a pull request, or before any git push.
metadata:
  aihub.tags: '["route:personal"]'
---

# Branch and PR — integration by merge commit

Work only on the existing authorized change branch, never directly on `main` or
the integration branch. While orchestration is suspended, create no branch,
clone, worktree, workspace, or alternate checkout unless the operator explicitly
expands scope.

- The repository owns Git branches, native gates, pull requests, and landing.
- Integration base comes from repository law/configuration. For `.agents` it is
  `dev`; `0.12.0-dev` belongs to FLEXT Infra and must never be used here.
- One git root per PR; never mix two repositories in one commit or PR.
- **Commit and push:** stage explicit scoped paths, commit, and push normally.
  Let
  pre-commit/pre-push/CI validate — do not re-run the full gate matrix by hand
  before every commit; `verification-loop` owns manual RED→GREEN evidence and
  CI owns the complete repeated matrix.
- If integration advanced or diverged, merge `origin/<integration>` into the
  change branch with `--no-ff`, resolve by preserving valid concurrent work,
  and revalidate. Never rebase or force-push an authorized branch.
- Open/update the PR against integration, resolve every conversation, obtain
  approval, require green checks, and merge by merge commit. Revalidate the
  exact merge SHA on integration.
- A failed check, actionable review finding, missing approval, or temporarily
  non-mergeable state keeps this landing cycle active. Fix, push, and rerun every
  actionable item; solicit or request help for independent approval only after
  the technical surface is green. Never switch task, phase, or repository merely
  by reporting the open PR state.
- Promotion to `main` waits for explicit operator approval.

A phase is `DONE` only after the approved PR is merged into integration and the
canonical tracker item is closed with evidence. Tracker runtime is suspended,
so no current phase can be called `DONE`.
