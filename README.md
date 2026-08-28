# `~/.agents` — canonical agent governance

`~/.agents` is the sole owner of universal skills, rules, commands, agent
profiles, validation, and projection policy. AI Hub may configure or invoke this
authority; it does not regenerate or compete with it. Legacy third-party skill
sources are retired: useful generic capabilities are agents-owned skills, and
no legacy package, command, rule, projection, or synchronization surface remains.

## Surfaces

- `AGENTS.md` and `UNIVERSAL_CORE.md`: universal execution law.
- `skills/`: canonical, independently materialized skill bundles.
- `agents/`, `commands/`, `rules/`, `workflows/`: personal agent capabilities.
- `config/skills.json`: skill BPE and line-budget policy; recursive paths and
  frontmatter own classification and distribution.
- `config/projections.json`: personal destinations and project-relative copy paths.
- `src/agents_governance/`: strict validation, discovery, orchestration, and
  provider-native projection behind the sole `agentsctl` runtime facade.
- `.waza.yaml` and `evals/`: Waza gates and behavioral evaluation.

When an explicitly authorized projection is applied, tool homes and project
repositories receive physical copies owned by their destination. Symbolic
links, cross-repository local-path references, and shared mutable skill
directories are forbidden.

## Distribution boundary

Personal targets receive `agent-wide` skills plus conditional skills, commands,
agents, and rules only when route and provider capability authorize them.
Technology and framework bundles never enter personal targets by default.
`agents/`, `commands/`, `rules/`, and `workflows/` remain distinct canonical
source types; provider representation never changes those types.

Explicit project roots receive only:

1. explicitly classified project-generic skills;
2. technology skills selected from detected project markers or dependencies;
3. conditional tool/domain skills selected by validated project evidence or an
   explicit opt-in.

Orchestrator, tracker, AI Hub, `~/.agents`, operator workflow, and repository-local
development contracts are private and must never enter generic project
projections. External skill sources, including FLEXT, are outside this
increment.

The current `.agents`-only increment validates projection behavior on local
fixtures. It does not apply changes to tool homes or external project checkouts.

## Workspace and storage

Gas City configuration owns project identity and placement through native city,
rig, Pack V2, agent, formula, run, and session primitives. Its runtime is
currently suspended, so only existing checkouts are execution surfaces; loose
clones and manual worktrees remain prohibited.

The [manual execution ledger](docs/execution/manual-ledger.md) owns increment
state while Gas City, Gas Town, Beads, and Dolt are suspended. It records work
but cannot satisfy tracker closure.

Storage registration and shell scratch placement are owned by
[`rules/storage.md`](rules/storage.md).
Every workflow validates its entire input, environment, child-process, and
publication contract before its first effect. A missing, empty, conflicting,
unexpanded, or invalid genuinely required external value raises immediately.
Canonical calculated defaults resolve once at their typed SSOT and are omitted
from environment variables, settings, parameters, and calls. There is no
error-triggered alternate scratch, credential store, compatibility path, retry,
partial execution, or alternate provider. Every projection remains an
independent physical copy.

## Runtime CLI

```bash
agentsctl help
agentsctl doctor
agentsctl check
agentsctl sync
agentsctl evaluate
agentsctl secure
agentsctl clean
agentsctl live
```

These are optionless single verbs. They accept no flags, positional arguments,
mode selectors, JSON switches, or compatibility aliases. Each verb loads and
validates every prerequisite it needs before its first effect. The first
exception terminates execution with its raw traceback and causal chain. The CLI
never catches a workflow failure or converts it into a finding, warning, skip,
neutral value, empty result, or manually selected exit code.

Make remains the repository's development and gate-composition surface. It does
not implement a second runtime API and never invokes private Python functions
directly. A phase is `DONE` only after its approved PR is merged into the
configured integration branch and its canonical tracker item is closed with
evidence. Tracker runtime is suspended, so no phase can currently be called
`DONE`.
