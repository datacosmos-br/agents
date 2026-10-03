---
description: "Resolve the coordinator from live evidence before the first coordinated effect: an active mayor or supervisor coordinator is the only Tier-1 authority; otherwise elect one agent through the mail channel by self-nomination inside the configured abandonment threshold; otherwise proceed as a degraded solo coordinator with bead-recorded decisions and human-channel reconciliation."
capsule_summary: |
  Operator ruling 2026-10-01: who coordinates is resolved, never assumed.
  Tier 1 — a Gas City mayor or supervisor coordinator proven active by the
  city's own status surface is THE coordinator; active rigs keep only their
  declared bounded exceptions and independent agent sessions also coordinate
  through it; work discovered outside its radar is reported and folded in,
  never run dark beside it. Tier 2 — with the coordinator tier down and the
  mail channel available, hold an election: candidates self-nominate on a
  shared thread, earliest nomination timestamp wins, ties break by the lowest
  session or agent identifier, safe non-conflicting work continues during the
  window, silence past the configured abandonment threshold leaves the
  assuming session the default coordinator, and the mayor's return hands
  duties back only through a handoff recorded on the same thread. Tier 3 —
  with the mail channel also unavailable, proceed as a degraded solo
  coordinator: record every coordination-relevant decision on the active
  bead with timestamps, reconcile through the human channel when it returns,
  and never treat silence as authorization for a destructive or irreversible
  action.
metadata:
  aihub.tags: '["decision:ADR-0032","effective:2026-10-01","route:personal"]'
---

# Coordinator ladder

## Resolve by evidence, at preflight and at every phase boundary

Probe the city's own status surface and record the observed state on the
active bead — the activation contract of
[gascity](gascity.md) forbids inferring it from installation, a process, or a
previous session. Then apply the first matching tier below. The session
declares its lane per
[lane-ownership-declaration](lane-ownership-declaration.md) whatever the
tier; the ladder decides who coordinates, not whether work starts.

## Tier 1 — an active mayor or supervisor coordinator

A coordinator session proven active by the status surface is the only
coordinator. Route everything through it: lane declarations, status,
questions, and approval requests over the mail channel per
[inter-session-mail](inter-session-mail.md). Active rigs keep only their
declared bounded exceptions — their own scoped workstreams — and independent
agent sessions not bound to a rig also coordinate through the mayor. No
parallel uncoordinated lane exists: work discovered outside the mayor's radar
is reported to it and folded into its coordination, never run dark beside it.

## Tier 2 — election through the mail channel

With the coordinator tier down and the mail channel available, elect one of
the active agents:

1. Discover candidates from live signals — the session list when the city
   runtime is up, otherwise worktree locks, running processes, and recent
   bead and mail activity. Multi-signal liveness only; a single stale signal
   proves nothing.
2. Send the election call on a shared thread; candidates self-nominate by
   replying on it. When rig-scoped destinations are rejected while the city
   is suspended, hold the thread on the rig's shared box or fall back to the
   human channel.
3. Continue safe, non-conflicting work during the window — an election never
   stalls execution.
4. The result is deterministic: the earliest self-nomination timestamp wins;
   ties break by the lowest session or agent identifier. A nomination
   unanswered past the abandonment threshold configured in
   [bead-branch-pr-cadence](bead-branch-pr-cadence.md) §2 leaves the assuming
   session the default coordinator; record the assumption on the thread and
   on the active bead.
5. The elected coordinator holds the coordinator duties — tracker state,
   serialized gates, integration ordering, merge approval, closure, and
   escalation to the operator — until an explicit handoff. The mayor's
   return is announced on the same thread and duties return only through a
   handoff recorded there; a returning mayor never silently displaces an
   elected coordinator, and an elected coordinator never silently loses
   duties.

## Tier 3 — degraded solo coordinator

With the mail channel also unavailable, the session proceeds as a degraded
solo coordinator: every coordination-relevant decision — decision, scope,
evidence, intended audience, timestamp — is recorded on the active bead, and
the session reconciles through the human channel as soon as the channel
returns, backfilling the election had other agents been live. Silence is
never authorization: destructive or irreversible actions wait for the
operator; everything else proceeds.

## Boundaries

- No invented approvals: an authorization that cannot be shown is absent, per
  [operator-precedence](operator-precedence.md).
- Escalation follows [lane-ownership-declaration](lane-ownership-declaration.md):
  critical doubt goes to the coordinator; the coordinator escalates to the
  human operator.
- The ladder decides coordination only; conduct, evidence, and landing stay
  with their own owners.
