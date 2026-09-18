---
description: Execute lane work only through selector-free root Make verbs
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-16","route:both"]'
---

# Execute a lane through its root Makefile

Work from the session's own worktree: its working directory is the lane root. Run
`git <verb>` and `make <public-verb>` there as plain commands. Claude Code worktree
isolation refuses `git -C <path>` and `env -C <path> make <verb>` when the path is not
the session's own worktree, so never use those forms, a `cd`, or `make -C` to reach
another checkout. Run bd as `direnv exec <dir> bd <verb>`. Each verb performs its
declared operation without an apply selector; do not substitute an underlying tool or a
Git/provider/package CLI for a root Make diagnostic, validation, generation, test,
publication, or deployment verb.

Guards are precise, not broad: they deny exact constructs and never block commands
agents legitimately need, such as `gh pr merge --admin`.

Preserve the exact command, worktree, exit code, decisive stdout, warning, and stderr.
Redirecting stdout to `/dev/null` is denied; `2>/dev/null` is allowed. Write long output
to `~/tmp/<scope>/<name>.log` and analyze it with rtk. Never chain a recovery command,
retry a denial, or reinterpret partial output as success. A guard refusal is RED: repair
the root Make/codegen owner, then invoke the same public verb once through that owner.
The first exception and raw traceback escape.
