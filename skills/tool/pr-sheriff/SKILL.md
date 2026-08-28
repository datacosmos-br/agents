---
name: pr-sheriff
description: 'Triage pull requests when GitHub review work is explicitly requested.'
allowed-tools: Bash(gh pr *), Bash(git *)
version: 3.0.0
author: .agents
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:pr-sheriff","provenance:agents-owned","route:agent","tool:github","updates:manual","usage:on-demand"]'
---

# PR sheriff

Triage pull requests only for repositories explicitly declared by active
configuration. Never infer scope from a directory or scan an organization.

1. Resolve repository and configured integration branch.
2. List open PRs, checks, reviews, unresolved threads, and merge state.
3. Classify each PR from its diff and checks: actionable, blocked, superseded,
   or ready to land.
4. Recommend the smallest owner-correct action; never bypass a check, dismiss a
   warning, or omit a PR.
5. Before landing, integrate a diverged base by non-fast-forward merge and rerun
   runtime plus native gates.
6. Land by the approved PR method and verify the integration SHA.

Gas City supplies declared orchestration identity only. This skill creates no
agents, formulas, runs, sessions, branches, worktrees, or tracker items. While
runtime is suspended, restrict work to Git/GitHub and the existing checkout.
