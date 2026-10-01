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
substitute.

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

## Test verbs

This section is the single declaration of the test-verb law (tracker memory
`operator-ruling-2026-10-01-testmon-make-test-only`). Every other rule, skill, command,
agent profile, and doc references it and never restates it.

- `make test` always runs with pytest-testmon selection active against the shared
  external persistent database. A run whose selection is deactivated is RED at the
  runner owner, never an accepted incomplete run.
- CI and pre-push run `make test`; CI persists the testmon database through its cache.
- Pre-commit runs no tests.
- `make test-full` runs only locally, without testmon and without any time limit. It
  never runs in CI, at pre-commit, or at pre-push.
- A `make test` run that executes no test is acceptable only as the typed cache hit of
  AGENTS.md law 14.
- Raw pytest, direct test-file selection, and deletion or replacement of the testmon
  database are prohibited; no raw, focused, or CI path bypasses these verbs.
