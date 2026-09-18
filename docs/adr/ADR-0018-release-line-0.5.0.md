# ADR-0018 — Release line 0.5.0: behavioral conscience and delivery contract

**Status:** Accepted **Date:** 2026-09-10 **Scope:** `pyproject.toml`, catalog tag
grammar, release line authority

## Context

The fleet landing corrections (`rules/coordination/fleet-landing-corrections`) fix
version-line authority to the declared tag/release timeline: read the tags before
bumping, follow the live declared line. The bundle measured on 2026-09-10 (commit
c4403561, `GovernanceBundle.load()` exit 0):

- Tag grammar v2 (ADR-0015) is fully conformant across the catalog: 128/128 skills carry
  `usage:` classes (78 on-demand, 50 router); 14/14 commands and 66/66 agents carry
  approval tags; 66/66 rules carry `effective:` ordering. No artifact carries a tag
  outside the closed namespace set.
- The remaining enforcement gap is code, not tags: agent approval tags are present on
  artifacts but not yet validated by `agent_profiles` / `_approved_artifacts` (assigned
  to ADR-0019).
- The session capsule measured 9,764 / 10,000 characters (prelude + 9 bootstrap rule
  summaries + skills router index), inside the hook ceiling with 236 characters
  headroom.

## Decision

1. The distribution version line advances `0.4.0` → `0.5.0` with this cycle, carrying
   ADR-0017 (behavioral conscience) and ADR-0019/0020 (delivery contract, advance
   command) in the same release. One release, one line — no intermediate consumable
   versions.
2. Tag grammar is declared closed as measured: no further tag reform is scheduled;
   future tag changes are amendments through new ADRs with `supersedes:` lineage.
3. Consumers (AI Hub runtime) target `agents-governance>=0.5.0`.

## Consequences

- The artifact gate proves `__version__ == distribution_version == 0.5.0` on every
  `make check`.
- Validation gaps are tracked as ADR-0019 scope, not as tag debt.
