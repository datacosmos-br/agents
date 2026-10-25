# ADR-0023 — Fronteira única de descoberta e manutenção de worktrees (wip ↔ executor)

**Status:** Accepted **Date:** 2026-09-19 **Scope:**
`rules/coordination/wip-persistence.md` · consumidores: todo projeto governado ·
owner de placement: Gas City · programa canônico: o programa wip do projeto (doc-10)

## Context

Preservação de WIP e isolamento eram indevidamente acoplados. ADR-0025 agora
seleciona placement pela chamada, adotando o contexto autorizado atual; a descoberta
não exige outro checkout. `gitflow-branch-pr` rege a retirada de lanes descartáveis.
O problema original era que as regras não nomeavam **quem descobre e
planeja** o estado WIP dos worktrees, nem garante que a **execução da aposentadoria**
tenha um dono único.

O deep-dive de 2026-09-19 (registrado em
`docs/plans/20260919-handoff-fecho-sessao-dedicado.md`, seção de worktrees) mediu a
lacuna: o lane de storage do ai-hub já correlaciona fatos de worktree ↔ bead/PR/ator e
fala o vocabulário do programa `wip/`, mas **a execução está duplicada** — o planejador
wip e o executor de storage planejam ações sobre os mesmos worktrees com políticas
distintas (estado de merge vs. janela de atividade), com risco de aposentadoria dupla
ou divergente. Worktrees órfãos (diretório sem registro em `.git/worktrees`) não são
descobertos por nenhum dos dois.

## Decision

1. **Descoberta e planejamento têm um dono: o programa wip do projeto.** O surface wip
   declarado pelo projeto — captura/plano/aposentadoria no vocabulário do doc-10, como
   o programa `wip/` do ai-hub — é o único que nomeia o conjunto de candidatos, a
   correlação read-only com beads/PRs/atores e a intenção de aposentadoria. O catálogo
   nomeia essa classe de owner; não reimplementa descoberta nem cria política paralela.
2. **Aposentadoria tem um único executor.** O executor residente consome a MESMA fila
   de candidatos que o planejador wip produz. Duas superfícies planejando aposentadoria
   sobre os mesmos worktrees com políticas diferentes são proibidas.
3. **Placement não é descoberta.** A chamada seleciona seu contexto segundo ADR-0025
   e `gascity.md`; descobrir WIP não cria uma exigência de isolamento. A descoberta
   lê registro e medição do projeto, nunca uma lista mantida à mão.
4. **Escopo.** Worktrees órfãos/husks sem entrada de registro estão no escopo da
   descoberta do projeto; worktrees de runtime de rig (estado da cidade) e clones
   estrangeiros same-origin ficam fora, salvo flag explícita.

## Consequences

- O lane de storage do ai-hub deixa de ser um segundo planejador: ele vira o executor
  residente que consome a fila do wip, e o wip permanece a fronteira de
  descoberta/captura.
- Uma lane que introduza política de aposentadoria própria sobre worktrees passa a ser
  defeito de conformidade, não uma variação aceitável.
- A lacuna de husks órfãos fica dentro do escopo declarado, com dono nomeado, em vez de
  ficar invisível aos dois lados.

## Emenda 2026-09-19 — dono entregador, cálculo do caminho, medida de conformidade

Rulings do operador de 2026-09-19, mais novos que o texto acima e adotados aqui:

1. **Dono entregador nomeado.** O "programa wip do projeto" da decisão 1 é o programa
   `wip` do ai-hub (`ai-hub wip <verbo>`: `start`, `save`, `ship`, `land`, `clean`,
   `status`, `next`, `doctor`; plano `wip-automation`, épico `aihub-hjsdg`). Toda outra
   implementação de wip no ai-hub é exterminada verbo a verbo, com exatamente uma
   implementação por verbo em cada momento.
2. **Placement delega o cálculo do caminho.** Apenas uma chamada que seleciona um
   novo contexto isolado pede seu caminho ao dono de placement. Uma worktree adotada
   não precisa ser realocada nem se torna descartável. A emenda de 2026-10-23
   (ag-wibx.2) substitui o cálculo universal de lanes; nenhum prefixo de diretório
   é exigência global.
3. **Conformidade é aderência, não existência.** Violação desta fronteira é uma
   superfície que atua fora do dono ou do placement efetivamente selecionado pela
   chamada. A existência ou localização de uma worktree adotada não é violação.
4. **A sonda git vive no dono autorizado.** O executor residente de storage consome fatos
   já apurados pelo programa wip, dono autorizado de git; ele não executa git. A escada
   de veto (dirty → unpushed → open-bead → active-session → retirável) permanece, e
   evidência desconhecida veta a retirada.
5. **Atores coordenam por correio.** `rules/coordination/inter-session-mail.md` rege a
   tomada e a liberação de lanes (`[coord] lane claim`, `[coord] lane changed`).
   Amendment (2026-10-01; tracker memory `operator-rulings-2026-10-01-governance`,
   ruling 3): the abandonment test is declared only in
   `rules/coordination/bead-branch-pr-cadence.md` §2; retirement still honors the city
   reaper's backup precondition.

## References

- `rules/coordination/wip-persistence.md` (regra dona)
- `rules/coordination/inter-session-mail.md` (coordenação entre atores)
- `rules/coordination/gascity.md` (placement/provisionamento)
- `rules/git/gitflow-branch-pr.md` (aposentadoria com prova de ancestralidade)
- `rules/coordination/fleet-landing-corrections.md` (ciclo de fecho com retirada de lane)
- `docs/plans/20260919-handoff-fecho-sessao-dedicado.md` (deep-dive medido)
