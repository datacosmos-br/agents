# ADR-0023 — Fronteira única de descoberta e manutenção de worktrees (wip ↔ executor)

**Status:** Accepted **Date:** 2026-09-19 **Scope:**
`rules/coordination/wip-persistence.md` · consumidores: todo projeto governado ·
owner de placement: Gas City · programa canônico: o programa wip do projeto (doc-10)

## Context

`wip-persistence` exige worktree e branch dedicadas por esforço, e
`gitflow-branch-pr` já legisla a aposentadoria de lane com prova de ancestralidade.
`gascity.md` declara que provisionamento é do owner transacional da cidade e que
`git worktree` ad-hoc é drift. Nenhuma dessas regras, porém, nomeia **quem descobre e
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
3. **Placement não é descoberta.** Provisionamento e placement permanecem com a Gas
   City (`gascity.md`); `git worktree` ad-hoc segue sendo drift. A descoberta lê as
   superfícies de registro e medição do próprio projeto, nunca uma lista mantida à mão.
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

## References

- `rules/coordination/wip-persistence.md` (regra dona)
- `rules/coordination/gascity.md` (placement/provisionamento)
- `rules/git/gitflow-branch-pr.md` (aposentadoria com prova de ancestralidade)
- `rules/coordination/fleet-landing-corrections.md` (ciclo de fecho com retirada de lane)
- `docs/plans/20260919-handoff-fecho-sessao-dedicado.md` (deep-dive medido)
