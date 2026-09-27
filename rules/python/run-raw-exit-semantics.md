---
globs: "**/*.py"
description: run_raw success means the command ran, not that it exited zero
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:both"]'s` means "the command ran" — decide on the exit code

`u.Cli.run_raw(...)` returns a result whose `.success` reflects invocation, not
the child's exit status. A command that ran and exited 1 is `.success` with
`outcome.raw_return_code == 1`.

## The failure shape this rule exists for

A "check for silence" command — the canonical case is
`git diff --cached --quiet`, which exits 0 when clean and 1 when there is
something to commit — was gated on `result.success`. That gate can never take
the dirty branch: the command always "runs successfully". The capture step was
silently skipped and the lane saved an empty state while reporting every effect
as applied.

## The rule

- Deciding **ran vs did-not-run** (spawn errors, timeouts): use `.success` /
  `.failure`.
- Deciding **exit-code semantics** (0 = clean, 1 = signal, 2 = usage…): use
  `u.Cli.process_succeeded(result.value.outcome)` or
  `result.value.outcome.raw_return_code` directly.
- Never infer "clean" from `.success` of a quiet-exit command.

```python
check = u.Cli.run_raw(["git", "diff", "--cached", "--quiet"], cwd=repo)
if check.failure:
    return r[...].from_failure(check)          # the command could not run
if not u.Cli.process_succeeded(check.value.outcome):
    ...                                        # exit != 0 → there IS something
```
