# Session-infrastructure plan closure — 2026-09-27

The operator-approved session-infrastructure plan (skills, commands, rules,
agents, docs so future sessions inherit working guidance) is complete. Every
slice below names its canonical home **on `dev`** as merged today; a slice was
accepted only where the fleet convention already owned an equivalent surface —
duplicating it was rejected under the SSOT law.

| Plan slice | Canonical home on dev | Vehicle |
| --- | --- | --- |
| Skills: session-preflight | `commands/governance/session-preflight.md` (the declared startup contract) | pre-existing command; `session-recover`/`session-startup` complete the family |
| Skills: lane-adoption | `skills/tool/lane-landing-cycle/` | pre-existing skill covering the full lane cycle (claim → gates → PR → merge → retirement) |
| Skills: coordination-protocol | `skills/tool/gc-change/` + `rules/coordination/tracker-curation-routing.md` | pre-existing Gas City change lifecycle + the curation-routing rule |
| Skills: runtime-validation | `skills/domain/runtime-heal/` + `docs/runbook-runtime.md` | the skill owns recovery; the runbook records the measured proof chains (NEW, PR #188) |
| Rules: session execution laws | `docs/rules/session-execution-rules-20260927.md` + `docs/session-execution-laws-20260927.md` (laws 1–10) | laws 8–10 landed additively (PR #187) |
| Beads: dedup, close, retitle, heartbeat | tracker itself — 2026-09-27 sweep closed 4 shells with proof, refreshed 6 with measured evidence; the 1h abandonment rule is enforced by the coordinator (`claude-coord-docs`) | recorded on `aihub-l42it`, `aihub-k0uqi` |
| Agents: coordinator | `agents/agent-wide/tracker-curator.md` (curation owner, abandon sweep, disposition census) + `agents/agent-wide/session-scribe.md` | pre-existing profiles; `agents/project-wide/session-documenter.md` carries the recording contract |
| Docs: retro/critique | `docs/retro-20260927-zcode-execution.md` | landed with PR #182; factual corrections folded into the dev merge |
| Docs: runtime runbook | `docs/runbook-runtime.md` | NEW (PR #188) |

## Gate cures carried by the same documentation work

The documentation landing also cured three red gates found on `dev` and one
numbering collision, all reproduced before curing:

1. `require-basic-usage-fixture` ×2 — `evals/runtime-heal/` and
   `evals/lane-landing-cycle/` gained physical scenario fixtures from the
   measured 2026-09-27 recovery and lane cycle (PR #188).
2. `waza spec verify` runtime-heal coverage 0/1 — the ADR-0030 session's
   description edit had left no task exercising it; aligned (PR #188).
3. ADR-0032 carried committed conflict markers (MD092) — resolved in the
   ai-hub PR #917.
4. The agents `ADR-0028` collision — environment truth renumbered to ADR-0030;
   the coordinated census duplicate (agents ADR-0031) retired with citations
   retargeted (merged via PR #182 and the dev-merge follow-ups).

## Disposition

No plan task remains open. Runtime bring-up items that surfaced during the
work are not documentation debts: they are tracked where they belong
(`aihub-6k1.27` pipeline/CCS, `aihub-k0uqi` closure conditions,
`aihub-kvx0x.7` hooks, `aihub-be097` Mimosa findings) with the owning sessions
escalated through gc-mail (`gc-wisp-bousqy`, `gc-wisp-g9xg88`,
`gc-wisp-bwal07`).
