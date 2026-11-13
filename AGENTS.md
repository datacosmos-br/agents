<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AIHUB Law — Prelude

Read `rules/law.md` before any work. It is the whole universal law, one page of
outcomes, ranked below only the operator's own words and above every other rule,
skill, ADR and document. Every other rule adds one tool or project fact and never
restates a law. When two paths are correct, take the shorter: less code, the native
tool called directly, the cause deleted rather than covered.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# AGENTS.md — agents

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
## Repository scope

`agents-governance` owns provider-neutral rules, skills, commands, agent profiles and
semantic evaluations. The supported boundary is
`from agents_governance import GovernanceBundle`; `GovernanceBundle.load()` validates
one immutable catalog. AI Hub owns provider adaptation, publication and delivery.

Read [README.md](README.md), [rules index](docs/rules-index.md),
[ADR index](docs/adr/README.md) and [change validation](VALIDATE_ON_CHANGE.md).
`make lint` checks Python, `make docs` links, `make audit` the bundle, `make waza` the
semantic suites.

Obligations live in `rules/`, procedures in `skills/`, grammar in `commands/`; a child
references its ancestor, never copies it. Run `commands/governance/session-preflight.md`
before any effect.
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->
