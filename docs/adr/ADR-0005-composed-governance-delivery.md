# ADR-0005 — Compose governance and project it through native lifecycle surfaces

- **Status:** Accepted
- **Date:** 2026-08-28
- **Scope:** Standing agent law, provider instructions, lifecycle refresh, concurrent work, and synchronization
- **Relates to:** ADR-0003 and ADR-0004
- **Supersedes:** One monolithic universal-law document and project-only projection

## Context

One large document duplicated procedures already owned by rules and skills and
made provider delivery depend on every client retaining that document across
session and compaction boundaries. The seven supported providers expose
different instruction files and lifecycle events. Treating those events as
identical would fabricate guarantees, while adding runtime verbs or bridges
would violate the strict CLI contract.

Concurrent lanes also need one invariant independent of provider: compatible
pre-existing and parallel work is accepted and integrated forward. Stash,
history rewrite, code rollback, and destructive conflict resolution require the
operator's exact approval.

Projects, users, forks, and hosts can authorize different auxiliary tooling.
Treating installation as activation made optional orchestration, tracking,
projection, live providers, and scanners restrict unrelated native work.

## Decision

`config/governance.json` is the typed composition owner. It selects the compact
bootstrap rules and skills and maps every clause retired from the monolithic
document to its final rule, skill, command, or `AGENTS.md` owner. Validation
requires complete clause coverage and resolves every owner before effects.

`agentsctl sync` remains one of exactly eight optionless public verbs. It
compiles static provider instructions, skills, rules, commands, agents, and
native lifecycle adapters; preflights all personal and authorized project
targets; then publishes them as one transaction. A publication failure
compensates only effects created by that invocation. It never discards pre-
existing or concurrent work.

Static instructions are the standing guarantee. Hooks only refresh the same
generated capsule. Managed regions preserve surrounding operator/project text;
manifests preserve foreign hook entries and reject edits to owned artifacts.
There is no daemon, repository Git hook, network bridge, hook verb, private
runtime entry point, retry, fallback, or compatibility projection.

Effective capability is the intersection of project authorization, explicit
operator/workflow selection, and current host readiness. Unselected absence is
a non-target and is neither loaded nor reported. A selected workflow validates
all of its inputs and prerequisites before effects; its first invalid or
unavailable state propagates unchanged. Canonical calculated defaults remain at
their typed owner and are not fallbacks.

| Context | Selected owner | Contract |
|---|---|---|
| Native project | Repository toolchain | No auxiliary hook, command, file, or gate |
| Standalone Beads | Project plus Beads | Beads owns tracking only after explicit selection and runtime availability |
| Gas City without Beads | Project plus pinned city/rig/Pack/store | Gas City owns orchestration; no Beads behavior or closure requirement |
| Gas City with Beads | Both selections | Gas City owns orchestration and Beads owns durable tracking/closure |
| Personal projection | `agentsctl sync` invocation | Current-process home surfaces are selected |
| Project projection | Physical `.agents/projection.json` | Tracked project surfaces are selected; absence writes nothing |

Gas City configuration and runtime semantics come from the project-selected,
pinned release rather than a version copied into standing policy. Current
primary evidence confirms Pack V2 explicit imports and a declared work-store
boundary; Beads is supported but not the only Gas City store.

Lifecycle coverage is explicit rather than inferred:

| Provider | Session | Prompt | Context refresh | Subagent |
|---|---|---|---|---|
| Claude | exact | exact | exact through compact-sourced `SessionStart` | exact |
| Codex | exact | exact | exact through compact-sourced `SessionStart` | exact |
| Cursor | exact | advisory | advisory | advisory |
| Copilot | exact | advisory | advisory | exact |
| Gemini | exact | exact | equivalent through `BeforeAgent` | equivalent |
| OpenCode | equivalent system transform | equivalent system transform | exact compaction hook | equivalent system transform |
| Antigravity | equivalent `PreInvocation` | equivalent `PreInvocation` | equivalent `PreInvocation` | equivalent `PreInvocation` |

`exact`, `equivalent`, and `advisory` are typed configuration values and appear
in generated manifests. An observational hook never becomes an injection claim.

## Provider evidence

- [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- [Codex hook schemas](https://github.com/openai/codex/blob/main/codex-rs/hooks/src/schema.rs)
- [Cursor hooks](https://cursor.com/docs/hooks)
- [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)
- [Gemini CLI hook reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md)
- [OpenCode plugins](https://opencode.ai/docs/plugins/)
- [Antigravity hooks](https://antigravity.google/docs/hooks)
- [Antigravity rules](https://antigravity.google/docs/rules-workflows)
- [Gas City README and prerequisites](https://github.com/gastownhall/gascity/blob/main/README.md)
- [Gas City Pack V2 release contract](https://github.com/gastownhall/gascity/releases)
- [Gas City bead lifecycle and `gc hook`](https://github.com/gastownhall/gascity/blob/main/engdocs/architecture/life-of-a-bead.md)
- [Beads project and workflow](https://github.com/gastownhall/beads)

## Consequences

- A single auditable map replaces duplicated universal prose.
- Provider limitations stay visible and cannot be silently upgraded.
- New sessions, prompts, compactions, and subagents receive the strongest native
  refresh each client actually supports, backed by static instructions.
- Severe incompatible intent stops before the effect for one operator decision;
  ordinary overlap is reconciled and validated forward.
- Forks without project authorization retain their native workflow and receive
  zero tracked projection output.
- Changes to governance, provider contracts, or lifecycle support require config,
  projection, evaluation, and documentation updates in the same cutover.
