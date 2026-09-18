# Handoff de repasse consolidado — campanha agents (F0–F7, executada) × campanha multi-repo (G0–G5, em execução)

**Data**: 2026-09-18 17:41 -03 · **Mandato**: agente único dedicado ao projeto agents;
fix-forward-adopt; colaboração com agentes de projetos paralelos por registro (nunca
competição); `bd` dentro do repo com direnv; revalidação máxima pela realidade
(comando → processamento → resultado; teste verde não basta).

## Fronteira arquitetural (corrigida pelo operador e medida em código)

**flext (público, flext-sh) não depende dos privados; os privados PODEM usar flext**
(algar/ai-hub/agents consumirem o codegen é o fluxo sancionado). A config de beads que
o flext gera é **genérica por design** — confirmado: backend `gascity|local|none`
plugável (tiers local/none 100% funcionais sem runtime privado; `AGENTS_GAS_CITY_ROOT`
guardado por env-var); toolchain `beads`/`gascity` aponta repos **públicos**
(`marlon-costa-dc/gascity`, `/beads`); `.mise.toml` não projeta a tool gc desde
`95baa0c0d`; o gerador funciona para um externo sem os privados (inventários com
fallback vazio; governança fail-closed exige cada org registrar-se na própria camada).
**Distribuição de artefatos de agente é exclusivamente do ai-hub**: ai-hub projeta
skills/commands/rules do catálogo agents para os repos e deixa comitado. O repo agents
é catálogo read-only (ADR-0008 puro).

## PARTE 1 — Plano antigo (campanha agents F0–F7): 100% EXECUTADO

Pushed `6978f43c..96f42c0d` em `dev`.

| Fase | Entregue | Commits |
| --- | --- | --- |
| F0 gates | cápsula 9450/9488 (causa real: reflow do prelude em `6978f43c`, NÃO `d08439df`); 2 references condensadas sob o teto waza | `a1213d2c`, `28b76f42` |
| F1 registro zcode | não-criação provada (não perda); consolidado em `20260918-handoff-zcode-catalog-sessions.md` | `4a1659b1` |
| F2 auditoria | `20260918-status-ledger.md` (veredito plano-a-plano, 59 beads [A]/[M]/[E]); headers retificados | `0d60299d` |
| F3 ADR-0008 | `cli.py`/`__main__.py` removidos; projection → `tools/governance_projection.py` (dev-only); wheel provado (18 módulos, 0 proibidos, sem entry_points); `.kilo/` varrido | `19e64c01`, `8f73e34e` |
| F4 home | desymlink c/ backup (`~/.agents-archive/home-desymlink-2026-09-18/`) + materialização — **mecanismo invalidado pelo operador; errata na G0** | `2be349fa` |
| F5 vocabulários | `config/skills.json` v3 seção `vocabulary` (usage/routes/activation/subjects); constantes extintas do código | `e16681a6` |
| F6 beads+conteúdo | 18 fechamentos com evidência + skills model-as-command/settings-vs-config/flext-service; tracker 209/250 closed | `bad28882`, dolt `miujh6vv` |
| F7 fecho | ci/build/validate/runtime EXIT=0; 63 testes executados; handoff `20260918-handoff-campanha-agents.md` | `96f42c0d` |

Retrovalidação ambiente frio: `setup`/`gen`×2/`fmt`/`fix`/`check`/`test` EXIT=0 com
árvore imutável. Guarda registrada: testmon não rastreia `rules/**` — `test-full` com
execução real é obrigatório em fronteiras que tocam markdown/config (L14).

## PARTE 2 — G0 errata (executada nesta sessão)

O operador invalidou `home-sync`/`home-check` (criavam mecanismo de distribuição
paralelo ao ai-hub; e sugerir adoção pelo flext-infra era erro arquitetural — flext
nunca depende do privado). Correções: targets removidos do `Makefile`;
`tools/home_projection.py` removido; ADR-0022 emendado (revogadas as cláusulas da
ferramenta/verbos; **permanece**: `~/.agents` não-symlink, projeção global de leitura,
**gestão do AI Hub** — surface catalog-home no G2/F6; transição = cópia estática
atual, manifesto `.agents-governance.json` já no formato ai-hub, stale documentado,
reparo = ai-hub assume, nunca restaurar symlink); errata no handoff da campanha e no
ledger. Knobs pyproject (`pythonpath`/`extraPaths`/`mypy_path=tools`) são internos do
repo e permanecem.

## PARTE 3 — O que falta (estado medido 17:41, adoção fix-forward das lanes)

