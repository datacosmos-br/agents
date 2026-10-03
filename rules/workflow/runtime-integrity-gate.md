---
description: No plan executes through a broken runtime — deployments are proven by observed real runtime, tmux included.
metadata:
  aihub.tags: '["decision:operator-ruling-2026-10-03", "effective:2026-10-03", "route:both"]'
---

# Runtime integrity gate: the plan stops where the runtime breaks

This composes validate-on-change (runtime functioning is the only proof, per change)
with two plan-level duties the 2026-10-03 incidents made non-negotiable.

## No plan step may land through, or leave, a broken runtime

1. Before executing a plan wave, the executing system resolves the runtime state of
   every surface the wave touches (services, daemons, agent homes, deployed configs).
   Green synthetic gates — unit suites, linters, generated checks — are bookkeeping,
   never the runtime state.
2. Discovering breakage outranks plan progress: announce `[coord] blocker` with the
   exact error, cure the owner first (fix forward, never suppress, never mask), and
   only then resume the plan. A wave that cannot state the observed runtime health of
   its surfaces is not complete.
3. Deprecations leave no residue: a retired projection, config file, or pointer that
   remains on disk and breaks a consumer at parse or load time is a live defect owned
   by the retire-er, even when every tracked gate is green. (Working example:
   an ignored orphan config holding an instruction pointer kept a whole agent
   runtime unparseable while every tracked check passed — 2026-10-03.)

## Deployments are proven by observed real runtime

Every deployment in ai-hub and flext — release activation, agent-home projections,
daemon surfaces, plugin and hook deployments — is accepted only after the deployed
surface is exercised in the REAL runtime and the claimed behavior is observed:
launch the real agent or daemon (tmux where the surface is interactive or
long-running), invoke the real verb against the live socket, and record command,
exit code, and decisive output. Synthetic verification and unit suites remain
mandatory bookkeeping around this observation; they never replace it. A deployment
proven only by gates is not deployed.

## Versions move only through generated locks

Fork and toolchain versions are never swapped by hand — not binaries, not pins, not
toolchain builds. New versions arrive exclusively through the declared upgrade path
(`make upg` regenerating locks) and are then re-provisioned by their owners. A
runtime broken by a version gap is cured by the agreement protocol
(ecosystem-synergy): announce, agree, upgrade the dependent through its own
declared path.
