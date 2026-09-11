# Governance Runtime Program — Plano de Ação e Status (ag-zrh; esteira ag-q4w1 · CRG ag-nq7q · piloto ag-m9lu)

Lane: `feat/governance-runtime-program` (repo `agents`, integração `dev`).
Autoridade: operador (monopólio pleno dos temas, sessão 2026-09-10).
Leis donas: `distribution-routing.md` (ADR-0015), `runtime-is-reality.md`,
`session-governance.md`, `capability-intake.md`.

## Objetivo

Fazer as leis valerem em runtime: SSOT/DRY/YAGNI reais no catálogo
(skills/rules/commands/agents), distribuição convergente por projeções
gerenciadas, prova produtiva em sessão real. Gates são insumo; sonda de
runtime é o único veredito.

## Status executado (evidência: comando, exit, output decisivo)

| # | Fase | Status | Evidência decisiva |
|---|------|--------|--------------------|
| 0 | Base limpa: lane reval250909 pousada | ✅ DONE | PR #133 merge `ab27a954` (--no-ff, operator-authorized); `make ci` exit 0 (4 passed, testmon integrity=ok); pós-merge `make gen` ×2 fixed point + `make check` exit 0; lanes `feat/reval250909-adoption` e `wip/beads-governance-reval250909` aposentadas local+remoto após `merge-base --is-ancestor` exit 0 |
| 0 | Tracker reval250909 | ✅ DONE | Fechados com 4 fontes: ag-645 (`make help` lista gen/build), ag-s8r (conteúdo superseded provado), ag-aq8.2 (prova pós-merge), ag-9qg (jscpd 5.1.2 correto + `make duplication` exit 0, 0 clones), ag-aq8.1 (`GovernanceBundle.load` 65 agents + audit zero raise). ag-1b5/ag-blh: notas de dono ai-hub, sem falso fechamento |
| 1 | Épico criado | ✅ DONE | ag-zrh + filhos ag-zrh.1..4 com cadeia de dependências |
| 2 | **F0 — inventário de violação (ag-zrh.1)** | ✅ DONE | 4 varreduras paralelas read-only + observação de runtime do operador. Causa raiz provada: `~/.agents` é symlink → checkout vivo (por isso só o Kilo vê os agents). Homes: 0/current (opencode 43 stale + 10 identidades aposentadas vivas + 1 foreign + 53 tags decorativas; claude 45 stale + 10 + 14 foreign incl. `python-production`; `.claude/agents` 8 stale + 57 faltando; `selection.agents: []` nunca distribuiu). Comandos: 14/14 frontmatter ok; `ghi-list`/`pr-list` shadows estrangeiras invertem contrato (pr-list esconde CHANGES_REQUESTED). Hardcode HIGH: `rules/flext/beads-continuity.md` → `~/wip-beads.sh` + caminho de projeção. Contrato de contagem quebrado: 121/56/64 vs runtime 128/63/65 |
| 3 | **F2 — corte temático (ag-zrh.3)** | 🔶 código completo; fechamento bloqueado por ag-zrh.2 | Absorção python-production em `rules/python.md` + `config-settings-ssot.md` (commit `0f7084fd`); cópias estrangeiras python-production/ghi-list/pr-list aposentadas no mesmo corte (resíduo zero, projeções canônicas de command intactas); wip-beads processor adotado no repo (`scripts/wip-beads.sh` + `bd_json_to_csv.py` provados em runtime); inviolable-rules colapsada a router + eval reescrito no mesmo corte; flext-boundary adotado como perfil project-wide (66 agents, audit limpo); de-provider (chief-of-staff, 4 agents CLAUDE.md→neutro, menções Kilo); caminhos quebrados corrigidos (opencode-handoff); SHAs do mcp-builder → `references/sdk-docs.md` (dono único); citações de dono nos skills com invariantes; make-check → project-wide/shell; contrato de contagem 66/63/128 em AGENTS.md. Gates: `gen` ×2 fixed point, `audit` exit 0 (128/14/66/63), `waza` 128/128 suítes, `check` exit 0. Commits `d68e2d8a`, `56fcebdc`, `0f7084fd` |
| 4 | **F1 — distribuição pelo dono (ag-zrh.2)** | 🔶 EM ANDAMENTO — cadeia ai-hub 4 defeitos radicais, 3 corrigidos | (1) Packaging: wheel sem a superfície de assets → **CORRIGIDO** (PR #734 merge `89294582e` no dev do ai-hub; build verde com 394 arquivos; lane aposentada com ancestor proof). (2) Renderer opencode: gate velho home-relative sobre campo morto `socket_path_json` → **CORRIGIDO** na lane `fix/opencode-renderer-stale-socket-gate` (commit `625601fb`; provado: 2559 diagnósticos pré-existentes idênticos com/sem o diff). (3) Registry poluído por teste: 8 projetos pytest (checkout-0..7) no `workspaces.json` de produção → **PODRADOS** + bug bead criado (isolamento de teste do workspace-discovery). Credenciais: forma canônica descoberta — `systemd-run --user -p LoadCredentialEncrypted=...` (sem exportar segredo). (4) Classificação de projetos: **CORRIGIDO POR DETECÇÃO** (origin owner ∈ owners → internal; fora → third_party_fork; sem registro por-repo, a pedido do operador). **Bloqueiro atual**: composição de agents atinge arquivos de instrução provider não-gerenciados (ex.: `CLAUDE.md` do steampipe) — desenho fechado: absorver o conteúdo local para o bloco local do AGENTS.md dentro da MESMA transação de plano; implementação em curso |
| 5 | model-pipeline daemon | ⚠️ lane de outro ator | Serviço failed; 2 intents órfãos `submitted` removidos com snapshots de evidência em `~/tmp/opencode/`; a falha restante vive na lane ativa `ai-hub-wt/model-pipeline-v3` — não invadir; deploy de skills não depende mais dela |
| 5a | P0 CRG sync (ag-nq7q) | ⏳ PENDENTE | drift medido: `ai-hub ai-hub-sync-crg-workspaces --check` exit 2 (10+ workspaces: steampipe, worker-vllm, ardupilot, invest, typeshed…) |
| 5b | Esteira global (ag-q4w1) | ⏳ PROPOSTA para aprovação | seção "PROPOSTA" abaixo; mutação só por SSOT codegen + `make gen APPLY=Y`; `make mod` agrega 48+package rules |
| 5c | Piloto homologação (ag-m9lu) | ⏳ PROPOSTA para aprovação | 7 critérios measuráveis → pouso ai-hub dev |
| 6 | **F3 — prova produtiva (ag-zrh.4)** | ⏳ PENDENTE de F1 | Sessão opencode nova real: skill dona carrega texto canônico na versão atual, `python-production` inexistente, zero dedução |

## Fase 1 em execução — Verde obrigatório ai-hub (lane fix/green-baseline)

Worktree dedicada: `~/ai-hub-wt/green-baseline` (branch `fix/green-baseline`,
pushed; base `fix/current-pointer-transport` com 4 commits de walker/pointer +
composed surfaces). Estado medido (`make check APPLY=Y`, pós-commit `ea29280b`):

- Baseline: 2564 → **atual: 2467** (lint 42, pyrefly 146, mypy 16, pyright 40,
  silent-failure 40, markdown 2, loc-cap 9, boundary 2, tier-whitelist 1,
  namespace 1100, codemod 1033, duplication 36) — pós `d590d1cfb` (docs, permission, DI). Nota: lint/pyrefly/
  mypy/pyright subiram porque código novo (protocolos + helpers aninhados)
  entrou no raio dos gates; namespace caiu 1122→1100 e codemod 1044→1033.
- Corrigido acumulado (commits `151278c2e`..`ea29280b`):
  - lint tail: os-sep-split → `PurePosixPath.parts`, undefined names em tests
    quebrados commitados (`ForgeGovernanceGhDouble` rename, imports r/m/Path,
    S105 stub, magic 409→`httpx.codes.CONFLICT`, docstring `__init__`,
    too-many-statements no walker via `_walk_pointer_segments`);
  - `tests/utilities.py`: 2 anotações `dict` → `t.Dict` (NS-CONTRACT-002);
  - reconstruct de `test_aihub_forge_governance_check_context` (7 duplicados
    módulo removidos, 5 testes mortos aninhados restaurados como métodos
    reais da classe, 4 helpers perdidos no merge do ator restaurados);
  - namespace −22: helpers top-level aninhados em classes em 6 test files
    (`workspace_git`, `workspace_reconcile`, `workspace_state_governance`,
    `workspace_state_ledger_demote`, `write_lock`, `zai_stdio_child_env`);
  - protocolo novo `p.AiHub.ForgeRouting` (`_protocols/forge.py`) + protocolo
    `GovernanceBundle` estendido com `snapshot()`; `_validate_agent_law_surface/
    base.py` e bases de forge sem reverse import de serviço concreto.
- `make mod APPLY=Y`: 197 achados detection-only (0 actionable) exigem reparo
  por dono — breakdown: test-no-mock-or-patch-identifiers 102,
  ban-test-doubles 35, hook-deploy-exception-group 12, retired-config-* 16,
  test-import-alias-mixed-root-facade 7, recursive-type-alias 6
  (`_models/learning.py:11`), ban-pass-through-wrapper 1 (`cli.py:118`),
  outros 19.
- Restante namespace (1100): NS-STRUCT-003/004 top-level functions em ~9 test
  files + `scripts/` + `_credential_source.py` + `_models/`; facade MRO de
  `tests/utilities.py` (NS-STRUCT-003); reverse imports em `tests/utilities.py`
  (NS-IMPORT-001/002) e `services/_forge_governance|_forge_operations/base.py`
  (consolidar para `p.AiHub.ForgeRouting`); local aliases NS-IMPORT-001 em 2
  test files.
- Loop de continuação (próximas sessões): make fix → make mod → reparo por
  classe (namespace restante; codemod recursive-type-alias; eliminação de
  mock/patch nos 102; doubles aprovados nos 35; retired-config rewire nos 16;
  typing pyrefly/pyright via `t.*/p.*`) → `make check` exit 0 → `make test`
  verde (testmon) → PR + merge `--no-ff` no dev do ai-hub.

## Autocrítica (2026-09-11, pós-revisão do operador)

Defeitos cometidos e corrigidos nesta lane — cada um com lei violada e
correção de raiz executada:

1. **Código sem prova.** O protocolo `GovernanceBundle` foi estendido e
   `p.AiHub.GovernanceBundle.snapshot()` chamado dentro de `prelude()` sem
   rodar gate algum. Protocol não tem implementação: a chamada retornaria
   `None` e quebraria o validator em runtime. Lei violada: gates após cada
   passo material. Correção de raiz: base pura com fail-loud de composição,
   `AiHubAgentLawSurface.prelude()` compõe o bundle concreto no composition
   root (`validate_agent_law_surface.py`), protocolo revisto ao mínimo (YAGNI).
   Prova: `.venv/bin/python -c "…prelude()"` → `prelude ok: True`, marker
   `<!-- AIHUB-INVIOLABLE-LAW-PRELUDE -->` correto (exit 0).
2. **Contaminação estrutural de teste.** Reconstrução do
   `test_aihub_forge_governance_check_context` apagou helpers vivos e deixou
   código morto pós-return em `_plan` (arquivo permission), sem `nameWithOwner`
   no cenário do double → falha de identidade em `TestAdminPermissionGate`.
   Correção de raiz: cenário funde payload de permissões com linha de
   identidade (`nameWithOwner`), bloco morto removido. Prova: 6 passed no foco
   (`pytest …forge_governance_permission.py`, exit 0).
3. **Docs citando seletores aposentados.** 12 docs citavam `make … WHAT=…`
   que nenhum dono declara (fail-closed do doc-vs-Make contract). 2 falhas
   estavam em blocos de código sem crase e escaparam à primeira passada —
   redisciplina: rodar o gate após CADA onda, não ao final. Correção mecanica
   por dono: verbos selector-free (`check/test/gen/fix/mod/duplication/deps
   APPLY=Y`, `make help`) + CLI owners reais (`ai-hub validate-agents`,
   `validate-references`, `validate-mcp-routing`, `workspace-discovery --audit`);
   citação do único dono custom vivo restaurada (`make status WHAT=daemon`).
   Prova: docs_make_verbs 9 passed (exit 0), testmon 62 passed / 2 failed
   externos.
4. **Medição enganosa.** 2465→2492 durante a rodada anterior: código novo
   entrou no raio dos gates sem medição; namespace caiu mas o TOTAL subiu, e
   a narrativa só reportou a queda. Lei violada: verdade escopada. Correção:
   burn-down por CLASSE (namespace, codemod, pyrefly, …) é a métrica; total é
   secundário; toda adição de código roda `make fix → check → test` na hora.
5. **Dois RED externos no testmon (adopted, donos roteados):**
   `tests/e2e/test_aihub_deployed_services_match_declaration` — unidade
   deployed inativa nesta máquina (surface do ator paralelo / lane
   model-pipeline; não invadir — vê plano linha 5);
   `hook_rules_engine TestsOperatorBudget[git status && pytest -q]` — orçamento
   de operador no guard (dono: config de hooks; bead a abrir quando fechar a
   cadeia verde, com medição com/sem diff como prova de pré-existência).

## Regime de produção — definição de "green" e "done"

A lane só pousa num estado que sobreviva a produção. Tradução operacional:

- **Devolução implícita de falha proibida**: nenhum catch/normalize/fallback/
  retry silencioso (silent-failure gate zerado), primeiro traceback escapa.
- **Contratos tipados**: Pydantic-2 nas bordas; sem `Any`/`object`/`Optional`/
  `dict` em contratos públicos e DI (namespace/codemod zerados); tudo via
  `t.*/p.*`.
- **Owners únicos**: sem alias local, sem redeclaração, sem reverse runtime
  import (services só tocam services via `p.AiHub.*` injetado no composition
  root — padrão já provado em `validate_agent_law_surface.py`).
- **Testes = comportamento**: zero mock/patch identifiers (102 achados são
  tests contra doubles aprovados — migrar para `ForgeGovernanceGhDouble`,
  fixtures canônicas); testmon integrity sempre verde; zero-execução só como
  cache-hit tipado com accounting completo.
- **Docs vivos**: toda citação de comando em docs resolve a um handler
  declarado (docs_make_verbs verde) — provado nesta rodada.
- **Runtime como única verdade**: após merge, deploy atômico em modo recovery
  (`systemd-run --user -p LoadCredentialEncrypted=…`, segredo nunca em env),
  receipt assinado no home, setInterval de ativação probeável, e a sonda F3
  sessão-real conclui a cadeia.

## Sequência de execução (estabilizada e por que nesta ordem)

| # | Passo | Definition of done (comando + exit + output decisivo) |
|---|-------|--------|
| 1 | Absorver `origin/dev` na lane (`git merge --no-ff origin/dev`), rezolver conflitos favorando o mais novo, re-medir | merge exit 0; `make check` medido pós-merge |
| 2 | Corrigir `silent-failure` (40) no código de produção — primeiro traceback deve escapar | `make check` silent-failure=0 |
| 3 | Namespace classe-a-classe (1100): reverse imports → DI no composition root; locals → facade; top-level fns → métodos da classe do módulo | namespace=0 |
| 4 | Codemod: `recursive-type-alias` em `_models/*` → alias finito `t.JsonValue`/`t.JsonMapping`; `pass-through-wrapper` deletion; rewire consumers | codemod=0, `make mod` 0 actionable |
| 5 | Testes: migrar 102 mock/patch + 35 test-doubles para os doubles/fixes aprovados; 2 RED externos adotados (beads com evidência com/sem diff) | `make test` exit 0 |
| 6 | Pyrefly/pyright/mypy/lint/duplication/loc-cap restantes | all=0; `make check` exit 0 |
| 7 | PR + merge `--no-ff` no dev do ai-hub; rerun dos gates no SHA merged; deploy atômico recovery com credencial encriptada; receipt + probe de ativação | receipt no home; `ai-hub validate-agents` exit 0 |
| 8 | `agentsctl` (ag-7hz): transacional, idempotente, receipt-first, rollback documentado — `sync` único comando | `agentsctl sync` converte homes ≥0.5.0 |
| 9 | Sonda R1 então F3 (ag-zrh.4): sessão opencode real | marker/versão == bundle; zero markerless; `python-production` inexistente |
| 10 | Pouso no `agents` dev + fechamento ag-zrh.2/3/4 + épico com 4 fontes; lanes e worktrees aposentadas | merges `--no-ff`; `merge-base --is-ancestor` exit 0; resíduo zero |

## PROPOSTA para aprovação — Automação global da execução (make mod · ast-grep · make gen · CRG) e piloto de homologação

Pesquisa de donos executada nesta lane (evidência: `Makefile`, `sgconfig.yml`
gerado com header codegen, `ast-grep-rules/` 48+7 regras, binário de host
`~/.local/share/ai-hub/host-tools/current/bin/code-review-graph --help`,
`ai-hub ai-hub-sync-crg-workspaces --check`). Surrei de aplicação:

### 1. Estado medido hoje (produção real)

- **CRG está RED na máquina**: `ai-hub ai-hub-sync-crg-workspaces --check`
  → *policy drift* — steampipe, rpa/worker-vllm, ardupilot, invest,
  cosmos-legacy, typeshed e 4+ sem `.code-review-graphignore`/
  `languages.toml` registrados; `~/.code-review-graph/crg-watch.toml`
  desatualizado vs `config.AiHub.workspaces`. Grafo existente (`graph.db`,
  registry.json, watch daemons vivos) — infra pronta, projeção em drift.
- **ai-hub `make mod`**: agrega 2 fontes de regras (projeto `ast-grep-rules/`
  48 regras + package `flext_infra codemod`), relatório tipado em
  `.reports/refactor/mod-findings.json` (schema com
  actionable/detection_only/classification/range/text); 197 detection-only.
  Regras com `fix:` são auto-aplicáveis; sem `fix` exigem reparo por dono.
  `sgconfig.yml` e regras do projeto são **gerados** (header codegen) —
  mudanças fluem por `config/codegen.yaml` → `make gen APPLY=Y`.
- **agents `make mod`**: `ast-grep test --config sgconfig.yml --update-all`
  (7 regras universais de eval-suite) — regenera snapshots aprovados.
- **CRG CLI (hoje produtivo)**: `code-review-graph impact|query|search|rename|
  dead-code --json|large-functions|refactor|flows|architecture` — grafo
  incremental multi-repo.

### 2. Esteira global por fase (CLI, sem seletores inventados)

| Fase do plano | Automação (comando real) | Produto |
|----|----|----|
| Habilitar CRG | `ai-hub ai-hub-sync-crg-workspaces` (apply, ai-hub) | drift zerado; `--check` vira gate permanente da lane |
| Blast-radius pré-merge | `code-review-graph impact --base origin/dev` na lane | lista de consumers tocados antes de cada PR |
| Namespace (1100) | `code-review-graph query`/`search` (callers de cada serviço) → rewire DI; `refactor rename --old-name --new-name --kind Class` para renames | search-first automatizado; zero rewire cego |
| Codemod (1033) | leitura focada: `ast-grep scan --config sgconfig.yml --json` filtrado por `rule_id` → listas por classe; mutação só via `make mod APPLY=Y` | burn-down lists versionadas em `.reports/refactor/` |
| Regras detection-only | (a) migração no código, ou (b) refinamento no SSOT `config/codegen.yaml` (Infra.codegen.sgconfig) + `make gen APPLY=Y` ×2 fixed-point | nunca hand-edit em `ast-grep-rules/`/`sgconfig.yml` |
| loc-cap (9) · resíduo | `code-review-graph large-functions` · `dead-code --json --repo <root>` por checkout | listas purgação, adotadas como achados |
| agents repo | `make mod APPLY=Y` (--update-all provado para snapshots de SUAS 7 regras); `make gen APPLY=Y` = projeções canônicas | conformância do catálogo |

Exemplo imediato de regra-dono: `ban-test-doubles` marca
`tests/fixtures/forge_governance.py:153` (harness aprovado injetando
`run_raw`/`run` — não é mock). Proposta: classificação tipada no SSOT
(`fixtures de harness` isento de `ban-test-doubles`/`test-no-mock`), com
justificativa no codegen config — NUNCA exceção per-file manual nem
suppression inline (a regra proíbe; a exceção é da regra, no dono dela).
Mesma correção para `ban-test-mocks.yml` do package (exceção declarada via
sobreposição no config do projeto) — a iteração sobe para o dono do flext_infra.

### 3. Piloto de homologação (o que se pede aprovar)

**Sujeito** (bead ag-m9lu): passos 1–7 da "Sequência de execução" pela esteira (bead ag-q4w1, dependente do sync CRG ag-nq7q)
acima, pousados na branch de integração (`dev` do ai-hub) com deploy recovery
real na máquina do operador.

**Critérios de aceite measuráveis (4 fontes por item)**:
1. `make check APPLY=Y` exit 0 na lane E no SHA merged;
2. `make test APPLY=Y` exit 0 (integrity testmon ok; RED externos fechados em beads com evidência com/sem diff);
3. `ai-hub ai-hub-sync-crg-workspaces --check` exit 0 (CRG sincronizado e sem drift);
4. `code-review-graph impact --base origin/dev` limpo de órfãos desautorizados antes do merge;
5. deploy recovery com `LoadCredentialEncrypted` → receipt no home + probe de ativação;
6. `ai-hub validate-agents` exit 0 nos homes;
7. docs citam só handlers declarados (`docs_make_verbs` 9 passed mantido).

**Autoridade**: executor = esta lane; revisor = operador (conferindo burn-down
por classe e receipts); homologação declarada no bead ag-zrh antes do pouso
final (passos 8–10). Divergência = absorção `--no-ff` contínua do
`origin/dev` (ator paralelo já pousou 0.5.0).

**Custo/retorno**: CRG já indexado (graph.db live, watching); custo marginal
= sync + 2 gates; retorno = blast-radius e callers sempre measuráveis em
vez de grep ad-hoc, e cancelamento de ~1033 achados por classes automáveis
em vez de curadoria manual total.


## Riscos de produção e mitigação

- **Divergência lane vs dev (ai-hub)**: ator paralelo pousou ADR-0019/0020 +
  version 0.5.0 no dev. Todo dia sem absorção aumenta o merge. Mitigação:
  passo 1 logo na próxima sessão, e re-absorção contínua durante o grind.
- **Registry poluído em PRODUÇÃO** (`workspaces.json` com checkout-0..7):
  podrado, mas o bug de isolamento do workspace-discovery segue aberto (bead
  próprio) — re-polução em qualquer rodada de teste é regression de produção.
- **Deploy parcial**: deploy é transação; só materializar com candidate_root
  validado + acceptance nativa; nunca publicar em duas ondas.
- **Credencial**: exclusivo `LoadCredentialEncrypted` (nunca env) — já
  provado; obrigatório no passo 7.
- **Beads DB por sessão**: `env -u BEADS_DOLT_SERVER_DATABASE` ao tocar beads
  de projeto alheio (lição de fleet 2026-09-08).

## Revisão consolidada — Feito vs Falta

### Feito (com evidência)

1. **Base de governance**: lane reval250909 pousada (PR #133, merge `ab27a954`);
   tracker reval fechado com 4 fontes; épico ag-zrh + filhos criados.
2. **F0 inventário** (ag-zrh.1 DONE): causa raiz do runtime provada
   (`~/.agents` symlink → checkout vivo), homes inventariados, contrato de
   contagem quebrado documentado.
3. **F2 corte temático** (ag-zrh.3, código completo): python-production
   absorvida em `rules/python.md`; cópias estrangeiras aposentadas; contrato
   66/63/128 em AGENTS.md; gates `gen`×2 fixed point, `audit`, `waza` 128/128,
   `check` exit 0 (commits `d68e2d8a`, `56fcebdc`, `0f7084fd`).
4. **F1 cadeia ai-hub**: packaging CORRIGIDO (PR #734, merge `89294582e`);
   renderer opencode CORRIGIDO (lane `fix/opencode-renderer-stale-socket-gate`);
   registry poluído PODRADO + bug de isolamento registrado; classificação por
   detecção CORRIGIDA.
5. **Walker/pointer fix** (ag-ey2k, em `fix/green-baseline`): travessia
   validada de ponteiros, comparação pointer-aware, sweep de órfãos, stderr do
   systemd como evidência — deploy chega à ativação.
6. **Verde obrigatório iniciado**: 2564→2492 diagnósticos; reconstrução de
   teste quebrado; protocolos `ForgeRouting`/`GovernanceBundle`; namespace −22.

### Falta (bloqueios e ordem)

1. **Verde ai-hub completo** (bloqueio raiz): 2492 → 0 por classe de achado
   (namespace 1100, codemod 1033, pyrefly 157, pyright 43, lint 44,
   silent-failure 40, mypy 25, duplication 36, loc-cap 9, boundary 2,
   tier-whitelist 1, markdown 2). Só após: PR + merge `--no-ff` no dev.
2. **Absorção provider** (ag-zrh.2, WS-C): implementar absorção automática de
   instruções provider não-gerenciadas na transação de deploy.
3. **agentsctl** (ag-7hz, P0): pacote novo com `sync` como comando único de
   ciclo de vida (bundle → projeções → homes → ativação → validate-agents).
4. **Sonda R1**: marker/versão runtime == bundle publicado; zero markerless;
   agents distribuídos nos homes.
5. **F3 prova produtiva** (ag-zrh.4): sessão opencode nova real — skill dona
   carrega texto canônico na versão atual, `python-production` inexistente.
6. **Pouso e fechamento**: merge do programa no `agents` dev; fechamento
   ag-zrh.2/3/4 + épico com quatro fontes; lanes aposentadas (resíduo zero).
7. **Push pendente do plano**: commits de docs locais aguardando liberação do
   WIP do ator no checkout compartilhado (`AGENTS.md`/`CLAUDE.md`).

## Próximos passos (ordem)

0. **Absorção (2026-09-10, autoridade do operador — monopólio do tema):** o
   programa de contrato de entrega e lei comportamental
   (`docs/plans/20260910-delivery-contract-behavioral-law.md`, bead `ag-p4a`)
   passa a rodar nesta lane. Assorve o escopo agents-repo de ag-zrh.2 (WS-C),
   herda a Tarefa 3 do plano .kilo (absorvida em `ag-p4a.8`; Tarefa 5
   superseded pelo corte de-provider), e a contraparte ai-hub segue o prompt
   da seção 5 daquele plano.

1. Implementar a absorção automática de instruções provider no plano de
   deployment (mesma transação) e levar `deploy --surface skills` ao verde.
2. PR da lane ai-hub (`fix/opencode-renderer-stale-socket-gate`: renderer +
   detecção) com a evidência do vermelho pré-existente (2559 idênticos).
3. Sonda R1: marker/versão do que o runtime carrega == bundle publicado;
   zero markerless nos homes; agents distribuídos.
4. F3: prova produtiva em sessão nova + `validate-agents`.
5. Pouso da lane do programa no `agents` dev (gates completos + PR + merge
   `--no-ff` + prova pós-merge) e fechamento ag-zrh.2/3/4 com quatro fontes.

## Decisões registradas do operador

- Pouso reval250909: PR + merge operator-authorized (✅ executado).
- ag-9qg dentro da lane (✅ executado).
- python-production: absorver, desduplicar por tema, otimizar o existente,
  frontmatter v2, tudo no waza (✅ executado).
- Mineração do histórico: TODO o histórico (agendado no corte — as correções
  de sessão já absorvidas: uso sempre-on de skills, anti-hardcode, fix-forward).
- Sem registros/regras hardcoded: classificação por detecção automática
  (✅ implementado no ponto de classificação).

## Lições de runtime desta lane

- `~/.agents` symlink → checkout vivo define runtime para Kilo/opencode
  (checkout editável não é distribuição — violação runtime-is-reality).
- Deploy atômico exige runtime saudável + fonte limpa + credenciais via
  `LoadCredentialEncrypted`; nunca segredo em ambiente.
- Gates de árvore vermelha pré-existente (2559 no ai-hub dev) são provados
  por medição com/sem diff — nunca normalizados.
