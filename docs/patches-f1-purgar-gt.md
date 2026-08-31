# Patches F1 — purgar `gt` da lei dos repos

Preparados em 2026-08-30. **Não aplicados**: `AGENTS.md` é arquivo protegido e a
aprovação do operador expirou sem resposta.

Cada bloco abaixo é uma substituição exata. Beads: `ag-cj6.2` (ai-hub),
`ag-cj6.3` (cosmos-main), `ag-cj6.4` (ccs).

Gate de saída, após aplicar os três:

```bash
for d in ~/ai-hub ~/cosmos-main ~/ccs ~/flext ~/gmn ~/invest ~/mcb ~/beads ~/agents; do
  echo "$(grep -cEi '\bgt (sling|done|prime|hook|convoy)\b|polecat|refinery|witness|deacon' $d/AGENTS.md)  $(basename $d)"
done   # esperado: 0 em todos
```

---

## F1.1 — ai-hub (`~/ai-hub/AGENTS.md` linhas 36-59)

O pior caso: mistura `gc sling` com `gt done` na mesma lista, produzindo uma lane
que ninguém consegue fechar.

### Substituir

```markdown
## Lane lifecycle

gascity owns the whole lane lifecycle. This project owns config, services, MCP, CRG, and workspace policy. Work flows through the rig's canonical gascity surface:

- `gc sling <bead>` spawns a polecat worktree/branch
- polecat commits, runs `gt done` → merge queue
- Refinery rebases, verifies, merges and closes the bead

```bash
gc sling <bead-id> <rig>
gc hook status
gt done
gc convoy status
```

This project must not create worktrees or branches itself, push, or open pull requests manually; the Refinery owns merges to the default branch. Stop at the integration lane unless the operator explicitly asks to promote.

An explicit operator-authorized manual execution while gascity is stopped uses
the rig's persistent `crew/<name>` workspace. It must never clone or materialize
a lane under `/tmp`, and must not place virtual environments, compiler caches,
test caches, database copies, or package caches inside the crew checkout. The
manual owner records disk usage before and after, publishes every recoverable
commit, and removes the crew workspace when the operator-declared exception
ends. See `UNIVERSAL_CORE.md` Law 13 and `docs/worktrees.md`.
```

### Por

```markdown
## Lane lifecycle

Gas City owns the whole lane lifecycle. This project owns config, services, MCP,
CRG, and workspace policy. Work flows through the rig's canonical Gas City
surface:

- `gc bd create "<title>" --rig aihub` files the work in this rig's store
- `gc sling aihub/<role> <bead-id> --on <formula>` routes it to a configured agent
- the formula owns the workspace, the branch, and their teardown
- the worker implements, runs the native gates, and records evidence on the bead
- landing is a PR onto this repository's integration lane, reviewed and merged there

```bash
gc bd create "<title>" --rig aihub
gc sling aihub/gc.implementation-worker <bead-id> --on <formula>
gc hook --claim --drain-ack --json     # how an agent finds its own work
gc status ; gc session logs <name> ; gc convoy status <id>
```

This project must not create worktrees or branches itself for dispatched work;
the formula owns them. Stop at the integration lane unless the operator
explicitly asks to promote.

An explicit operator-authorized manual execution — while the city is suspended or
the work is outside any rig — uses a persistent workspace on the destination
filesystem. It must never clone or materialize a lane under `/tmp`, and must not
place virtual environments, compiler caches, test caches, database copies, or
package caches inside that checkout. The manual owner records disk usage before
and after, publishes every recoverable commit, and removes the workspace when the
operator-declared exception ends. See `UNIVERSAL_CORE.md` Law 13 and
`docs/worktrees.md`.
```

**Nota:** o rig é `aihub` (prefixo `aihub`, path `~/ai-hub`) conforme
`~/gc/city.toml`. O role `gc.implementation-worker` é um exemplo — os 12 roles do
pack `gascity/roles` estão em `gc agent list`.

---

