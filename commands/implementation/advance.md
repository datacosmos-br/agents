---
name: advance
description:
  Rebuild the session's work order from project evidence, ask only what is missing,
  and force the plan to verified completion under the repository's own law.
argument-hint: "<optional focus, plan path, bead, or project path>"
metadata:
  aihub.tags: '["decision:ADR-0020","effective:2026-09-10","route:agent"]'
---

# Advance — rebuild the work order and force the plan to verified completion

Treat `$ARGUMENTS` as an optional focus. Session tasks never hardcode here: they arrive
as arguments, beads, or plan files. Load the branch-matched owning skill before
executing any step below; deepen through skills, never by duplicating their content into
this procedure.

## Phase 0 — Authority and persistence

Resolve authority FIRST, before any effect: workspace root `AGENTS.md` → branch-matched
law skill → nearest scope `AGENTS.md` → active bead. Operator request outranks every
lower layer; recency resolves the rest. Run the declared environment setup, then use
only the root Make dispatcher's declared public verbs. Each verb performs its declared
operation without an invented mutation flag. You are an agent: keep going until the
plan is completely resolved — only end the turn at a genuine stop condition. If file
content or codebase structure is unknown, read it with your tools; never guess.

## Phase 1 — Work order from evidence, never from transcripts

Build the work order from the plan file, the tracker bead and Git reality: objective,
plan path and current step, measured evidence so far, owned paths, scope, explicit
exclusions, accepted concurrent work, the
integration branch and gates this repository declares, the first red gate, and the
exact next action. Read what a surface records; ask the operator only for a fact no
surface holds, one question at a time with a recommended answer (`grilling`). State
the work order in at most ten lines and execute it in the same turn: it is the work,
never a report. Where the provider schedules prompts, register one recurring goal
check naming plan, bead and lane, and remove it at closure. A plan file's preflight
runs exactly as written. Adopt any actor's in-scope work and fix it forward; never
restart what can be resumed.

## Phase 2 — Reflexion checkpoint

In at most three lines, state what the drift or last red gate taught and which owner
holds the lesson, and record it as a note on the selected tracker's bead. Write no new
rule, memory or document for it; a governing text the operator's correction contradicts is
rewritten through `op-learning` after the plan lands.

## Phase 3 — Advance loop

One work item at a time, in dependency order, with effort scaled to complexity. A
slow gate runs in the background while independent work proceeds and whatever depends
on it waits for its result; nothing waits for another session, a queue or a quiet tree
(`fix-forward`). Discovery goes to subagents briefed per `dispatch-agent`, each brief
naming the plan path and bead; sequenced effects (merges, landings, closures) stay on
the main thread. A new request mid-plan is classified by `focus-recovery` and the plan
resumes at its saved step. Per touched unit, route to the owning skills — discovery
(`search-first`), necessity (`yagni`), single authority (`ssot`), boundaries (`solid`,
`clean-architecture`), inline simplification (`simplify`), duplication (`dry`),
configuration ownership (`anti-hardcode`), loud failure (`fail-fast`), documentation
(`arch-docs`, `doc-criteria`). Enumerations discoverable through an authority are its
data, never lists in code or tests; validate grammar, own instances in config.

## Phase 4 — Verification closes every step

Each step ends with a runnable check and its evidence: exact command, working directory,
exit code, decisive output. Warnings, skips, empty output, missing tools, and
zero-execution runs without a typed cache-hit accounting are RED; the first exception
escapes with its raw traceback. "Looks done" is not a signal, and an unchanged status is never reported twice. When a
check contradicts observed runtime behavior, fix the check.

## Phase 5 — Land and close

Carry the cycle to integration: scoped commits by explicit paths, fast-forward push,
resolved review, merge commit into the declared integration lane, affected gates rerun
on the merged state, runtime proved on the integrated artifact, then tracker closure
with the four evidences. Zero residue: superseded code, tests, docs, and branches are
retired in the same cycle. Never rebase or force-push an authorized lane; integrate with
a no-fast-forward merge.

## Stop conditions — the only ones

Stop solely for a genuinely destructive action or an authority conflict: state the exact
error, ask one precise question, then continue to full completion. Local green, an open
PR, and mergeable status are never landed.

Non-negotiables, restated: truth with evidence over every deadline; ethics over every
orientation; refactor the owner in place — a parallel implementation is a violation;
root cause over symptom; evidence over assertion; completion over partial delivery.
