---
name: session-postmortem
description: "Run the adversarial post-mortem auditor over one agent session: bead trail, branches, PRs, CI verdicts — numbered findings with rules and structural fixes."
argument-hint: "<bead-id> [branch] [PR-number]"
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:project"]'
---

# Session post-mortem audit

Audit one finished (or stalled) agent session against the fleet laws and produce
a numbered findings report. Inputs: $ARGUMENTS = the session's bead id, plus
optionally its branch and PR number.

1. **Gather the trail.** `bd show <bead>` and every comment on it; `git log`
   over the session's branches; `gh pr list --state all` filtered to the
   session's branches; CI verdicts at each pushed head. Delegate heavy log
   extraction to the `session-postmortem-auditor` agent.
2. **Establish the intent baseline.** Quote the bead's description and the
   declaration mail/comment (bead + branch + PR). Anything promised there and
   not merged is finding class "delivery gap".
3. **Audit the four surfaces.** Startup (census + declaration, rule
   `coordination/session-startup-census.md`), execution (collisions, keepalive,
   serialization, protocol instantiation — rules `coordination/`,
   `git/pre-push-keepalive-and-batching.md`, `python/run-raw-exit-semantics.md`),
   understanding (runtime-first vs test-chasing, canonical-tree misreads — rule
   `workflow/runtime-first-contract-tests.md`), hygiene (stale worktrees, silent
   beads, PRs without owners).
4. **Verify every claimed merge.** `git merge-base --is-ancestor <head>
   <integration>`; ancestry without a green post-merge CI is finding class
   "unproven landing".
5. **Prescribe structural fixes.** For each finding, name the rule file that
   now prevents it (create the rule file in this audit if the lesson is new)
   and the exact checklist step. Findings without a structural fix are
   incomplete.
6. **Record.** Post the full report as a comment on the session's bead, and
   send the summary to the coordinator via `gc mail send human`. If the audit
   found lessons not yet in `~/agents/rules/` or the skills tree, land those
   rule/skill files before closing the bead.
