---
description: Execute lane work only through selector-free root Make verbs
metadata:
  aihub.tags: '["decision:ADR-0027","effective:2026-09-24","route:both"]'
---

# Execute a lane through its root Makefile

Run `git <verb>` and `make <public-verb>` against the lane root. From the session's own
worktree they run as plain commands; a lane in another checkout or repository is reached
with the owner-directed forms `git -C <lane> <verb>` and `env -C <lane> make <verb>`.
Never `cd` into another checkout or use `make -C`. Run the tracker CLI from the project
home through the project's environment loader. Each verb performs its declared operation
without an apply selector; do not substitute an underlying tool or a
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
