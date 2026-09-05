---
description: Use selector-free root Make verbs as the only operational surface
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-28","route:both"]'
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

The public incremental test verb always activates pytest-testmon and its shared
external persistent database. The public full-test verb first invokes that
incremental verb, then invokes pytest-testmon no-selection against the same
database. CI calls those exact owners. No raw, focused, full, or CI path may
bypass or clear the cache.

The first command failure and raw traceback propagate. Warning, skip, empty
output, missing tool/report, partial execution, retry, normalization, or a
successful wrapper around a failed child is RED.
