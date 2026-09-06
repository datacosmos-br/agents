---
description: Rehydrate governance at session, prompt, compaction, and subagent boundaries.
---

# Rehydrate governance at every agent context boundary

Static provider instructions own the complete standing contract. Provider hooks
refresh a compact governance capsule at every native equivalent of session
start, prompt submission, context compaction, and subagent start. A hook is a
delivery mechanism; it is never a policy owner, public command, fallback,
daemon, or second runtime path.

Content and delivery have separate owners, and neither writes the other's
surface. Optionless `agentsctl sync` owns the content: skills, commands, rules,
and the governance capsule rendered from them. Hook delivery belongs to the
consuming runtime that the hook actually executes, and it projects only into
the agent's own home, never into a project or workspace. A hook that names an
interpreter and a script is alive only on the host where that runtime is
installed; writing one into a repository bakes one machine's absolute paths
into a portable tree, where it is dead everywhere else. Two owners writing one
provider configuration file is the second runtime path this rule forbids: the
last writer wins and the capsule silently stops being delivered.

At session start, load the current operator and repository instructions before
work. At each prompt, apply the newest operator intent and route only the skills
material to that request. After compaction, restore the active goal, evidence,
scope, exclusions, accepted concurrent work, first red gate, and next action.
Every subagent inherits the current authority, fix-forward contract, and a
bounded assignment; it may not discard, stash, roll back, or overwrite another
actor's work.

Provider capability is explicit in the declared configuration of whichever
owner projects that surface. An exact native event is used when available. A documented per-turn or pre-model equivalent is
used when it is the provider's only delivery point, and observational events
remain observational. Never claim an exact lifecycle semantic that the provider
does not expose. Declarative instructions and projected skills/rules remain the
standing guarantee when a hook can only observe or advise.

Compose with `operator precedence` (rule file),
`fix-forward collaboration` (rule file),
`strict execution` (rule file), and
`runtime evidence` (rule file).
