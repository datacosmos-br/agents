---
description: Execute lane work only through selector-free root Make verbs
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-03","route:both"]'
---

# Execute a lane through its root Makefile

From outside an authorized lane, use
`env -C <worktree> make <public-verb>` so the selected root remains explicit.
Each verb performs its declared operation without an apply selector. Do not
change directory, use `make -C`, pass a selector, call an underlying tool, or
substitute Git/provider/package CLIs for a root Make diagnostic, validation,
generation, test, publication, or deployment verb.

Preserve the exact command, worktree, exit code, decisive stdout, warning, and
stderr. Never redirect evidence away, chain a recovery command, retry a denial,
or reinterpret partial output as success. A guard refusal is RED: repair the
root Make/codegen owner, then invoke the same public verb once through that
owner. The first exception and raw traceback escape.
