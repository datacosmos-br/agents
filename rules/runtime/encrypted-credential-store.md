---
description: Service credentials come only from the systemd encrypted credential store.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-19","route:personal"]'
---

# Service credentials come only from the systemd encrypted credential store

This host rule owns the credential-delivery mechanism that
`required-environment.md` (rule file) and `no-keyring.md` (rule file) point to.

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

## User-manager sessions

`systemctl --user`, `systemd-run --user`, and `journalctl --user` need `XDG_RUNTIME_DIR`
and `DBUS_SESSION_BUS_ADDRESS`, which PAM sets for the login session. A shell without
them (an agent spawned outside the session) fails loud there; that failure is correct.
Never export either variable statically from a generator, profile, or hook — a frozen
value points at a runtime directory that disappears with the session. A one-shot command
that needs a sealed credential runs as
`systemd-run --user -p LoadCredentialEncrypted=<name>:<path> ...` from a shell that
already carries the session variables; that is the declared delivery.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
