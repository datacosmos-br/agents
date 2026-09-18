---
description: Validation of genuinely non-derivable process-environment inputs.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:both"]'
---

# Required environment values are exact

First resolve every deterministic default from its typed SSOT. Do not require an
environment variable, setting, parameter, or call argument for a value that the owner
can derive and validate without operator input. Only a current external value with no
canonical derivation is required.

Read each genuinely required environment variable once at the typed boundary from the
current process environment. A variable that is absent, empty, whitespace-only,
conflicting with another owner, contains an unexpanded placeholder, violates its schema,
or is unauthorized raises immediately before effects.

Do not load a missing value from a file, shell profile, OS keyring, service, alternate
name, inherited compatibility alias, prompt, or error-triggered default. Do not silently
trim, coerce, repair, or substitute it. Never print secret values, derived fingerprints,
or full environments in failure evidence.

## One credential, one variable, every consumer

A credential that authenticates one external service is read from a single variable
shared by every project and every tool that needs it. A tool-scoped alias of the same
credential is a prohibited compatibility alias, even when the tool documents it: the
tool is configured to read the shared variable instead.

The consequence of an absent credential is the tool's own declared failure, not a
degraded mode. A tool that silently continues unauthenticated — with a lower quota,
reduced verification, or unsigned artifacts — is failing quietly; require the variable
at its boundary so the workflow stops instead.

## Encrypted credential store

A service's credentials come only from its encrypted credential store:
`systemd-creds`-sealed secrets, declared with `LoadCredentialEncrypted=` and read from
`$CREDENTIALS_DIRECTORY` at startup. The process environment carries only what the
service's own loader injects from that directory — never a secret set by a shell
profile, a `.env` file, a CI variable, or an inherited parent-process export.

A unit that has credentials configured but omits `LoadCredentialEncrypted=`, or whose
`$CREDENTIALS_DIRECTORY` is unset or empty at startup, fails loud immediately and keeps
failing until the unit is fixed. That crash loop is the correct behavior, not a defect
to route around with a default, a cached secret, or an environment-variable fallback:
fix the unit file, never the service's startup check.

A service never reads the OS keyring (`rules/runtime/no-keyring.md`): that store belongs
to the operator's login session, and the encrypted credential store is a distinct,
systemd-owned mechanism that is never substituted with a keyring access path or treated
as equivalent to one.

## Session-bus variables belong to the login session

`systemctl --user`, `systemd-run --user`, and `journalctl --user` need `XDG_RUNTIME_DIR`
and `DBUS_SESSION_BUS_ADDRESS`, which PAM sets for the login session. A shell without
them (an agent spawned outside the session) fails loud there; that failure is correct.
Never export either variable statically from a generator, profile, or hook — a frozen
value points at a runtime directory that disappears with the session. A one-shot command
that needs a sealed credential runs as
`systemd-run --user -p LoadCredentialEncrypted=<name>:<path> ...` from a shell that
already carries the session variables; that is the declared delivery.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
