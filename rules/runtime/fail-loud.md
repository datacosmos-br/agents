---
description: Typed expected branches and causal failure at the responsible boundary.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-10-29","route:both"]'
---

# Preserve failures at their responsible boundary

The 2026-10-29 operator supersession in
ADR-0021 (failure-boundary supersession, 2026-10-29)
replaces the blanket no-catch/no-aggregation and global-explosion requirements.
This is the canonical failure-boundary contract; consumer guidance references it.

Expected conditions use the owner's typed Result, validation outcome or explicit
branch before dependent effects. Do not raise/catch an exception to choose an ordinary
branch. Defaults apply only to declared optional absence, never invalid values,
required input, unavailable selected capabilities or failed execution.

Translate genuine external exceptions once at the responsible public boundary;
preserve exception, cause, traceback, code and data through native APIs. A formatted
message alone loses causality. Preserve existing typed failures, without repeated
wrapping or helper catches.

Stop unsafe dependents on their first failure. Proven independent units retain each
outcome; any required failure makes the aggregate nonzero. Partial-effect evidence is
not complete success, a warning waiver or a reduced population. Unknown independence
does not authorize continuing dependent effects.

Record and contain unexpected errors at the real isolation/cleanup boundary; retain
their causal failure without crashing unrelated units or acknowledging success.
Without a proven boundary, propagate the original error, never invent a global catch.
Cancellation/termination retain native control semantics after owned cleanup, never
ordinary recovery or success.

Cleanup failure is secondary evidence attached to the original cause, never its
replacement. Recovery follows [atomic effects](atomic-effects.md): preserve published
effects and correct forward. No catch-and-success, fallback, error-triggered default,
unchanged retry or unreported dropped outcome is permitted.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
