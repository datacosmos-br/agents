---
description: Complete publication or attributable rollback with no partial success.
---

# Effects publish atomically

Build and validate the complete change set before mutation. Stage outputs on the
destination filesystem, validate staged bytes and ownership, and expose the new
state through the workflow's single declared atomic commit point. Success means
every required effect and publication completed; partial success is failure.

Rollback may remove or restore only effects attributable to the current
invocation and only from already validated recovery data. Rollback failure is
attached to the original exception, which remains the exception re-raised.
Never delete unknown, foreign, live, dirty, or ownership-ambiguous state.
