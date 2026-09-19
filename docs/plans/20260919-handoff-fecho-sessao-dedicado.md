# Handoff de fecho de sessão — agente dedicado agents (2026-09-19)

**Mandato**: agente único dedicado; fix-forward-adopt; colaboração por registro nos
beads (`bd` com direnv no repo); revalidação pela realidade; PRs encerradas como
aberto-verde-atualizado ou exterminadas com veredito; merges --no-ff com a tip da
branch de integração.

## Estado por repositório (medido 02:4x–03:1x)

### agents (datacosmos-br/agents, dev) — ESTÁVEL, VERDE
- `19bea8b7` fix(wip-beads): o veredito [unblock] contava dentro de subshell de
  pipeline (CRITICAL da review da PR 130 que pousou sem reparo) — corrigido com
  process substitution; gates verdes.
- PR #154 (dev→main) e #155 merged; **PR #156 (ci workflow_dispatch) MERGED verde**.
- Arqueologia (vereditos com evidência, heads preservados no objeto local:
  e427e9213, f6391798c, 2a982fe9c, d10788a72): **150/130 ALREADY-LANDED**,
  **120 JUNK** (PR de 0 bytes; a feature pousou por #17/#19 e a doutrina de
  projeção migrou ao ai-hub), **119 SUPERSEDED** (comentário do próprio autor;
  subsystem deletado não existe mais). Ação residual registrada: triage dos
  WARNINGs da review da 130 (waza_gate version parsing, check_docs_links
  fences, wip-beads CSV quoting) — P3.

### algar-oud-mig (0.12.0-dev) — PR #32 MERGED (00:04Z); grind 96→1
- Onda de grind (9 subagentes + integração local): namespace 96→1 (resta
  settings.py:19, **resolvida fleet-side** pelo carve-out settings-c no
  flext-infra), lint/silent-failure/loc-cap/markdown-format/layout zerados,
  loc-cap converter 1231→912 LOC, part-classes canônicas `AlgarOudMig*`
  (validator, comparator_helpers, acl_transform, acl_io, schema_validation_*,
  _typings acl+migration), renames `AlgarOudMigPermissions*`, codemod
  ast-grep-rules criado (que ativou o scan de frota — 62 linhas de dívida nova
  expostas), org layer `config/codegen-org.yaml` com provider, cooldown
  dependabot 7 dias (algar-r5t) e roots canônicos.
- **Cauda restante registrada com precisão em algar-gm9** (codemod 62 linhas,
  duplication 6, type-tail mypy16/pyrefly5/pyright13, census 3, markdown 1,
  lint 1) — não executada: os 3 agentes de cauda exauriram a cota semanal
  (reset 24/09) e a lane de integração iniciou EM PARALELO a migração do algar
  para o mirror datacosmos-br/flext-infra + política no-lock (stand-down
  coordenado; não colidir).
- CI: runs vermelhos pós-merge são os "wip" da lane + a cauda acima; o bead
  algar-y3u guarda o retorno ao verde.

### ai-hub (dev) — lanes ativas em runtime stabilization
- Org layer: `providers` ficou obsoleto (identidade manifest-free, 208716f4f —
  extra_forbidden no schema novo); lane já corrigiu no dev; **o bloco layout
  project_overrides (wip/ canônico, ignores de runtime) precisa viver no org
  layer do próprio repo** — sem ele o gate layout reprova 13 raízes canônicas.
- PR 799 (storage lane) foi **superada pela própria lane** → PR 802 (daemon
  residente). Antes do fecho, um passe de integração independente da 799
  produziu findings herdados e registrados em aihub-oig6s.3: F821 `raw` no
  loader de manifesto (nunca lê o arquivo!), typing JsonDict do
  agents_markdown, mise merge incondicional, exists() em vez de sentinela no
  newest_mtime, e o item (4) do org layer acima.
- TEMP debug commit 8f78914d3: **dangling, nunca chegou a origin** — nada a
  reverter.
- Gates do ai-hub: donos registrados (aihub-l42it.3 zerar gates,
  aihub-jlp8n.5 census 111) — mapa de alavancagem postado no bead.

### flext-infra (flext-sh/flext-infra, 0.12.0-dev) — lanes em fluxo contínuo
- Corte G1 pushed (b97622068..b5237b9a6): config pública sem dados privados +
  mecanismo de camadas (local gitignored no clone do gerador + org layer
  tracked no repo consumidor) + knob dependabot_cooldown_days + título de
  docs sem marca de frota + untracks de projeções de máquina.
