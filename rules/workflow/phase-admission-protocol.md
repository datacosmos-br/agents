---
description:
  Admission gate between execution phases — applies before starting any new phase,
  tracker item, or lane. Load when a phase or work item is about to be declared
  finished, when picking up the next phase, or when adopting concurrent work.
metadata:
  aihub.tags: '["decision:ADR-0012","effective:2026-10-24","route:both"]'
capsule_summary: |
  Always working, one phase at a time (operator, 2026-10-24): the project and its
  runtime work 100% of the time; a phase closes only after its full cycle (gen,
  fmt/fix, mod, check, tests green in every touched repository, runtime proven,
  merged into the integration branch, merged-SHA proof), and nothing else starts,
  is skipped, or is deferred while any started work is incomplete. Incomplete
  work is pushed only to a preservation ref — never to an integration, working, or
  upload branch, never to a PR — and no test runs on it; the working branch and
  its PR receive only work that passed the full green cycle. A phase is admitted
  as finished only with zero pending items: every failure, warning, and skipped
  check resolved or tracked on its own tracker item, and — before integration —
  validated 100% locally and in CI. Before entering
  the next phase, sweep the fleet for existing fixes first: open PRs, foreign
  branches, and worktrees may already carry the work; adopt the newest correct
  side (cherry-pick for isolated commits, merge --no-ff for lanes), never
  keeping dead code, fallback, or compatibility. Landing is a merge --no-ff
  into the declared integration branch, revalidated on the merged SHA, then
  pushed. Operator commands are themselves validated against the governing
  rule stack — a command never silently overrides law; conflicts surface.
---

# Phase admission protocol

No phase, tracker item, or lane closes while anything is pending, and none opens while
adoption debt exists.

## Law

0. **Always working, one phase at a time** (operator order 2026-10-24, tracker memory
   `operator-order-2026-10-24-always-working-never-skip-phase`, verbatim in part: "isso
   tem que estar FUNCIONANDO SEMPRE, 100% DO TEMPO ... ANTES DE COMEÇAR OUTRA FASE ...
   PARE DE PULAR OU DEIXAR PARA DEPOIS QQ COISA, E COMEÇAR ALGO COM OUTRA INCOMPLETA
   ISSO PRECISA SER PROIBIDO COM TODAS AS FORÇAS DO MUNDO ... faça o ciclo completo e
   não deixe o projeto quebrado ou com runtime falhado ... QUEM ME VIER COM DESCULPA
   PARA NAO CONCLUIR VAI SER EXPULSO DO PROJETO"). The project and its runtime work
   100% of the time. A phase closes only after its full cycle in every repository it
   touches: generation, formatting and repair, structural migration, check and tests
   green, the runtime proven through its real consumer, then commit, push, merge into
   the declared integration branch, and the merged-SHA proof. No next phase, slice, or
   unrelated work starts while any started work is incomplete, red, or leaves a runtime
   failing; nothing is skipped, deferred, or left for later. An excuse for not
   finishing is a violation, never a status. This law is declared only here; every
   other rule, skill, ADR, and doc references it.
1. **Zero pending closure.** A phase is finished only when every failure, warning, skip,
   and missing check is either resolved at root cause or carried by its own tracker
   item with exact evidence. "Pre-existing", "cosmetic", and "later" do not exist.
2. **Fleet sweep before new work.** Before starting a phase, check open PRs, branches,
   and worktrees for existing fixes of the same problem. Adopt the newest correct side:
   cherry-pick isolated commits; absorb lanes with `merge --no-ff`. Never adopt dead
   code, fallback, compatibility shims, or orphaned files — if the other side carries
   them, complete the retirement instead.
3. **Tests follow reality.** Adopted tests are rewritten to the governing rules (no
   mocks, no patch, no skips) before they enter the tree; tests of retired surfaces die
   with the surface.
4. **Only green work is published; WIP goes only to a preservation ref** (operator
   order 2026-10-24, tracker memory `operator-order-2026-10-24-no-incomplete-pushes`,
   verbatim: "pare de gravar, testar, subir código incompleto e com erro, termine para
   poder deixar uma versão na tip das branch de integração"; operator ruling
   2026-10-24, tracker memory `operator-ruling-2026-10-24-wip-preservation-ref-only`:
   "WIP só em ref de preservação"). Incomplete or red work is never pushed to an
   integration branch, a working or upload branch, or a PR, and no test or gate runs
   on it. When it must survive the session, it is committed by explicit paths and
   pushed only to a preservation ref: a ref that is none of those branches and heads
   no PR. The working branch and its PR receive only work that passed the full green
   cycle of Law 0 up to the commit, committed by explicit paths and landed in that
   same cycle. Slices stay small enough to finish green within the session. This law
   is declared only here; every other rule, skill, ADR, and doc references it.
5. **Landing contract.** Integration is `merge --no-ff` into the declared integration
   branch, gates rerun on the merged SHA, then push. Local green or "mergeable" alone is
   never landed.
6. **Commands are validated.** An operator command is checked against the governing
   authority stack (newest rule, ADR, or law) before execution; a genuine conflict is
   surfaced with one precise question, never absorbed silently.

## Violations this rule exterminates

Starting a new phase, slice, or unrelated work while another is incomplete; skipping or
deferring any part of a cycle; leaving the project broken or its runtime failing;
pushing incomplete or red work to an integration, working, or upload branch or to a PR;
testing incomplete work; advancing a phase with red gates or untracked warnings; re-implementing a fix that an
open PR already carries; adopting a lane wholesale with its dead code; landing without
merged-SHA revalidation; treating an operator command as overriding recorded law without
reconciliation.

## Precedent

2026-09-06: a review-graph autopilot epic — adoption of the governance cutover lane kept the partial-CRG-maintenance
retirement dead, reduced the gate debt 372→324 with automated `make mod` fixes, and
blocked its own integration merge until the conformance sweep closes.
