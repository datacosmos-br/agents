---
description: The fleet is one linked ecosystem — every runtime cooperates through gc-mail agreements before shared infrastructure moves.
metadata:
  aihub.tags: '["decision:operator-ruling-2026-10-03", "effective:2026-10-03", "route:both"]'
---

# Ecosystem synergy: linked runtimes, formal agreements, shared objectives

The operator's fleet is ONE linked ecosystem, not a set of parallel sessions. Bound
runtimes today: Gas City (city, rigs, dispatchers, witnesses, dogs), Hermes and the
WhatsApp bridges, Kilo Code, ZCode — and every future runtime adopts this rule on
attach. Each runtime is addressable: directly through `gc mail` when it holds a
registered alias, otherwise through its bridge owner, who carries the same contract
into it. "Not a registered session" never means "outside the rules."

- Cooperation outranks lane territory. Lanes have owners; objectives are shared. A
  system that can unblock another's objective proposes the unblock in-thread instead
  of holding its lane.
- Work integrates by the collaboration protocols: fix forward, adopt current state,
  supersede with evidence. Provenance never exempts a contribution from adoption, and
  never exempts a defect from cure (see fix-forward-collaboration).

## Formal agreements before shared infrastructure moves

A mutation to infrastructure OTHER systems depend on — tracker stores and their
schema versions, shared daemons and their ports, toolchains on the fleet PATH,
deployed surfaces in agent homes, city config — requires a prior gc-mail agreement:

1. `[coord] agreement <topic>` announces the intended mutation: what moves, the exact
   store/tool/surface, the new version, and every system it can break.
2. The affected systems ACK in-thread, or the announcer executes after the stated
   quiet window expires. An objection stops the mutation until adjudicated.
3. The executing system posts `[coord] landed <what> <version>` with the sealing
   evidence, and states which binaries/sessions must upgrade before their next call.
4. A system discovered broken by a migration announces `[coord] blocker` with the
   exact error; it does not loop retries against the moved target, and it does not
   mask the skew — the cure is upgrading the dependent, never downgrading the store.

Working example (2026-10-03): a tracker store migrated ahead of the fleet binaries;
rig dispatchers failed their work queries in a retry loop. The agreement protocol
above exists to make that incident structurally impossible.

## Presence is proven, and silence means offline

The liveness rule is message-based: a runtime counts as working only if it produced a
message today (mail, event, or bridge receipt). Every lane whose last evidence
predates today is abandoned and adoptable by any live system through fix-forward.
Roll-calls are answered, never inferred from processes, sockets, locks, or checkouts.
