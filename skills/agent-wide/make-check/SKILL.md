---
name: make-check
description: 'native gates, project validation, command discovery'
license: MIT
metadata:
  aihub.tags: '["policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","provenance:agents-owned","role:verification","updates:manual","usage:router"]'
  version: 2.0.0
---

# Make Check

Discover and use the repository's canonical Make surface before running build,
test, lint, format, generation, security, or release commands.

## Procedure

1. From the authorized repository root, read project law and run `make help`.
2. Select the declared target that owns the requested behavior. Use its scoped or
   changed-file option only when the help surface documents one.
3. Exercise the real runtime before tests when behavior changes.
4. Run the chosen target and record working directory, exit code, decisive output,
   covered scope, and warnings.
5. If a required target, dependency, or tool is missing or broken, stop that
   invocation, correct its canonical owner, and rerun the native target. Keep the
   same task active; request authority only when the required owner is materially
   outside the approved scope. Never substitute a raw command.

## Rules

- Do not invent target names or copy another repository's Make contract.
- Do not call destructive, deployment, release, or promotion targets without the
  authority required by project law.
- A warning, skip, empty report, or missing tool is red. Preserve its exact
  output, correct the owner, and rerun only the invalidated native target.
- Later edits invalidate earlier gate evidence for their affected scope.
