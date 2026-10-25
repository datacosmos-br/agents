---
description: Atomic cutover and extermination of every superseded contract.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-30","route:both"]'
---

# A cutover leaves zero active residue

In the same coherent change, rewire every current consumer and delete every superseded
implementation, entry point, option, alias, configuration key, generated projection,
test, fixture, document, and dependency. Do not retain a shim, compatibility reader,
TODO, deprecation window, old/new coexistence, or follow-up cleanup item outside the
deprecated-signature window declared below; an unmarked, behavior-carrying, or
open-ended window is exactly that forbidden residue. Do not move residue into a backup,
archive, retirement, quarantine, `.bak`, or hidden sibling; after proven rewire, delete
it.

Search semantic and textual opposites across source, configuration, tests, docs, evals,
build/CI owners, manifests, and generated artifacts. Any active opposite blocks landing.
Historical Git and evidence records remain truthful history; they are not runtime
residue or rollback authority.

## Exterminate without fear

Operator order 2026-10-24 (verbatim): "é melhore apagar e se precisar podemos recuperar
do histórico do git, e o a funcionalidade tem que ser a real e tirar exageros, coisas
erradsa e que duplciacoes de execucoes como essa em qq lugar".

- For tracked source, Git history is the recovery contract. Deleting committed code,
  tests, configuration or docs needs no backup, archive, approval or second opinion:
  delete it, rewire the consumers, and recover it from history if it is ever needed.
- Keep only the real functionality a current consumer exercises. Exaggerations (ceremony
  that adds no guarantee), wrong behavior, and duplicated executions are defects to
  exterminate at their owner wherever they are found, not tolerated scope.
- A duplicated execution is the same verification, resolution or derivation run twice
  for one purpose: a setup that re-checks what `check` owns, a planner re-run that
  re-derives an artifact already in hand, two owners of one fact. Keep the single owner
  in the verb that owns that concern and delete the copy.
- Uncertainty about an unexercised path is resolved by measuring its consumers (code
  graph, ast-grep, grep, runtime), never by keeping it "just in case".

The `safe delete` skill governs untracked, foreign, live or ownership-ambiguous state,
which Git cannot restore. It never protects tracked code from extermination.

See also: `strict-execution.md` (rule file) — aggregate parent policy.

## Deprecated-signature window

This section is the single declaration of how a cutover reaches zero residue without
breaking any consumer (tracker memory
`operator-ruling-2026-10-24-deprecated-signature-window`). Every other rule, skill,
command, agent profile, ADR, and document references it and never restates it. It is
the mechanism of the atomic cutover above for a rewiring that spans more than one
change: it is not an exception to zero residue and not a compatibility path to retain.

Operator orders 2026-10-24 (verbatim):

- "tudo que for código antigo, compatibilidade , fallback vc tem que ser sempre marcar
  compatibildidade e como corrigir com warning enquanto estiver ajustando wiring para
  exterminar o caminho por ele em todo o codeset".
- "código marcado stdlib de warning em sua declaracao nao faz o CI travar, mas os seus
  usaurios tem que travar com CI falhando".
- "lembre-se, toda a assinatura antiga fica marcada com warning indicando o caminho novo
  até migrarmos tudo e daí exterminamos o código antigo (isso tem que incluir os
  projetos externos mais tarde)".
- "não é contradição, é garantir que não vamos manter ABSOLUTAMENTE NADA DE CÓDIGO
  ANTIGO DE COMPATIBILIDADE E SEM QUEBRAR O PROJETO !!!!!!, AJUSTE AS REGRAS,
  INDICAÇÕES, skills, opiniões, ADRs, AGENTS.md para isso ser sempre o padrão usado em
  tudo".

The procedure:

1. **Scope.** Every removed or renamed public signature — function, method, class,
   alias, constant, or command entry point — that still has a consumer, in
   this repository or in any consumer project, external projects included. A signature
   with no consumer is deleted at once under the atomic cutover above. Persisted data
   and configuration formats are not signatures: they migrate atomically through their
   schema owner, and old-format input fails explicitly.
2. **Thin pass-through.** The old signature survives only as a delegation to its new
   owner. It carries no behavior of its own: no conversion, branch, fallback, default,
   or second implementation.
3. **Native marker.** In Python the marker is the standard-library `warnings.deprecated`
   (PEP 702) on the old function, method, class, or alias, with the message
   `compat: <old> -> <new owner>; fix: <exact rewire>`. A declaration that decorator
   cannot mark, and every other language, uses the language's native deprecation
   marker with the same message shape.
4. **Census in CI.** The marked declaration itself never fails CI; every use of it is
   reported (deprecated use is an error in the repository's type checkers and
   analyzers) and fails CI. That report is the census, and the rewire cannot be
   postponed.
5. **Rewire by rule in waves.** Consumers are rewired by the repository's structural
   migration rules and generators, project by project in dependency waves, never by
   hand where a rule can express the rewrite.
6. **Extermination.** The pass-through, its marker, and every test, fixture, and
   document that exists only for it are deleted in the same cycle the census reaches
   zero across every consumer project, external projects included. No marker means no
   surviving path.

An unmarked old path, a marked path that carries its own behavior, a marker without the
exact fix, and a marked path with zero uses still present are each a blocking defect,
never a resting state.
