---
name: plan-focus-recovery
description: 'execution plan continuity, interruption triage, bounded detour recovery'
license: MIT
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:continuity","updates:manual","usage:router"]'
  version: 1.0.0
---

# Plan Focus Recovery

Activate when an execution plan is active and a new request, correction, or
external adjustment arrives before its next step completes. Preserve this skill
as a personal agent workflow; never project it as project or technology law.

Before the detour, save one execution cursor: objective, current step, next
unfinished step, owned paths, latest evidence, and gates invalidated by the new
work. Classify the incoming request once:

- A replacement supersedes the prior plan; update the plan explicitly.
- A required adjustment becomes the smallest bounded detour needed for the
  active objective. Change only its owner and required consumers, validate it,
  and satisfy its declared landing boundary before returning to the saved step.
  A failed check, actionable review, open PR, missing approval, or pending merge
  keeps the detour active; reporting that state is not a detour outcome.
- Unrelated additive work stays outside the active plan unless the operator
  explicitly expands scope. Record or ask one precise question when deferral
  would lose a required decision; do not begin a side investigation.

Do not turn a local blocker into a repository-wide repair, repeat discovery whose
owner evidence is still current, or treat a useful adjacent defect as permission
to change it. A detour inherits the active authorization; it does not broaden it.
Newest operator intent wins over the saved cursor.
Across runtimes, use `plan-handoff`.

Resume only after stating the integrated detour outcome, exact evidence, plan
adjustment, invalidated gates, and the concrete next command for the restored
step. Correct every actionable red result first. If only an irreducible external
condition or new authority remains, keep the cursor and phase active and ask one
targeted question instead of drifting or resuming unrelated work.
