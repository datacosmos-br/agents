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
`make audit` validates the bundle, `make docs` checks links and `make waza` verifies the
semantic suites.

Obligations live in `rules/`, conditional procedures in `skills/`, invocation grammar in
`commands/`. A child artifact references its ancestor and never copies it. Coordinate
through `rules/coordination/inter-session-mail.md`.
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->
