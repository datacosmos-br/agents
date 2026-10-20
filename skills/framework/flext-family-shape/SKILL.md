---
name: flext-family-shape
description:
  "flext family shape, five private families, flat entity declarations, rope rules"
license: canonical flext law
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0014","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-09-09","route:project","subject:flext","usage:on-demand"]'
---

# FLEXT Family Shape

Composes with `$flext-law` and ADR-014; this skill owns only the family part shape delta
for internal FLEXT packages.

## Family layout law

- Five private families per package: `_constants/`, `_typings/`, `_protocols/`,
  `_models/`, `_utilities/`; each begins with `base.py` (namespace-gate law).
- A family part file declares ONE part class (`<FlextStem><Family>...`) and nests its
  content directly — entities only, one level deep: Pydantic models (`m.*Model`), enums
  (StrEnum), protocols (`Protocol`), behavior classes (bodies with function
  definitions).
- Top-level classes beside the part class are **orphans** — forbidden. Hoist into the
  part class as a public nested entity (PascalCase, underscore stripped); never keep a
  private class plus an alias attribute.
- Direct children of the part class with no entity base and no functions are **pure
  namespace wrappers** — forbidden. Flatten their members one level up (prefix-merge on
  collision) and rewire consumer chains package-wide (`X.Wrapper.Y` → `X.Y`).
- Facade roots inherit the canonical layer letter(s), nest exactly one domain namespace
  composing ≥2 part classes via multiple inheritance, and end with the canonical bottom
  alias (`c`/`t`/`p`/`m`/`u`).

## Declarative Rope rules

- Resolve rule resources through the active branch's typed rule catalog. One
  declarative document owns each rule's identity, severity, scope and semantic action;
  do not revive a historical source path or maintain a second rule list.
- Parsed once through `u.Cli.yaml_*` into typed `m.Infra` rope-rule models; the loader
  fails loud. Thresholds/globs are rule data, never hardcoded.

## Change and safety cycles (mandatory)

- Rewrites extend the common base (`FlextInfraUtilitiesRopeRuntime`,
  `RefactorNamespaceMoves` patterns): every mutation is a Rope `Change` applied via
  `rope_project.do(changes)` so changes replicate to all referencing modules, followed
  by rewritten-file normalization — inside the `make mod` guarded fixed-point circuit.
- Use the existing native candidate preview and authenticated publication owner.
  Validate producer and consumer changes as one dependency group before publishing.
  Abort an unpublished candidate without changing live work; reconcile any published
  effects forward through its journal. Never restore an older source snapshot, discard
  shared WIP, create private backups or introduce another publication engine.

## Gates

- `make check` enforces the same laws in the namespace validator; message text matches
  the rule files. Platform exceptions stay encoded once
  (`NAMESPACE_PLATFORM_FACADE_SINGLETONS`, `cli.py` `main`, `api.py` composition-root
  singleton).

Historical executions remain in Git and their canonical tracker records. They do not
select the current repository, rule resource or migration state.
