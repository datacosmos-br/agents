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
- `config/skills.json`: skill classification and distribution policy.
- `config/projections.json`: personal and registered-project destinations.
- `src/agents_governance/`: validation, normalization, discovery, and copying.
- `config/model-pipeline.json`: stable model-pipeline owner; generated into Waza and agent surfaces.
- `.waza.yaml` and `evals/`: generated model projections plus Waza behavioral gates.

Tool homes and project repositories receive physical copies owned by their
destination. Symbolic links, cross-repository local-path references, and shared
mutable skill directories are forbidden.

## Distribution boundary

Personal targets receive workflows and non-technological capabilities. They do
not receive technology profiles.

Registered project checkouts receive only:

1. explicitly classified project-generic skills;
2. technology skills selected from detected project markers or dependencies;
3. FLEXT-owned skills when, and only when, the project is detected as a FLEXT
   consumer.

Orchestrator, tracker, AI Hub, `~/.agents`, operator workflow, and repository-local
development contracts are private and must never enter generic project
projections. FLEXT is a conditional framework source, not a universal project
template.

## Workspace and storage

Gas City configuration owns project identity and placement through native city,
rig, Pack V2, agent, formula, run, and session primitives. Its runtime is
currently suspended, so only existing checkouts are execution surfaces; loose
clones and manual worktrees remain prohibited.

Storage placement and bounded scratch are owned by [`rules/storage.md`](rules/storage.md).
Managed build/test commands use unique repository-local scratch; shells retain
only a small state-owned fallback. Every projection remains an independent
physical copy.

## Canonical gates

```bash
make audit
make check
make test
make temp
make discover-projects
make sync SCOPE=personal
make sync SCOPE=projects
make spec
make gate
```

`APPLY=Y` is required for mutating audit, projection, normalization, description,
or cleanup targets. A phase is complete only after its approved PR is merged
into the configured integration branch and its Bead is closed with evidence.
