# Architecture decisions

| ADR | Status | Decision |
|---|---|---|
| `ADR-0001` (doc file) | Accepted | Skills, commands, agents, and rules retain distinct canonical types. |
| `ADR-0002` (doc file) | Accepted | Skill paths own distribution/primary group; tags own orthogonal semantics. |
| `ADR-0003` (doc file) | Accepted | Provider outputs are typed, provider-native physical projections. |
| `ADR-0004` (doc file) | Accepted | Agent runtime uses one optionless fail-loud `agentsctl` facade and no keyring. |
| `ADR-0005` (doc file) | Accepted | Governance composes typed owners and projects through provider-native instructions and lifecycle surfaces. |
| `ADR-0006` (doc file) | Accepted | Historical governance is synthesized by behavior into current owners, never copied by structure. |

Implementation order, runtime evidence, and landing state belong to the active
`master v7 execution package` (doc file), not to these
decision records.
