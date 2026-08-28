---
globs: "**/*.py"
---

# Python failures remain explicit

Never swallow, mask, demote, or invent a successful result for a failed
operation.

- Catch only the specific exceptions a boundary can handle meaningfully.
- Preserve causes with `raise ... from exc` when translating.
- Use the repository's declared result/error contract; generic Python guidance
  does not invent a project-specific facade.
- Do not return `None`, an empty collection, or a default value to conceal an
  error.
- Do not add compatibility accessors, aliases, dual behavior, retry-to-another
  provider, or silent degradation.
- Tests prove the material error, cancellation, timeout, and should-not-trigger
  behavior through the public surface.
