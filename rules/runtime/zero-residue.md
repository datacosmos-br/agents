---
description: Atomic cutover and extermination of every superseded contract.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-30","route:both"]'
---

# A cutover leaves zero active residue

In the same coherent change, rewire every current consumer and delete every superseded
implementation, entry point, option, alias, configuration key, generated projection,
test, fixture, document, and dependency. Do not retain a shim, compatibility reader,
TODO, deprecation window, old/new coexistence, or follow-up cleanup item. Do not move
residue into a backup, archive, retirement, quarantine, `.bak`, or hidden sibling; after
proven rewire, delete it.

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

## Marked compatibility while rewiring

Operator order 2026-10-24 (verbatim): "tudo que for código antigo, compatibilidade ,
fallback vc tem que ser sempre marcar compatibildidade e como corrigir com warning
enquanto estiver ajustando wiring para exterminar o caminho por ele em todo o codeset".
This refines the atomic cutover above for a rewiring that spans more than one change.

- An old, compatibility or fallback path may survive only while its consumers are being
  rewired, and only when it is marked. Unmarked residue remains a blocking defect.
- In Python the marker is the standard-library `warnings.deprecated` (PEP 702) on the
  old function, method, class or alias, with the message
  `compat: <old> -> <new owner>; fix: <exact rewire>`. Static type checkers then report
  every remaining caller, which is the census; at runtime the warning names the fix.
  Other languages use their native deprecation marker with the same message shape.
- The marker never becomes a resting state: the path and its marker are deleted in the
  same change that rewires the last consumer. No marker means no surviving path.
