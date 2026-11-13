# Beads revalidation role

Use for an explicitly requested revalidation of registered issues, including closed
issues. Do not activate for an unrelated implementation or translation.

Read the procedure below completely before changing tracker state.
Evidence follows `rules/workflow/beads-traceability.md`; the active intent follows
`rules/law.md`.

Beads owns execution state and the resumption cursor. Exported inventories are read-only
evidence, never a second status ledger. Use only the selected available tracker;
suspension does not authorize a substitute.

Revalidation is semantic: a stale closed issue may require correction, while an open
issue may already be implemented or superseded. Neither status nor text similarity
establishes reality. Preserve unique evidence before consolidation.

## Procedure: revalidate registered work against reality

Resolve the authorized issue scope and active intent before writes. Inspect the
installed tracker command contract and enumerate all matching open and closed issues,
including pagination. Prove completeness; do not invent list flags or treat a failed or
truncated query as an empty result.

For each issue, compare its registered premise with integration history, current
integrated code and measured native behavior under
`rules/workflow/beads-traceability.md`. Include relevant operator decisions, plans, ADRs,
dependencies and linked issues. Record commands, working directory, exit codes, decisive
output and integration revision in Beads.

Keep execution and resumption in Beads, including the current issue and next action. Do
not maintain CSV progress, Markdown task status or a parallel ledger. Historical exports
may supply provenance but never override live registration. If the selected runtime is
suspended, follow the governing suspension contract; do not invent another tracker or
claim closure.

The orchestrator decides whether the premise remains valid, is implemented, is
superseded or was false. Update both open and closed issues when evidence changes their
meaning. A label, closed blocker or similar title is not sufficient proof to close,
reopen or deduplicate. Move unique requirements and evidence to the surviving issue
before retiring a duplicate; record the survivor explicitly. Realign dependencies with
the proven owner and implementation relationship.

Keep each repair in the active intent through native validation, reviewed integration
and post-merge evidence before proceeding. A documentation-only revalidation does not
authorize unrelated implementation. Follow the existing Git and closure owners instead
of reproducing their workflow here.

Preserve concurrent changes. Investigate causality using immutable Git history, the
current combined tree and native measured behavior; never stash changes or manufacture a
pristine worktree to allocate blame. Correct the causal owner within authorized scope,
recording an external blocker precisely when necessary.

Refresh evidence after integration, status or dependency changes. An earlier sweep tag
is provenance, not a permanent declaration of correctness.
