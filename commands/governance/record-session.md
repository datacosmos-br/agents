---
description: Session recording checklist — turn the session into canonical records at close
capsule_summary: |
  Operator ruling 2026-09-27: the handoff is an index, not content. At session
  close, record the work in the five canonical destinations (beads, landing
  record, ADRs, governance repo, handoff index) with a mandatory critical
  retrospective, then land the records themselves through the full cycle.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:both"]'
---

# Record session

Run this at session close — before the handoff, because the handoff only
points here. The role package for doing this as a dispatched job is the
`session-chronicler` agent.

## 1. Gather evidence

Merged PR numbers with dev tips, closed bead ids with their evidence notes,
the mail trail with the coordinator, measurements (profiles, load, durations),
and the inherited reds with their owners. No claim without one of these.

## 2. Write the five destinations

1. **Beads**: every work unit tracked; closure evidence on closed units;
   re-verified scope on future units. The queue lives here, not in docs.
2. **Landing record**: `docs/plans/<date>-<slug>-landing.md` in the product
   repo — per PR: content, root causes, measurements, inherited reds.
3. **ADR**: one per durable architectural decision, catalog row in the ADR
   README. Decisions that bind future work only.
4. **Governance repo** (`~/agents`): new acting rulings → rules; verified
   mechanical cycles → skills; dispatchable roles → agents; checklists →
   commands. Bundle-contract frontmatter (one route + `decision:ADR-XXXX`).
5. **Handoff index**: rewrite to reference 1–4 only. Content elsewhere.

## 3. Critical retrospective (mandatory, no diplomacy)

Answer in the landing record's `## Retrospective` section:
- **Startup**: what did I not read/claim/search that a rule already covered?
- **Execution**: where did work get lost, redone, or broken by wrong context?
- **Delivery**: what reached the coordinator late, incomplete, or as a blob?
- For every failure, name the mechanism that now prevents it (rule, skill,
  command, or bead note). A retrospective without mechanisms is a diary.

## 4. Land the records

The records are work: gates, PR, merge in each repo touched, post-merge SHA
into the handoff index, closure evidence on the activity bead, closing mail
with the triple.

## Reference execution

`docs/plans/2026-09-27-real-activation-f4-f5-landing.md` (ai-hub) and
agents PR #182 (rule + skill + agent + commands) are the worked example of
this command.
