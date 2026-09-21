# Fleet-Wide Beads Reorganization & Cleanup Plan

**Date**: 2026-09-21
**Author**: agents dedicated session
**Scope**: All 4 bead stores (agents, algar-oud-mig, ai-hub, flext-infra)
**Tracking bead**: ag-t8r3 (P1, claimed)

## Census (2026-09-21)

| Store | Total beads | Non-closed | Open | In-progress | Blocked | Deferred | Unassigned |
|---|---|---|---|---|---|---|---|
| agents | 258 | 37 | 18 | 15 | 1 | 3 | 23 |
| algar-oud-mig | 112 | 1 | 0 | 1 | 0 | 0 | 0 |
| ai-hub | 2826 | 254 | 140 | 107 | 7 | 0 | 46 |
| flext-infra | 3470 | 478 | 331 | 142 | 1 | 7 | 339 |
| **Total** | **6666** | **770** | **489** | **265** | **9** | **10** | **408** |

## Categories

| Category | Count | Stores | Description |
|---|---|---|---|
| gate-grind | 92 | agents 7, ai-hub 25, flext 60 | namespace, types, duplication, lint |
| deploy/runtime | 55 | agents 10, ai-hub 31, flext 14 | hooks, timers, activation |
| distribution | 25 | agents 1, ai-hub 9, flext 15 | projection, surface |
| bug/fix | 25 | agents 2, ai-hub 9, flext 14 | bugs and hotfixes |
| epic/child | 24 | ai-hub 13, flext 11 | structural hierarchy needed |
| types | 37 | agents 1, ai-hub 9, flext 27 | pyrefly, mypy, pyright |
| duplication | 18 | ai-hub 7, flext 11 | jscpd, dedup |
| other | 491 | all stores | needs triage |

## Protocol de execução (por item)

Cada bead é processada individualmente com:

1. **Assessment**: obsoleta? redundante? reassign? structural update?
2. **Claim cleanup**: remover claims obsoletos/incorretos
3. **Traceability**: linkar PRs e branches remotas à bead
4. **Hierarchical alignment**: mapear Tasks/Bugs ao Epic pai correto
5. **Protocol compliance**: categorizar Bugfixes/Hotfixes por protocolo (fora do epic hierarchy quando requerido)
6. **Pruning**: fechar beads 100% superadas (verificado contra a tip da branch de integração)

## Prioridades

### P0 — Limpeza imediata
- Fechar beads 100% superadas (prova de ancestralidade ou conteúdo absorvido)
- Remover claims de sessões suspensas/encerradas
- Deduplicar beads que descrevem o mesmo trabalho

### P1 — Reassignment + alignment
- Reassign unassigned P0/P1 para lanes ativas
- Mapear Tasks/Bugs aos Epics pais corretos
- Garantir que cada Epic tem seus children corretos

### P2 — Grind consolidation
- Consolidar gate-grind beads que se sobrepõem
- Agrupar bugs/hotfixes por domínio
- Consolidar duplication beads por repositório

### P3 — Bulk triage
- Processar as 491 beads "other" em batches de 50
- Cada batch: classificar, reassignar ou fechar

## Critério de conclusão
- Toda bead non-closed tem: assignee, epic pai (onde aplicável), PR link, categoria
- Zero beads referenciando branches ou PRs inexistentes
- Zero beads duplicando outras beads
- Todas as beads stale/superadas fechadas com evidência
