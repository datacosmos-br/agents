---
description:
  Internal code uses precise typing and the full declared runtime language level.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-04","route:project"]'
---

# Runtime floor and language level

Apply this rule only to `internal` and `internal_flext` profiles. A `third_party_fork`
follows the upstream language level, typing policy, toolchain, and style without local
modernization.

The project manifest is the only owner of supported runtime versions. Compiler,
formatter, linter, type checker, build, CI, and editor targets must agree with its
minimum version. Internal code uses precise public types and the strongest native syntax
and standard-library capabilities available at that floor when semantically applicable.
Downlevel syntax, polyfills, compatibility branches, and vague types retained for an
older undeclared runtime are defects.

When the floor changes, update the manifest owner, regenerate derived config, remove
superseded compatibility, and prove build plus runtime on the new floor.
