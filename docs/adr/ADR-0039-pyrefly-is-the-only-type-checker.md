# ADR-0039 - Pyrefly is the only type checker

**Status:** Accepted **Date:** 2026-11-15 **Scope:** static type checking in every
governed project; the typed tooling configuration in flext-infra that executes it

## Authority

The operator's words are recorded in the tracker memory
`operator-order-2026-11-15-no-mypy-no-pyright`: Mypy and Pyright are no longer used
anywhere as lint, and a mention of either is removed where it is found. Dated records
are history and stay as written (operator answer of 2026-11-15 on historical records).

## Context

Projects ran three type checkers over the same sources. Two of them repeated the third,
added a gate each to every check, and kept their own configuration tables, caches and
dependency pins in every generated project file.

## Decision

1. Pyrefly is the one type checker. No gate, hook, configuration table, dependency,
   cache path, editor setting or workflow step runs or configures another one.
2. flext-infra owns the removal: its gates, tooling tables, templates and dependency
   declarations drop the two retired checkers, and each project loses the generated
   sections through its upgrade and generation verbs. A project removes only what it
   authored itself.
3. Active governance text (rules, skills, commands, accepted ADRs, guides) names
   neither retired checker. Superseded ADRs and dated plans are not rewritten.
4. The restoration clause of ADR-0037 stands on its own in
   [the law](../../rules/law.md) 11: a proven regression is corrected by new fix-forward
   commits restricted to its causal hunks.

## Consequences

ADR-0037 is superseded. The `pydantic-development` skill carries this decision.
A project's check reports one type gate; its count is comparable only with runs under
the same checker and configuration.
