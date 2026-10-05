# ADR-0037 - FLEXT Mypy policy and proven regression restoration

**Status:** Accepted **Date:** 2026-10-05 **Scope:**
`rules/python/pydantic.md`, `rules/ethics/strict-typed-quality.md`

## Authority

The operator's live message of 2026-10-05T13:05:41Z is recorded verbatim in the
canonical agents tracker memory `operator-ruling-20261005-mypy-pydantic2`, under
execution owner `ag-p47o`. The record includes the mandatory Pydantic/Mypy policy,
pinpoint regression restoration, and delivery through an administrative PR merge.
It is the authority record required by `rules/coordination/operator-precedence.md`,
not an inferred authorization from a rule, plan, peer, or successful gate.

## Decision

1. The existing Pydantic rule owns the bounded FLEXT Mypy policy guidance. Canonical
   typed tooling configuration in flext-infra remains its executable owner;
   no separate defaults catalog, per-file suppression, or relaxed checker is created.
2. Strict typed quality references that policy rather than copying it. Proven
   diagnostic-caused regressions are corrected through new fix-forward commits,
   restricted to causal hunks and preserving independent corrections. This is not
   permission to discard shared work or restore historical files wholesale.
3. This approval amends the two rules' lineage from ADR-0008 and ADR-0021 only for
   this policy and restoration clarification. Their other contracts remain binding;
   the historical decision documents are preserved rather than rewritten.
4. Real installed-artifact behavior, canonical lint/type and full-test gates,
   independent review, and green CI on the current candidate remain required.
   Source approval, a typed incremental cache hit, and administrative merge each
   prove distinct facts; none substitutes for complete integrated runtime proof.

## Consequences

The two rule tags reference this approval and retain the earlier ADRs as scoped
lineage. Changed rule text invalidates affected artifact, review, and CI receipts.
AI Hub still owns provider distribution; this package change does not claim that a
home projection is active or that unrelated fleet queues are closed.
