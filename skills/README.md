# Skills

Recursive discovery from `skills/<category>/<slug>/SKILL.md` is the identity and
primary semantic-group authority. `config/skills.json` owns only schema version
and token/line budgets; it never lists skills, destinations, providers, or
activation state.

- `agent-wide` and `project-wide` state the unconditional semantic route.
- `technology`, `framework`, `tool`, and `domain` state the primary conditional
  subject; validated tags carry route, activation, and detector semantics.
- Every skill is a self-contained physical bundle and has exactly one
  provider-neutral suite under `evals/<slug>/`.

Specialization is an explicit acyclic graph declared with `extends:<skill>`.
Compose from the broadest owner to the narrowest: project-wide capability,
technology/language, framework or library, then project-local policy. A child
references `$<parent>` and contains only its delta; it never copies or weakens
the parent. Parents never import knowledge from descendants. The catalog rejects
missing parents, cycles, reversed layers, and implicit parent references.

Keep `SKILL.md` as a concise activation router. Detailed procedures, scripts,
and assets stay inside that same bundle. A change is complete only when
`make audit APPLY=Y`, `make check APPLY=Y`, and `make waza APPLY=Y` validate the physical
inventory through their root Make owners. AI Hub alone interprets routing
semantics for discovered projects and providers; this repository writes no
destination or generated inventory.
