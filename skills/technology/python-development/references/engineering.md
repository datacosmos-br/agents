# Python engineering

## Establish the contract

Read the project's Python version, package metadata, lockfile, source layout,
public exports, and native verification commands. Preserve the dependency
manager and formatter, linter, type checker, and test runner already selected by
the project.

## Implementation

- Parse external data once at the boundary into explicit project-owned types.
- Keep functions cohesive and make ownership of mutable state visible.
- Prefer immutable values where mutation is not part of the domain contract.
- Use `pathlib.Path` for filesystem paths and context managers for resources.
- Configure logging at entry points; libraries emit records without installing
  handlers.
- Catch the narrow exception that can be handled. Preserve causal context when
  translating an error at a boundary.
- Pass subprocess arguments as a sequence and handle a non-zero result
  explicitly.
- Keep import-time behavior free of network, process, and persistent-state side
  effects.
- Annotate public boundaries using the syntax supported by the project. Do not
  introduce `Any`, casts, or ignores to silence a type defect.

## Refactoring

Prove observable behavior before changing structure. Remove dead paths and
duplication, keep public behavior stable, and follow the codebase's established
abstractions. Function length, class count, and use of a particular standard
library helper are evidence to inspect, never universal thresholds.

Edit a generator or schema owner rather than its output. Re-run the affected
runtime path, then the project's focused static and behavioral gates.
