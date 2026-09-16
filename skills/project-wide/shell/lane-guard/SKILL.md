---
name: lane-guard
description: 'lane command forms, gate evidence, output preservation, guard repetition'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-03","supersedes:skill:bash-guard-lane-execution","usage:router"]'
  version: 1.0.0
---

# Bash Guard Lane Execution

Use the selector-free root Make contract from
`rules/shell/bash-guard-lane-execution.md`: plain `git` and `make` from the
session's own worktree, `direnv exec <dir> bd` for bd. Preserve exact verb,
worktree, exit code, decisive output, warning, and stderr. A guard denial
remains RED and is corrected at the command owner; it never authorizes a raw
tool, alternate checkout, hidden selector, retry, or partial-success claim.
