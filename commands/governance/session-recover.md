---
name: session-recover
description:
  Open an agent session from the recorded surfaces instead of rediscovering context.
argument-hint: "[--repo PATH] [--bead ID]"
metadata:
  aihub.tags: '["decision:ADR-0030","effective:2026-09-27","route:project"]'
---

Recover the context for `$ARGUMENTS` in order and present the cursor (last step)
before any effect. Each step records what it found, or that its surface is absent.
`rules/coordination/inter-session-mail.md` owns adoption and lane declaration; this
command owns the recorded surfaces, the environment truth and the cursor.

1. Read the newest handoff/resume document in the repository's handoff surface
   (`docs/handoffs/`, latest date first) and the cursor plan it names. State
   the owning session and the next unexecuted step.
2. Resolve the explicitly selected tracker route and its activation through
   `rules/workflow/beads-traceability.md`; confirm its native context identity
   before mutation. Local `.beads/` presence neither selects nor revokes a route.
3. Census the integration tip, open PRs, worktrees and branches, and beads under
   the abandonment test of `rules/coordination/inter-session-mail.md`.
4. Scan the coordinator's `gc mail` inbox newest-first for directives, claims by
   other sessions, and critiques that concern the mandate.
5. Environment preflight: the session shell's own cgroup leaf
   (`.service` vs `.scope`), inherited unit markers, and whether the
   worktree's generated artifacts exist for an honest battery.
6. Apply the tracker owner's selected, unavailable or explicitly suspended contract
   before any tracker operation; create no substitute store or discovery probe.
7. Present the recovered cursor: mission, measured state, ordered next steps
   with their owners, and the traps that apply. Then await direction or
   continue the declared plan — never re-derive what the surfaces already
   record.
