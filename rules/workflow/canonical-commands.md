---
description: Use root Make, structural codemods, CRG, and LSP as the operational surface
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-05","route:both"]'
---

# Use selector-free root Make verbs

Diagnostics, validation, generation, formatting, correction, tests, Waza,
builds, publication, deployment, and maintenance execute only through one
explicit verb in the repository root Makefile. No Make selector, underlying-tool
argument, environment-dispatched sub-operation, file/match filter, inline
Python, raw tool, private module, wrapper, alias, or compatibility entry point
is an operational substitute.

`fix`, `fmt`, `check`, and every test verb require exactly `APPLY=Y`. Every
other mutating verb uses that same acknowledgement. Do not introduce a second
apply flag, truthy alias, dry-run inversion, or hidden mode. A distinct
operation receives a distinct public root verb; a missing verb is repaired at
the Make/codegen owner before work continues.

Before a non-trivial refactor, the declared CRG verb resolves symbols,
relationships, consumers, and blast radius from its current index, then the LSP
verb confirms language-owned definitions and references. Repeated structural
wiring changes execute through `make mod APPLY=Y` and tested ast-grep rules;
manual file-by-file rewiring is forbidden. A missing or stale index, unavailable
LSP, absent `mod` verb, failed codemod test, unexpected match cardinality, or
non-idempotent rewrite is RED and is corrected at its toolchain owner without a
textual-search or manual-edit fallback.

The public incremental test verb always activates pytest-testmon and its shared
external persistent database. The public full-test verb first invokes that
incremental verb, then invokes pytest-testmon no-selection against the same
database. CI calls those exact owners. No raw, focused, full, or CI path may
bypass or clear the cache.

The first command failure and raw traceback propagate. Warning, skip, empty
output, missing tool/report, partial execution, retry, normalization, or a
successful wrapper around a failed child is RED.
