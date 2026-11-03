# Skills

Recursive discovery from `skills/<category>/<slug>/SKILL.md` is the identity and primary
semantic-group authority. `config/skills.json` owns the schema version, resource formats
and modes, token/line budgets and tag vocabulary; it never lists skills, destinations,
providers, or activation state.

- `agent-wide` and `project-wide` state the unconditional semantic route.
- `technology`, `framework`, `tool`, and `domain` state the primary conditional subject;
  validated tags carry route, activation, and detector semantics.
- Every skill is a self-contained physical bundle and has exactly one provider-neutral
  suite under `evals/<slug>/`.

Specialization is an explicit acyclic graph declared with `extends:<skill>`. Compose
from the broadest owner to the narrowest: project-wide capability, technology/language,
framework or library, then project-local policy. A child references `$<parent>` and
contains only its delta; it never copies or weakens the parent. Parents never import
knowledge from descendants. The catalog rejects missing parents, cycles, reversed
layers, and implicit parent references.

Keep `SKILL.md` as a concise activation router. Detailed procedures, scripts, and assets
stay inside that same bundle. A change is complete only when `make audit`, `make check`,
and `make waza` validate the physical inventory through their root Make owners. AI Hub
alone interprets routing semantics for discovered projects and providers; this
repository writes no destination or generated inventory.

## Naming and tags (ADR-0015, ADR-0038)

Slugs are one or two words, target ≤ 14 characters, family-consistent (`gc-*`, `*-dev`),
and catalog-unique. `aihub.tags` use only the namespaces the catalog accepts, and their
usage, route, activation and subject values come from `config/skills.json`. External
material enters only in this form, with its license and provenance kept in its bundle.
