# PR/branch archaeology sweep — 2026-09-18 (ag-y19j)

One-by-one evaluation of every local branch, stray worktree, closed-unmerged PR and subprojects of this repository against the integration branch `dev`, each measured from
subproject of this repository against the integration branch `dev`, each measured from
its own last fork point (`git merge-base dev <head>`). Safety patches for every
discarded lane with content are archived outside the repository at
`~/agents-worktrees/archives/sweep-20260918-ag-y19j/` (manifest included there).
Tracked in beads issue `ag-y19j` (agents store).

Integration-type note (operator ruling, 2026-09-18): cycle-closing PRs go from a
Integration-type note (operator ruling, 2026-09-18): cycle-closing PRs go from a worktree branch INTO the integration branch (`dev`), never from the integration
branch to `main`.

## Stray worktrees (5) — all discarded

| Worktree | Branch | Fork-point evidence | Verdict |
|---|---|---|---|
| `agents-worktrees/crg-skill` | `feat/crg-skill` | tip == fork, ancestor of `dev`, 0 unique commits | Delivered via #151; discarded (only a generated `uv.lock` inside) |
| `agents-worktrees/crg-wiki-docs` | `docs/crg-wiki-cli` | `dev...branch` empty | Delivered via #153; discarded |
| `agents-worktrees/rtk-guard-skills` | `docs/rtk-guard-skills` | tip == fork, 0 unique commits | Delivered via #152; discarded (generated `uv.lock` inside) |
| `agents-worktrees/stage-guard` | `fix/stage-no-worktree-gitlink` | tip == fork, 0 unique commits; uncommitted `math.isclose` draft in `skill_evals.py` | Draft superseded: `dev` carries the stricter evolved form (numeric typecheck + `isclose` tol 0, `src/agents_governance/skill_evals.py`); delivered via #145; discarded |
| `.flext-runtime/.../agents-skills` | `docs/bead-skills-fleet-protocol` | tip == fork, 0 unique commits; stale generated CLAUDE.md header | `dev` carries a newer generator output (`config/governance.json`, `make gen`); delivered via #146/#147/#143; discarded |

## Local branches without worktrees (3) — all discarded

| Branch | Fork-point evidence | Verdict |
|---|---|---|
| `fix/bundle-load-performance` | tip `9d605b9d` ("wip") is ancestor of `dev`, 0 unique commits | Delivered via #141; deleted |
| `fix/bundle-load-tree-validation` | tip `9eb0a69f` ancestor of `dev` | Delivered via #144; deleted |
| `docs/governance-reconciliation` | tip `a0666c04` ("wip", origin branch deleted upstream) is ancestor of `dev` | Absorbed (CRG evals, lane-guard, ADR-0016 tweaks); deleted |

## Closed, unmerged PRs (13) — all superseded, none carried unlanded improvement

Tip-ancestry proven absorbed (no action needed): #130, #74, #28, #24.

Evaluated from fork point, content probed in `dev` (patch archived where non-empty):

| PR | Branch-side content | Why superseded | Patch (lines) |
|---|---|---|---|
| #150 plan-reconciliation make contract | empty (head is a bare dev merge) | Lane landed via #148/#149 — merge commit `cfd84f8d` in `dev`, key files verified | 0 |
| #120 project skill distribution | empty (branch emptied before close) | Theme delivered via #108, #84, #131, #63, #59 | 0 |
| #119 retire hooks projection surface | 25 files, +758/−1526 | Goal delivered by the ADR-0022 materialized-projection lane; no `test_hook_projection.py` nor `hook_projection` refs remain in `dev` | 2853 |
| #76 react-dom bump (dependabot) | empty | Absorbed with #77 | 0 |
| #54 hotfix frontmatter v2 | 10 files, +192/−150 | `rules/coordination/beads-verification.md` exists in `dev` in a much stronger form (four independent sources); skills restructured since | 437 |
| #53 restore frontmatter openers | 9 files, −9 | All touched skills open with `---` in `dev` | 81 |
| #50 cosmos docgen retirement / direnv | empty | `dev` `.envrc` is generated from the same `base/.envrc.beads-workspace.j2` template | 0 |
| #33 pr-sheriff mergeability | 1 file, +7/−1 | `pr_triage.py` surface retired in the skill cutover; mergeable/clean gate lives in `skills/tool/pr-sheriff/references/triage.md` | 26 |
| #6 ai-hub primary contract (era artifact) | 187 files, +1291/−710 | Touched surfaces (`tests/test_waza_config.py`, `src/agents_governance/cli.py`) no longer exist; contract evolved via #139 + ADR-0022 | 5200 |

## Subprojects and orphans

- No submodules, no nested git repositories; the npm fixtures under `evals/` are
  tracked test fixtures managed by dependabot (all their PRs merged).
- `~/agents-worktrees/ag-2wq-home/` (1102 generated projection files, unreferenced by
  `dev`) discarded; `ag-2wq.pathscope.patch` moved into the archive (lane landed via #102).

## Canonical make cycle at `dev` tip (fb22af55)

`make setup` (environment built), `make gen` (fixed point: 10 hooks + 1 plugin +
2 pointers), `make fix` (ruff: all checks passed), `make fmt` (14 files unchanged) —
zero tracked changes: `dev` was already in canonical state.

## Outcome

- 8 branches + 5 worktrees + 13 closed PRs resolved one-by-one: every one either
  already delivered in `dev` or superseded by a stronger landed form; nothing of
  value discarded without an archived patch.
- The superseded worktree residue is gone; `~/agents-worktrees/` keeps only `archives/`.
- Operator ruling recorded: markdown-code gate taken out of the default check gate
  set fleet-side (flext-infra `7be655062`, ai-hub `a3271ff7e`), review pending in
  bead `flext-uz0dt`.
