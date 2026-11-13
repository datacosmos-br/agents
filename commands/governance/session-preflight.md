---
name: session-preflight
description:
  Open a session from the recorded surfaces, verify runtime and tracker identity, and present the cursor before any effect.
argument-hint: "<optional repository paths>"
metadata:
  aihub.tags: '["decision:ADR-0028","effective:2026-09-27","route:agent","supersedes:command:session-recover","supersedes:command:session-startup"]'
---

# Session preflight

Resolve each requested repository from `$ARGUMENTS`; otherwise use the active project.
Follow `rules/coordination/inter-session-mail.md`, which owns adoption and lane
declaration, and the operator's current scope. Run the steps in order before the first
edit. This preflight inspects and reports; claims, adoption, lane creation and
announcements are later, explicit effects. Each step records what it found, or that
its surface is absent.

1. Read `rules/law.md`, the rules the work touches, and the newest handoff in the
   repository's handoff surface with the cursor plan it names. A handoff directory is
   opened by `plan-handoff <directory>`, whose accepted cursor and claim this preflight
   reuses. State the owning session and the next unexecuted step.
2. Read the selected tracker route from its owner
   (`rules/workflow/beads-traceability.md`) and prove the intended identity through its
   declared context command before mutation. Installation, a directory or a local
   `.beads/` neither selects nor revokes a tracker. Apply the owner's selected,
   unavailable or explicitly suspended contract; create no substitute store or
   discovery probe, and keep unavailable orchestration and separately available
   tracking distinct.
3. Establish source, physical environment, lock and consumed dependency identities
   through the project's native provenance operation. A mismatch invalidates dependent
   receipts. Setup reconciles declared locks; dependency advancement uses its separate
   owner. Reuse a currently valid environment rather than reinstalling it per gate.
4. Read the session shell's own cgroup leaf (`.service` vs `.scope`), never inherited
   unit markers, and whether the worktree's generated artifacts exist for an honest
   battery.
5. Resolve the coordinator and selected communication channel through their canonical
   rules. Read its inbox newest-first for directives, claims by other sessions,
   conflicts and critiques that concern the mandate. Report any missing declaration
   before the first coordinated effect; do not resume suspended orchestration.
6. Inspect the integration tip, open PRs, local and remote branches, worktrees, recent
   documents, ready beads and recorded ownership for the scope. Preserve relevant WIP
   (`rules/law.md` item 11) and adopt a survivor under the abandonment test of the
   coordination rule before creating a competing lane or bead; placement follows
   `rules/git/gitflow-branch-pr.md`. Do not infer abandonment from one old signal.
7. Identify unpublished owned commits and incomplete prior units. Reconcile them through
   their existing lane and tracker before accumulating another independent unit.
8. Identify the active approved plan and every instruction, document, skill, rule and
   command the planned change would contradict (`rules/law.md` item 12); report each
   before implementation.
9. For an authorized transaction, identify the owner that makes its effect complete or
   absent (`rules/law.md` item 8) and report a missing one instead of inventing a
   substitute. The agreed specification stands (`rules/law.md`); a faster validation
   route keeps its declared population and acceptance evidence.

Run only discovered public commands under `rules/workflow/canonical-commands.md`.
Return one evidence-bearing result per inspection, its scope and the first causal
failure. A missing inspection is unresolved, not a pass. Do not use skip switches to
omit required ownership or coordination evidence.

Present the cursor: mission, measured state, ordered next steps with their owners, the
traps that apply, and the cycle — which integration branch, which gates and what runtime
proof close the unit (`rules/law.md` item 10). Then, in a selected tracker workflow,
claim the bead unless the handoff already did, and record the actual branch and PR state there and in the coordination
channel before the first effect; a declaration grants no branch creation or Git
publication authority. Continue the declared plan; never re-derive what the surfaces
already record.
