---
description:
  Tag grammar v2 and distribution routing — which tags exist, where skills may project,
  and the versioned managed marker that makes every projection sweepable.
metadata:
  aihub.tags: '["decision:ADR-0015","effective:2026-10-28","route:both"]'
capsule_summary: |
  Skill tags are exactly route, usage, activation/detect, lineage
  (decision/effective/supersedes), and short subject tags wired to detectors;
  decorative namespaces (policy, provenance, updates, role, intent, risk,
  long category forms) are deleted everywhere. Homes take personal+both minus
  opt-in; projects take project+both only when the skill's subject detector
  matches the project profile; opt-in projects nowhere automatically. Every
  projection carries a managed-by marker with the publishing bundle version.
  Drift identifies reconciliation candidates; retirement requires declared scope
  and authenticated current ownership. Preserve foreign content. Renames carry
  supersedes lineage and consumer retire globs in the same release.
---

# Distribution routing and tag grammar v2

One grammar, one routing authority, one sweepable reality.

## Law

1. **Closed tag set.** The namespaces are `route:`, `usage:`, `activation:`, `detect:`,
   `decision:`, `effective:`, `supersedes:`, `mode:` (profiles), and short subject tags.
   Anything else in `aihub.tags` fails validation. Decorative tags do not exist: law
   lives in rules and capsules.
2. **Subjects route, nothing blankets.** A conditional skill names its subjects
   (`python`, `pydantic`, `flext`, `go`, …) with detectors (`dependency:<eco>:<pkg>`,
   `marker:<path>`, `selected-tag:<tag>`, `owned-glob:<glob>`). Projection into a
   project requires a detector hit against the project profile; absence of a hit means
   absence of the skill. Homes receive personal and both skills minus opt-in; opt-in
   skills move only by explicit operator selection.
3. **Managed and versioned ownership.** Projections carry the managed-by marker and the
   publishing bundle version in frontmatter; sources never do. Missing markers and
   foreign or older versions identify reconciliation candidates, not deletion
   authority. Retire only declared artifacts whose current ownership is authenticated;
   preserve foreign/manual content and fail before effects on ownership conflicts.
   Consumer surfaces declare `retire_globs` in `config/workspaces.yaml` per workspace
   for legacy, renamed, and vendor artifacts so publication reconciles authenticated
   historical residue. Each `retire_globs` entry must be a relative,
   repository-local glob pattern (no absolute paths, no `..` traversal); the projection
   tool enforces this schema at load time. Globs bound discovery, not ownership.
   Minimum changes and byte-identical no-ops follow
   [atomic-effects](../runtime/atomic-effects.md) and
   ADR-0022's 2026-10-28 minimum authenticated publication amendment.
4. **Renames are lineage events.** A slug rename ships `supersedes:` against the old
   identity, rewires `extends:`, bootstrap, guarantees, and capsule references in the
   same change, and retires the old slug from consumers in the same release.

## Violations

Decorative tags returning through any writer; conditional skills projected without a
detector hit; newly published managed artifacts missing ownership metadata;
unauthenticated retirement; a rename without supersedes or authenticated consumer
retirement.
