---
name: bash-guard-lane-execution
description: 'lane command forms, gate evidence, output preservation, guard repetition'
license: MIT
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-09-03","policy:atomic-effects","policy:fail-loud","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:governance","updates:manual","usage:router"]'
  version: 1.0.0
---

# Bash Guard Lane Execution

Select owner-directed worktree commands from `rules/shell/bash-guard-lane-execution.md`:
`git -C`, `env -C ... make`, `bun run --cwd`, and provider CLIs from the city root.
Preserve exact command, worktree, exit code, and decisive output; never discard stdout
or stderr. Use the export-only semicolon exception and only one top-level `&&`, `||`,
or `|`. Repeat a bare check/test only as an identical guard experiment after its
scoped command was denied, and treat every denial as a red gate.
