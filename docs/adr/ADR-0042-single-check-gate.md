# ADR-0042 — `make check` is the single gate

**Status:** Accepted (operator, 2026-11-27). Supersedes ADR-0041.
**Scope:** `Makefile`, `.github/workflows/release.yml`, `rules/workflow/agent-delivery-doctrine.md`,
`skills/project-wide/shell/make-check/SKILL.md`, `README.md`.

## Context

ADR-0041 kept `gen`, `fix`, `fmt` and `ci` public here as a pre-#2791 repository. On
2026-11-27 the operator ordered: "use o padrão novo de make check, acabe com o gen, fmt,
fix". Measured at `97fcce7b`: the commit hook already ran `make check`, the Makefile had
no `ci` target, and `release.yml` still ran `make ci`.

## Decision

This repository adopts FLEXT ADR-037 (flext-infra #2791):

- Public verbs drop `gen`, `fix`, `fmt` and `ci`; their recipes become private steps.
- Outside CI, `make check` runs gen → fix → fmt, then the read-only gates. In CI
  (`GITHUB_ACTIONS=true`, so `CI := Y`) it converges nothing and is verify-only.
- `make upg` stays the only lock writer.
- The commit hook runs `make check`. CI runs `make setup`, `make check` and `make test`.

## Consequences

Instructions that name `make gen`, `make fix`, `make fmt` or `make ci` in our
repositories are stale and are corrected at their owner. Forks keep their upstream verbs.
