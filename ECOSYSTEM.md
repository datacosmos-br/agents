# Ecosystem boundary

## Provides

`agents-governance` provides one immutable, provider-neutral
`GovernanceBundle`. Its resources are authored here and packaged together.

## Consumes

The package consumes Python, PyYAML, and its own packaged resources. It does not
consume AI Hub, provider homes, project workspaces, daemons, trackers, model
transports, or deployment state at runtime.

## Connection to AI Hub

AI Hub depends on the released `agents-governance` distribution and is the only
owner of project discovery, provider-specific generation, hook transport,
transactional deployment, activation receipts, and runtime reconciliation.
Generated artifacts point back to their AI Hub owner and regeneration command;
they never become writable governance authorities.

## Validation

Discover exact commands with `make help`. The public material runtime is
`GovernanceBundle.load()`. Repository gates validate that API, Waza semantic
resources, static types, packaging, duplication, workflows, and testmon-backed
public behavior.
