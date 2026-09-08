---
name: make-check
description: 'native gates, root make verbs, runtime-first validation'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","usage:router"]'
  version: 2.3.0
---

# Make Check

1. Read the authorized repository law and root Makefile, then use its public
   selector-free verbs only.
2. Provision with `make setup APPLY=Y`. A stale generator, pin, downgrade, or
   version guard that blocks the newest owner is RED.
3. Exercise changed behavior through its real public runtime before tests.
4. Run `make check APPLY=Y` and the smallest distinct public root verb that owns
   each additional required gate. Never invoke a raw underlying tool or private
   module.
5. Every test verb uses `APPLY=Y`, pytest-testmon, and the same external
   persistent database. The full verb first runs incremental selection and then
   no-selection.
6. Record verb, cwd, exit, decisive output, scope, warning, and cache accounting.

A warning, skip, empty output, missing tool/report, zero collection, cache
corruption, retry, catch, or normalized failure is RED. Zero execution is valid
only as a typed incremental testmon cache hit with integrity and complete
deselection accounting; never call it tests passed. Correct a broken Make or
codegen owner and rerun the same root verb.
