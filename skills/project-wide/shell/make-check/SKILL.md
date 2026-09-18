---
name: make-check
description: "native gates, root make verbs, runtime-first validation"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","usage:router"]'
  version: 2.3.0
---

# Make Check

1. Read the authorized repository law and root Makefile, then use its public
   selector-free verbs only.
2. Provision with `make setup`. A stale generator, pin, downgrade, or version guard that
   blocks the newest owner is RED.
3. Exercise changed behavior through its real public runtime before tests.
4. Run `make check` and the smallest distinct public root verb that owns each additional
   required gate. Never invoke a raw underlying tool or private module.
5. Invoke every test verb directly with pytest-testmon and the same external persistent
   database. The full verb first runs incremental selection and then no-selection.
6. Record verb, cwd, exit, decisive output, scope, warning, and cache accounting.

A warning, skip, empty output, missing tool/report, zero collection, cache corruption,
retry, catch, or normalized failure is RED. Zero execution is valid only as a typed
incremental testmon cache hit with integrity and complete deselection accounting; never
call it tests passed. Correct a broken Make or codegen owner and rerun the same root
verb.

## Idempotency pre-push guard (evidence 2026-09-11, plan `docs/plans/2026-09-11-flext-conformance-sweep.md`)

- Before pushing any change that touches the generation surface, run `make gen` twice
  from the same tree and require byte-identical results. Only push on the doubled fixed
  point.
- A second run that diverges is a P0 product defect in the scaffolder (every fleet
  member consumes its projections), not a flaky environment. Instrument with file-based
  diffs (`difflib.unified_diff` to a log file; never stdout — codegen floods it), fix
  the divergent block at its writer, and add a convergence regression test for that
  exact block.
- A timed-out lock on the codegen journal is a bead (`harvest`), and the lock owner
  process is killed — never `rm -f` the lock preemptively.

## Graph-informed sweep loop (research 2026-09-11, plan section 10-11)

- Before structural or deletion-heavy edits, establish blast radius and rewiring maps
  with the code-review graph operated per `$crg` (freshness gate, `impact --files`,
  `query`); a graph built at another commit is no evidence, and the built-at commit is
  recorded with every cited result.
- Mechanical rewrite order per unit: crg map -> `make mod` detect/apply (cwd-scoped;
  rules SSOT `flext-infra/codemod/rules/` + the agent ast-grep universal rules archive)
  -> `make gen` (projection convergence) -> `make check` -> `make test`. Never bypass
  `make mod` with raw `sg`/ast-grep invocations; inline scan rules belong in the rules
  SSOT with a snapshot test, not ad-hoc command lines.
- Graph dead-code output and impact depth gate deletions only as candidates: a "dead"
  symbol with fleet callers is not dead, and a graph-versus-grep disagreement is a
  finding, not a green.
