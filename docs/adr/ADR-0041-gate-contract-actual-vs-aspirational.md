# ADR-0041 — Gate contract: actual `make ci` vs aspirational `make check`

**Status:** Accepted
**Date:** 2026-11-26
**Scope:** `rules/workflow/agent-delivery-doctrine.md`, `skills/project-wide/shell/make-check/SKILL.md`, `docs/plans/20261125-governance-alignment.md`, `.githooks/pre-commit`, `.github/workflows/eval.yml`

## Context

The `agent-delivery-doctrine.md` (effective 2026-11-24, ADR-0040) stated that the commit hook runs only `make check CHECK_PHASE=primary` and CI runs `CI=Y make check CHECK_PHASE=primary` plus `CI=Y make tests`. It also claimed `make check` absorbs `gen`, `fix`, `fmt` internally and there are no public `gen`, `fix`, `fmt` verbs.

Measurement on 2026-11-25 (agents dev `b8c1d6ea`, PRs #444/#445) revealed:

- `.githooks/pre-commit` runs `exec make ci` (installed by `make setup` via `core.hooksPath`).
- `.github/workflows/eval.yml` runs `make setup` then `make ci`.
- `Makefile:166` defines `ci: lint shell duplication test`.
- `Makefile:71` defines `check: runtime docs static mod-check conform waza`.
- `PUBLIC_VERBS` includes `gen`, `fix`, `fmt` as public verbs.
- `CHECK_PHASE` does not exist in the Makefile or any executable code.

The doctrine, `make-check` skill, and alignment plan all described a FLEXT #2791 cycle that this repository (pre-#2791) does not implement.

## Decision

This repository is pre-#2791 and its actual gate contract is:

- **Commit hook:** `make ci` (runs `lint`, `shell`, `duplication`, `test`)
- **CI:** `make setup` + `make ci` (named "Runtime-first governance validation")
- **Full non-test acceptance gate:** `make check` (runs `runtime`, `docs`, `static`, `mod-check`, `conform`, `waza`) — not run by hook or CI
- **Public verbs:** `gen`, `fix`, `fmt`, `test`, `ci`, `check`, `test-full`, etc. remain public and are run locally as needed
- `CHECK_PHASE` is removed from all documentation

The aspirational FLEXT #2791 cycle (`make check` absorbs `gen`/`fix`/`fmt`, hook runs `make check CHECK_PHASE=primary`) is documented as the target for Phase 2 (FLEXT/ai-hub) but does not apply to this repository today.

## Consequences

1. Updated `rules/workflow/agent-delivery-doctrine.md` lines 9-10, 41-48, 53-54 to describe the actual `make ci` gate.
2. Updated `skills/project-wide/shell/make-check/SKILL.md` lines 18-20 to describe actual hook/CI.
3. Updated `docs/plans/20261125-governance-alignment.md` to describe the actual cycle.
4. Removed all `CHECK_PHASE` references from documentation.
5. The `agent-delivery-doctrine.md` effective date remains 2026-11-24 (the operator orders); the gate description is corrected.
6. Phase 2 (FLEXT/ai-hub adoption of the #2791 cycle) is tracked separately and does not block this repository's gates.

## Verification

- `make audit` passes (128 skills, 23 commands, 71 agents, 23 rules)
- `make docs` passes (ADR bijection, links OK)
- `make waza` passes (128 suites, 18.4s)
- `make check` passes (complete non-test acceptance)
- `make ci` passes (hook/CI gate)
- PRs #444/#445 merged with required checks green

## Amendment 2026-11-27 — gen/fix/fmt retired

Superseded on the public-verb point by the operator order of 2026-11-27 and FLEXT
ADR-037: `gen`, `fix` and `fmt` are retired here too, and `make check` runs generation,
lint repair and formatting before its validators. The commit hook runs `make check`;
CI runs `make setup`, `make lint shell duplication` and `make test`.