# ADR-0031 — Census validity requires the locked runtime

**Status:** Accepted **Date:** 2026-09-27
**Provenance note:** coordinated authorship. The rule
`rules/runtime/locked-runtime-census.md` cites this decision; its owning
session authored the rule and the underlying evidence. This record was written
by the ai-hub surfaced-inventory session during the 2026-09-27 governance
alignment so the bundle audit could resolve the citation; the owning session
retains custody and may emend in place.

## Context

The flext-infra zero-red campaign (PR #947, 2026-09-27) carried an
87-finding census decomposition plan that proved to be an artifact of an
installed scanner two generations behind the lock (`flext_core` `fe50ef07f`
installed versus `3efdfd9ba6` resolved in `uv.lock`). After the declared
upgrade verb ran and the base was re-aligned, the same gate reported zero.
Planning decomposition from a stale-runtime map would have spent days
repairing findings that did not exist.

## Decision

1. A census, smell map, or enforcement finding is evidence only when the
   executing runtime equals the lock resolution. For a Git dependency this is
   `vcs_info.commit_id` in the installed distribution's `direct_url.json`
   versus the `#<commit>` fragment resolved in `uv.lock`.
2. On mismatch the map is void: sync through the repository's declared upgrade
   verb, recompute, and only then plan. A debt map measured against a stale
   runtime is retired, not repaired.
3. A record of census state travels with three facts — findings count,
   executing scanner's commit, lock's resolved commit. A record missing one is
   not evidence of debt.
4. Decomposition planned from a pre-sync map must not execute until
   re-measurement reproduces the finding on the locked runtime.

## Consequences

- `rules/runtime/locked-runtime-census.md` is the operative rule; this record
  is its approval lineage.
- Census workflows gain a lock-verification preflight before any measuring
  effect.
