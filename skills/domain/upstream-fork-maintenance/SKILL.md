---
name: upstream-fork-maintenance
description: 'third-party forks, upstream style, delta provenance'
license: MIT
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:selected-tag:third-party-fork","effective:2026-09-04","route:project","subject:upstream","usage:router"]'
---

# Upstream fork maintenance

Activate only for a managed fork whose verified upstream owner is outside the
internal owner set. Read the pinned upstream revision, contribution guide,
architecture, formatting, typing, runtime, build, and test contracts before
changing its delta. Match them exactly.

Do not apply internal Clean Architecture, dependency injection, stricter typing,
newer language features, framework conventions, or stylistic modernization.
When upstream itself requires one of these, comply because it is upstream policy.

Keep the patch minimal, attributable, replayable against its declared base, and
validated by upstream-native gates. Local governance additionally proves exact
remote identity, delta provenance, immutable artifact integrity, and runtime
deployment through `deployment-lifecycle`.
