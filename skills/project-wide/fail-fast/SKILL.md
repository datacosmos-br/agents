---
name: fail-fast
description: 'silent failure, failover removal, error propagation'
license: MIT
metadata:
  aihub.tags: '["provenance:agents-owned","role:reliability","updates:manual","usage:router"]'
  version: 1.0.0
---

# Fail Fast

Silent failure and automatic failover are critical runtime hazards. They can
publish false success, corrupt state, lose or duplicate data, leave owned work
running, cross security boundaries, or operate against the wrong model,
provider, endpoint, credential, or database. They must never be introduced or
retained; one confirmed occurrence blocks delivery until it is removed.

Activate when code, automation, tests, or runtime paths may swallow errors,
publish stale success, continue after a failed dependency, or reroute to an
alternate implementation, provider, model, endpoint, database, or artifact.

Every failure must remain loud and propagate until its root cause is corrected,
an owning CLI boundary returns a nonzero exit with an actionable error, or the
agent exposes the unresolved warning or blocker in its final response. Logging,
catching, or warning internally and then continuing is silent failure.

Read the [complete procedure](references/procedure.md). It owns semantic
inventory, root-cause replacement, injected-failure tests, and closure gates.

Do not trigger from a keyword alone. A UI loading placeholder, typed optional
value, exhaustive validator, or explicitly nonfatal business result is not a
silent failure when its contract remains observable and tested.
