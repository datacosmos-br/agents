---
description: Atomic cutover and extermination of every superseded contract.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-25","route:both"]'
---

# A cutover leaves zero active residue

In the same coherent change, rewire every current consumer and delete every superseded
implementation, entry point, option, alias, configuration key, generated projection,
test, fixture, document, and dependency. Do not retain a shim, compatibility reader,
TODO, old/new coexistence, or follow-up cleanup item outside the deprecated-signature
window below. An unmarked or behavior-carrying old path remains forbidden residue.
Do not move residue into a backup, archive, retirement, quarantine, `.bak`, or hidden
sibling; after proven rewire, delete it.

Search semantic and textual opposites across source, configuration, tests, docs, evals,
build/CI owners, manifests, and generated artifacts. Any active opposite blocks landing.
Historical Git and evidence records remain truthful history; they are not runtime
residue or rollback authority.

## Deprecated-signature window

This is the single declaration of the migration mechanism authorized by the operator
on 2026-10-24, recorded in tracker memory
`operator-ruling-2026-10-24-deprecated-signature-window`. Other rules, skills, ADRs,
documents and provider memories reference this section rather than maintaining a
second contract.

The operator's words: "lembre-se, toda a assinatura antiga fica marcada com warning
indicando o caminho novo até migrarmos tudo e daí exterminamos o código antigo
(isso tem que incluir os projetos externos mais tarde)".

1. A removed or renamed public signature with consumers survives only as a marked
   delegation to its new owner. It has no conversion, branch, fallback, default or
   second implementation. A signature without consumers is removed immediately.
2. Python functions, methods, classes and overloads use `warnings.deprecated`
   with the message `compat: <old> -> <new owner>; fix: <exact rewire>`.
   PEP 702 does not mark variables or constants; those require the repository's
   declared analyzer and structural-rule marker, with the same ownership and rewire
   information. Never claim that decorating an unsupported declaration supplies
   deprecation coverage.
3. The declaration itself does not fail CI. Every use is a blocking diagnostic,
   produced by the type checker or the declared rule. That report is the consumer
   census, including external projects.
4. Rewire consumers through existing structural rules and generators in dependency
   order. Do not remove a used signature before its consumers can use the new owner.
5. Delete the delegation, marker and artifacts that exist only for it in the same
   cycle that proves zero remaining consumers. A marker with no fix, independent
   behavior or zero consumers is a defect, never a resting state.

Persisted data and configuration formats migrate through their schema owner; the
signature window authorizes neither an old-format reader nor dual behavior. A newer,
specific operator cutover still governs its scope, including the DI-only dialect
boundary that forbids registries and server-name selection.

External contract: [PEP 702](https://peps.python.org/pep-0702/) and the
[Python 3.13 warning API](https://docs.python.org/3.13/library/warnings.html).
## Exterminate without fear

The 2026-10-24 removal and marked-rewire orders are reconciled here on 2026-10-29.
Their valid intent is to retain real functionality and remove excess, wrong behavior
and duplicated execution at the causal owner. The deprecated-signature window above
is the sole migration contract; it grants no behavior-carrying fallback or frozen alias.

A duplicated execution is the same verification, resolution or derivation repeated
for one purpose: setup rechecking what check owns, a planner re-deriving an artifact
already in hand, or two owners of one fact. Keep the operation's existing owner.
Resolve uncertainty by measuring consumers through current source and runtime,
never by retaining an unused path "just in case".

Within an authorized source cutover, Git retains history; do not create backup or
archive copies of retired tracked source. History is evidence, not permission to
restore published effects or discard current WIP. Apply `atomic-effects.md` and
fix forward. The `safe delete` skill still guards exact ownership, untracked,
foreign, live and ownership-ambiguous state; tracked status alone is not deletion
authority over another contribution.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
