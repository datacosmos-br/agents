# ADR-0023 — Single worktree discovery and maintenance boundary (wip ↔ executor)

**Status:** Superseded by ADR-0038 **Date:** 2026-09-19 **Scope:**
`rules/coordination/wip-persistence.md` · consumers: every governed project ·
placement owner: Gas City · canonical program: the project's wip program (doc-10)

## Context

WIP preservation and isolation were improperly coupled. ADR-0025 now
selects placement by the call, adopting the current authorized context; discovery
does not require another checkout. `gitflow-branch-pr` governs the retirement of disposable lanes.
The original problem was that the rules did not name **who discovers and
plans** the WIP state of worktrees, nor guarantee that **retirement execution**
has a single owner.

The 2026-09-19 deep-dive (recorded in
`docs/plans/20260919-handoff-fecho-sessao-dedicado.md`, worktrees section) measured the
gap: the ai-hub storage lane already correlates worktree ↔ bead/PR/actor facts and
speaks the vocabulary of the `wip/` program, but **execution is duplicated** — the wip
planner and the storage executor plan actions on the same worktrees with different
policies (merge state vs. activity window), with a risk of double or divergent
retirement. Orphan worktrees (directory with no record in `.git/worktrees`) are not
discovered by either of the two.

## Decision

1. **Discovery and planning have one owner: the project's wip program.** The wip surface
   declared by the project — capture/plan/retirement in the doc-10 vocabulary, like
   the ai-hub `wip/` program — is the only one that names the candidate set, the
   read-only correlation with beads/PRs/actors and the retirement intent. The catalog
   names this owner class; it does not reimplement discovery or create parallel policy.
2. **Retirement has a single executor.** The resident executor consumes the SAME candidate
   queue that the wip planner produces. Two surfaces planning retirement
   over the same worktrees with different policies are forbidden.
3. **Placement is not discovery.** The call selects its context according to ADR-0025
   and `gascity.md`; discovering WIP does not create an isolation requirement. Discovery
   reads the project's registry and measurement, never a hand-maintained list.
4. **Scope.** Orphan worktrees/husks without a registry entry are within the scope of the
   project's discovery; rig runtime worktrees (city state) and same-origin foreign
   clones are out of scope, unless an explicit flag is given.

## Consequences

- The ai-hub storage lane stops being a second planner: it becomes the resident
  executor that consumes the wip queue, and wip remains the
  discovery/capture boundary.
- A lane that introduces its own retirement policy over worktrees becomes a
  conformance defect, not an acceptable variation.
- The orphan husks gap falls within the declared scope, with a named owner, instead of
  staying invisible to both sides.

## Amendment 2026-09-19 — delivering owner, path computation, conformance measure

Operator rulings of 2026-09-19, newer than the text above and adopted here:

1. **Named delivering owner.** The "project's wip program" of decision 1 is the ai-hub
   `wip` program (`ai-hub wip <verb>`: `start`, `save`, `ship`, `land`, `clean`,
   `status`, `next`, `doctor`; plan `wip-automation`, epic `aihub-hjsdg`). Every other
   wip implementation in ai-hub is exterminated verb by verb, with exactly one
   implementation per verb at any moment.
2. **Placement delegates path computation.** Only a call that selects a
   new isolated context asks the placement owner for its path. An adopted worktree
   does not need to be relocated nor does it become disposable. The 2026-10-23 amendment
   (ag-wibx.2) replaces the universal lane computation; no directory prefix
   is a global requirement.
3. **Conformance is adherence, not existence.** A violation of this boundary is a
   surface that acts outside the owner or the placement actually selected by the
   call. The existence or location of an adopted worktree is not a violation.
4. **The git probe lives in the authorized owner.** The resident storage executor consumes facts
   already established by the wip program, the authorized git owner; it does not run git. The veto
   ladder (dirty → unpushed → open-bead → active-session → retirable) remains, and
   unknown evidence vetoes retirement.
5. **Actors coordinate by mail.** `rules/coordination/inter-session-mail.md` governs
   lane claiming and release (`[coord] lane claim`, `[coord] lane changed`).
   Amendment (2026-10-01; tracker memory `operator-rulings-2026-10-01-governance`,
   ruling 3): the abandonment test is declared only in
   `rules/coordination/bead-branch-pr-cadence.md` §2; retirement still honors the city
   reaper's backup precondition.

## References

- `rules/coordination/wip-persistence.md` (owning rule)
- `rules/coordination/inter-session-mail.md` (coordination between actors)
- `rules/coordination/gascity.md` (placement/provisioning)
- `rules/git/gitflow-branch-pr.md` (retirement with ancestry proof)
- `rules/coordination/fleet-landing-corrections.md` (closing cycle with lane retirement)
- `docs/plans/20260919-handoff-fecho-sessao-dedicado.md` (measured deep-dive)
