# ADR-0039 - Pyrefly is the only type checker

**Status:** Accepted **Date:** 2026-11-15 **Scope:** static type checking in every
governed project; the typed tooling configuration in flext-infra that executes it

## Authority

The operator's words are recorded in the tracker memory
`operator-order-2026-11-15-no-mypy-no-pyright`: Mypy and Pyright are no longer used as
lint, their references leave code and documentation, and their rules in the tooling
configuration, the projected project tables and the axioms stay only so a developer who
runs them locally keeps working. Dated records are history and stay as written.

## Context

Projects ran three type checkers over the same sources. Two of them repeated the third
and added a gate each to every check.

## Decision

1. Pyrefly is the one type checker. No gate, hook or workflow step runs another one,
   and no result of another one is evidence.
2. flext-infra owns the removal of the two retired gates. Its tooling configuration
   keeps their rules, each project keeps the projected tables, and the axioms stay, for
   local compatibility only; nothing depends on them.
3. Active governance text and project documentation name a retired checker only to
   discourage its use. Superseded ADRs and dated plans are not rewritten.
4. The restoration clause of ADR-0037 stands on its own in
   [the law](../../rules/law.md) 11: a proven regression is corrected by new fix-forward
   commits restricted to its causal hunks.

## Consequences

ADR-0037 is superseded. The `pydantic-development` skill carries this decision.
A project's check reports one type gate; its count is comparable only with runs under
the same checker and configuration.
