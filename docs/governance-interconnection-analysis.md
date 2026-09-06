# Governance interconnection analysis

> Status: `ANALYSIS` (findings + proposed improvements; not all executed)
> Scope: `~/agents` repository only. Priorities 11–12 describe `~/ai-hub`
> behavior and are out of scope here — tracked on the `~/ai-hub` side.
> Counts below are physical-discovery facts as of the last update; re-derive
> with `find skills -name SKILL.md`, `find rules -name '*.md'`,
> `find commands -name '*.md'` before acting.

## Resumo

`config/governance.json` é a **única** camada explícita de interconexão entre
`rules/`, `skills/`, `commands/` e `AGENTS.md`. Ele mapeia 49 "garantias"
semânticas para seus proprietários (rule, skill, command, ou document). A
pesquisa abaixo identifica gaps, duplicações, inconsistências e interligações
ausentes, com propostas de melhoria para execução futura.

## Escopo de análise

- **Rules**: 39 arquivos em `rules/` (14 subdirectories + 5 root-level)
- **Skills**: 91 bundles em `skills/` (6 categories: agent-wide, project-wide, technology, framework, tool, domain)
- **Commands**: 8 files in `commands/` organized by category (implementation, inspection, security, governance)
- **Guarantees**: 50 mappings em `config/governance.json` (verifique com `_EXPECTED_GUARANTEES`)
- **Bootstrap**: 8 rules, 9 skills
- **Policy tags**: 9 `policy:*` tags correspondendo a `runtime/*` rules

## Findings

### 1. Gaps — interconexões ausentes

#### 1a. Sete de nove `policy:*` runtime rules sem guarantee entry

As 9 tags `policy:*` nos skills correspondem 1:1 a `rules/runtime/*.md`, mas
apenas 2 têm garantia explícita:

| Policy tag | Rule | Has guarantee? |
|---|---|---|
| `policy:strict-execution` | `runtime/strict-execution` | ✅ (`strict-execution`) |
| `policy:zero-residue` | `runtime/zero-residue` | ✅ (`complete-cutover`, `safe-deletion`, `root-owner`, `immediate-removal`) |
| `policy:fail-loud` | `runtime/fail-loud` | ❌ |
| `policy:no-fallback` | `runtime/no-fallback` | ❌ |
| `policy:preflight-before-effects` | `runtime/preflight-before-effects` | ❌ |
| `policy:required-environment` | `runtime/required-environment` | ❌ |
| `policy:atomic-effects` | `runtime/atomic-effects` | ❌ |
| `policy:causal-subprocess` | `runtime/causal-subprocess` | ❌ |
| `policy:no-keyring` | `runtime/no-keyring` | ❌ |

Fonte: `docs/execution/master-v7/09-runtime-extermination-plan.md` §"Central
policies" lista explicitamente a sintaxe `policy:strict-execution` composta por
essas 8 policy tags. `docs/execution/master-v7/11-governed-project-skill-distribution-plan.md`
§5.5 lista as mesmas rules como "contracts". Mas `config/governance.json` não
expõe 7 delas como garantias.

#### 1b. Setes de oito commands órfãos do guarantee map

| Command | In guarantee map? | Referenced in docs? |
|---|---|---|
| `synthesize-governance` | ✅ (`legacy-source-adjudication`) | `ADR-0006` |
| `add-language-rules` | ❌ | `02-skill-taxonomy.md` §"Convert to commands" |
| `database-migration` | ❌ | `02-skill-taxonomy.md` §"Convert to commands" |
| `feature-development` | ❌ | `02-skill-taxonomy.md` §"Convert to commands" |
| `ghi-list` | ❌ | `02-skill-taxonomy.md` §"Convert to commands" |
| `pr-list` | ❌ | `02-skill-taxonomy.md` §"Convert to commands" |
| `ralph-loop` | ❌ | `02-skill-taxonomy.md` §"Convert to commands" |
| `security-triage` | ❌ | `docs/security/security-triage.md` |

Os 7 commands convertidos em `commands/` (6 do `02-skill-taxonomy.md` +
`security-triage`) têm suas eval suites em `evals/commands/` (8 de 8
correspondem), mas não têm entrada no mapa de garantias.

#### 1c. Quarenta e nove rules órfãs — não referenciadas por garantia, AGENTS.md, ou outra rule

Das 39 rules, apenas 20 aparecem como garantia ou em AGENTS.md. 19 rules não
são referenciadas em **nenhum** lugar:

```
gascity, python, python/no-hidden-errors, rust, typescript, storage,
shell/bash-guard-chaining-precision, coordination/shared-venv-guard,
coordination/multiagent-edit-breadcrumb, architecture/generalized-abstraction,
security/prompt-defense, security/scanner-closure, security/supply-chain,
testing/observable-runtime, git/destructive-git-guard,
runtime/fail-loud, runtime/no-fallback, runtime/no-keyring,
runtime/preflight-before-effects, runtime/required-environment,
runtime/atomic-effects, runtime/causal-subprocess
```

#### 1d. Dezessete de dezenove always-on rules não no bootstrap

O bootstrap lista 8 rules, todas always-on. Mas existem 19 rules always-on
adicionais que NÃO estão no bootstrap — elas são "enforcement via policy tags
or AGENTS.md" em vez de "explicit bootstrap composition":

