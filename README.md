# `~/agents` — canonical agent governance

`~/agents` is the sole owner of universal skills, rules, commands, agent
profiles, validation, and projection policy. AI Hub may configure or invoke this
authority; it does not regenerate or compete with it. Legacy third-party skill
sources are retired: useful generic capabilities are agents-owned skills, and
no legacy package, command, rule, projection, or synchronization surface remains.

## Surfaces

- `AGENTS.md`: strict project prelude, local scope, and operator-owned facts.
- `config/governance.json`: typed bootstrap and auditable semantic guarantees,
  each mapped to its final rule, skill, command, or document owner.
- `skills/`: canonical, independently materialized skill bundles.
- `agents/`, `commands/`, `rules/`, `workflows/`: personal agent capabilities.
- `config/skills.json`: skill BPE and line-budget policy; recursive paths and
  frontmatter own classification and distribution.
- `src/agents_governance/`: strict validation, discovery, orchestration, and
  calculated provider-native contracts and projection behind the sole
  `agentsctl` runtime facade.
- `.waza.yaml` and `evals/`: Waza gates and behavioral evaluation.

When `agentsctl sync` is invoked, the nearest ancestor that owns a physical
`.git/` directory is the candidate project. Personal surfaces are selected by
the invocation; a physical project-owned `.agents/projection.json` additionally
authorizes project surfaces. Selected surfaces are fully preflighted and
published as one transaction. Provider-native instructions and hooks refresh the
composed governance capsule without becoming policy owners or public commands.
Managed regions and manifests preserve foreign content and reject modified owned
content. Symbolic links, cross-repository local-path references, and shared
mutable skill directories are forbidden.

## Distribution boundary

`agent-wide` and `route:agent` sources are canonical personal-governance inputs
published by the same optionless `sync`; there is no personal mode or second
verb. Technology and framework bundles never enter personal targets. `agents/`, `commands/`,
`rules/`, and `workflows/` remain distinct canonical source types; provider
representation never changes those types.

The invocation project's physical Git root receives only:

1. explicitly classified project-generic skills;
2. technology skills selected from detected project markers or dependencies;
3. conditional tool/domain skills selected by validated project evidence or an
   explicit opt-in from `.agents/projection.json`;
4. project-routed commands and rules on supported provider surfaces;
5. detected or explicitly selected project-wide agents on supported provider
   surfaces.

Orchestrator, tracker, AI Hub, `~/agents`, operator workflow, and repository-local
development contracts are private and must never enter generic project
projections. External skill sources, including FLEXT, are outside this
increment.

The source checkout remains the only catalog authority. `sync` derives the
project from which it is called and the current process home; it has no scope,
provider, surface, target, project-root, environment-override, or personal mode.

Install the facade from that physical checkout so the executable and catalog
share the same authority:

```bash
cd ~/agents
uv tool install --force --editable .
```

A detached wheel is invalid because it cannot own the repository data consumed
by the runtime.

## Workspace and storage

Gas City configuration owns project identity and placement through native city,
rig, Pack V2, agent, formula, run, and session primitives. Its runtime is
currently suspended, so only existing checkouts are execution surfaces; loose
clones and manual worktrees remain prohibited.

While Gas City, Beads, and Dolt are suspended, create no substitute
tracker or ledger. Preserve evidence only in separately authorized Git commits,
pull requests, reviews, checks, and CI; tracker closure remains unresolved.

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

`agentsctl evaluate` is the sole offline evaluation workflow. It verifies Waza
skill specifications, coverage, and token contracts and executes deterministic
provider-native command, agent, and rule evaluations. It does not claim live
skill behavior: Waza's mock executor cannot provide that evidence.

`agentsctl live` first proves the exact transport, model, and tool path, then
executes every discovered skill scenario and material grader with
`aihub-primary`. It stages every result on the repository filesystem and
publishes one restrictive `results/latest/results.json` only after the entire
corpus succeeds. Missing credentials, transport errors, task failures, grader
failures, timeouts, and incomplete artifacts remain raw failures; no partial
result becomes current.

External-token workflows are auxiliary gates. When their token is absent, they
remain unselected and are recorded as `NOT EXECUTED`; this is not green evidence
for scanner or live semantics and does not block offline CI, Git landing, or
post-merge proof. Invoking `secure` or `live` selects that workflow, so its
credential becomes mandatory and every failure above remains strict.

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

A failed required check, actionable review finding, pending approval, or open
merge is not a handoff boundary. Keep the same phase active, correct and
republish every actionable cause, rerun invalidated evidence, obtain independent
approval, merge, and verify the integration SHA before changing work.
