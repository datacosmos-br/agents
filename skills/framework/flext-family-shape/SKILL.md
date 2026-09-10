---
name: flext-family-shape
description: 'flext family part shape law, five private families, flat entity declarations, rope rules'
license: canonical flext law
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0014","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-09-09","route:project","subject:flext","usage:on-demand"]'
---

# FLEXT Family Shape

Composes with `$flext-law` and ADR-014; this skill owns only the family part
shape delta for internal FLEXT packages.

## Family layout law

- Five private families per package: `_constants/`, `_typings/`,
  `_protocols/`, `_models/`, `_utilities/`; each begins with `base.py`
  (namespace-gate law).
- A family part file declares ONE part class (`<FlextStem><Family>...`) and
  nests its content directly — entities only, one level deep: Pydantic models
  (`m.*Model`), enums (StrEnum), protocols (`Protocol`), behavior classes
  (bodies with function definitions).
- Top-level classes beside the part class are **orphans** — forbidden. Hoist
  into the part class as a public nested entity (PascalCase, underscore
  stripped); never keep a private class plus an alias attribute.
- Direct children of the part class with no entity base and no functions are
  **pure namespace wrappers** — forbidden. Flatten their members one level up
  (prefix-merge on collision) and rewire consumer chains package-wide
  (`X.Wrapper.Y` → `X.Y`).
- Facade roots inherit the canonical layer letter(s), nest exactly one domain
  namespace composing ≥2 part classes via multiple inheritance, and end with
  the canonical bottom alias (`c`/`t`/`p`/`m`/`u`).

## Declarative Rope rules

- One YAML file per rule in
  `src/flext_infra/codemod/rope_rules/<rule-module>/*.yml`, ast-grep-like
  shape: `id`, `severity`, `message`, `files` globs, and a `rope:` action
  section (`hoist_into_part_class`, `flatten_wrapper_children`).
- Parsed once through `u.Cli.yaml_*` into typed `m.Infra` rope-rule models;
  the loader fails loud. Thresholds/globs are rule data, never hardcoded.

## Change and safety cycles (mandatory)

- Rewrites extend the common base (`FlextInfraUtilitiesRopeRuntime`,
  `RefactorNamespaceMoves` patterns): every mutation is a Rope `Change`
  applied via `rope_project.do(changes)` so changes replicate to all
  referencing modules, followed by rewritten-file normalization — inside the
  `make mod APPLY=Y` guarded fixed-point circuit.
- Every mutating execution wraps its files in the centralized cycle
  `FlextInfraUtilitiesSafety.execute_safely` (backup → transform → validate →
  cleanup | rollback). Ad-hoc writes, private backups, and repo-wide rollback
  are forbidden.

## Gates

- `make check` enforces the same laws in the namespace validator; message
  text matches the rule files. Platform exceptions stay encoded once
  (`NAMESPACE_PLATFORM_FACADE_SINGLETONS`, `cli.py` `main`, `api.py`
  composition-root singleton).

## First execution

`flext-dbt-oracle-wms`: `_Materialization` hoist, `Dbt` wrapper flatten,
consumer paths `c.DbtOracleWms.PROJECT_NAME` and
`c.DbtOracleWms.Materialization.VIEW.value`. Evidence lives in the
branch-matched Bead.
