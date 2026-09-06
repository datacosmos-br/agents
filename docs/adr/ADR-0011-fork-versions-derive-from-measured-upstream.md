# ADR-0011: Fork versions derive from measured upstream releases

Date: 2026-09-06
Status: Accepted
Rule: `rules/git/fork-version-locality.md`

## Context

Managed forks carry deployment deltas over external upstream products. On
2026-09-06 the code-review-graph fork changelog claimed a `2.4.0+dc1`
release that upstream never published: upstream's latest release was
`v2.3.8` and the fork tree was `2.3.8+dc.3` (evidence: upstream release API,
upstream `pyproject.toml`, fork `pyproject.toml`). An invented version breaks
upgrade planning, provenance audits, and host-tools pinning, and it can leak
into tests and documentation as if it were real.

## Decision

A managed fork never invents a version ahead of its upstream. The fork
version is a local version of the current **measured** upstream release:

- Python distributions use PEP 440 local versions: `<upstream>+dc.N`.
- Ecosystems that cannot express local versions use `<upstream>-fc.N`
  (the gascity mise install pattern).
- `N` increments once per fork release and restarts at `1` when upstream
  publishes a new release.
- The upstream version is measured from the upstream source (release API,
  tags, or manifest) immediately before every fork release; it is never
  recalled from memory.
- Every version surface (manifest, package metadata, lockfile, installer
  manifest) agrees with the measured truth or is corrected in the same
  change. Test constants and documentation never repeat an invented
  version.

## Consequences

- Release tooling and audits can derive the expected fork version from the
  upstream release plus local suffix without trusting the fork's claim.
- A fork version greater than or equal to a not-yet-released upstream
  version is a defect with a defined fix: measure, correct every surface,
  and record the evidence.
- Existing compliant patterns (gascity `1.4.1-fc1`, `1.4.1-fc2` over
  upstream `v1.4.1`) are the model; the code-review-graph correction on
  lane `dc-autopilot-docs` is the precedent recorded in the rule.