- **Carve-out settings-c** (decisão do operador 2026-09-19): settings podem
  importar `c` em runtime p/ defaults declarados — imports.py + teste
  atualizado; absorvido e pushed pela lane (c7e788510).
- **Defeito real consertado**: a migração manifest-free estava pela metade —
  `_manifest_repository_ref` falha-dura sem config/workspace.yaml enquanto
  `_local_repository_ref` já resolvia (CI da base vermelho, 118 runs).
  Fix: perna manifest-free ligada no caminho do conform; provado por
  load_workspace_spec neste checkout (flext-sh, standalone). Absorvido pela
  lane na branch feat/workspace-identity-manifest.
- PRs 749/756/757/755: **EXTERMINADAS com veredito** (3 ALREADY-LANDED com
  evidência de commits; 755 destruiria a facade lazy — ideia preservada como
  candidato de limpeza a re-derivar na tip). Guarda: 0 strings privadas nos 4.

## Arqueologia ai-hub (9 PRs, suspeita do operador)
Nenhuma perda real: 757/589/732 (mesma head WIP, regressiva) JUNK; 764/792
SUPERSEDED (revertiam lei vigente); 785 ALREADY-LANDED; 795 JUNK (86% churn de
lockfile); 740 SUPERSEDED (patch mantido como referência de compat Dolt↔Beads);
**796 = única salva real** (design da decomposição do god-module 687 LOC,
_generate_workspace_config_parts + _allocation) — patch arquivado em
~/ai-hub-worktrees/eval-patches-20260918/, minerável no bead aihub-jlp8n.3
(registrado). Patches de todas em eval-patches-20260918/.

## Deep-dive: descoberta e manutenção de worktrees (alinhamento wip)
- **Programa canônico**: `ai-hub/wip/` = wip-hier (captura hierárquica;
  10-git.sh é o único gateway git; 60-retire aposenta worktrees/branches/PRs;
  --apply captura/alinha/puxa; --no-retire/--gates modulam). Regra do
  operador: manutenção de worktrees deve falar o vocabulário doc-10 do wip,
  nunca inventar um paralelo.
- **Lane storage (aihub-oig6s.3, pousada)**: descoberta pura por filesystem
  (`.git/worktrees/*` → root + branch do HEAD, detached = vazio), correlação
  read-only worktree↔bead (metadata `gc.work_dir` → `branch` → padrão
  `polecat/<bead>`) ↔ PR/ator/sessão, flag `retire_candidate`, e plano de
  prune por janela de atividade + policy.
- **Estágio do alinhamento**: FATOS correlacionados ✓ (a lane já fala wip);
  **EXECUÇÃO de aposentadoria ainda dupla** — wip-hier (--apply) e o
  storage-prune planejam ações sobre os mesmos worktrees com políticas
  distintas (merge-state vs janela de atividade): risco de dupla aposentadoria
  / divergência. Próximo passo natural (beads oig6s.4/.5, STO-S5 aguarda
  autorização do operador): o storage-prune vira o executor residente
  (PR 802: daemon supervisionado) consumindo a MESMA fila de candidatos que o
  wip-hier planeja, com o wip-hier como fronteira de descoberta/captura.
- **Lacunas conhecidas**: worktrees órfãos (diretório sem registro em
  .git/worktrees) não são descobertos por nenhum dos dois (husk cleanup está
  no escopo do oig6s.3); worktrees de rigs gascity (`<rig>/worktrees/<lane>`)
  deliberadamente fora (runtime state); clones same-origin estrangeiros só com
  --include-foreign.

## Restante da campanha (para a próxima janela)
1. Algar: cauda do grind (lista precisa em algar-gm9) + retorno ao verde
   (algar-y3u) APÓS a onda mirror/no-lock da lane pousar.
2. ai-hub: PR 802 herda os findings do bead oig6s.3; gates = l42it.3/jlp8n.5;
   deploy+registro claude + synced/ (ag-lw57.10) quando o dev estiver estável.
3. STO-S5 (oig6s.5): cutover Gas City aguarda autorização do operador.
4. flext-infra: CI da base volta com a branch workspace-identity-manifest
   pousando; volume de grind (itpd1/5fxu6) é das lanes.
5. agents: triage WARNINGs review 130 (P3); cadeia G2 de distribuição aberta
   e não reclamada (ag-lw57.*, ag-vblj.*, ag-m9lu) — bloqueada menos por
   design que por pickup.
