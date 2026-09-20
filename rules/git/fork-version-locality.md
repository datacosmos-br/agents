---
description:
  Cutting or auditing a managed fork release, bumping a fork version, or syncing with
  upstream. Load when the user versions a fork, tags a fork release, updates fork
  version surfaces, or measures upstream releases.
metadata:
  aihub.tags: '["decision:ADR-0011","effective:2026-09-06","route:both"]'
capsule_summary: |
  A managed fork never invents a version ahead of its upstream. The fork
  version is a PEP 440 local version of the current measured upstream
  release — `<upstream>+dc.N` for Python, `<upstream>-fc.N` where the
  ecosystem uses that form — with N incremented per fork release and reset to
  1 when upstream publishes a new version. The upstream version is measured
  from the upstream source (release API, tags, or manifest) before every
  release, never recalled from memory. Version surfaces that disagree with
  the measured truth are defects fixed at their owner the same change, and
  any test constant or doc that repeats an invented version is corrected with
  them.
---

# Fork version locality

Every fork the repository declares as managed versions itself against its upstream as a
local version, and a fork added later is covered the moment it is declared. The
upstream release is measured, not remembered: query the upstream release API, tags, or
manifest immediately before cutting a fork release.

## Law

1. The fork base version equals the latest published upstream release at the moment of
   the fork release. It is never a version that only exists on an upstream branch, PR,
   or draft.
2. The fork suffix is a monotonic local identifier: `+dc.N` (PEP 440 local version) for
   Python distributions, `-fc.N` where the ecosystem's tooling uses that form. Each fork
   release increments N by one.
3. When upstream publishes a new release, the fork rebases onto it and the suffix
   restarts at 1.
4. Version surfaces stay consistent (project manifest, package metadata, lockfile,
   installer manifest) or are corrected in the same change.
5. Test constants and documentation never repeat an invented version; they use the
   current fork scheme or an explicitly fake placeholder.

## Violations this rule exterminates

A changelog entry or tag claiming a release upstream never published; a fork version
ahead of upstream's latest; a test asserting a stale invented string; a version recalled
from memory without measuring upstream. Each is fixed at its owner immediately, with the
measured evidence recorded in the fix.

## Precedent

2026-09-06: the code-review-graph fork changelog claimed `2.4.0+dc1` while upstream's
latest release was `v2.3.8` and the fork tree was `2.3.8+dc.3` (evidence: GitHub release
API, upstream `pyproject.toml`, fork `pyproject.toml`). Corrected on lane
`dc-autopilot-docs`.
