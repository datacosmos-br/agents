---
name: make-check
description: 'Discover and run canonical project gates when code or configuration changes require validation.'
bundle: governance
scope: universal
license: MIT
metadata:
  aihub.tags: '["provenance:agents-owned","role:verification","updates:manual","usage:router"]'
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
5. If the target, dependency, or tool is missing or broken, fix its canonical
   owner; never substitute a raw command to produce a green result.

## Rules

- Do not invent target names or copy another repository's Make contract.
- Do not call destructive, deployment, release, or promotion targets without the
  authority required by project law.
- A warning, skip, empty report, or missing tool is red unless the target's public
  contract explicitly classifies the outcome and the operator approved it.
- Later edits invalidate earlier gate evidence for their affected scope.
