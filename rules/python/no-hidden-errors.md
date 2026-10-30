---
globs: "**/*.py"
description: Python failures remain explicit
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-10-29","route:both"]'
---

# Python failures remain explicit

Never swallow, mask, demote, or invent a successful result for a failed operation.

Apply the [failure-boundary owner](../runtime/fail-loud.md) and its 2026-10-29
operator supersession. The former blanket prohibitions on CLI translation and
independent error aggregation are no longer operative.

- Expected conditions follow the declared typed return/branch contract before effects;
  exceptions are not a substitute for ordinary condition testing.
- Select Python exception handling from the actual native APIs and responsible public
  boundary, not a mechanical catch list. Preserve genuine causes, traceback and typed
  failure metadata through that boundary. For FLEXT, inspect the selected `r` and
  `p.Result` contracts and compose existing failure operations; message-only rebuilding
  loses evidence. Do not add helper catches merely to satisfy a Result annotation.
- Independence, aggregate failure, unexpected-error containment and cancellation follow
  the failure-boundary owner. Cleanup uses the original cause and attaches secondary
  failures; the [atomic-effects rule](../runtime/atomic-effects.md) owns recovery.
- Do not return `None`, an empty collection, or a default value to conceal an error.
- Do not add compatibility accessors, aliases, dual behavior, retry, alternate
  providers, error-triggered or competing defaults, invented exit translation, partial
  results presented as complete, or silent degradation. A typed canonical default is
  legitimate only for the owner's declared optional absence. An old public signature
  with consumers follows
  the `zero residue` rule's "Deprecated-signature window" section.
- Tests prove the material error, cancellation, timeout, and should-not-trigger behavior
  through the public surface.

See also: `config-settings-ssot.md` (rule file) — configuration authority owner.
