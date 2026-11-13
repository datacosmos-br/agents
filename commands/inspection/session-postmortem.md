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
3. **Audit the four surfaces** against `rules/law.md`: startup (census and
   declaration, `rules/coordination/inter-session-mail.md`), execution (collisions,
   keepalive, serialization, protocol instantiation), understanding (runtime-first
   versus test-chasing, canonical-tree misreads), hygiene (stale worktrees, silent
   beads, PRs without owners).
4. **Verify every claimed merge.** `git merge-base --is-ancestor <head>
   <integration>`; ancestry without a green post-merge CI is finding class
   "unproven landing".
5. **Prescribe structural fixes.** For each finding, name the law item or rule it
   breaks and the fix at its owner. Findings without a structural fix are
   incomplete.
6. **Record.** Post the full report as a comment on the session's bead, and
   send the summary to the coordinator via `gc mail send human`. A lesson that
   changes governance corrects its owning text (`rules/law.md` item 12) before the
   bead closes.
