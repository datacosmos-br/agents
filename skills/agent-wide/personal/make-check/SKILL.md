---
name: make-check
description: 'native gates, project validation, command discovery'
license: MIT
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-29","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","provenance:agents-owned","role:verification","updates:manual","usage:router"]'
  version: 2.3.0
---

# Make Check

Use the repository's canonical Make surface.

## Procedure

1. From the authorized repository root, read project law and run `make help`.
2. Run declared `make setup` before every development or validation verb. A pin,
   downgrade, stale generator, or version guard blocking the newest owner is red.
3. Select only the exact command grammar documented by the current project's
   law or `make help`. A generic skill phase such as test, build, runtime, or
   documentation never authorizes synthesizing a `WHAT`, `PROJECT`, `FILE`,
   `MATCH`, `ARGS`, or other selector.
4. Exercise changed behavior through its real runtime before tests.
5. Record command, cwd, exit, decisive output, scope, and warnings.
6. On a broken owner, stop that invocation, fix the owner, and rerun the native
   target in the same task. Never substitute a raw command.

## Rules

- Never invent syntax or skip setup for an existing environment. Copy the
  owner's declared command exactly; do not combine valid fragments.
- For a configured duplication gate, use only flags supported by the selected
  executable and require its canonical zero-clone exit status. Never invent a
  baseline flag, ad hoc threshold, or substitute report.
- Do not call destructive, deployment, release, or promotion targets without the
  authority required by project law.
- Warning, skip, empty output, missing tool, or newest-version diagnostic is red.
  Never cap, downgrade, override, substitute, suppress, or call it compatibility
  without prior operator discussion, reproducible proof, and authorization.
- Later edits or integration commits invalidate earlier gate evidence in their
  affected scope until the same native check is rerun.
