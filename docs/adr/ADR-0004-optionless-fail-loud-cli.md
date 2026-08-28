# ADR-0004 — Enforce one optionless fail-loud runtime CLI

- **Status:** Accepted
- **Date:** 2026-08-28
- **Scope:** Deterministic agent runtime invocation, validation, errors, environment, subprocesses, and publication
- **Relates to:** Master v7 runtime extermination plan
- **Supersedes:** Nested `agentsctl` subcommands, CLI flags, compatibility routes, keyring-backed credentials, and catch-based error normalization

## Context

The repository exposed runtime behavior through nested subcommands, flags,
Make targets, console scripts, and direct module entry points. Those parallel
surfaces permitted different defaults, partial validation, hand-selected exit
codes, aggregated findings, compatibility behavior, and credential loading from
keyring. Operators could not infer whether a command executed the complete
workflow or a reduced mode.

The runtime must have one obvious interface. Every invocation must load the
complete contract, validate all prerequisites before effects, and preserve the
actual Python and child-process failure.

## Decision

`agentsctl` is the sole runtime facade. Its complete public grammar is exactly
one optionless verb:

```text
agentsctl help
agentsctl doctor
agentsctl check
agentsctl sync
agentsctl evaluate
agentsctl secure
agentsctl clean
agentsctl live
```

No verb accepts flags, positional arguments, modes, format selectors, aliases,
or compatibility syntax. Configuration and environment SSOTs supply the full
typed contract. Make remains development support and gate composition and may
invoke only these public verbs when it needs runtime behavior.

Every verb performs complete preflight before its first effect. A missing,
empty, conflicting, unexpanded, or invalid required environment value raises
immediately. Keyring code and integration do not exist. Live evaluation reads
only `CLIPROXY_API_KEY` from the current process environment and uses exact
`aihub-primary`.

The first exception escapes with raw traceback and chained cause. CLI and
orchestrators do not catch workflow failures. Validators stop at the first
defect. Errors are never converted into findings, warnings, skips, neutral
values, empty collections, manual exit codes, retries, fallbacks, alternate
providers, operational defaults, compatibility behavior, or partial execution.
Only cleanup and rollback may catch; they attach secondary failure and re-raise
the original cause. Child nonzero exit, timeout, signal, and incomplete
publication propagate without normalization.

## Consequences

- Runtime behavior is discoverable from eight verbs and cannot drift between
  modes or wrappers.
- Automation moves inputs into typed configuration and required environment
  rather than command-line switches.
- Existing scripts, tests, docs, entry points, Make targets, and CI consumers
  must be rewired atomically; compatibility aliases are prohibited.
- An invalid prerequisite prevents every effect, and an effect failure cannot
  be reported as a successful partial result.
- Source and AST gates must reject every superseded entry point, forbidden
  catch, aggregate validator, manual error translation, operational default,
  fallback, retry, and keyring consumer.

## State of implementation

Accepted as the binding contract. Runtime cutover and full gate evidence remain
open under the master v7 Plan 2 execution record. No phase is `DONE` while the
canonical tracker runtime is suspended.
