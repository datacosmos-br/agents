# Plano de migração do workflow de desenvolvimento → Gas City

**Data:** 2026-08-30 · **Autor:** sessão Hermes · **Status:** F0 aplicado; F1 aplicado (F1.1–F1.3 aterrissados, F1.4 em PRs); F2–F4 pendentes

Avaliação do estado real medido + plano de cutover.

## Registro de execução (revisão 2026-08-30)

| Fase | Estado | Evidência |
|---|---|---|
| Tracker | **feito** — 18 beads sob o epic `ag-cj6`, com grafo de dependência | `bd show ag-cj6` |
| F0 | **aplicado e validado** (`ag-cj6.1` fechado) | `agentsctl check`/`doctor` exit 0; `waza` 41/41; grep de `suspend\|gt\|polecat` em `~/gc/AGENTS.md` = 0 |
| F1.1/F1.2/F1.3 | **aterrissado** — por outros atores: ai-hub PR #622 (merge `9fde3679` em `dev`, fecha `ag-cj6.2`), cosmos-main `988ae8e5` (em `develop`, fecha `ag-cj6.3`/`ag-cj6.15`), ccs `7b22df34` (em `main`, fecha `ag-cj6.4`) | fechamentos `ag-cj6.2/.3/.4/.15` com 4 fontes (2026-09-02) |
| F1.4 | **em review** — PRs [cosmos-main #214](https://github.com/datacosmos-br/cosmos-main/pull/214), [ccs #26](https://github.com/marlon-costa-dc/ccs/pull/26), [mcb #233](https://github.com/marlonsc/mcb/pull/233) (branch `docs/gascity-naming-sweep`, commits escopados; ccs fast pre-push gate 384 testes OK) | bead `ag-cj6.16` fecha após os merges |
| F2–F4 | não iniciado (F2: `ag-cj6.5`–`.11`; F3: `.12`/`.13`/`.17`; F4.8 hermes feito) | F2 depende de F1 merge |

**Achados que a execução revelou e esta versão do plano incorpora:**

- **ADR-134 do cosmos-main declara Gas Town owner das lanes** (L89-90, L105,
  L140-142, L160) e é a autoridade que o próprio `AGENTS.md` cita. Corrigir só o
  `AGENTS.md` deixaria a fonte citada contradizendo a lei nova. Novo bead
  `ag-cj6.15` (F1.2b), bloqueia o piloto.
- **A referência legada vai além dos `AGENTS.md`**: arquivos em `docs/`/`skills/`
  com `gt <verbo>`/"Gas Town" (excluindo URLs `gastownhall`) — ai-hub 7,
  cosmos-main 16, ccs 1, flext 2, mcb 1. Novo bead `ag-cj6.16` (F1.4).
- **cosmos-main está 6 commits atrás de `origin/develop`** com working tree sujo
  (submódulos, ADRs, `.beads/issues.jsonl` deletado). Novo bead `ag-cj6.17`
  (F3.0), bloqueia a propagação.
- **`bd ready` não aceita `--flat`** (só `bd list` aceita). Correção de fato
  contra a skill `beads`.
- Escrita em `AGENTS.md` exige aprovação interativa do operador; um plano que
  assume edição autônoma desses arquivos está errado por construção.

---

## Parte I — Avaliação do estado atual (medido)

### I.1 A city está viva e saudável — a lei diz que não

`gc doctor --check-timeout 20s` em `~/gc` (248 linhas, exit 0):

```
216 passed, 14 warnings, 4 failed, 4 advisory
```

Os 4 `✗` são **todos timeout de check**, não defeito de estado:
`v2-routed-to-namespace`, `run-target-routed-to-backfill`, `hold-label-routed-to`,
`work-option-metadata-migration` — "timed out after 20s and was abandoned
(outcome unknown)". Sem o `--check-timeout` reduzido, `gc doctor` **não termina
em 180s**. Store: `NativeDoltStore`, `native_store_eligible: true`. Controller
supervisor-managed PID 98454, `suspended: false`, `health.usable: true`.

Sessões vivas agora (`gc session list`): 15, incluindo `mayor` e
`core.control-dispatcher` com 1 dia de idade, 7 `core.control-dispatcher` de rig,
6 `gc.issue-triager` e um `aihub/gc.implementation-worker` ativo há 30min.

**O drift:** `~/gc/AGENTS.md` descreve a city como *"Gas City migration
workspace… owns the one-time logical migration"* e `rules/coordination/gascity.md`
condiciona quase tudo a *"while its runtime is suspended"*. A city não está
suspensa e não está migrando — está operando. **A lei descreve um estado que
acabou.**

### I.2 O trabalho real não passa pelo `gc`

| Repo | branch atual | esperado | worktrees |
|---|---|---|---|
| ai-hub | `fix/forge-governance-permission-contract` | dev | **6** |
| flext | `fix/untrack-beads-runtime-metadata` | 0.12.0-dev | 3 |
| cosmos-main | develop ✓ | develop | 3 |
| mcb | `merge-rustsec-to-develop` | develop | 2 |
| agents | dev ✓ | dev | 2 |
| gmn | `fix/regenerate-and-declare-beads-identity` | 0.12.0-dev | 1 |
| invest | `fix/the-gitmodules-topology-names-the-role` | dev | 1 |
| ccs | `fix/conflict-marker-self-match-and-governance` | main | 1 |
| cosmos-docgen | `fix/typed-route-contract` | dev | 1 |

7 de 9 rigs fora do branch default, com worktrees hand-rolled. `gc doctor` marca
cada um como `⚠ rig:<x>:root-branch … (advisory)`. Existem ainda diretórios de
lane fora da city: `~/ai-hub-worktrees`, `~/aihub-worktrees`, `~/flext-worktrees`,
`~/codex-worktrees`, `~/gc-worktrees`.

**Diagnóstico:** a city roda `issue-triager` e `control-dispatcher`, mas o
trabalho de implementação é feito em lanes manuais. A orquestração está ligada e
ociosa; o desenvolvimento acontece ao lado dela.

### I.3 A lei dos repos manda rodar um binário que não existe

`gt` não resolve: `mise ERROR No version is set for shim: gt`.

| Repo | linha | conteúdo |
|---|---|---|
| ai-hub | AGENTS.md L40-42 | "`gc sling <bead>` spawns a **polecat** worktree/branch · polecat commits, runs **`gt done`** → merge queue · **Refinery** rebases, verifies, merges" |
| ai-hub | L47 | bloco de comandos com `gt done` |
| ai-hub | L51 | "the **Refinery** owns merges to the default branch" |
| ai-hub | L54 | "uses the rig's persistent **`crew/<name>`** workspace" |
| cosmos-main | L25-26 | "**Gas Town** owns branch, worktree, hook, merge queue… start through **`gt sling <bead> cosmos`** and finish through **`gt done`**" |
| cosmos-main | L107, L163 | "Gas Town creates and owns work branches… follow the **Gas Town lifecycle**" |
| ccs | L153-157 | "**`gt prime`** loads the current lifecycle, **`gt hook`** identifies the assigned bead… finish with **`gt done`**" |

O `AGENTS.md` do ai-hub é o pior caso: **mistura `gc sling` com `gt done` na mesma
lista** — uma lane que ninguém consegue completar. cosmos-main L25 proíbe
explicitamente `make`/`git worktree` e manda usar `gt sling`, que não existe:
**a lei bloqueia o único caminho que funciona hoje.**

`flext`, `gmn`, `invest`, `beads`, `mcb` só têm menções inertes (URLs
`gastownhall/beads`, que são o repo correto do Beads). `~/agents/AGENTS.md`: limpo.

### I.4 Skills em `~/agents` — o que orienta o caminho

92 skills. As que governam este workflow:

| Skill / rule | Papel | Estado |
|---|---|---|
| `rules/coordination/gascity.md` | **owner** da fronteira Gas City | correto no modelo, **preso em "suspended"** |
| `rules/coordination/beads-verification.md` | cross-check de 4 fontes | válido, é a espinha |
| `rules/workflow/canonical-commands.md` | superfície canônica só | válido |
| `skills/tool/gascity-change-lifecycle` | ciclo de mudança | **texto inteiro condicionado a "while runtime is suspended"** |
| `skills/tool/gascity-workspace-lifecycle` | placement de workspace | idem |
| `skills/domain/gascity/gc-dispatch` | `gc sling`, formulas | **references citam 9 formulas inexistentes** |
| `skills/domain/gascity/gc-work` | beads, claim/close | ok |
| `skills/domain/gascity/gc-{city,rigs,agents,mail,dashboard}` | superfícies | ok, não auditadas em detalhe |
| `skills/domain/gascity/gascity-docs` | estilo de docs | ok |
| `skills/tool/beads-{orchestrator,worker}` | papéis separados | ok |

**Formulas citadas que NÃO existem na city** (`gc formula list` = 42; grep em
`skills/**/*.md`):

| Formula fantasma | Citada em |
|---|---|
| `mol-polecat-work` | `gc-dispatch/references/formulas.md` |
| `mol-port-review` | `gc-dispatch/references/formulas.md` |
| `mol-refinery-patrol` | `gc-dispatch/references/legacy-formulas.md` |
| `mol-witness-patrol` | idem |
| `mol-deacon-patrol` | idem |
| `mol-idea-to-plan` | idem |
| `mol-digest-generate` | idem |
| `mol-review-leg` | idem |
| `mol-shutdown-dance` | idem |

Existem e são citadas corretamente: `mol-do-work`, `mol-scoped-work`,
`mol-polecat-{base,commit,report}`, `mol-review-quorum`, `mol-prompt-synth`.

Vocabulário legado no corpo das skills: **polecat 26×, refinery 16×**, mayor 7×,
witness/deacon/crew 1× cada. O `AGENTS.md` do repo gascity classifica nome de role
hardcoded como bug; `mol-polecat-*` sobrevive só como *nome de formula do core
pack*, não como role.

`gc-dispatch/references/formulas.md` L36-46 descreve o "refinery handoff" como
mecânica ativa — **não existe agente refinery em nenhum rig**. `gc agent list`
mostra 12 roles `gc.*` por rig, e nenhum se chama refinery, polecat, witness,
deacon ou reaper.

### I.5 Governança e gates que precisam mover junto

`~/agents` (branch `dev`, HEAD `e6bc298`) — runtime `uv run agentsctl`
(verbos: `help doctor check sync evaluate secure clean live`), Makefile com
`check`, `waza`, `static`, `spec`, `coverage`, `test`, `projection`.

- `config/governance.json` — bootstrap de 5 rules + 9 skills. **Nenhuma skill
  gascity está no bootstrap** (são `activation:opt-in`, `usage:on-demand`).
- `evals/` tem suítes dedicadas: `gascity-change-lifecycle`,
  `gascity-workspace-lifecycle`, `gascity-docs`, `gc-agents`, `gc-city`,
  `gc-dashboard`, `gc-dispatch`, `gc-mail`, `gc-rigs`, `gc-work`,
  `commands/inspection/gc-session-triage`. Cada uma com
  `basic-usage` / `edge-case` / `should-not-trigger`.
  **Toda edição de skill exige a eval correspondente no mesmo commit.**
- `waza` impõe teto de tokens (router ≤500, references ≤2000).

### I.6 Estado do tracker

`bd count` em `~/agents`: 34. City store (do doctor): **416 open, 131 claimable,
15 control-plane**. Um bead legado: `ag-rig-agents [gt:rig]` — label `gt:` do
runtime antigo. Warnings relevantes: `≥501 closed order-tracking beads`
(retention watchdog), `9 dangling owner_bead references`, `34 formula requirement
warnings`, `fork-rate 352 forks/s`.

### I.7 Skill Hermes desatualizada

`~/.hermes/skills/cosmos-systems/SKILL.md` ainda declara `gt = Gas Town; gt prime
lifecycle, gt done closes lanes` e "rigs per project under `~/ccs/<town>`" (falso
— rigs são os repos, registrados em `~/gc/city.toml`).

---

## Parte II — Os cinco problemas, em ordem de dano

| # | Problema | Dano | Evidência |
|---|---|---|---|
| **P1** | Lei manda `gt` (inexistente) em ai-hub/cosmos-main/ccs | agente trava ou improvisa; cosmos-main proíbe o único caminho viável | §I.3 |
| **P2** | Trabalho real em lanes manuais, fora do `gc` | sem evidência no tracker, sem review handoff, 7/9 rigs off-branch | §I.2 |
| **P3** | Skills citam 9 formulas e 2 roles que não existem | agente sling num alvo inexistente e falha | §I.4 |
| **P4** | `rules/coordination/gascity.md` congelado em "suspended" | a lei nega o estado operacional real | §I.1 |
| **P5** | `gc doctor` >180s | ninguém roda o gate; drift acumula silencioso | §I.1 |

**Ordem obrigatória:** P1 antes de P2 (não dá para mandar usar `gc` enquanto a lei
manda `gt`). P3 e P4 antes de P2 (o agente precisa de skills verdadeiras antes de
receber trabalho). P5 é paralelo.

---

## Parte III — Plano de migração

Cinco fases. Cada uma tem gate de saída verificável. **Nenhuma fase avança com a
anterior vermelha.**

### F0 — Reconhecer o fim da migração (bloqueia tudo)

**Owner:** `~/gc/AGENTS.md` + `rules/coordination/gascity.md`

| # | Ação | Arquivo |
|---|---|---|
| F0.1 | Reescrever `~/gc/AGENTS.md`: de "migration workspace" para **contrato operacional de city ativa**. Preservar: `managed_city`, `BEADS_DIR`, verificação de 4 fontes, proibições de Dolt. Remover: enquadramento de migração, "former runtime". | `~/gc/AGENTS.md` |
| F0.2 | Em `rules/coordination/gascity.md`, trocar o eixo "activation state is resolved" de **suspended-por-default** para **ativo-por-default com escopo declarado**. A regra já diz "resolve at preflight for that exact city" — só o exemplo está invertido. | `~/agents/rules/coordination/gascity.md` |
| F0.3 | Registrar em `~/gc/AGENTS.md` a lista de rigs ativos e seu branch de integração (é o que `gc doctor` valida). | `~/gc/AGENTS.md` |

**Gate F0:** `uv run agentsctl check` verde em `~/agents`; `gc doctor` sem regressão.

---

### F1 — Purgar `gt` da lei dos repos

**Owner:** `AGENTS.md` de cada repo. **Nenhum toca código.**

| # | Repo | Mudança exata |
|---|---|---|
| F1.1 | **ai-hub** | Substituir L36-59. `gc sling <rig>/<role> <bead> --on <formula>`; remover `gt done`, "polecat", "Refinery … owns merges". Definir o fechamento real: worker → gate nativo → PR → merge na lane de integração. L54: `crew/<name>` → workspace do formula. |
| F1.2 | **cosmos-main** | L24-27: `gt sling <bead> cosmos` → `gc sling cosmos/<role> <bead> --on <formula>`; `gt done` → fecho por bead+PR. L107, L163: "Gas Town" → "Gas City". Manter a proibição de lane manual — ela passa a ser cumprível. |
| **F1.2b** | **cosmos-main ADR-134** | `ADR_134_DEVELOP_INTEGRATION_BRANCH_AND_EPIC_LANES.md` L89-90, L105, L140-142, L160 declaram Gas Town owner das lanes. É a autoridade que o `AGENTS.md` cita — corrigir só o `AGENTS.md` deixa a fonte contradizendo a lei. Emendar ou supersede conforme a política de ADR do repo. Referenciada por 10 arquivos em `docs/`. |
| F1.3 | **ccs** | L150-160: `gt prime` → `gc prime`, `gt hook` → `gc hook --claim --json`, `gt done` → fecho por bead+PR. L117: "Gas Town workspace" → "Gas City rig". |
| **F1.4** | **docs/ e skills/** | Varredura além dos `AGENTS.md`: ai-hub 7 arquivos, cosmos-main 16, ccs 1, flext 2, mcb 1 (excluindo URLs `gastownhall`). Não bloqueia o piloto, mas mantém a lei contraditória em docs secundários. |
| F1.5 | flext, gmn, invest, mcb, beads | Sem ação nos `AGENTS.md`. Menções são URLs `gastownhall/beads` (repo correto do Beads). |

**Os patches exatos de F1.1–F1.3 estão prontos em
[`patches-f1-purgar-gt.md`](patches-f1-purgar-gt.md)** e aguardam aprovação do
operador — `AGENTS.md` é arquivo protegido e não pode ser escrito autonomamente.

**Gate F1:** nenhum `AGENTS.md` de rig contém `gt <verbo>`, `polecat`, `refinery`,
`witness`, `deacon` como mecânica ativa. Verificação:

```bash
for d in ~/ai-hub ~/cosmos-main ~/ccs ~/flext ~/gmn ~/invest ~/mcb ~/beads ~/agents; do
  grep -nEi '\bgt (sling|done|prime|hook|convoy)\b|polecat|refinery|witness|deacon' $d/AGENTS.md
done   # esperado: vazio
```

---

### F2 — Corrigir as skills que orientam o caminho

**Owner:** `~/agents`. Cada edição de skill exige sua eval no mesmo commit (§I.5).

| # | Alvo | Mudança |
|---|---|---|
| F2.1 | `skills/domain/gascity/gc-dispatch/references/legacy-formulas.md` | **Deletar.** Todas as 7 formulas que descreve não existem. É o arquivo que mais engana. |
| F2.2 | `.../gc-dispatch/references/formulas.md` | Remover `mol-polecat-work` e `mol-port-review`. Manter e verificar: `mol-do-work`, `mol-scoped-work`, `mol-polecat-{commit,report}`, `mol-review-quorum`. Reescrever a seção "refinery handoff" — **não há refinery**; o fechamento é bead + PR na lane. |
| F2.3 | `.../gc-dispatch/references/dispatch-commands.md` | Trocar exemplos `hello-world/polecat`, `hello-world/refinery` pelos roles reais: `<rig>/gc.implementation-worker`, `<rig>/gc.implementation-reviewer`, `<rig>/gc.issue-triager`. |
| F2.4 | `.../gc-dispatch/references/router-procedure.md` | L56 "Polecats — ephemeral worker activity" → linguagem de sessão/pool. |
| F2.5 | `skills/tool/gascity-change-lifecycle/SKILL.md` | Reescrever para a city **ativa**: preflight, dispatch, evidência, fechamento. Manter o bloco de verificação de 4 fontes intacto. |
| F2.6 | `skills/tool/gascity-workspace-lifecycle/SKILL.md` | Idem: placement derivado do formula, não "no effect while suspended". |
| F2.7 | **Nova** `skills/domain/gascity/gc-roles` | Os 12 roles reais do pack `gascity/roles` e quando slingar cada um. **Não existe hoje** — é o buraco que faz o agente cair no vocabulário do Gas Town. |
| F2.8 | `evals/gascity-*`, `evals/gc-dispatch` | Atualizar `output_contains` para casar as descrições novas; adicionar `should-not-trigger` que **falha se a resposta mencionar polecat/refinery/gt**. |

**Gate F2:**
```bash
cd ~/agents && make check && make waza && make spec && uv run agentsctl doctor
# + grep de formula fantasma:
```
```bash
gc formula list > /tmp/f.txt
grep -rhoE 'mol-[a-z0-9-]+' ~/agents/skills/ | sort -u | while read m; do
  grep -qx "$m" /tmp/f.txt || echo "FANTASMA: $m"; done   # esperado: vazio
```

---

### F3 — Mover o trabalho para dentro da city (piloto → frota)

Só depois de F1+F2 verdes. **Um rig por vez, verificado antes do próximo** — é o
que `rules/coordination/gascity.md` já manda ("resume rigs one at a time").

| # | Ação |
|---|---|
| F3.1 | **Escolher o rig piloto.** Recomendo `mcb` (1 bead aberto, 2 worktrees, menor blast radius) ou `agents` (já em `dev`, e é onde a governança vive — dogfood). **Não** ai-hub (6 worktrees, lane complexa em voo). |
| F3.2 | Fechar as lanes manuais em voo do piloto: cada worktree ou vira PR na lane de integração, ou é absorvido. Zero residue antes do cutover. |
| F3.3 | Rodar o ciclo completo **uma vez**, ponta a ponta, com um bead real: `gc bd create --rig <rig>` → `gc sling <rig>/gc.implementation-worker <bead> --on mol-scoped-work` → observar `gc session logs` → verificar as 4 fontes → fechar. |
| F3.4 | Registrar o que quebrou. Cada defeito vira bead no owner (skill, rule, formula, ou o próprio `gc`), **nunca workaround na lane**. |
| F3.5 | Repetir o ciclo até verde duas vezes seguidas sem intervenção manual. |
| F3.6 | Só então propagar rig a rig, na ordem: `agents` → `gmn` → `invest` → `ccs` → `cosmos-docgen` → `flext` → `cosmos-main` → `ai-hub` (mais complexo por último). |

**Gate F3 por rig:** `gc doctor` sem `⚠ rig:<x>:root-branch`; sem worktree órfão;
bead fechado com evidência das 4 fontes.

**Ponto honesto:** o fluxo de `gc sling` até merge **não foi exercitado nesta
sessão**. F3.3 é onde se descobre se a formula, o role e o gate nativo do repo
realmente compõem. Tratar como spike, não como rollout.

---

### F4 — Higiene operacional (paralelo, não bloqueia)

| # | Ação | Evidência |
|---|---|---|
| F4.1 | Investigar os 4 checks que estouram 20s (`v2-routed-to-namespace`, `run-target-routed-to-backfill`, `hold-label-routed-to`, `work-option-metadata-migration`). São queries de migração de schema sobre 416 beads — provável full scan. **Bead no rig `gct`** (repo gascity). | `gc doctor` termina <60s |
| F4.2 | `≥501 closed order-tracking beads` — retention watchdog. Confirmar se `order-tracking-sweep` está rodando. | warning some |
| F4.3 | 9 `dangling owner_bead references` em resource-census | check verde |
| F4.4 | 34 formula requirement warnings | triado |
| F4.5 | `fork-rate 352 forks/s` — investigar qual processo | identificado |
| F4.6 | Bead `ag-rig-agents` com label `[gt:rig]` — relabel ou fechar obsoleto | sem label `gt:` |
| F4.7 | `jsonl-archive` em local-only — decidir se quer backup off-box | decisão registrada |
| F4.8 | Atualizar `~/.hermes/skills/cosmos-systems` (declara `gt` ativo e caminho de rig errado) | skill correta |

---

## Parte IV — Beads propostos

Nenhum criado. Prefixo sugerido `ag-` (rig `agents`), exceto F4.1 → `gct`.

| Bead | Título | P | Depende de |
|---|---|---|---|
| `ag-cj6` | **[epic]** Cutover do workflow de desenvolvimento para Gas City | 1 | — |
| `ag-cj6.1` | F0 — Reescrever `~/gc/AGENTS.md` e rule gascity para city ativa | 1 | — ✅ **fechado** |
| `ag-cj6.2` | F1.1 — ai-hub: purgar `gt done`/polecat/refinery | 1 | F0 ✅ **fechado** (PR #622) |
| `ag-cj6.3` | F1.2 — cosmos-main: `gt sling`/`gt done` → `gc` | 1 | F0 ✅ **fechado** (`988ae8e5`) |
| `ag-cj6.15` | F1.2b — cosmos-main ADR-134 declara Gas Town owner | 1 | — ✅ **fechado** (emenda em `develop`) |
| `ag-cj6.4` | F1.3 — ccs: `gt prime`/`gt hook`/`gt done` → `gc` | 1 | F0 ✅ **fechado** (`7b22df34`) |
| `ag-cj6.16` | F1.4 — varredura de `docs/` e `skills/` | 2 | — 🔁 em review (PRs #214/#26/#233) |
| `ag-cj6.5` | F2.1 — Deletar `legacy-formulas.md` | 1 | F0 |
| `ag-cj6.6` | F2.2 — Corrigir `formulas.md`, reescrever refinery handoff | 1 | F2.1 |
| `ag-cj6.7` | F2.3 — Exemplos de dispatch com roles reais | 2 | F2.2 |
| `ag-cj6.8` | F2.5 — Reescrever `gascity-change-lifecycle` | 1 | F0 |
| `ag-cj6.9` | F2.6 — Reescrever `gascity-workspace-lifecycle` | 2 | F0 |
| `ag-cj6.10` | F2.7 — Nova skill `gc-roles` | 1 | F2.2 |
| `ag-cj6.11` | F2.8 — Evals + guard anti-vocabulário-legado | 1 | F2.2 |
| `ag-cj6.17` | F3.0 — cosmos-main 6 commits atrás, worktree sujo | 2 | — |
| `ag-cj6.12` | F3.1 — Piloto ponta a ponta em um rig | 1 | F1.1, F1.2, F1.3, F1.2b, F2.8 |
| `ag-cj6.13` | F3.6 — Propagar rig a rig | 2 | F3.1, F3.0 |
| `ag-cj6.14` | F4.6 — Fechar/relabelar bead `ag-rig-agents [gt:rig]` | 3 | — ✅ **fechado** |
| `gct-1ev0z` | F4.1 — 4 doctor checks estouram timeout (**rig gct**) | 2 | — |

Grafo: `bd dep tree ag-cj6`. F4.1 vive no rig `gct` (repo gascity) porque o
defeito é do `gc doctor`, não da governança.

---

## Parte V — Riscos

| Risco | Mitigação |
|---|---|
| **F3 revela que a formula não fecha o ciclo** (sling→PR→merge nunca foi exercitado aqui) | F3 é spike num rig só; defeito vira bead no owner, não workaround |
| **`AGENTS.md` exige aprovação interativa** — o agente não edita esses arquivos sozinho | patches prontos em `patches-f1-purgar-gt.md`; o operador aplica ou aprova. **Confirmado na execução de 2026-08-30.** |
| **Autoridade citada contradiz a lei corrigida** (ADR-134 ↔ `AGENTS.md` do cosmos-main) | F1.2b corrige a ADR junto; regra geral: ao corrigir um `AGENTS.md`, seguir cada fonte que ele cita |
| **7 lanes manuais em voo** | F3.2 exige fechar as do piloto antes; os outros rigs continuam manuais até sua vez |
| **Editar skill sem editar eval** quebra `make spec` | F2.8 no mesmo commit; `make check && make waza && make spec` antes do push |
| **`gc doctor` lento esconde regressão durante o cutover** | F4.1 (`gct-1ev0z`) em paralelo; enquanto isso usar `--check-timeout 20s` e aceitar os 4 abandonados |
| **`~/agents` é rig da city**: o pack runtime reprojeta `.claude/skills`/`.codex/skills` sozinho | guard já existe e deve assertar o que o **Git** carrega, nunca ausência em disco |
| **Cutover parcial** = pior que nenhum (lei nova, hábito velho) | ordem F1→F2→F3 é obrigatória; sem F1 a lei continua impossível |

---

## Parte VI — Verificação de fechamento

O cutover está completo quando, simultaneamente:

1. Nenhum `AGENTS.md` de rig referencia `gt <verbo>` ou role do Gas Town como mecânica ativa.
2. Toda formula citada nas skills existe em `gc formula list`.
3. `cd ~/agents && make check && make waza && make spec && uv run agentsctl doctor` verde.
4. `gc doctor` termina sem timeout e sem `⚠ rig:*:root-branch`.
5. Pelo menos um bead por rig foi criado, slingado, executado e fechado **pela
   city**, com as 4 fontes declaradas.
6. Nenhum worktree manual fora do que o formula criou.

Itens 1-3 são estáticos e verificáveis hoje. **4-6 exigem execução real** — são o
critério que separa "lei corrigida" de "workflow migrado".
