# Governance interconnection analysis — TODO

> Status: `PLANNED` (plan mode — no source modifications)
> Plan file: `/home/marlonsc/.local/state/poolside/plans/governance-interconnection-gaps-plan-47e5a9b.md`

## Resumo

`config/governance.json` é a **única** camada explícita de interconexão entre
`rules/`, `skills/`, `commands/` e `AGENTS.md`. Ele mapeia 49 "garantias"
semânticas para seus proprietários (rule, skill, command, ou document). A
pesquisa abaixo identifica gaps, duplicações, inconsistências e interligações
ausentes, com propostas de melhoria para execução futura.

## Escopo de análise

- **Rules**: 39 arquivos em `rules/` (14 subdirectories + 5 root-level)
- **Skills**: 82 bundles em `skills/` (6 categories: agent-wide, project-wide, technology, framework, tool, domain)
- **Commands**: 8 flat files em `commands/`
- **Guarantees**: 49 mappings em `config/governance.json`
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

### 4. Análise de cobertura de testes existentes

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

Análise dos 14 planos em `/home/marlonsc/.local/state/poolside/plans/` para
identificar alinhamentos, conflitos, e oportunidades de coordenação.

### Planos diretamente alinhados (mesmo repositório: `~/.agents`)

| Plano | Workspace | Relevância para governança | Ponto de alinhamento |
|---|---|---|---|
| `flext-strict-c-t-p-m-u-hARMONIZATION` | `~/.agents` | Harmonia de código Python na `src/agents_governance/`. Referencia `rules/python.md` como fonte de law | ✅ **Conflito potencial**: Ambos propõem reorg do root-level rule anomaly (`python.md` ↔ `gascity.md`). O plano flext deve usar `rules/python/config-settings-ssot.md` após reorganização. |
| `skills-cohesion-gastown` | `~/.agents` | Limpeza de skills/docs/AGENTS.md de Gas Town. Referencia `skills/beads/SKILL.md` e contexto `rules/gascity.md` | ✅ **Complementar**: Propõe limpeza de skills; meu plano propõe guarantee coverage para as skills gascity-* e gascity rule. Deve ser feito no mesmo cutover. |

### Planos indiretamente relacionados (outros workspaces, referenciam `~/.agents`)

| Plano | Workspace | Relevância | Ponto de alinhamento |
|---|---|---|---|
| `ai-hub-puro-dev-beads` | `~/.ai-hub` | Runtime package. Declara `~/.agents` como SSOT | ✅ **Dependência**: O runtime package (`ai-hub install|generate-configs|...`) depende da integridade do guarantee map. Mudanças no governance.json afetam a projeção. |
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
   skills ao guarantee map. Ambas as mudanças no `~/.agents` devem ser
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
| Landing | `ai-hub-puro-dev-beads` (runtime) | `~/.agents` governance.json deve ser validado antes do runtime package depender nele |
| Post-landing | todos os planos | Re-validate `agentsctl check` + `make test` no repo `~/.agents` antes de propagar para consumer projects |
