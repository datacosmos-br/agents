---
name: lane-landing-cycle
description: "beads, git worktree, landing cycle, pr merge, ci generation, lane retirement"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0021","detect:opt-in:lane-landing-cycle","effective:2026-09-27","route:agent","subject:beads","subject:git","subject:github","usage:router"]'
---

# Lane landing cycle

The verified mechanical cycle for one work unit on a governed repository lane,
from authorized placement to any authorized retirement. Composes with the rules `full-landing-cycle`,
`beads-canonical-epics`, and `bead-branch-pr-cadence`.

## 1. Lane and bead first

Resolve placement through `rules/coordination/gascity.md`, environment identity
through `shared-venv-guard` and WIP preservation through `fix-forward-collaboration`.
This skill does not create isolation or grant checkout-changing authority.
- Claim the bead and declare the triple (bead + branch + PR) to the
  coordinator via `gc mail human` at claim time. `bd update --append-notes`
  keeps the bead alive; abandonment follows rule `bead-branch-pr-cadence` §2.

## 2. The gate, in order

First complete documented alignment, implementation and real public-runtime proof
under `engineering-core` and `runtime-is-reality`. Only then enter this validation
sequence or change regression tests; the gate list is not permission for test-first work.

```bash
CI=Y env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make gen   # twice
env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make fix
env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make fmt
env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make check
env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make test
env -C <lane> -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make test-full  # local, background
```

Within final test validation, run targeted tests before the full local landing suite.
Where each test verb runs, and its testmon contract, are declared in
`rules/workflow/canonical-commands.md` (section "Test verbs"). A red is red: cure the
root cause in the wave, or record it with its owner and sequence — never bypass, never
normalize.

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
gh pr create --base dev --head fix/<slug>-<date> --title '...' --body-file pr-body.md   # bead, scope, evidence
gh pr checks <n> --repo datacosmos-br/ai-hub     # ci, merge-guard, release-plan, Kilo review
gh pr merge <n> --repo datacosmos-br/ai-hub --merge
```

Base movement before landing is integrated with `git merge --no-ff origin/dev` (never
`git rebase` or `git pull --rebase`). After the PR merges, leave the lane branch
unchanged: fetch, prove its tip is reachable from `origin/dev`, rerun the targeted tests
on the fetched integration tip, close the bead with the evidence, then assess retirement:

The following retirement example is conditional on explicit removal authority for
an owned disposable isolated lane and the Git owner's full tracked, staged and untracked
preservation proof, runtime-reference and activity checks. Integration ancestry alone
does not authorize removal. Never apply it to an adopted primary, integration,
shared or foreign context.

```bash
git fetch origin dev \
  && git merge-base --is-ancestor fix/<slug>-<date> origin/dev \
  && git switch --detach origin/dev \
  && make test \
  && cd ~/ai-hub \
  && git worktree remove ~/ai-hub-worktrees/<slug>-<date> \
  && git branch -d fix/<slug>-<date> \
  && git push origin --delete fix/<slug>-<date>
```

A failed ancestry check, a red test, or a dirty worktree stops the chain; never force it.

## 5. Judgment calls this cycle encodes

- Before starting: research branches, PRs, and beads for prior art; adopt the
  survivor, never re-implement (dedupe mandate,
  `bead-branch-pr-cadence`).
- Environmental timeouts under host load: prove with a profile and a serial
  rerun before blaming code. Template case: the deploy-staging fsync budget,
  bead `aihub-5j4cw.5` in ai-hub.
- End-to-end reference for the whole cycle executed under fire:
  `docs/plans/2026-09-27-real-activation-f4-f5-landing.md` (ai-hub).
