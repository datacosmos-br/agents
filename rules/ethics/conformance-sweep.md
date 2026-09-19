---
description:
  Full-standards conformance sweep — truth, canonical verbs, root cause, closure
capsule_summary: |
  Operator directive (2026-09-16, any rig): truth with evidence only (fake green
  is P0); canonical Make verbs only (no invented selectors, no raw tool
  bypasses); testmon always through make test; root cause + zero residue +
  immediate rewire (no compat/shims/deferred); reality > tests (public facades
  only, no mocks, tm fixtures); strict FLEXT chain (settings→config→c→t→p→m→u→
  base→services→api→cli; reverse imports TYPE_CHECKING-only; lazy imports via
  __init__ preferred for performance — import cycles come from broken strict
  rules, never from the init design); generated files only via generator +
  idempotence; fix-forward, scoped commits, docs in the same change; closure =
  full gitflow (scoped commit → push → PR → --no-ff merge → gates on merged SHA
  → runtime proved → release → deploy) or nothing. Performance: anything over
  ~1 minute without feedback is wrong and gets fixed. Max automation: ast-grep
  search/replace, make mod, crg hierarchy discovery, lsp refactor; list
  registries (e.g. class-nesting-mappings.yml) are exterminated in favor of
  SSOT functions. Gain from every cycle: improve skills/commands/rules/docs/ADRs.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:both"]'
---

# Full-standards conformance sweep (universal, any rig)

Truth with evidence · canonical verbs only · testmon always · root cause + zero
residue + immediate rewire · reality > tests · strict FLEXT chain and module pattern ·
no aliases/redeclarations/compat · DRY/YAGNI/SSOT/CA/DI always · no hand-edits of
generated files · nothing deferred · governance self-repair every session · full
gitflow + runtime closure or nothing.

The lazy import via `__init__` is the PREFERRED form (performance): generated inits
carry the package's real export surface. An empty generated init for a package with
public children is a planner defect — fix the engine, never accept the emptiness. Import
cycles are symptoms of violated strict rules, not of the init design.

The following artifacts are BANNED fleet-wide (operator extermination order, revalidated
2026-09-16): `exclude-newer` (any form, including config vestiges like
`uv_exclude_newer`), and the tool lockfiles. They freeze resolution against the
always-newest contract. Presence in any producer or consumer is a regression: delete at
the owner, commit, push, and record on the tracker.
