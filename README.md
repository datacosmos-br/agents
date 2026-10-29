# agents-governance

`agents-governance` is the provider-neutral semantic authority consumed by AI Hub. The
repository owns canonical rules, skills, commands, agent profiles, their typed metadata,
approval lineage, and one semantic evaluation suite per skill. AI Hub owns project
discovery, provider adaptation, hooks, generated instructions, transactional deployment,
runtime reconciliation, and global distribution.

## Public API

```python
from agents_governance import GovernanceBundle, catalog_resources

bundle = GovernanceBundle.load()
resources = catalog_resources(bundle)
```

The returned frozen snapshot exposes `root`, `schema_version`, `distribution_version`,
`config`, `eval_policy`, `skills`, `skill_metadata`, `commands`, `agents`, `rules`, and
`law`. Loading is read-only and fails on the first catalog, evaluation-resource,
approval, ownership, metadata, profile, command, rule, or strict-prelude defect.

The central-catalog data boundary is `catalog_resources(bundle)`, returning a
path-sorted tuple of frozen `CatalogResource(relative_path, content, mode, sha256)`
records. Paths are portable relative physical-file identities, content is bytes,
mode is the publication permission bits, and SHA-256 addresses those exact bytes.
Construction rejects mutable content, noncanonical paths, negative/non-integer modes
or bits outside native permissions, and digests that do not match the immutable bytes.
Loading captures the enrolled inputs before semantic validation; the capsule and
catalog use those same inputs. Later source edits or additions affect only a new
load. Publication permissions are validated when the catalog API is requested;
loading does not construct and discard a publication. Physical-file checks remain
mandatory.
The existing wheel `force-include` enrollment in `pyproject.toml` selects the
catalog; configuration and the packaged enrollment document are SDK inputs, not
central publications. The sdist retains these same enrolled sources. No arbitrary
checkout traversal or repository-root copy is part of this protocol.

As specified by [ADR-0022](docs/adr/ADR-0022-home-global-materialized-projection.md),
AI Hub must consume these records to publish the neutral central catalog. In particular,
the central `AGENTS.md` consists of `bundle.law.prelude` and
`render_capsule(bundle).text`, never the checkout's repository-local scope block or
AI Hub's own instructions. Legacy `UNIVERSAL_CORE.md` is not enrolled by this
contract. AI Hub retains transaction, destination, activation and withdrawal ownership.
`make audit` loads the public bundle and captures this catalog through the same public
API; `make runtime` compares that inventory, its content digests and modes in each
installed wheel and sdist against the public source API, separately from skill resources.
This source contract is not an installed-artifact or live-publication receipt;
source/installed byte, mode and digest equality must be measured separately. Native
AI Hub adoption of this API is not established by this SDK source change.

There is deliberately no executable runtime, projector, provider adapter, hook
generator, home-directory writer, cleanup command, live model runner, security runner,
compatibility alias, or second loading path in this package.

## Development

`make upg` resolves dependency and tool locks; `make setup` installs the declared
locked environment. Generation and gates run the existing environment without
implicit dependency synchronization. Run setup explicitly when installation is
required and authorized.

`make gen` retains the development-local provider outputs selected by `ag-la3h`
and commits `19e64c01` and `8226eafc`, as clarified in
[ADR-0008](docs/adr/ADR-0008-governance-bundle-as-public-facade.md).
Its renderer lives outside the package, writes only inside this checkout and
proves a deterministic fixed point. It neither publishes HOME/runtime surfaces
nor replaces AI Hub's installed delivery owner.

`make gen` also projects the portable `.beads/metadata.json` from
`config/beads.yaml`, `config/beads-activation.yaml`, and `.beads/identity.toml`,
and the tracked `.envrc` from
`tools/templates/agents.envrc`. Both files are committed so a new linked worktree
can select the canonical Beads database before setup. The managed `gc bd context`
route supplies the live server host and port; local Dolt data remains ignored.

