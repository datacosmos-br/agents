---
description: The OS keyring is the operator's store; application code never reads it.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-06","route:both"]'
---

# The keyring is the operator's store, never an application ingress

The operating-system keyring is the official place a person keeps a secret on
their own machine, and the tools they drive interactively — the forge CLI, the
package manager, the browser — legitimately hold their credentials there. An
operator storing, reading, or rotating a secret in it is normal custody, not a
violation.

What is prohibited is the layer above reaching into it. Application code,
configuration, entry points, shell integration, services, tests, documentation,
and generated projections contain no keyring owner, reader, writer, loader,
profile, alias, migration, maintenance, discovery, or compatibility path. A
service that reads the keyring directly acquires an ambient credential whose
presence depends on a desktop session, an unlocked collection, and a login
agent; it then behaves differently under systemd, in CI, and over SSH, and the
difference surfaces as an authentication failure far from its cause.

A service receives its credentials only from the encrypted credential store
(`systemd-creds` + `LoadCredentialEncrypted` + `CREDENTIALS_DIRECTORY`) or from
validated variables already present in its own process environment. Missing or
invalid credentials raise immediately; nothing falls back to the keyring, and no
code path treats the two as interchangeable.

An operator-held keyring value is external user state to every automated actor:
an agent does not enumerate the collection, migrate entries between stores, or
delete them. It writes or reads one entry only when the operator asks for that
exact entry.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
See also: `required-environment.md` (rule file) — the encrypted credential
store is the sole service-credential mechanism.
