---
name: fail-fast
description: "silent failure, failover removal, error propagation"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","usage:router"]'
  version: 2.0.0
---

# Fail Fast

Applies wherever code can hide a failure. The outcome is `rules/law.md` law 8, with the
original traceback intact and every child process the work started stopped.

- Delete catch-and-continue, retries, alternate paths, cached or partial success,
  ignored child exits, remapped exit codes and log-only errors.
- Check prerequisites before any effect; publish only after the producer and its
  validation succeed.
- Only the responsible boundary translates a failure, keeping its cause; independent
  outcomes are each kept; any required failure fails the whole.

A typed optional result, a loading placeholder or a default the owner resolves before
any failure is not a fallback.