```text
make help
make setup
make upg
make audit
make check
make runtime
make crg-check
make waza
make lint
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

The development toolchain is supported on Linux x64, the platform declared in
`.mise.toml` and resolved in `mise.lock`. The published Python sdist and wheel remain
platform-neutral and are validated as installed artifacts by `make runtime`.

The test verbs, their testmon contract, and where each runs are declared in
[`rules/workflow/canonical-commands.md`](rules/workflow/canonical-commands.md). CI runs
`make ci`, whose root Makefile composition holds only fast external gates and
`make test`, as [`rules/workflow/gate-budget.md`](rules/workflow/gate-budget.md)
requires; `make check` and `make test-full` run only locally. The Waza gate proves the
projected suite schema, every skill/evaluation reference, the exact spec threshold, and
token ceilings; model execution belongs to a selected AI Hub runtime and is not claimed
by this package.

Workspace placement has one owner:
[`rules/coordination/gascity.md`](rules/coordination/gascity.md). Project procedures
reference that contract rather than deriving a universal isolation requirement from
a campaign's selected checkout. The correction and historical attribution boundary
are recorded in [ADR-0025](docs/adr/ADR-0025-manual-worktrees-during-orchestration-suspension.md).

`make check` and `make ci` validate the immutable package without requiring the host's
AI Hub runtime. Under [ADR-0010](docs/adr/ADR-0010-optional-host-runtime-boundary.md),
host CRG convergence is a separate, mandatory installed-integration acceptance step:
run `make crg-check` alongside the package gates on the selected host. That explicit
verb requires the public `ai-hub` command and propagates any missing command or policy
failure. Remote package CI proves the package; it never claims host CRG convergence.

Release sdists and wheels contain every resource required by `GovernanceBundle.load()`:
configuration, skills, semantic skill evals, rules, commands, agents, the strict prelude
owner, and documents referenced by the governance map. Each artifact is validated
without a source checkout and performs no writes when loaded.

Skill resources expose their format, SHA-256 and configured publication mode through
`GovernanceBundle`. `make runtime` attests the exact resource inventory, bytes and
physical modes after installing both artifacts. It also exercises the public catalog
API and compares its paths, bytes, modes and digests with the source snapshot.
`make static` includes every Python resource selected from that inventory, with SDK
dependencies owned by the development dependency group.

For causal artifact-runtime diagnosis, `ARTIFACT_PROFILE=1 make check` (or the
existing `make runtime`) enables cProfile on that same operation. It changes no
gate, artifact, dependency, deadline or validation scope. Captures use unique,
retained directories under the existing external `ARTIFACT_STATE_ROOT`: the
parent profile measures coordination and child waits after its bootstrap; each
isolated artifact's public-load profile starts before the package import. Make
stage timestamps precede command activation, while profile starts and elapsed
command times are emitted separately with parent/child capture paths. Native termination checkpoints
preserve the original signal action and failures; missing captures remain missing
evidence. This binding does not add a profiling verb or claim source validation
is installed delivery. The docs-first and runtime-before-tests work remains with
`ag-wibx`; the active Bead records command outcomes.

For continuation, use `plan-handoff` and `strategic-compact`: retain links to the
current owner/source revision, refs, measured gates, freshness and next action in the
existing authorized plan or PR, not a second status ledger. Claude and Poolside
resources are pure private parsers; ZCode's parser likewise reads only stdin. The caller
must authenticate and select the source before piping it to the parser. Discovery and
transactional publication remain consumer responsibilities.

## Plan reconciliation

Project and provider publication runs only through AI Hub. This package has no
project-tree generation verb; its native gates validate the read-only bundle and
packaged resources without replacing a local `.agents` tree.

The `/reconcile-plans` command selects the
[plan-reconciliation procedure](skills/tool/plan-reconciliation/references/procedure.md).
It composes the existing documentation, architecture, tracker-revalidation, and
interruption owners. Collection adapters and projection destinations remain consumer
configuration; AI Hub alone distributes the complete skill resources.

Reconciliation transfers valid pending work to Beads and maintained documentation before
retiring one fully accounted plan at a time; it does not implement historical proposals.
The [tracker rule](rules/workflow/beads-traceability.md) owns AI Hub's required automatic,
versioned, own-project `TODO.md` view, never an independent checklist or automatic Git
publication. This governance contract does not claim that the automation is implemented
or activated; real runtime and delivery receipts remain with AI Hub.
