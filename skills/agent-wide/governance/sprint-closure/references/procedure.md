# Sprint closure procedure

## Preflight

Resolve the increment scope, integration branch, merged SHA, public runtime surface,
applicable native gates, generated owners, review and landing state, tracker mode, and
every touched producer and consumer before changing closure state. Classify
external-token workflows before invocation. If a token is absent, record the workflow as
`NOT EXECUTED`; it supplies no green evidence but does not block the remaining closure
contract. That exclusion never applies to an independently observed alert or finding:
every actionable item remains open until its owner is corrected and the available
authoritative evidence is clean.

Missing, stale, conflicting, or inaccessible evidence stops at the first causal defect.
Do not run a substitute command, infer a tracker endpoint, accept a warning or skip,
repeat a failed gate, or narrow the closure claim.

When the canonical tracker runtime is explicitly suspended, create no alternate
database, tracker, or ledger. Preserve evidence only in separately authorized Git, PR,
review, check, and CI surfaces; the tracker item remains unresolved and the increment is
not done.

## Required evidence

All evidence must describe the same merged integration SHA:

1. the repository-owned applicable native gates, with command, working directory, exit
   code, decisive output, and covered scope, plus each excluded external-token workflow
   recorded as `NOT EXECUTED`;
2. material use through the shipped public runtime surface;
3. deployment or reconciliation of the shipped runtime from the same merged integration
   SHA when the repository owns that runtime;
4. completed independent review and merged change record;
5. canonical tracker closure when its runtime is available;
6. removal of the increment's lane workspace after landing;
7. net line change for a replacement, or an explicit additive-capability classification
   when nothing was superseded.

Do not treat local or branch-only green, an open review, a pushed commit, or an unmerged
artifact as integration evidence.

Do not label the implementation complete, delivered, resolved, or ready while any
required CI, approval, merge, post-merge, residue, or tracker row is open. Such a split
claim is partial closure even when the report separately says the phase remains open.

## Zero-residue audit

Require every row to be empty:

- dead code and obsolete generated artifacts;
- compatibility shims, aliases, wrappers, fallbacks, or dual readers;
- consumers and tests still using the superseded contract;
- deferred cleanup notes, follow-up deletion tasks, or partial publications;
- independently observed security alerts or findings, even when a separate token-gated
  scanner is `NOT EXECUTED`;
- open increment workspace, review, or tracker item.

Inspect structurally where available and review every match. A valid remaining consumer,
nonzero gate, incomplete publication, or open row keeps the whole increment active.
Correct every actionable row and repeat its invalidated proof; never carry it forward as
a warning, blocker report, or next-phase task.

## Atomic closure

Publish the closure record and change canonical closure state only after all required
evidence and zero-residue checks succeed. If any final write or owner operation fails,
preserve its raw causal chain and leave the increment open.

The exit record contains the merged SHA, exact evidence, zero-residue results, net line
change, review and tracker state, workspace removal, and any blocker. Never claim phase
completion from commit, push, review, or green CI alone.
