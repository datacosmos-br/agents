# Rules

`rules/` is the physical rule authority consumed by `GovernanceBundle`; it
contains rule files only. Do not place indexes, READMEs, generated summaries, or
provider projections in that directory.

Use the public bundle rather than a copied inventory:

- `make audit` validates and prints the current semantic inventory.
- `from agents_governance import GovernanceBundle` loads the typed rule catalog.
- [Architecture decisions](adr/README.md) record rule approval and supersession.

Every rule identity is its lowercase path relative to `rules/`. Rule metadata
declares exactly one supported route and the approval lineage required by the
bundle. Add, rename, or retire a rule atomically with its consumers, evaluations,
ADRs, and AI Hub projections.
