---
name: session-recover
description:
  Open an agent session from the recorded surfaces instead of rediscovering context.
argument-hint: "[--repo PATH] [--bead ID]"
metadata:
  aihub.tags: '["decision:ADR-0030","effective:2026-09-27","route:project"]'
---

Recover the context for `$ARGUMENTS` in order, and stop at step 9 to present
the cursor before any effect. Every step records what it found; a step whose
surface is absent says so explicitly. Compose with
`rules/coordination/session-startup-census.md`: it owns the census steps
(tip, PRs, worktrees, beads, declaration); this command owns the recorded
surfaces, the environment truth, and the cursor presentation.

1. Read the newest handoff/resume document in the repository's handoff surface
   (`docs/handoffs/`, latest date first) and the cursor plan it names. State
   the owning session and the next unexecuted step.
2. Prime the tracker (`bd prime` where the repository contains `.beads/`) and
   confirm the store identity (`bd context --json`) before any tracker
   mutation.
3. Run the startup census exactly as the census rule declares (integration
   tip, open PRs, worktrees and branches, beads under the abandonment test of
   rule `bead-branch-pr-cadence` §2).
4. Scan the coordinator inbox (gc-mail human) newest-first for directives,
   claims by other sessions, and critiques that concern the mandate.
5. Environment preflight: the session shell's own cgroup leaf
   (`.service` vs `.scope`), inherited unit markers, and whether the
   worktree's generated artifacts exist for an honest battery.
6. Verify the tracker-boundary rule applies (repository contains `.beads/` or
   the tracker is explicitly suspended) before any tracker operation.
7. Present the recovered cursor: mission, measured state, ordered next steps
   with their owners, and the traps that apply. Then await direction or
   continue the declared plan — never re-derive what the surfaces already
   record.
