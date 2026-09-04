---
description: Running any ccs / cliproxy command (doctor, cliproxy start/restart). Load before touching the CCS proxy so live opencode sessions are not killed.
---

# Do not run ccs commands that recycle the proxy mid-session

`ccs doctor --fix` and `ccs cliproxy` restarts cycle the CLIProxy on :8317 and
kill live opencode sessions (a `--fix` was interrupted and dropped active
sessions). Do not run them while sessions are active; warn the operator first.

- Live in-proxy 429 cooldowns are not shown by `ccs ... quota`; fill-first can
  route to a rate-limited account. Treat transient upstream 429/quota as
  retry-and-degrade, never a hard task failure.

## This rule governs a live request, not tier allocation

Retry-and-degrade applies to a request already in flight. It does not apply to
the model pipeline deciding which models compose a tier: a candidate whose probe
did not succeed in the current cycle is not allocated, and a tier that cannot be
filled fails the cycle rather than publishing a degraded generation (ADR-0022).

The two are not in conflict and neither weakens the other. Do not cite this rule
to relax a tier floor, to keep a rate-limited candidate eligible, or to publish
an incomplete generation; and do not cite the allocator's fail-closed behaviour
to turn a transient 429 on a live request into a task failure.
