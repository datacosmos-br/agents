# Complete phase-cycle procedure

## Critical transition prohibition

Never switch to another task, advance the plan cursor, hand off as complete, or
declare a phase DONE before its entire approved cycle finishes. Tests, a commit,
a push, an open PR, green CI, or elapsed effort are intermediate evidence, never
phase closure.

Premature transition can ship behavior never exercised through the real public
surface, strand branches and worktrees, omit concurrent changes, hide failed
checks, leave tracker state open, and make later phases depend on code that is
not present on the integration branch. Treat one confirmed skip as a critical,
delivery-blocking defect.

## Freeze the phase contract

At entry, identify the bounded value unit, canonical owner, authorized scope,
configured integration branch, real runtime surface, native gates, projection
owners, security gates, PR requirements, tracker owner, and exact exit criteria.
If any item is unknown, the phase is blocked until it is resolved; never invent
a command, branch, tracker, or substitute record.

Newly discovered work that is required by the exit criteria belongs to the
current phase. Unrelated work does not silently expand scope. It remains outside
the phase unless the operator explicitly changes the plan.

## Mandatory cycle

Complete these steps in order, repeating invalidated evidence after every edit:

1. Research canonical code, configuration, documentation, runtime, and current
   repository state. Reproduce the defect or establish the requested baseline.
2. Correct the root cause at the owner. Rewire every consumer and remove obsolete
   fallback, compatibility, generated, test, fixture, and documentation paths.
3. Exercise the changed behavior through its real public runtime surface on the
   working branch. A mock, import-only smoke test, or static check is insufficient.
4. Run the repository's complete native unit, integration, static, type, build,
   shell, security, generation, and projection fixed-point gates. Missing tools,
   warnings, skips, empty reports, and partial scans are red.
5. Fetch the configured integration branch and incorporate its current state
   through the repository-approved non-destructive merge flow. Resolve concurrent
   work semantically, then repeat runtime and every affected gate.
6. Commit the exact phase scope, push normally, and open or update a PR against
   the configured integration branch. Resolve every review thread and required
   check, obtain the required independent approval, and merge through the
   approved merge strategy.
7. Update the integration checkout to the merged SHA. Run the real public runtime
   and closure gates again on that SHA, not on the feature branch artifact.
8. Prove zero phase residue: no dead or compatibility code, stale projection,
   unrewired consumer/test, open PR, residual branch/worktree, unexplained warning,
   or unresolved required finding.
9. Close the canonical tracker item with the merged SHA and decisive runtime/gate
   evidence. Only then may the phase state become DONE and the next task begin.

## Runtime requirement

Runtime validation is mandatory before general gates, after integration changes,
and after merge on the integration SHA. It must call the shipped CLI, API,
service, daemon, or import surface with representative input and verify the
material artifact or state transition. Authentication, quota, timeout, missing
dependency, or unavailable service remains a loud nonzero failure; never select
an alternate runtime or declare tests equivalent.

## Blocking and suspension

If an authorized external dependency prevents a cycle step, keep the phase open.
Report the exact command, working directory, exit code, decisive output, impact,
and required owner action as a prominent warning or blocker. Do not switch tasks
unless the operator explicitly pauses or reorders the phase.

When the canonical tracker is explicitly suspended, do not invoke it or create
an alternate database. Update the repository-declared manual ledger after each
material state change. Even if Git, PR, CI, and post-merge runtime are green,
tracker closure is unresolved and the phase is not DONE.

Parallel agents may inspect or implement independent parts of the current phase,
but they do not advance the phase cursor. Their changes and evidence must be
adopted, integrated, and revalidated by the owner before closure.

## Completion statement

The final phase report lists the integration SHA, real-runtime commands before
and after merge, every native gate and exit code, PR approval/merge evidence,
residue checks, and tracker closure. Any missing row must say `OPEN` or `BLOCKED`;
never use `DONE`, “complete,” or an equivalent success claim.
