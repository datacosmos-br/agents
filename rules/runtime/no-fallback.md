---
description: Prohibition of error-triggered alternates, retries, and partial execution.
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-09-29","route:both"]'
---

# One authorized path or failure

A workflow selects exactly one typed owner, provider, model, credential source,
algorithm, destination, and execution path during preflight. Failure of that path
terminates the invocation.

Retries, fallback implementations, alternate providers/models/accounts, cached-success
substitution, undeclared or competing defaults, compatibility aliases, dual
reads/writes, deprecated inputs, best-effort branches, partial execution, and reduced
modes are prohibited. Optional behavior exists only as an explicit typed absence in the
canonical schema; it cannot be inferred from a failure.

A retry is any repetition of a failed operation: a retry helper (`u.retry` and its
kind), automatic reconnection, or an `until` loop around a state-changing task. A
readiness wait is not a retry: it polls a read-only condition until an explicit deadline
and fails loud with the last observation when the deadline passes; it never repeats the
operation it waits for.

A deterministic default resolved and validated by the typed owner before any failure is
normal SSOT behavior, not fallback. Consumers omit equal environment variables,
settings, parameters, and arguments; only overrides remain explicit.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
