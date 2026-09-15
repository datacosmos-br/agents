---
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","route:project"]'
---

# Beads canonical epics

## Epic assignment rules

1. **bugfix/hotfix/bug beads: NO epic parent, ever.**
   If a `bugfix`, `hotfix`, or `bug` bead has a parent epic, it is a governance
   violation. The `classify` mode reports it for removal; operator confirms on
   `--apply`.

2. **task/feature beads: consolidated under FEW canonical epics.**
   Prefer the exact epic family from the newest plan (§0.4/§0.7 of the canonical
   plan, or latest ADR) over shallow or intermediate parents. One canonical
   survivor per concept; others close `SUPERSEDED` naming the survivor in
   `--reason`.

## Closure law (three legal reasons only)

A bead may be closed ONLY with one of these reasons, each requiring evidence:

- **SUPERSEDED** — canonical owner named in the plan absorbs the scope.
  Evidence: reference to surviving bead ID + plan/ADR section.
- **OBSOLETE** — scope/explicit intent disappeared with proof.
  Evidence: `gh pr view` showing merged/closed without merge, branch deleted,
  feature flag removed, config deleted.
- **DONE** — measurable execution proved by command, working directory, exit
  code, and decisive output.
  Evidence: pasted cmd/cwd/exit/output; `bd show` confirms integration.

**LEGITIMATE** = comment both beads with cross-reference, DO NOT close either.

## Mandatory pre-close checks

1. `bd show <id>` BEFORE any mutation — measure by real evidence, never accept
   bead text at face value.
2. Zero parent closed with child pending — check `↳` in `bd show` of parent
   before close; re-home child by child (`bd update <child> --parent <owner>`),
   no batch.
3. Cap 20 closes per batch (`bd batch`); re-run dedup gate + `bd doctor
   --check=validate` + `bd orphans` after each batch.
4. Never mutate beads of ACTIVE third-party lanes (from §0.7 + claims ≤24h).
5. Every dedup and duplicate scan runs exhaustively — `bd find-duplicates
   --limit 0`, never the default limit. A partial scan misses pairs: its
   clean result is not evidence and its hit list is not the full set.

## Family consolidation

- One canonical survivor per concept family (defined by newest plan/ADR).
- Survivors remain open; others close `SUPERSEDED` naming the survivor.
- Preference: units of lessons/hygiene/infraletters close `DONE` if integration
  demonstrable by grep on target; otherwise keep with note but DO NOT close falsely.
- Evidence of absorption recorded in coordinator bead + plan update.

(End of file)
