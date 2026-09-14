# agents-governance

`agents-governance` is the provider-neutral semantic authority consumed by AI
Hub. The repository owns canonical rules, skills, commands, agent profiles,
their typed metadata, approval lineage, and one semantic evaluation suite per
skill. AI Hub owns project discovery, provider adaptation, hooks, generated
instructions, transactional deployment, runtime reconciliation, and global
distribution.

## Public API

```python
from agents_governance import GovernanceBundle

bundle = GovernanceBundle.load()
```

The returned frozen snapshot exposes `root`, `schema_version`,
`distribution_version`, `config`, `eval_policy`, `skills`, `skill_metadata`, `commands`,
`agents`, `rules`, and `law`. Loading is read-only and fails on the first
catalog, evaluation-resource, approval, ownership, metadata, profile, command,
rule, or strict-prelude defect.

There is deliberately no executable runtime, projector, provider adapter, hook
generator, home-directory writer, cleanup command, live model runner,
security runner, compatibility alias, or second loading path in this package.

## Development

```text
make help
make setup
make audit
make check
make runtime
make waza
make static
make conform
make fmt
make fix
make mod-check
make mod
make shell
make duplication
make build
make validate-artifacts
make test
make test-full
make ci
```

`make test` and the declared full form both use the same testmon cache; the full
form uses testmon no-selection rather than bypassing cache collection. CI invokes
the same Make owners. The Waza gate proves the projected suite schema, every
skill/evaluation reference, the exact spec threshold, and token ceilings; model
execution belongs to a selected AI Hub runtime and is not claimed by this package.

Release sdists and wheels contain every resource required by `GovernanceBundle.load()`:
configuration, skills, semantic skill evals, rules, commands, agents, the strict
prelude owner, and documents referenced by the governance map. Each artifact is
validated without a source checkout and performs no writes when loaded.

## Plan reconciliation

Project and provider publication runs only through AI Hub. This package has no
project-tree generation verb; its native gates validate the read-only bundle
and packaged resources without replacing a local `.agents` tree.

The `/reconcile-plans` command selects the
[plan-reconciliation procedure](skills/tool/plan-reconciliation/references/procedure.md).
It composes the existing documentation, architecture, tracker-revalidation, and
interruption owners. Collection adapters and projection destinations remain
consumer configuration; AI Hub alone distributes the complete skill resources.