### G1 — Fronteira flext-infra: CIRÚRGICA (auditoria fina concluiu: design é genérico)
Fica intocável: enum de backend com tiers local/none; toolchain com seletores públicos
+ `protected_mise_tools`; parametrização Jinja; gitignore/excludes de projeções de
runtime; mecanismos providers/project_overrides/ci_private_submodules/github_repos
(defaults vazios). **Sai do público** (dados privados comitados; mecanismo permanece):
`codegen.yaml` providers `datacosmos-br`/`marlonsc` (L258–271) + `docs.github_repos`
privados (L462–477) + `move_docs_files` cosmos-docgen (L845); `codegen-overrides.yaml`
`ci_private_submodules` cosmos-main/invest (remotes SSH/deploy-keys, L21–46) +
`project_overrides` de ai-hub/cosmos-*/neptor/vectorbt.pro/invest (L93–227; seções
`flext-*` ficam); `config/infra.yaml` `- ai-hub` em publishable_prefixes; template
`ci.yml.j2` + fragment: string "datacosmos-ci-dependencies" → neutro; copyrights
"Datacosmos" (`stabilization-native.yml` sai inteiro; `codegen_file_plan.py`; teste);
docs/security triages internos; fixtures `datacosmos-br/ai-hub`; prosa ADRs 006/016.
**Untrack de runtime comitado em violação ao próprio ignore**:
`flext-infra/.claude/settings.json` (paths `/home/marlonsc/workspaces/agents-skill-sync/…`),
`.github/hooks/aihub-governance.json`, `.github/hooks/.aihub-governance.json.agents-governance.json`
— projeção do ai-hub; o gerador da projeção (G2.4) passa a não emitir paths de máquina.
Overrides privados migram para camada local não-comitada do gerador
(`codegen-overrides.local.yaml` gitignored + contrato documentado) instalada nos repos
privados. Beads do dono-template no corte: `algar-r5t`, `ag-q6uo`. **Sem onda de regen
dos 31 submodules — os submodules públicos estão limpos.** Estado lá: `4e117ef3b3 wip`
+ 34 sujos no superprojeto, 7 no flext-infra (agente paralelo ativo — adotar, não
competir).

### G2 — ai-hub (coração)
Adotada a onda de docs (`eaf71f823`); restam ~3 sujos. Fila: (1) check/test verdes
(`aihub-l42it.8`, wave7 "1 arquivo quebrado"); (2) `make deploy` + `deploy --agent
claude --surface skills` + registro consumidor `claude` + exclusão formal de
`synced/`; (3) **superfície projetar-em-repo-comitado** (`aihub-agfq7` P0): cópias
carimbadas versão+digest em `<repo>/.agents/**`, transação managed-artifact, dry-run
funcional (ag-lw57.10), sem paths de máquina; piloto algar substituindo os 2 symlinks
comitados (tríplice `flext-law` resolvida pela catalogada ADR-0014); (4) rework
F0→F3 (F3 = `ag-bwqu` acceptance real); (5) cadeia P0 (ag-ey2k→ag-nq7q→ag-q4w1→
ag-vblj.*→ag-lw57.*→residuais) → piloto `ag-m9lu` com os 4 critérios de homologação.

### G3 — algar
Fix do `algar-79t` pousado pela lane paralela (`056d66d4`) — adotar e validar
processamento real. Fila: push `07096205`; adotar onda duplication-29 (38 arquivos,
`_cli_support.py`) + F811 `engine.py:43`/F821 se remanescerem; STRUCT final gm9/qou
(namespace 118→0) + loc-cap/layout 7/codemod 1/runtime-census 113/docs-audit ~48 →
`make check` VERDE; PR #32 CONFLICTING → integrar base `--no-ff`, ci verde (merge→main
aguarda operador); Round 11 + handoff + beads com evidência.

### G4 — flext consumidor + gc
Tríplice flext-law/symlinks→cópias via G2.4; par mayor = fix no runtime gc (handoff na
lane flext); `ag-bgs`/`ag-av2` se couber.

### G5 — agents residual + fecho geral
`ag-a11`; `ag-9xp` (sessão viva); épicos destravados por G2 fechados com evidência
(ag-zrh.2/.4, ag-2sc, ag-lw57, ag-m9lu); handoff final multi-repo; memory atualizada
(errata home-projection; fronteira flext×privado); pushs por repo no verde.

## Guardas permanentes

Fix-forward-adopt; gates via Make do dono; `bd` com direnv no repo (env+cwd do mesmo
store); sem force-push; merge `--no-ff`; exclusão fora do git só com backup tar +
manifesto; primeira falha causal → dono → re-roda a mesma gate; cache-hit testmon não
é prova (L14); budget da cápsula é contrato (10000/512); **guard por PR no flext-sh:
nenhum dado privado novo no público** (grep `datacosmos|marlonsc|ai-hub|workspaces/`
no diff); coordenação com lanes por registro.
