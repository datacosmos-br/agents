<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AIHUB Inviolable Law — Strict Prelude

This is the compact entry to the canonical rules below, not a second rule body.

1. Evidence: `rules/ethics/professional-integrity.md`.
2. Root-cause correction: `rules/architecture/engineering-core.md`.
3. Selected tracker and unavailable capabilities: `rules/workflow/beads-traceability.md`.
4. Research before effects: `rules/workflow/discovery-before-decision.md`.
5. Reuse the declared owner: `rules/workflow/declared-tool-ownership.md`.
6. Continue within authorized scope: `rules/coordination/operator-alignment.md`.
7. Integration and closure: `rules/git/gitflow-branch-pr.md`.
8. Preserve and integrate WIP: `rules/coordination/fix-forward-collaboration.md`.
9. Resolve non-derivable uncertainty: `rules/coordination/never-deduce.md`.
10. Authority and recency: `rules/coordination/operator-precedence.md`.
11. Workspace placement: `rules/coordination/gascity.md`; storage: `rules/storage.md`.
12. Phase exit evidence: `rules/workflow/phase-admission-protocol.md`.
13. Commands, deadlines and test selection: `rules/workflow/canonical-commands.md`.
14. Results: a native failure, warning or missing required proof remains RED.
    Zero test execution is acceptable only as an integrity-checked incremental cache
    hit with complete deselection accounting, never as tests passed. Availability
    prerequisites follow `rules/testing/observable-runtime.md`.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# AGENTS.md — agents

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
## Repository scope

`agents-governance` owns provider-neutral rules, skills, commands, agent profiles and
semantic evaluations. The supported boundary is
`from agents_governance import GovernanceBundle`; `GovernanceBundle.load()` validates
one immutable catalog. Its public inventory owns counts and identities.

AI Hub owns provider adaptation, publication, withdrawal and runtime delivery.
Repository-local tools do not establish another delivery authority. This local
section describes the governance repository; it is not universal project instruction.

Read [README.md](README.md), [rules index](docs/rules-index.md),
[ADR index](docs/adr/README.md) and [change validation](VALIDATE_ON_CHANGE.md).
Use the public root Make verbs. `make audit` validates the bundle; `make docs` checks
links; `make waza` verifies the semantic suites. The command rule owns their execution
and failure contract. A successful structural evaluation is not native agent proof.

Keep mandatory obligations in `rules/`, conditional procedures in `skills/`, invocation
grammar in `commands/` and discovery metadata in their existing catalogs. Compose
ancestors by reference; do not copy their bodies into child artifacts.

Resolve current integration and workspace authorization before effects. Host
coordination follows `rules/communication/ecosystem-systems-registry.md` and
`rules/coordination/inter-session-mail.md` only when that capability is selected.
Source validation, reviewed integration and installed delivery are separate receipts.
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->
