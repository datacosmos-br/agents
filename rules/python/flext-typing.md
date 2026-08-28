---
globs: "**/*.py"
---

# FLEXT-only typing delta

Apply this file only when project-local dependency/marker detection proves the
repository consumes FLEXT. It is never a generic Python rule, personal
technology profile, or reason to read another checkout.

Use the FLEXT aliases, protocols, models, result types, and exception families
exported by the project's pinned FLEXT dependency. Verify exact names against
that installed artifact; never invent an alias from another release.

- Prefer precise aliases/protocols over `Any`, `object`, and concrete
  implementation coupling.
- Follow the Python and Pydantic compatibility declared by the pinned FLEXT
  release; do not hardcode a version from an external repository.
- Fix type defects at the owner. No blanket ignore, `noqa`, compatibility
  shim, fallback, or old/new coexistence.
- Runtime, native gates, and project-local tests prove the change without a
  local FLEXT checkout, symlink, editable path, or cross-repository reference.
