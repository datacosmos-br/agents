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

## Registro de execução — rodada 2026-09-21 (noite)

Validação item-a-item contra runtime real (grep/probe no código da tip + gates + scans):

**Fechadas com evidência (10)**:
- agents: `ag-vblj.5` (rota github mise-provisionada, binário em runtime), `ag-lw57.10` (staging dry-run/output implementado), `ag-lw57.5` (artefatos aihub exterminados dos homes), `ag-lw57.4` (one-release: recovery.conf ausente, units em runtime/current), `ag-bwqu` (_noop_acceptance 0 hits; AiHubNativeDeploymentAcceptance pousada)
- ai-hub: `aihub-aooib` (AGENTS.md real no release instalado, 19967 bytes), `aihub-zj4l3` (check 20/20 failed=0; vermelho 22:04 era corrida com merge 202e603c5), `aihub-agfq7.11` (letras d/e/h/r/x vivas em flext_core; mypy/pyright 0), `aihub-agfq7.10` (AiHubSettingsSources(FlextSettings) pousado; runtime-census 0), `aihub-6o75i` (rota generate-configs wired → services/generate_configs.py)

**Evidência atualizada em abertas (5)**: `ag-lw57.8` (resta 1 fail: test_concurrent_fragment_creation_is_never_overwritten), `ag-vblj.1` (censo 338 linhas de import direto), `ag-lw57.7` (references/ existe mas vazio), `aihub-73b244ef` (bloqueio sistêmico: mint de credencial falha em todo run pull_request), `aihub-636vd` (esta rodada)

**Descobertas estruturais (novas beads flext)**:
- `flext-yj3s0` (P1): gerador emite `flext-sh/flext` hardcoded no docs/index.md (`docs_render.py:220 _LINK_PREFIX_DOCS_INDEX = c.Infra.GITHUB_REPO_URL`) — termo que a própria auditoria proíbe fora do org flext-sh; fix = derivar do mapa governado `make.docs.github_repos`. Bloqueia o vermelho final do algar (14º issue de docs).
- `flext-zxdl5` (P1): censo jscpd — 17 clones em `codegen/_conform/` (landlords misc.py/plan.py; consumidores beads_routes, docs_ownership, existing_plan, file_plans). algar/ai-hub/agents PASS 0 no mesmo gate.

**Diagnóstico publicado**: PR #836 ai-hub (release dev→main) — dois bloqueios: mint de credencial em contexto PR (Sprint-G) + skew de pins flext entre main e dev no merge-ref (gen ImportError `mp`).

**Estado de gates na rodada**: ai-hub check interno 20/20 failed=0 (único vermelho = post-check de homes = deploy pendente, cadeia aihub-oig6s); algar gen/docs em fixed-point com cadeia I001+13/14 docs fixes no worktree (14º aguarda flext-yj3s0); algar/ai-hub/agents duplication PASS 0.

**Segurança (scan Mimosa deep, selado)**: algar 0 findings (249 pacotes, seal 216b458f), ai-hub 0 findings (406 pacotes, seal 87a3f2b2); programa semgrep flext-p57t COMPLETO (0 abertas, PR #793 mergeada). SonarQube 2wjm.* (P2) e flext-z89p (P1) permanecem como programa contínuo.

**Hierarquia verificada**: clusters B/C/D/E/G (aihub-4b4rr et al) corretamente parentados ao épico aihub-z82dg com dependências reais — sem órfãos. Semgrep/SonarQube fora da hierarquia de épicos (protocolo bugfix/hotfix respeitado).
