# Verification loop procedure

Fresh executable evidence bounds a readiness or completion claim. A command
name, stale report, warning, skip, or successful later stage cannot replace a
missing or failed earlier stage.

## Preflight

Before executing a gate or generated-owner effect, resolve and validate:

- the exact changed behavior, paths, consumers, and claim boundary;
- the repository's current authoritative development and public runtime
  commands from its declared owners;
- required environment, toolchain, fixtures, services, and credentials;
- generated surfaces and their canonical owner;
- detector baselines and their exact threshold, mode, formats, ignores,
  reviewed-file set, and baseline-file identity;
- CI workflows and every changed-path trigger required to select them;
- the ordered gate set required for the affected scope.

For CI changes, inventory every physical workflow and its source generator before
execution. Prove one workflow/job owns the repository's native CI composition;
reject overlapping duplicate owners, scanners that inspect their own workflow
source, `uses:` references not pinned to a full commit SHA, `|| true` or other
error masking, and jobs that never execute the declared native owner. A green
check name is not evidence that `make ci` or the repository-equivalent owner ran.

Do not invent selectors, options, aliases, private entry points, or direct-tool
substitutes. Resolve external-token workflows before invocation: when the token
is absent, exclude the dormant workflow from the applicable set and record it
as `NOT EXECUTED` because the external token is unavailable. This is not green
evidence and cannot prove that workflow's semantics, but it does not block the
remaining validation or landing. A missing or conflicting prerequisite for an
applicable workflow stops with zero gate effects.

## Ordered evidence

Run each applicable owner in repository order:

1. environment and bootstrap health;
2. repository check, lint, and formatting owner;
3. static and type analysis owner;
4. complete affected test owner;
5. material use through the shipped public surface;
6. generated-owner convergence and fixed point when generated surfaces changed;
7. runtime deployment or reconciliation from the merged integration SHA when
   the repository owns the shipped facade;
8. native CI on the current published commit, including workflow-source trigger
   coverage when CI configuration changed, single-owner workflow inventory,
   full-SHA action pins, unmasked failures, and decisive output from the native
   CI owner; and
9. zero-residue and integration evidence at an increment boundary.

The first nonzero exit, timeout, signal, incomplete publication, or missing
decisive output stops the invocation and propagates as the causal result. Do not
catch, retry, switch tools, narrow the gate, continue to later stages, or publish
partial green evidence. Diagnose and correct that root cause at its canonical
owner, then rerun the failed and invalidated stages. This is a new invocation in
the same active phase, not an unchanged retry or a handoff. Ask for help only
when the remaining condition is external or requires authority the active task
does not grant.

For a shell, Make recipe, script, or other composite command, the process's final
exit status is the status of the entire invocation. Successful prefix output or
individual substeps may be reported only as bounded observations; they never
make the composite green after a later substep fails. Do not parse a placeholder
value from a failed command substitution, continue to later proof, or replace a
native Make owner with its underlying test runner.

Directly invoking an external-token workflow makes it applicable. Missing or
invalid credentials then remain its raw first failure; never convert that
attempt into the preflight exclusion above.

Generated effects must stage on the destination filesystem, verify completely,
and publish atomically. Cleanup may attach a secondary failure only while
re-raising the original cause. Leave no generated or temporary residue.

## A shrinking failure count is not evidence of a correct fix

When a change is supposed to make a whole class pass and the class only gets
smaller, that is evidence the change does not do what it claims — not evidence
of a second, independent cause. Prove the mechanism on an input where it
matters before accepting the remainder as a new problem: a normalization that
is meant to make two representations equal must be shown to produce the same
result from both, on a case where they actually differ. A gate that turns green
because the affected inputs were too small to expose the mechanism proves
nothing about it.

## An empty check set is not a green CI

A check rollup that lists nothing is undetermined, not passing. The two states
are structurally identical to any filter that counts failures: zero failing and
zero pending is what both "every check passed" and "no check has been created
yet" look like. Reading the second as the first merges unreviewed code, and the
mistake is invisible afterwards because the checks arrive and pass a minute
later.

Require an affirmative token per check before calling CI green: a non-empty
check set in which every entry reports both that it finished and that it
finished successfully. Anything else — an empty set, a check still running, a
check whose conclusion the API has not written yet — is red for the purpose of
merging, and the wait continues.

Re-read the head commit of the branch on every poll. A push during the wait
retargets CI at a new commit, and checks that passed against the previous one
say nothing about what is about to merge.

A detector gate is scoped to its exact comparison configuration. Changing the
threshold, mode, formats, ignores, reviewed files, or baseline contents
invalidates every overlapping prior result: triage the changed set, replace the
baseline deliberately at its owner, and rerun the gate. A lower duplicate count
from a coarser threshold is not a fix.

## Report

For every attempted stage record the exact command, working directory, exit
code, decisive output, artifact or runtime observation, timestamp where owned,
and covered scope. For every excluded external-token workflow, record `NOT
EXECUTED`, the absent prerequisite by name without its value, and the
operator-authorized applicability rule. Distinguish tests from public-surface
proof. State the first failure and leave later stages unclaimed while fixing it;
a report never advances the phase cursor.

The final claim cannot exceed the common scope of the fresh evidence. Local or
branch-only green cannot be called an implementation completion while required
CI, approval, merge, or post-merge proof remains open. Any later overlapping
edit invalidates earlier evidence without converting it into a warning.
