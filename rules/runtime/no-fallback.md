---
description: Prohibition of retries, fallbacks, alternates, defaults, and partial execution.
---

# One authorized path or failure

A workflow selects exactly one typed owner, provider, model, credential source,
algorithm, destination, and execution path during preflight. Failure of that
path terminates the invocation.

Retries, fallback implementations, alternate providers/models/accounts,
cached-success substitution, operational defaults, compatibility aliases,
dual reads/writes, deprecated inputs, best-effort branches, partial execution,
and reduced modes are prohibited. Optional behavior exists only as an explicit
typed absence in the canonical schema; it cannot be inferred from a failure.
