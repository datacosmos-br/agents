---
name: lane-landing-cycle
description: "beads, git worktree, landing cycle, pr merge, ci generation, lane retirement"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0021","detect:opt-in:lane-landing-cycle","effective:2026-09-27","route:agent","subject:beads","subject:git","subject:github","usage:router"]'
---

# Lane landing cycle

The verified mechanical cycle for one work unit on a governed repository lane,
from lane creation to retirement. Composes with the rules `full-landing-cycle`,
`beads-canonical-epics`, and `bead-branch-pr-cadence`.

## 1. Lane and bead first

```bash
git fetch origin dev
git worktree add ~/ai-hub-worktrees/<slug>-<date> -b fix/<slug>-<date> <dev-tip>
chmod 700 ~/ai-hub-worktrees/<slug>-<date>/.beads
env -C ~/ai-hub-worktrees/<slug>-<date> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make setup
```

- One mandate per lane; the primary checkout is never a work surface; the
  worktree lives on the destination filesystem, never `/tmp`, with its own
  physical `.venv` from `make setup`.
- Claim the bead and declare the triple (bead + branch + PR) to the
  coordinator via `gc mail human` at claim time. `bd update --append-notes`
  keeps the bead alive; abandonment follows rule `bead-branch-pr-cadence` §2.

## 2. The gate, in order

```bash
CI=Y env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make gen   # twice
env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make fix
env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make fmt
env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make check
env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make test-full  # bounded background
```

Run targeted tests first for fast feedback; the full suite is the landing
gate. A red is red: cure the root cause in the wave, or record it with its
owner and sequence — never bypass, never normalize.

## 3. Classify generated outputs by owner

Read the project generator declaration and inspect each changed output before
staging. A generated file belongs in the PR when its tracked source changed and
the canonical generator produced it. In this standalone `agents` project,
`make gen` owns `.beads/metadata.json` and `.envrc`; both are committed for
fresh linked worktree activation. In projects where `CI=Y` changes emission,
regenerate through that project's declared CI context and verify the fixed
point. Preserve unrelated worktree changes and repair source drift at its owner.

## 4. Land, prove, retire

```bash
git push -u origin fix/<slug>-<date>
gh pr create --base dev --head fix/<slug>-<date> --title "..." --body "bead, scope, evidence"
gh pr checks <n> --repo datacosmos-br/ai-hub     # ci, merge-guard, release-plan, Kilo review
gh pr merge <n> --repo datacosmos-br/ai-hub --merge
```

Post-merge proof: merge `origin/dev` into the lane, rerun the targeted tests,
close the bead with the evidence, retire the lane:

```bash
git worktree remove --force ~/ai-hub-worktrees/<slug>-<date>
git branch -D fix/<slug>-<date> && git push origin --delete fix/<slug>-<date>
```

## 5. Judgment calls this cycle encodes

- Before starting: research branches, PRs, and beads for prior art; adopt the
  survivor, never re-implement (dedupe mandate,
  `bead-branch-pr-cadence`).
- Environmental timeouts under host load: prove with a profile and a serial
  rerun before blaming code. Template case: the deploy-staging fsync budget,
  bead `aihub-5j4cw.5` in ai-hub.
- End-to-end reference for the whole cycle executed under fire:
  `docs/plans/2026-09-27-real-activation-f4-f5-landing.md` (ai-hub).
