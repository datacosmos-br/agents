# Governance Runtime Program — Plano de Ação e Status (ag-zrh)

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
| 0 | Base limpa: lane reval250909 pousada | ✅ DONE | PR #133 merge `ab27a954` (--no-ff, operator-authorized); `make ci APPLY=Y` exit 0 (4 passed, testmon integrity=ok); pós-merge `make gen` ×2 fixed point + `make check` exit 0; lanes `feat/reval250909-adoption` e `wip/beads-governance-reval250909` aposentadas local+remoto após `merge-base --is-ancestor` exit 0 |
| 0 | Tracker reval250909 | ✅ DONE | Fechados com 4 fontes: ag-645 (`make help` lista gen/build), ag-s8r (conteúdo superseded provado), ag-aq8.2 (prova pós-merge), ag-9qg (jscpd 5.1.2 correto + `make duplication` exit 0, 0 clones), ag-aq8.1 (`GovernanceBundle.load` 65 agents + audit zero raise). ag-1b5/ag-blh: notas de dono ai-hub, sem falso fechamento |
| 1 | Épico criado | ✅ DONE | ag-zrh + filhos ag-zrh.1..4 com cadeia de dependências |
| 2 | **F0 — inventário de violação (ag-zrh.1)** | ✅ DONE | 4 varreduras paralelas read-only + observação de runtime do operador. Causa raiz provada: `~/.agents` é symlink → checkout vivo (por isso só o Kilo vê os agents). Homes: 0/current (opencode 43 stale + 10 identidades aposentadas vivas + 1 foreign + 53 tags decorativas; claude 45 stale + 10 + 14 foreign incl. `python-production`; `.claude/agents` 8 stale + 57 faltando; `selection.agents: []` nunca distribuiu). Comandos: 14/14 frontmatter ok; `ghi-list`/`pr-list` shadows estrangeiras invertem contrato (pr-list esconde CHANGES_REQUESTED). Hardcode HIGH: `rules/flext/beads-continuity.md` → `~/wip-beads.sh` + caminho de projeção. Contrato de contagem quebrado: 121/56/64 vs runtime 128/63/65 |
| 3 | **F2 — corte temático (ag-zrh.3)** | 🔶 código completo; fechamento bloqueado por ag-zrh.2 | Absorção python-production em `rules/python.md` + `config-settings-ssot.md` (commit `0f7084fd`); cópias estrangeiras python-production/ghi-list/pr-list aposentadas no mesmo corte (resíduo zero, projeções canônicas de command intactas); wip-beads processor adotado no repo (`scripts/wip-beads.sh` + `bd_json_to_csv.py` provados em runtime); inviolable-rules colapsada a router + eval reescrito no mesmo corte; flext-boundary adotado como perfil project-wide (66 agents, audit limpo); de-provider (chief-of-staff, 4 agents CLAUDE.md→neutro, menções Kilo); caminhos quebrados corrigidos (opencode-handoff); SHAs do mcp-builder → `references/sdk-docs.md` (dono único); citações de dono nos skills com invariantes; make-check → project-wide/shell; contrato de contagem 66/63/128 em AGENTS.md. Gates: `gen` ×2 fixed point, `audit` exit 0 (128/14/66/63), `waza` 128/128 suítes, `check` exit 0. Commits `d68e2d8a`, `56fcebdc`, `0f7084fd` |
| 4 | **F1 — distribuição pelo dono (ag-zrh.2)** | 🔶 EM ANDAMENTO — cadeia ai-hub 4 defeitos radicais, 3 corrigidos | (1) Packaging: wheel sem a superfície de assets → **CORRIGIDO** (PR #734 merge `89294582e` no dev do ai-hub; build verde com 394 arquivos; lane aposentada com ancestor proof). (2) Renderer opencode: gate velho home-relative sobre campo morto `socket_path_json` → **CORRIGIDO** na lane `fix/opencode-renderer-stale-socket-gate` (commit `625601fb`; provado: 2559 diagnósticos pré-existentes idênticos com/sem o diff). (3) Registry poluído por teste: 8 projetos pytest (checkout-0..7) no `workspaces.json` de produção → **PODRADOS** + bug bead criado (isolamento de teste do workspace-discovery). Credenciais: forma canônica descoberta — `systemd-run --user -p LoadCredentialEncrypted=...` (sem exportar segredo). (4) Classificação de projetos: **CORRIGIDO POR DETECÇÃO** (origin owner ∈ owners → internal; fora → third_party_fork; sem registro por-repo, a pedido do operador). **Bloqueiro atual**: composição de agents atinge arquivos de instrução provider não-gerenciados (ex.: `CLAUDE.md` do steampipe) — desenho fechado: absorver o conteúdo local para o bloco local do AGENTS.md dentro da MESMA transação de plano; implementação em curso |
| 5 | model-pipeline daemon | ⚠️ lane de outro ator | Serviço failed; 2 intents órfãos `submitted` removidos com snapshots de evidência em `~/tmp/opencode/`; a falha restante vive na lane ativa `ai-hub-wt/model-pipeline-v3` — não invadir; deploy de skills não depende mais dela |
| 6 | **F3 — prova produtiva (ag-zrh.4)** | ⏳ PENDENTE de F1 | Sessão opencode nova real: skill dona carrega texto canônico na versão atual, `python-production` inexistente, zero dedução |

## Próximos passos (ordem)

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
