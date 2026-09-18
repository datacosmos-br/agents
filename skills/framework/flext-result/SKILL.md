---
name: flext-result
description: "flext result, railway composition, result mnemonics, failure metadata"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0014","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-09-17","extends:flext-development","route:project","subject:flext","usage:on-demand"]'
---

# FLEXT Result

Activate for a detected internal FLEXT consumer when explaining or simplifying
`FlextResult`/`r` construction, composition, failure propagation, or extraction. Do not
activate for plain Python values, another library's Result, or unrelated FLEXT layout
changes.

Load `$flext-development` and its ancestors first: `$solid`, `$py-dev`, then
`$flext-development`. This child owns only Result operation selection, not architecture
or general exception policy. Apply `$yagni` to proposed abstractions.

Read [the operation guide](references/operations.md). Verify the selected runtime's
public facade, implementation, and `p.Result` protocol before edits. Prefer a direct
return; otherwise select one operation by its exact value, exception, metadata, and
effect contract. Missing callback or boundary contracts block the rewrite, not an
invitation to invent them.

Remember: `ok/fail` construct; `map` changes a value; `flat_map` composes a Result;
`flow_through` keeps one payload type; `tap` observes; `fold` exits; `from_failure`
carries failure fields. These are not blanket fail-fast promises. Keep explicit control
flow when raw exceptions must escape. Add no local helper, long lambda pipeline,
speculative abstraction, or broad stylistic refactor.
