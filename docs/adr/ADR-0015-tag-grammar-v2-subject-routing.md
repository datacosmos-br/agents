# ADR-0015: Tag grammar v2 — subject routing and versioned managed projections

Date: 2026-09-07 Status: Accepted Amends: ADR-0002 (validated tag namespaces) Rule:
`rules/coordination/distribution-routing.md`

## Context

Measured on 2026-09-07 against the live catalog and the AI Hub projection path:

- `policy:` alone is 673 tags — 40% of all skill tags — with zero machine consumers;
  `provenance:agents-owned` and `updates:manual` are constants on all 105 skills;
  `role:`, command `intent:`/`risk:`, and the long category subject tags (`tool:`,
  `technology:`, `framework:`, `domain:`) have no consumer: the recursive path already
  owns category identity (ADR-0002).
- The project selector (`activation:`/`detect:`) is orphaned: its consumer chain has no
  live callers, while three uncoordinated writers fill provider homes and project trees.
  Five homes hold five different realities (70/55/72/53/53 copies of one 105-skill
  catalog), not one file carries the managed marker, 26 opt-in skills are
  blanket-projected into every home, project-only skills sit in personal homes, and a
  flext detection rule leaked into another project's projection state.
- The operator directive: subject tags must route (python skills to python projects,
  pydantic to python projects with pydantic, flext to flext projects), nothing may be
  routed everywhere by default, and every projected artifact must be detectably managed
  with its version bound to the `agents-governance` package version.

## Decision

1. **Grammar v2 namespaces.** Skill tags are exactly: `route:` (personal / project /
   both), `usage:` (waza budget class), `activation:` + `detect:` (conditional
   subjects), lineage (`decision:`, `effective:`, optional `supersedes:`), and short
   subject tags (`python`, `go`, `pydantic`, `flext`, `react`, `mcp`, …) paired with
   detector values `dependency:<eco>:<pkg>`, `marker:<path>`, `selected-tag:<tag>`,
   `owned-glob:<glob>`. Profiles keep `mode:` (and their activation/detect coupling).
   Dropped from the grammar and deleted from every record: `policy:`, `provenance:`,
   `updates:`, `role:`, command `intent:`/`risk:`, `lens:`, and the long category
   subject forms. A project that needs the dropped semantics reads law from rules and
   capsules, not from decorative tags.
2. **Routing authority.** Homes receive `personal` and `both` skills minus opt-in.
   Projects receive `project` and `both` skills whose subject detectors match the
   project profile; a conditional skill with no matching detector is never projected
   there. Opt-in skills project nowhere automatically. Blanket projection of conditional
   skills is a defect.
3. **Versioned managed projections.** Every projected artifact carries machine-readable
   ownership in its frontmatter (`managed-by` naming the publishing distribution) plus
   the `agents-governance` version that produced it. Canonical sources carry no marker:
   the projector injects it at render time. A projected file whose version differs from
   the installed bundle version is stale and is swept by the planner on the next
   publish. Retirement reach is explicit: `retire:` globs in the consumer surface config
   cover pre-marker residue, renamed slugs, and unmanaged vendor copies.
4. **Rename lineage.** Slug renames travel with `supersedes:skill:<old>` (rules: their
   path identity), and the old slug appears in the consumer retire globs of the same
   release. The catalog validator enforces that a superseded slug is absent from the
   tree and present in git history.

## Consequences

- Deleting the decorative namespaces is a breaking grammar change: `agents-governance`
  bumps to 0.4.0 and consumers regenerate, never tolerate, the old forms.
- The subject/detector model becomes the live project-routing path; leaving it unwired
  while conditional categories exist is a defect against this ADR.
- Homes converge to one reality: managed, versioned, sweepable. A projected file without
  a marker is by definition residue to retire.
