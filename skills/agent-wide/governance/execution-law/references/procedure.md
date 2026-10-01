# Engagement procedure — sole-executor execution law

The contract for a cleanup, finalization, or quality engagement run under a
monopoly directive. Each section cites its owner; nothing here restates a
rule the catalog already carries. Project-specific patterns belong to the
project's declared domain law, never to this file.

## 1. Startup

Open with the measured census (`rules/coordination/session-startup-census.md`):
fetched integration tip, open PRs, worktrees, branches, beads — adopting
anything abandoned inside the configured threshold, never rebuilding it.
Resolve the coordinator through `rules/coordination/coordinator-ladder.md`
and record the tier and its evidence on the active bead. Declare the lane —
bead, branch, receiving integration branch — per
`rules/coordination/lane-ownership-declaration.md` before the first effect.
Ask the project's wip surface what the next permitted action is; never
improvise lane state.

## 2. Research and adoption before any mutation

Inventory before designing: open and recently merged PRs, WIP branches and
worktrees, ready and open beads, superseded attempts. Adopt the surviving
implementation fix-forward and discard the duplicate without resentment;
deduplication must delete more than it adds. An active lane carrying work
you need is adopted by cherry-pick immediately, never awaited. Runtime
reality precedes implementation and tests: establish correct behavior from
the official contract and the real public consumer first; when runtime and
tests disagree, the runtime is the authority and the test is fixed.

## 3. Extermination and zero residue

Obsolete, useless, or rule-incompatible material is exterminated in every
surface — source, tests, examples, scripts, configuration, rules, templates,
docs, CI, generated facets. Workarounds stay exterminated: never reintroduce
a removed fallback, fake path, or compatibility layer; adjusting code to wire
the correct functionality is always allowed. The superseded implementation
dies in the same cutover with its callers rewired; exterminated material
stays dead and residue is hunted, never archived. Defects surfaced in the
blast radius are adopted, not excused (`rules/workflow/production-readiness.md`).

## 4. One declaration site per fact

Every orientation, policy, or value has exactly one declaration site; every
other occurrence is a reference or a regenerated projection. Mutable rule
values live as gated configuration at their canonical owner with per-project
override — a policy literal hardcoded in code, rule, template, test, or doc
is an extermination target, moved to the gated owner and regenerated in the
same change. Projections are never hand-edited; when a declarative automation
exists, manual propagation is forbidden.

## 5. Native commands and evidence

Every action runs through the repository's canonical command surface —
selector-free native verbs — and so does every diagnosis; ad-hoc sweeps over
generated projections are not evidence. Record verb, working directory, exit
status, decisive output, and scope. A warning, skip, empty output, zero
collection, retry, or normalized failure is red. A broken or missing verb is
a defect repaired at its owner and rerun through, never routed around.

## 6. Landing

Commit and push early by explicit paths; never accumulate uncommitted mass
(`rules/workflow/mass-rewrite-discipline.md` for tree-wide effects, test
evidence bracketing the mass). Absorb the integration base before publishing,
merge with review of both sides, and land the full cycle —
`rules/coordination/full-landing-cycle.md`: a green local run, an open PR,
or a mergeable state is not landed. Prove repeated generation and repair
verbs are no-ops on the unchanged candidate before pushing.

## 7. Closure

Close only through `$sprint-closure`: zero residue, merged integration SHA,
runtime proof where the repository owns a runtime, PR and tracker closed
with evidence, lane retired. A green partial, a plan, or a self-report is
not done.

## 8. Concurrent work under a monopoly directive

The monopoly assumption is a scheduling default, not an observation. When
live evidence contradicts it — unowned dirt, another session's lane, a moved
tip — adopt and fix forward per
`rules/coordination/fix-forward-collaboration.md`: never blame, never
discard, never destructive Git on shared work. Re-run the census instead of
retrying unchanged.

## 9. Stop conditions

Stop only for a genuine authority conflict or a destructive, irreversible
action: then one precise question carrying the exact error or the conflicting
rule numbers (`rules/coordination/operator-precedence.md`,
`rules/coordination/never-deduce.md`). Everything else continues to the
observable stop condition; blockers and their exact evidence go on the bead,
never into excuses.