## F1.2 — cosmos-main (`~/cosmos-main/AGENTS.md` linhas 24-27, 107, 163)

A lei proíbe `make`/`git worktree` e manda usar `gt sling`, que não existe: hoje
ela bloqueia o único caminho viável.

### Substituir (L24-27)

```markdown
1. Run `git status --short --branch`; preserve and integrate concurrent work.
   Gas Town owns branch, worktree, hook, merge queue, and lane lifecycle. Start
   through `gt sling <bead> cosmos` and finish through `gt done`; never create
   or manage a project lane through Make or raw `git worktree`.
```

### Por

```markdown
1. Run `git status --short --branch`; preserve and integrate concurrent work.
   Gas City owns branch, worktree, and lane lifecycle. Start through
   `gc sling cosmos/<role> <bead-id> --on <formula>` and finish by landing a PR
   on `develop` with the bead carrying its evidence; never create or manage a
   project lane through Make or raw `git worktree`.
```

### Substituir (L107, dentro do bullet do branch de integração)

```markdown
  pull request. Gas Town creates and owns work branches, worktrees, and integration
  queue entries. See ADR-134.
```

### Por

```markdown
  pull request. Gas City creates and owns work branches and worktrees through the
  dispatched formula. See ADR-134.
```

### Substituir (L163, em Learned User Preferences)

```markdown
- Pull relevant beads and follow the Gas Town lifecycle into `develop`; promote `develop` to `main` only when the operator explicitly approves production promotion.
```

### Por

```markdown
- Pull relevant beads and follow the Gas City lifecycle into `develop`; promote `develop` to `main` only when the operator explicitly approves production promotion.
```

**Verificar junto:** ADR-134 é citada como fonte da regra de branch. Se ela
descreve Gas Town como owner, precisa da mesma correção — não foi inspecionada.

---

## F1.3 — ccs (`~/ccs/AGENTS.md` linhas 117, 150-160)

### Substituir (L150-160, seção Governed Execution)

```markdown
## Governed Execution

Beads is the execution source of truth when this repository is attached to Gas
Town. `gt prime` loads the current lifecycle, `gt hook` identifies the assigned
bead, and `bd show <id>` provides its durable requirements and evidence.

Hooked workers use only the Gas Town-created lane, keep evidence on the bead,
and finish with `gt done`. Gas Town owns branch and worktree creation, remote
submission, the merge queue, and tracker closure. Generic Git handoff examples
in the managed Beads section do not replace that lifecycle. External
contributors follow [`CONTRIBUTING.md`](./CONTRIBUTING.md).
```

### Por

```markdown
## Governed Execution

Beads is the execution source of truth when this repository is registered as a
Gas City rig. `gc prime` renders the agent's operating context,
`gc hook --claim --drain-ack --json` claims the assigned bead, and `bd show <id>`
provides its durable requirements and evidence.

Dispatched workers use only the lane the formula created, keep evidence on the
bead, and land through a reviewed PR on `main`. Gas City owns branch and worktree
creation; review and merge stay with this repository's own gates. Generic Git
handoff examples in the managed Beads section do not replace that lifecycle.
External contributors follow [`CONTRIBUTING.md`](./CONTRIBUTING.md).
```

### Substituir (L117)

```markdown
reports. In a Gas Town workspace, the assigned Bead remains the execution
```

### Por

```markdown
reports. In a Gas City rig, the assigned Bead remains the execution
```

**Nota:** a lane de integração do rig `ccs` é `main` (`~/gc/city.toml`), e o
próprio `AGENTS.md` do ccs já diz "Do not commit directly to `main`" — o fecho
por PR revisado é consistente com as duas regras.

---

## Repos sem ação

`flext`, `gmn`, `invest`, `mcb`, `beads`, `agents`: as ocorrências são URLs
`github.com/gastownhall/beads`, que é o repositório correto do Beads, e o script
`pr-preflight.sh --repo gastownhall/beads`. Não são referências ao runtime antigo.
