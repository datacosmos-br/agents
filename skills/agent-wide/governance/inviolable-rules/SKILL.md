---
name: inviolable-rules
description: "gate routing, rule owners, session gate sequence"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","usage:router"]'
---

# Inviolable Rules — gate router

Universal law lives in `rules/` and `UNIVERSAL_CORE`; this skill only routes the gate
sequence. Load the named owner at each moment; never restate its law.

| Moment                                                                                 | Owner                                                                                           |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Session start: read request, law, Bead, decisions; verify root/branch/paths/owners/WIP | `coordination/session-governance` + `coordination/beads-verification`                           |
| Truth: done = command+cwd+exit+output+scope; fake green = P0                           | `workflow/runtime-is-reality` + `ethics/professional-integrity`                                 |
| Roles: orchestrator vs worker lane limits                                              | `beads-worker` + `beads-orchestrator` skills                                                    |
| Execution: Make/CLI verbs only, fix-forward, no stash/reset/force on unknown WIP       | `runtime/strict-execution` + `coordination/fix-forward-collaboration` + `git/gitflow-branch-pr` |
| Incident: remote is ground truth, never mutate shared venv, missing tool is RED        | `workflow/runtime-is-reality` + `runtime/required-environment`                                  |
| Refactor: build final owner, migrate all, delete superseded, no old+new                | `architecture/engineering-core`                                                                 |
| Tracker before mirror; Bead updated each state change                                  | `workflow/beads-traceability`                                                                   |
| Continuous green + evidence + review at close                                          | `verification-loop` skill + `workflow/production-readiness`                                     |

Stop only for a real blocker: destructive action, competing contracts, security/privacy,
`main`/prod promotion, final release, authority conflict, material scope change. One
Bead question; else continue.
