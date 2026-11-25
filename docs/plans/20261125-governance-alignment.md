# Governance alignment — agents ↔ FLEXT ↔ ai-hub (2026-11-25)

Operator decision 2026-11-25: the delivery cycle of FLEXT #2791 (`4bf12d062d`) prevails;
the Kilo sessions' 2026-11-24 17:28 cycle (separate gen/fix/fmt, `check CI=Y`) is superseded.
Canonical text: [delivery doctrine](../../rules/workflow/agent-delivery-doctrine.md#the-delivery-cycle).

| Surface | State measured 2026-11-25 | Owner of the gap |
|---|---|---|
| FLEXT verbs | `setup upg mod check tests tests-full`; default `check` does not converge yet | flext-infra `feat/check-converges` |
| FLEXT workspace | root Makefile pinned before #2791; AGENTS.md lists gen/fix/fmt | FLEXT workspace |
| ai-hub | Makefile generated before #2791; delivers only `law.prelude`; pins agents `@dev`; OpenMoat cohort off (`5c79f0b27`) | ai-hub |
| agents | own verbs (`gen fix fmt check test ci`) unchanged; rules aligned in this change | — |
| Trackers | `bd` from flext/ai-hub resolves to the agents store | ai-hub tracker connections |

Done in agents: single cycle source, adoption by `cherry-pick -x`, duplicated rules linked,
ADR-0040 amended, ADR-0038 count, superseded ADR tags, tool-surface rule, OpenMoat runbook.