```
architecture/generalized-abstraction, coordination/shared-venv-guard,
git/destructive-git-guard, git/gitflow-branch-pr,
runtime/atomic-effects, runtime/causal-subprocess, runtime/fail-loud,
runtime/no-fallback, runtime/no-keyring, runtime/preflight-before-effects,
runtime/required-environment, runtime/zero-residue,
security/prompt-defense, security/scanner-closure, security/supply-chain,
shell/bash-guard-chaining-precision, testing/observable-runtime,
workflow/beads-traceability, workflow/generators-not-projections,
workflow/living-documentation
```

De acordo com `docs/execution/master-v7/10-additive-capability-composition-plan.md`
§"Phase 1": "Add one always-on rule for authorization, selection, readiness,
typed absence, workflow-local failure, calculated defaults, and applicable
closure gates" — e "Add the rule to the typed governance bootstrap so session
capsules and static provider instructions inherit it without copying prose."

#### 1e. AGENTS.md referencia apenas 2 rules por file-path

AGENTS.md menciona `rules/gascity.md` (linha 18: "Workspace placement: follow
the declared Gas City city/rig/Pack V2 contract in `rules/gascity.md`") e
`rules/storage.md` (linha 54: "Storage and scratch follow `rules/storage.md`").
Nenhuma das outras 37 rules é referenciada. **Nenhuma dessas 2 rules está no
guarantee map** — `gascity` não é referenciada por nenhuma guarantee, e
`storage` é apenas indiretamente conectada via markdown link de
`engineering-core`.

AGENTS.md linha 47 afirma: "The canonical static contract is `rules/gascity.md`."
Isto significa que `gascity` é a owner única para "Gas City configuration owns
orchestration identity and dispatch" — mas esta rule não tem guarantee entry.

#### 1f. Documentos órfãos

`document:AGENTS.md` é o **único** document-type owner no guarantee map (6
garantias). O AGENTS.md navigation map declara referências para `README.md`,
`docs/execution/master-v7/README.md`, `docs/adr/README.md`,
`docs/security/security-triage.md`, `skills/README.md` — mas **nenhum** desses
documentos aparece como guarantee owner. `README.md` é descrito como
"Repository overview" no próprio AGENTS.md, e `docs/security/security-triage.md`
é listado como "Security evidence". Ambas são fontes autoritativas com
conteúdo sem garantia de propriedade.

#### 1g. Gas City skills órfãs com todas as policy tags

As duas skills `gascity-change-lifecycle` e `gascity-workspace-lifecycle`
(ambas `tool/gascity`, `detect:opt-in:gascity`) carregam **todas as 9 policy
tags** — incluindo as 7 runtime rules sem guarantee (`fail-loud`,
`no-fallback`, `preflight-before-effects`, `required-environment`,
`atomic-effects`, `causal-subprocess`, `no-keyring`). Ambas têm
`route:agent` (projetam apenas para agent homes pessoais) e
`activation:opt-in` (ativam apenas quando o projeto autoriza Gas City +
workflow seleciona explicitamente). Nenhuma das duas aparece no guarantee
map.

#### 1h. Skills e commands nunca referenciam rules ou outros skills

Análise de todos os `SKILL.md` e command files: **zero** contêm links
Markdown para `rules/*.md` ou `skills/*/`. A única ligação entre o conjunto de
runtime rules e as skills é a convenção `policy:*` tag. O `gascity` rule
referencia os Gas City primitives (city, rig, Pack V2, agent, formula, run,
session) apenas no texto, sem links estruturados.

### 2. Duplicações — garantias redundantes

Cinco pares de garantias são **totalmente redundantes** — mapeiam para o
mesmo rule com nenhum owner adicional:

| Garantia A | Garantia B | Rule compartilhada |
|---|---|---|
| `canonical-command-surface` | `cli-usability` | `rule:workflow/canonical-commands` |
| `complete-cutover` | `safe-deletion` | `rule:runtime/zero-residue` |
| `exact-execution` | `operator-precedence` | `rule:coordination/operator-precedence` |
| `current-tracker-state` | `tracker-evidence` | `rule:workflow/beads-traceability` |
| `concurrent-work-adoption` | `fix-forward-collaboration` | `rule:coordination/fix-forward-collaboration` |

Além disso, 3 pares compartilham um rule mas têm skills adicionais:

| Garantia A | Garantia B | Rule compartilhada | Skills distintas |
|---|---|---|---|
| `immediate-removal` | `safe-deletion` | `rule:runtime/zero-residue` | `skill:safe-delete` vs nenhuma |
| `root-owner` | `complete-cutover`/`safe-deletion` | `rule:runtime/zero-residue` | nenhuma vs `skill:safe-delete` |
| `operator-precedence` | `fix-forward-collaboration`/`history-evidence`/`lane-ownership`/`evidence-backed-blocker` | `rule:coordination/operator-precedence` ou `rule:coordination/fix-forward-collaboration` | diferentes skills |

### 3. Inconsistências — lacunas estruturais

#### 3a. Frontmatter de rule inconsistente (31 de 39 rules sem tags)

Apenas 3 rules declararam `metadata.aihub.tags`:

| Rule | Tags |
|---|---|
| `architecture/governance-artifact-composition` | `route:project` |
| `git/gitflow-branch-pr` | `route:personal` |
| `workflow/beads-traceability` | `route:personal` |

As outras 36 rules não têm tags de rota. Rules always-on sem tags recebem
`RuleDistribution.BOTH` por padrão (`rules.py`), e path-scoped rules sem tags
recebem `RuleActivation.PATH_SCOPED` apenas pelo globs. Isso é inconsistente
com `docs/execution/master-v7/02-skill-taxonomy.md` que exige tags
explícitas para conditional groups e `docs/execution/master-v7/04-agent-rule-projection-contract.md`
§"Universal rule composition" que afirma "Rules are always active or path
scoped" — implicando que a tag de rota deve ser declarada, não inferida.

#### 3b. Cross-references entre rules ausentes na maioria

Apenas 6 rules contêm links Markdown para outras rules:

- `architecture/engineering-core` → 5 rules (generalized-abstraction, strict-execution, runtime-is-reality, storage, scanner-closure)
- `coordination/fix-forward-collaboration` → 5 rules
- `coordination/multiagent-edit-breadcrumb` → 1 rule
- `coordination/plan-topic-monopoly` → 1 rule
- `coordination/session-governance` → 4 rules
- `runtime/strict-execution` → 8 rules (todos os runtime/*)

As outras 33 rules são completamente isoladas. Especificamente, os 7 runtime
rules órfãos (fail-loud, no-fallback, etc.) não linkam a strict-execution
(como aggregate pai) nem entre si. `docs/execution/master-v7/11-governed-project-skill-distribution-plan.md`
§5.5 afirma que "strict execution" é um "owner" que deve ser referenciado, não
copiado.

#### 3c. `gascity` rule naming anomaly

`rules/gascity.md` é a única rule sem subdirectory de categoria — identity
é `gascity` em vez de `<category>/gascity`. Todas as outras 38 rules seguem o
padrão `<category>/<name>`. As 5 root-level rules (`gascity`, `python`,
`rust`, `typescript`, `storage`) são anômalas nesse aspecto, mas apenas
`gascity` tem um tag `route:personal` sem globs.

#### 3d. Guarantee naming inconsistency

13 de 49 garantias são single-owner. Algumas usam o nome direto da identity
(`fix-forward-collaboration`, `operator-precedence`, `topic-monopoly`,
`sprint-closure`, `strict-execution`, `professional-integrity`,
`session-heartbeat`, `canonical-first`, `no-hidden-code`, `living-documentation`,
`observable-tests`, `small-batches`), enquanto outras usam prosa semântica
(`evidence-backed-truth`, `concurrent-work-adoption`, `complete-cutover`,
`cli-usability`, `current-tracker-state`).

### 5. Gaps na distribuição automática de skills

#### 5a. Dois sistemas de projeção concorrentes para o mesmo diretório

O `agentsctl sync` projeta skills de `~/agents/skills/` para os diretórios
de cada provider (personal: `~/.claude/skills/`, project: `.claude/skills/`).
Mas o ai-hub `ssot-relink --mode adopt` → `agent_skills()` projeta DIRETAMENTE
do `~/ai-hub/skills/<bundle>/<path>/` para o MESMO `<agent_home>/skills/<name>/`.
Ambos escrevem no mesmo path sem coordenação — race condition quando skills são
ativadas via `agentsctl sync` e o `ssot-relink` sobrescreve.

**Caminhos exatos de conflito:**
- `ssot_relink.py` → `driver.py:project_hub_skills()` (line 128-148): projeta para `~/agents/skills/`
- `ssot_relink.py` → `driver.py:~110 agent_skills()`: projeta para `<agent_home>/skills/`
- `runtime.py:168-200 sync()`: projeta para `${HOME}/.claude/skills/` (personal)
- `projections.json`: claude personal skills → `${HOME}/.claude/skills`

**Nomeação divergente:** ai-hub `inviolable-rules` (bundle: `governance/rules`)
não existe no catalog canônico do `~/agents`. `agentsctl sync` não consegue
resolver este nome.

#### 5b. Nenhum trigger automático de `agentsctl sync`

O `ai-hub-watch.service` (incremental CRG) e `ai-hub-maintain.service` não
disparam `agentsctl sync` quando skills mudam. O fluxo atual exige:
1. `ai-hub ssot-relink --mode apply` (manual)
2. `cd ~/agents && agentsctl sync` (manual)

Nenhum daemon monitora mudanças em `~/agents/skills/` ou
`~/agents/config/governance.json` para disparar sync automaticamente.

#### 5c. 10+ ai-hub skills sem equivalente canônico no `~/agents`

| ai-hub `name` | ai-hub `path` | `~/agents` canonical |
|---|---|---|
| `inviolable-rules` | `governance/rules` | ❌ (closest: `architecture/engineering-core`) |
| `make-check` | `governance/make` | ❌ |
| `cdk-roles` | n/a | ❌ |
| `cosmos-config` | n/a | ❌ |
| `flext-rules` | `governance/typescript` | ❌ |
| `lint-rules` | `governance/python` | ❌ |
| `semver` | n/a | ❌ |
| `universal-entrypoints` | n/a | ❌ |
| `workspace-standards` | n/a | ❌ |
| (mais) | | |

#### 5d. cliproxy-mgmt: CLIProxy não é provider em `projections.json`

O `connect-poolside-openai-api` plan adiciona perfil `poolside` ao CCS via
CLIProxy (porta 8317). O CLIProxy é um serviço (`ccs-cliproxy.service` em
`services.yaml`), não um "agent" no `projections.json`. Mas skills que gerenciam
model routing (como `flext-rules`) precisam ser propagadas via `agentsctl sync`.
Nenhuma skill no `~/agents` referencia configuração de CLIProxy.

#### 5e. Fork management: PRs sempre para `marlon-costa-dc/agents:dev`

O `~/agents` repo não é fork: `gh api repos/marlon-costa-dc/agents --jq
.parent` retorna `null`. O remote canônico é `marlon-costa-dc/agents` e a linha
de integração é `dev`, com promoção a `main` apenas sob autorização explícita do
operador. Nenhuma skill/command propaga para um fork sem validação de garantia;
a política de forks vive no seu próprio owner, não aqui.

### 6. Gaps no auto-learning loop (operator-correction-learning + doc-drift)

#### 6a. Duas skills de auto-learning existem mas não são gatilhadas automaticamente

O `~/agents` já contém o mecanismo de **auto-learning determinístico**:

1. **`operator-correction-learning`** (`skills/agent-wide/`):
   - `SKILL.md`: personal, `updates:manual`, `usage:router`
   - Carrega ALL 7 policy tags: `atomic-effects`, `causal-subprocess`,
     `fail-loud`, `no-fallback`, `preflight-before-effects`, `strict-execution`,
     `zero-residue`
   - `evals/operator-correction-learning/eval.yaml`: grader força: find
     causal owner, prove producer contract, update canonical owners (not
     projections), remove semantic opposites, add regression, repeat
     contradiction search, keep suspended runtime untouched
   - Fixture `correction-state.yaml`: `mode: explicitly_suspended`,
     `canonical_tracker_available: false`

2. **`doc-drift`** (`skills/project-wide/`):
   - `SKILL.md`: project-wide, `updates:manual`, `usage:on-demand`
   - Audita documentation vs code/config/upstream source
   - `evals/doc-drift/eval.yaml`: grader força: compare claims with
     canonical owner, identify extinct contracts, propose corrections,
     never invoke suspended runtime, zero residue

**Gap**: Ambas têm `updates:manual` — são evals que rodam quando invocados,
mas NÃO são gatilhados automaticamente como parte do `agentsctl check` gate.
Não há feedback automático de eval failures → rule/skill/command improvements.

#### 6b. `doc-drift` e `operator-correction-learning` não validam plan ↔ code alignment

O `doc-drift` skill compara documentation → code. Mas NÃO compara
**plan document ↔ code**. O plano de governança
(`governance-interconnection-gaps-plan`) pode divergir do código implementado
sem que nenhum gate detecte.

#### 6c. agentsctl não é instrumentado pelo ai-hub

`agentsctl` é instalado em `~/.local/bin/agentsctl` (symlink → uv-managed venv
em `~/.local/share/uv/tools/agents-governance/bin/agentsctl`). O usuário
mencionou `~/local/bin/agentsctl` — precisa verificar se este path existe.
O ai-hub NÃO instrumenta `agentsctl` via systemd — não há serviço que dispare
`agentsctl sync` automaticamente após mudanças.

### 4. Análise de cobertura de testes existentes

`tests/test_governance_config.py` (6 tests) valida:

1. `test_repository_governance_resolves_every_guarantee_owner` — todos os
   guarantee owners resolvem para rules/skills/commands/documents existentes
2. `test_governance_config_rejects_incomplete_guarantee_map` — garante que
   a garantia `fix-forward-collaboration` existe (fail-fast on popped key)
3. `test_governance_config_rejects_retired_v1_schema` — schema v2 obrigatório
4. `test_governance_audit_rejects_missing_and_non_always_bootstrap_rules` —
   bootstrap rules devem existir e ser always-on
5. `test_governance_audit_rejects_missing_guarantee_owner` — owner faltando
   levanta erro
6. `test_active_governance_contract_has_no_monolith_residue` — não pode
   conter `UNIVERSAL_CORE`, `legacy_core`, etc.

**Gap de teste**: Nenhum teste valida que **toda** rule, skill, e command
é coberta por pelo menos uma guarantee (ou está no bootstrap). O teste
`test_repository_governance_resolves_every_guarantee_owner` verifica o
direção oposta — que todos os owners de garantias existem — mas não que todos
os artifacts existentes são referenciados.

## Propostas de melhoria

### Prioridade 1: Fechar o gap policy-tag → guarantee (runtime rules)

Adicionar 7 garantias para as runtime rules sem guarantee, mapeando cada uma
1:1 para seu rule e policy tag:

```jsonc
// config/governance.json additions
"atomic-effects": ["rule:runtime/atomic-effects"],
"causal-subprocess": ["rule:runtime/causal-subprocess"],
"fail-loud": ["rule:runtime/fail-loud"],
"no-fallback": ["rule:runtime/no-fallback"],
"no-keyring": ["rule:runtime/no-keyring"],
"preflight-before-effects": ["rule:runtime/preflight-before-effects"],
"required-environment": ["rule:runtime/required-environment"],
```

Estender `_EXPECTED_GUARANTEES` em `governance_config.py` com estes 7 nomes.
Estes são os owners semânticos das tags `policy:*` já existentes em todos os
skills — a mudança é puramente aditiva e validada pelo `catalog.py` que já
enforça `_POLICY_TAGS`.

### Prioridade 2: Mapear commands órfãos para guarantees

Adicionar 7 garantias para os commands não mapeados:

```jsonc
"database-migration": ["command:database-migration", "rule:runtime/atomic-effects"],
"feature-development": ["command:feature-development", "skill:search-first"],
"language-rule-authoring": ["command:add-language-rules", "rule:architecture/governance-artifact-composition"],
"github-issue-transparency": ["command:ghi-list", "rule:coordination/operator-precedence"],
"pull-request-transparency": ["command:pr-list", "rule:coordination/operator-precedence"],
"delivery-iteration": ["command:ralph-loop", "skill:anti-phase-skip"],
"security-triage-closure": ["command:security-triage", "skill:governance-audit", "rule:security/scanner-closure"],
```

### Prioridade 3: Consolidar garantias redundantes

Unir 5 pares de garantias redundantes (manter o nome mais descritivo):

| Remover | Manter |
|---|---|
| `cli-usability` | `canonical-command-surface` |
| `safe-deletion` | `complete-cutover` |
| `exact-execution` | `operator-precedence` |
| `current-tracker-state` | `tracker-evidence` |
| `concurrent-work-adoption` | `fix-forward-collaboration` |

### Prioridade 4: Reconciliar bootstrap vs guarantee

Adicionar 4 skills (`anti-phase-skip`, `dispatch-agent`, `safe-delete`,
`skill-governance`) ao `bootstrap.skills` — elas já estão nas guarantees mas
não no bootstrap, o que significa que elas não são carregadas no
`sync` personal root por padrão.

### Prioridade 5: Adicionar route-tag frontmatter a 21 always-on rules

Rules without `metadata.aihub.tags` recebem `["route:both"]`:

```yaml
---
description: One-line mandatory invariant.
metadata:
  aihub.tags: '["route:both"]'
---
```

Path-scoped rules (`python`, `rust`, `typescript`) recebem `["route:project"]`.
`storage` recebe `["route:personal"]` (referenciada por AGENTS.md line 54).
`gascity` já tem `["route:personal"]` (referenciada por AGENTS.md line 18).

### Prioridade 6: Adicionar cross-references entre rules relacionadas

- Cada `runtime/*` rule linka para `runtime/strict-execution.md` (seu aggregate pai)
- `python/no-hidden-errors.md` linka para `python/config-settings-ssot.md`
- `security/prompt-defense.md` linka para `architecture/engineering-core.md`
- `git/destructive-git-guard.md` linka para `coordination/operator-precedence.md`
- `testing/observable-runtime.md` linka para `workflow/runtime-is-reality.md`
- `coordination/shared-venv-guard.md` linka para `runtime/strict-execution.md`

### Prioridade 7: Mover `gascity` rule para uma categoria

`rules/gascity.md` → `rules/coordination/gascity.md` para seguir o padrão
`<category>/<name>`. O `gascity` rule é a owner do Gas City static boundary —
um dos três orchestration primitives (com Beads e Dolt) — e deve ser
categorizado como `coordination/` (ou uma nova `orchestration/`). Atualizar
referências em AGENTS.md.

### Prioridade 8: Mapear Gas City skills para garantias

Adicionar garantia `gas-city-orchestration` que mapeia as duas Gas City skills
(`gascity-change-lifecycle`, `gascity-workspace-lifecycle`) ao `gascity` rule.
Estas skills carregam todas as 9 policy tags — ao adicionar as 7 garantias de
runtime rules na Prioridade 1, estas skills serão automaticamente traceadas
para todas as runtime rules owners:

```jsonc
"gas-city-orchestration": ["rule:gascity", "skill:gascity-change-lifecycle", "skill:gascity-workspace-lifecycle"],
```

### Prioridade 9: Mapear documentos órfãos para garantias

Adicionar `README.md` e `docs/security/security-triage.md` ao guarantee map:

```jsonc
"repository-authority": ["document:README.md", "rule:architecture/engineering-core"],
"security-evidence-authority": ["document:docs/security/security-triage.md", "skill:security-review", "rule:security/scanner-closure"],
```

### Prioridade 10: Adicionar teste de cobertura de garantias

Extender `tests/test_governance_config.py` com teste que assegura:
1. Toda rule/skill/command aparece como guarantee owner ou no bootstrap
2. Nenhum par de garantias compartilha o mesmo single-owner set
3. Todo bootstrap skill/rule aparece em pelo menos uma guarantee

## Conformidade com regras existentes

- `rules/architecture/governance-artifact-composition.md` §"Type correction rule":
  cada mudança é atomic — create one canonical owner, rewire consumers, remove wrong owner
- `docs/execution/master-v7/04-agent-rule-projection-contract.md` §"Universal rule composition":
  "Universal engineering behavior is injected as rules, not repeated inside every skill or agent"
- `docs/execution/master-v7/09-runtime-extermination-plan.md` §"Central policies":
  lista a sintaxe `policy:strict-execution` com 8 policy tags filhas
- `docs/execution/master-v7/10-additive-capability-composition-plan.md` §"Phase 1":
  "Add one always-on rule for authorization, selection, readiness, typed absence, workflow-local failure, calculated defaults, and applicable closure gates"
- `rules/gascity.md` §"Repository boundary during suspension":
  "Work only in the existing authorized checkout" e "Static Gas City skills are
  personal governance and never project projections" — confirma que as Gas City
  skills são `route:agent` e nunca devem ser project-scoped
- `docs/execution/master-v7/02-skill-taxonomy.md`:
  "agent-wide and project-wide derive distribution only from their paths;
  route:*, activation:*, and detect:* are forbidden there" — confirma que
  conditional skills (technology/framework/tool/domain) requerem route +
  activation + detect + subject tags. Todas as 30 conditional skills já as
  possuem. O problema não é tag validation, é garantee coverage.
- `docs/execution/master-v7/11-governed-project-skill-distribution-plan.md`
  §5.5: lista os runtime rules como "contracts" que devem ser referenciados
  por skills, não copiados — afirma: "The plan links those owners instead of
  copying their mutable procedures."
- `docs/execution/master-v7/01-artifact-contracts.md` §"Rule and agent contracts":
  "A skill may reference a rule by stable local contract but must not duplicate it"
  — confirma que skills devem linkar rules, não embed-las.

## Execução futura — ordenação por dependência

| Ordem | Tarefa | Motivo |
|---|---|---|
| 1 | **Prioridade 1**: 7 runtime rules → guarantees | Base para Gas City skills (carregam estas tags) |
| 2 | **Prioridade 3**: Consolidar 5 pares redundantes | Limpar antes de adicionar novas garantias |
| 3 | **Prioridade 7**: Mover `gascity` → `coordination/` | Necessário antes de Prioridade 8 |
| 4 | **Prioridade 8**: Gas City skills → guarantee | Depende de `gascity` rule identity corrigido |
| 5 | **Prioridade 2**: 7 commands órfãos → guarantees | |
| 6 | **Prioridade 4**: Bootstrap alignment (4 skills) | |
| 7 | **Prioridade 6**: Rule cross-references | Necessário antes do fixed-point `agentsctl sync` |
| 8 | **Prioridade 5**: Route-tag frontmatter | Normalizar após repositionamento |
| 9 | **Prioridade 9**: Documentos órfãos → guarantees | |
| 10 | **Prioridade 10**: Tests de cobertura | Validar tudo no final |

## Alinhamento com outros planos existentes

Análise dos 14 planos em `~/.local/state/poolside/plans/` para
identificar alinhamentos, conflitos, e oportunidades de coordenação.

### Planos diretamente alinhados (mesmo repositório: `~/agents`)

| Plano | Workspace | Relevância para governança | Ponto de alinhamento |
|---|---|---|---|
| `flext-strict-c-t-p-m-u-hARMONIZATION` | `~/agents` | Harmonia de código Python na `src/agents_governance/`. Referencia `rules/python.md` como fonte de law | ✅ **Conflito potencial**: Ambos propõem reorg do root-level rule anomaly (`python.md` ↔ `gascity.md`). O plano flext deve usar `rules/python/config-settings-ssot.md` após reorganização. |
| `skills-cohesion-gastown` | `~/agents` | Limpeza de skills/docs/AGENTS.md de Gas Town. Referencia `skills/beads/SKILL.md` e contexto `rules/gascity.md` | ✅ **Complementar**: Propõe limpeza de skills; meu plano propõe guarantee coverage para as skills gascity-* e gascity rule. Deve ser feito no mesmo cutover. |

### Planos indiretamente relacionados (outros workspaces, referenciam `~/agents`)

| Plano | Workspace | Relevância | Ponto de alinhamento |
|---|---|---|---|
| `ai-hub-puro-dev-beads` | `~/.ai-hub` | Runtime package. Declara `~/agents` como SSOT | ✅ **Dependência**: O runtime package (`ai-hub install|generate-configs|...`) depende da integridade do guarantee map. Mudanças no governance.json afetam a projeção. |
| `aihub-ajuste-execution-rev2` | `~/.ai-hub` | Análise crítica de execution plan. Enfatiza root-cause + fail-loud | ✅ **Conceito alinhado**: A crítica "o plano nunca lista 'o CLI deve importar' como pré-gate" paralela com meu gap de teste "nenhum teste valida coverage de artifacts → guarantees". |
| `gt-up-vm-explosion` | `~/gt` | Bug de pressure gating em `gt up` | ✅ **Phase 1 de 10-additive**: O bug de `isAgentSession` sublinha a necessidade do "capability-selection rule" (Phase 1) — authorization × selection × readiness. |
| `assume-sweep-dedicated-agent` | `~/gt` | Sweep de beads do Mayor para epic `agents` | ✅ **Co-track**: Referencia o plano `skills-cohesion-gastown` para update. Mostra o padrão de cross-plan tracking via beads. |
| `build-idempotent-incremental-publish` | `~/.ai-hub` | Build idempotency do dcdoc | ❌ Não relacionado a governance catalog |
| `datacosmos-padronizacao-layouts` | `~/.ai-hub` | Layout standardization | ❌ Não relacionado a governance catalog |
| `connect-poolside-openai-api` | `~/.ccs` | Conectar Poolside AI API | ❌ Não relacionado a governance catalog |
| `unify-cache-hierarchy` | dev-env | Cache unification | ❌ Não relacionado a governance catalog |
| `recover-fix-gt-bd-doctor-issues` | `~/gt` | Fix gt/bs doctor issues | ❌ Operacional, não governance |

### Conflitos críticos identificados

1. **`flext-strict` vs. reorganização de rules**: O plano `flext-strict` referencia
   `rules/python.md` (root-level). Se `gascity` é movido para `coordination/`,
   `python.md` também deve ser movido para `python/` para consistência. Isso
   requer atualização do plano flext-strict para referenciar
   `rules/python/config-settings-ssot.md` em vez de `rules/python.md`.

2. **`skills-cohesion-gastown` vs. Gas City guarantee coverage**: O plano
   gastown propõe limpeza de skills/docs. Meu plano propõe adicionar Gas City
   skills ao guarantee map. Ambas as mudanças no `~/agents` devem ser
   coordenadas no mesmo cutover para evitar fixed-point divergence.

3. **AGENTS.md references**: O plano `skills-cohesion-gastown` propõe
   corrigir AGENTS.md. Meu plano propõe atualizar a referência
   `rules/gascity.md` → `rules/coordination/gascity.md`. Este update deve
   ser feito como parte do mesmo AGENTS.md cleanup.

### Sincronização recomendada

| Etapa | Plano envolvido | Ação de sincronização |
|---|---|---|
| Pre-landing | `flext-strict`, `governance-interconnection` | Confirmar que root-level rules (`gascity`, `python`, `rust`, `typescript`, `storage`) são reorganized antes do landing |
| Pre-landing | `skills-cohesion-gastown`, `governance-interconnection` | Gas City skills + gascity rule guarantee coverage deve ser mapeado no mesmo PR |
| Landing | `ai-hub-puro-dev-beads` (runtime) | `~/agents` governance.json deve ser validado antes do runtime package depender nele |
| Post-landing | todos os planos | Re-validate `agentsctl check` + `make test` no repo `~/agents` antes de propagar para consumer projects |

---

### Matriz completa de coordenação com todos os 14 planos existentes

Análise de como cada plano atua, em qual workspace, e como o plano de
interconexão de governança deve se coordenar.

#### Arquitetura atual: dois sistemas paralelos de distribuição de skills

**Sistema 1 — ai-hub SSOT** (`~/ai-hub/config/skills.yaml` + `services/ssot_relink.py`):
- 30+ skills declaradas em `config/skills.yaml` com `bundle/path/scope/class/distribute/owner`
- `ssot-relink --mode hub` → `project_hub_skills()`: copia de `~/ai-hub/skills/<bundle>/<path>/` → `~/agents/skills/<entry.name>/`
- `ssot-relink --mode adopt` → `agent_skills(home)`: copia de `~/ai-hub/skills/<bundle>/<path>/` → `<agent_home>/skills/<entry.name>/` (ex: `~/.claude/skills/caveman/`)
- Systemd services: `ai-hub-watch.service` (incremental CRG), `ai-hub-maintain.service` (manutenção), `ai-hub-hooks.service` (daemon de hooks), `ai-hub-mcp.service` (gateway MCP)

**Sistema 2 — agentsctl projection** (`~/agents/projections.json` + `src/agents_governance/projection.py`):
- 7 providers (claude, codex, cursor, copilot, gemini, opencode, antigravity) × 2 contexts (personal, project) × 4 surfaces (skills, commands, agents, rules)
- `agentsctl sync` projeta de `~/agents/` para paths específicas de cada provider
- Personal: `${HOME}/.claude/skills/`, etc.
- Project: `.claude/skills/`, etc. (relativo ao project root)
- Usa `skills.lock.json` para tags de distribuição
- Usa `.agents/projection.json` para seleção de projeto

**CONFLITO ARQUITETURAL**: Ambos os sistemas escrevem para `<agent_home>/skills/` (ex: `~/.claude/skills/`) — o `agent_skills()` do ai-hub e o `agentsctl sync` (context personal) escrevem no MESMO diretório com NOMES DIFERENTES de skills. Cria race condition e estado inconsistente.

#### Plano por plano — matrix de coordenação

| # | Plano | Workspace | Domínio | Status | Coordenação com governance |
|---|---|---|---|---|---|
| 1 | `flext-strict-c-t-p-m-u-hARMONIZATION` | `~/agents` | Code quality (pydantic, ruff, pyright) | ⚠️ Blocked (needs pydantic sign-off) | **Step 5**: rule cross-references + **Step 6**: gascity move. Flext propõe `c.py/t.py/m.py` que validariam garantias via Pydantic. Coordenar para que os novos tests (Step 10) usem Pydantic models. |
| 2 | `governance-interconnection-gaps-plan` | `~/agents` | Gap analysis (este plano) | ✅ In progress | Self. |
| 3 | `ai-hub-puro-dev-beads` | `~/ai-hub` | Pure package refactor | ✅ Merged (per integrated-stabilization) | **Step 7-8**: Gas City guarantee. O `ssot_relink` projeta skills para `~/agents/skills/` — precisa validar que as skills projetadas resolvem guarantees. |
| 4 | `aihub-ajuste-execution-rev2` | `~/ai-hub` | Execution fix (SyntaxError, model routing) | ✅ Completed root-cause fixes | **Step 1**: runtime rules → guarantees. A crítica "types without wiring" paralela ao gap de orphaned guarantees. |
| 5 | `ai-hub-generator-refactor` | `~/ai-hub` | Merge resilience motor + pure package | ✅ Integrated (Phase 3) | **Bead claim/close**: usar `bd claim` antes de editar skills em `~/agents`; `bd close` após validação. |
| 6 | `integrated-stabilization-plan` | multi-repo | Master coordination | ✅ Active | **Phase 4** = este plano. Implementar Steps 1-10 em `precoce/` modules. Coordenar fases. |
| 7 | `workspace-consolidation-integrated-plan` | multi-repo | Workspace paths | ✅ Done | `~/` paths consolidados. `~/agents` é `~/agents`. |
| 8 | `gt-up-vm-explosion` | `~/gastown` | Daemon pressure gating | ✅ Code fixes proposed | **Step 11**: capability-selection rule (Phase 1). O bug de `isAgentSession` confirma necessidade do capability-selection rule. Gas Town runtime SUSPENSO — não executar, apenas planejar. |
| 9 | `recover-fix-gt-bd-doctor-issues` | `~/gastown` | Fix gt/bd doctors | ❌ Cancelled | N/A — GT suspensa. |
| 10 | `skills-cohesion-gastown` | `~/agents` | Remove non-canonical bead/gt/dolt refs | ✅ Complete (2 edits) | **Step 7**: gascity rule move. AGENTS.md já foi limpo. Mas `CLAUDE.md` do `~/agents` ainda referencia "local Dolt DB" — precisa verificar se foi corrigido. |
| 11 | `assume-sweep-dedicated-agent` | `~/gastown` | Bead sweep do Mayor | ✅ Executed (persistido) | Cross-plan tracking via beads. O epic `agents` foi criado em `hq` db. |
| 12 | `connect-poolside-openai-api` | `~/.ccs` | CLIProxy model routing | ⚠️ In progress | **Coordenação cliproxy-mgmt**: o `projections.json` define quais providers recebem skills. CLIProxy é um provider — precisa garantir que skills de routing/model são propagadas via `agentsctl sync` para o diretório do CLIProxy. |
| 13 | `build-idempotent-incremental-publish` | `~/cosmos-docgen` | Build idempotency | ✅ Complete | N/A — cosmos-docgen, não governance. |
| 14 | `datacosmos-padronizacao-layouts` | `~/cosmos-docgen` | UX standardization | ⚠️ Pending | N/A — dcdoc, não governance. |

#### Conflitos críticos de coordenação

1. **Skill distribution duplication** (ai-hub `ssot_relink` vs `agentsctl sync`):
   - `agent_skills()` projeta diretamente para `<agent_home>/skills/` (ex: `~/.claude/skills/caveman/`)
   - `agentsctl sync` (personal context) projeta para o MESMO path (`${HOME}/.claude/skills/caveman/`)
   - **Solução**: Unificar em um único mecanismo. O `agent_skills()` deve ser removido ou convertido em uma chamada a `agentsctl sync` após o `ssot_relink` hub step completar. O `~/agents` deve ser o único projeta para provider directories.

2. **Nomeação de skills divergente** (ai-hub vs `~/agents`):
   - ai-hub: `inviolable-rules` (bundle: `governance/rules`) ↔ `~/agents`: não existe equivalente direto (closest: `architecture/engineering-core`)
   - ai-hub: `make-check` (bundle: `governance/make`) ↔ `~/agents`: não existe
   - ai-hub: `beads-orchestrator` ↔ `~/agents`: `tool/beads-orchestrator` ✅
   - ai-hub: `caveman` ↔ `~/agents`: `agent-wide/caveman` ✅
   - **Solução**: Adicionar campo `canonical_skill` em `config/skills.yaml` que mapeia para o nome canônico do `~/agents` catalog. Skills sem equivalente no `~/agents` precisam ser criadas.

3. **Orquestração Gas City suspensa**:
   - AGENTS.md do `~/agents` declara: "Gas City runtime is currently suspended"
   - `integrated-stabilization` confirma: "Gas Town runtime is SUSPENSO"
   - **Implicação**: Steps 6-7 (mover `gascity` rule, mapear Gas City skills) devem ser feitos como mudanças estáticas/documentais — não requerem execução de `gt`/`bd` comandos
   - **Coordenação**: O `skills-cohesion-gastown` plano completou a limpeza de referências não-canônicas. O `gascity` rule move deve ser parte do mesmo cutover AGENTS.md + CLAUDE.md.

4. **cliproxy-mgmt**:
   - `connect-poolside-openai-api` conecta Poolside AI API ao CCS via CLIProxy (porta 8317)
   - `services.yaml` declara `ccs-cliproxy.service` + `ai-hub-model-pipeline.service` (conecta ao cliproxy)
   - **Coordenação**: O CLIProxy não é um "agent" no `projections.json` — ele é um serviço. Mas skills que gerenciam model routing devem ser propagadas via `agentsctl sync` para o diretório do CLIProxy. Verificar se `~/.ccs` tem um `.ccs/skills/` equivalente.

5. **Bead claim + branch finalization**:
   - `ai-hub-generator-refactor` e `assume-sweep-dedicated-agent` usam `bd claim`/`bd close` para gestão de trabalho
    - **Coordenação**: Antes de implementar Steps 1-10, claimar um bead no `~/agents` repo. Após cada step + validação (`agentsctl check` green), atualizar o bead. Ao final, `bd close` com evidence.

6. **Fork management**:
   - `workspace-consolidation` lista 9 workspaces com remotes: `marlon-costa-dc/*`, `datacosmos-br/*`, `flext-sh/*`
   - O `~/agents` repo é `marlon-costa-dc/agents` e não é fork (`.parent` = null)
    - **Coordenação**: PRs para `~/agents` vão para `marlon-costa-dc/agents` → `main`. Não para `datacosmos-br/`.

> **Escopo**: Os itens de coordenação cross-repo que dependem de `~/ai-hub`
> (`ssot_relink`, `canonical_skill` em `config/skills.yaml`, triggers no
> `ai-hub-watch` daemon, projeção `~/.ccs`) foram removidos deste documento
> por pertencerem ao repositório `~/ai-hub`, não a `~/agents`. Acompanhe-os no
> lado `~/ai-hub`. Os Steps 1–10 acima cobrem todo o trabalho in-scope de
> `~/agents`.
