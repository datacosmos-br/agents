# Architecture decisions

| ADR | Status | Decision |
|---|---|---|
| [ADR-0001](ADR-0001-artifact-type-boundaries.md) | Accepted | Skills, commands, agents, and rules retain distinct canonical types. |
| [ADR-0002](ADR-0002-skill-distribution-paths-and-tags.md) | Accepted | Skill paths own distribution/primary group; tags own orthogonal semantics. |
| [ADR-0003](ADR-0003-provider-native-physical-projections.md) | Accepted | Provider outputs are typed, provider-native physical projections. |
| [ADR-0004](ADR-0004-optionless-fail-loud-cli.md) | Accepted | Agent runtime uses one optionless fail-loud `agentsctl` facade and no keyring. |
| [ADR-0005](ADR-0005-composed-governance-delivery.md) | Accepted | Governance composes typed owners and projects through provider-native instructions and lifecycle surfaces. |

Implementation order, runtime evidence, and landing state belong to the active
[master v7 execution package](../execution/master-v7/README.md), not to these
decision records.
