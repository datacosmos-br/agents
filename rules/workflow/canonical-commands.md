---
description: Use root Make, structural codemods, CRG, and LSP as the operational surface
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-01","route:both"]'
---

# Use selector-free root Make verbs

The repository's own declared instructions — its AGENTS.md, README, docs, and selected
skills — own the canonical command inventory and practices. Resolve them before the
first effect in that repository. Never execute a guessed command, flag, signature, or
practice: an unverifiable form is verified at its canonical owner (declared docs,
source, the tool's own help) or not executed. A plausible command that succeeds without
a canonical basis is still a defect.

Diagnostics, validation, generation, formatting, correction, tests, Waza, builds,
publication, deployment, and maintenance execute only through one explicit verb in the
repository root Makefile. No Make selector, underlying-tool argument,
environment-dispatched sub-operation, file/match filter, inline Python, raw tool,
private module, wrapper, alias, or compatibility entry point is an operational
substitute. A parameter a verb declares in `make help`, such as `make test-file FILE=`,
is part of that verb, not a selector.

Invoke each verb directly to perform its declared operation. Do not introduce an apply
selector, acknowledgement flag, or hidden execution mode. A distinct operation receives
a distinct public root verb; a missing verb is repaired at the Make/codegen owner before
work continues.

Every command inventory honors the repository `.gitignore` through the shared Git-aware
owner. It does not disable language caches, delete ignored caches in ordinary flows,
bypass standard ignores, or maintain a parallel artifact list.

Before a non-trivial refactor, use the repository's declared structural capabilities.
Repeated wiring changes execute through `make mod` and tested ast-grep rules; manual
file-by-file rewiring is forbidden. When the host runtime has selected CRG or LSP, its
public command/hook/MCP resolves symbols, relationships, consumers, definitions, and
references. A portable library must not import that host, produce its index, or fail
merely because the optional runtime is absent. An available selected runtime that fails,
an absent `mod` verb, failed codemod test, unexpected match cardinality, or
non-idempotent rewrite is RED and is corrected at its owner without a manual fallback.

The host runtime that owns an indexed tool also owns initial build, incremental update,
storage, and readiness. Directory existence, an empty database, or a file left by failed
initialization is not proof of a usable index. Consumers query only the public runtime
contract; they never infer readiness from private artifacts. Never attempt update and
retry as build, create placeholder state, or normalize an incomplete index.

The first command failure and raw traceback propagate. Warning, skip, empty output,
missing tool/report, partial execution, retry, normalization, or a successful wrapper
around a failed child is RED.

## Command deadline and performance

Every command has a maximum wall-clock duration of 120 seconds, including activation,
preflight, lock acquisition, subprocesses and termination. This operator requirement
also applies to setup, complete test suites and profiling. A deadline wrapper is
permitted only to enforce that bound; it does not replace the declared operation,
change its scope, suppress output or turn a failure into success.

Reserve termination time inside the bound: request termination no later than 118
seconds and finish terminating owned children by 120 seconds. Nested operations consume
the remaining invocation budget, never a fresh budget per child. Do not signal another
actor's process or remove its lock to obtain the window.

A timeout is an incomplete failed invocation. Preserve its native output, exit,
completed scope and available profile. Before another invocation, identify and correct
the measured cause; do not retry unchanged, increase the limit, move the command into
an unbounded background job, or split its output into a false complete receipt.

For Python generation or migration slowness, use cProfile through the existing native
profiling verb. Bind the capture to source, runtime, configuration and scope; record wall
time separately from cumulative function time and distinguish parent waits from child
work. Change one measured cause, revalidate its public behavior and compare the same
operation before scaling. Reuse existing analysis owners rather than adding a parallel
cache, scanner or execution engine. Gate placement and opt-in instrumentation follow
[`gate-budget.md`](gate-budget.md).

When the operator authorizes documentation only, a missing deadline implementation or
broken generator remains an implementation finding. Correct its documentation and
record the exact code obligation without editing excluded code or claiming enforcement.

## Test verbs

This section is the single declaration of the test-verb law (tracker memory
`operator-ruling-2026-10-01-testmon-make-test-only`). Every other rule, skill, command,
agent profile, and doc references it and never restates it.

- `make test` always runs with pytest-testmon selection active against the persistent
  database at testmon's own default location (`.testmondata` at the pytest rootdir,
  ignored by Git); nothing forces it elsewhere (`rules/storage.md`). A run whose
  selection is deactivated is RED at the runner owner, never an accepted incomplete
  run.
- CI and pre-push run `make test`; CI persists the testmon database through its cache.
- Pre-commit runs no tests.
- `make test-full` runs only locally, without testmon selection, while preserving the
  existing database. It never runs in CI, at pre-commit, or at pre-push. It obeys the
  command deadline above; an interrupted full run is not complete-suite evidence.
- A `make test` run that executes no test is acceptable only as the typed cache hit of
  AGENTS.md law 14.
- `make test-file FILE=<repository-relative path>` is the sole allowed single-file
  path. `FILE` is that verb's declared parameter, not a selector. flext-infra owns the
  verb; this rule records the contract and does not define the implementation.
- Raw pytest, any other test-file or match selection, and deletion or replacement of the
  testmon database are prohibited; no raw, focused, or CI path bypasses these verbs.

The repository command owner implements this contract. A template, runner or workflow
that still runs tests at pre-commit, changes this selection contract or removes the
deadline is nonconforming; its presence does not create another permitted workflow.

## Zero-violation code gate

This section is the single declaration of the zero-violation code gate (operator
order 2026-10-03). Every other rule, skill, command, agent profile, and doc
references it and never restates it.

- New code is accepted only after `make mod` passes.
- A change is never closed while `make fmt`, `make fix`, `make check`, `make mod`,
  or the spelling gate reports any violation. The spelling gate is whichever of
  `make spell` and `make spells` the repository `make help` lists.
