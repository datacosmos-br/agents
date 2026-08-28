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
- `config/projections.json`: personal destinations and project-relative copy paths.
- `src/agents_governance/`: validation, normalization, discovery, and copying.
- `.waza.yaml` and `evals/`: Waza gates and behavioral evaluation.

When an explicitly authorized projection is applied, tool homes and project
repositories receive physical copies owned by their destination. Symbolic
links, cross-repository local-path references, and shared mutable skill
directories are forbidden.

## Distribution boundary

Personal targets receive the non-technological skills and supported
command/rule surfaces declared by the projection owner. Technology profiles
never enter personal targets. `agents/` and `workflows/` remain canonical
personal source material; they are not silently copied by an undeclared
projection surface.

Explicit project roots receive only:

1. explicitly classified project-generic skills;
2. technology skills selected from detected project markers or dependencies;
3. FLEXT-owned skills when, and only when, the project is detected as a FLEXT
   consumer.

Orchestrator, tracker, AI Hub, `~/.agents`, operator workflow, and repository-local
development contracts are private and must never enter generic project
projections. FLEXT is a conditional framework source, not a universal project
template.

The current `.agents`-only increment validates projection behavior on local
fixtures. It does not apply changes to tool homes or external project checkouts.

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
make discover-projects PROJECT_ROOTS="<repo-a> <repo-b>"
make sync SCOPE=personal
make sync SCOPE=projects PROJECT_ROOTS="<repo-a> <repo-b>"
make spec
make gate
```

`APPLY=Y` is required for mutating audit, projection, normalization, description,
or cleanup targets. Project discovery and projection accept only explicit,
repeatable `--project-root` values; the global `--root` option selects the
governance source and is never a project selector. A phase is `DONE` only after
its approved PR is merged into the configured integration branch and its
canonical tracker item is closed with evidence. Tracker runtime is suspended,
so no phase can currently be called `DONE`.
