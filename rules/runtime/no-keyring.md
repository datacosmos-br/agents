---
description: Total prohibition of keyring code, storage, discovery, and integration.
metadata:
  aihub.tags: '["decision:ADR-0004","effective:2026-08-29","route:both"]'
---

# Keyring does not exist in the application contract

Application code, configuration, entry points, shell integration, services,
tests, documentation, and generated projections must contain no keyring owner,
reader, writer, loader, profile, alias, migration, maintenance, discovery, or
compatibility path.

Required credentials come only from validated variables already present in the
current process environment. Missing or invalid credentials raise immediately.
Existing operating-system keyring values are external user state: do not
inspect, enumerate, migrate, mutate, or delete them.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
See also: `required-environment.md` (rule file) — the encrypted credential
store (`systemd-creds` + `LoadCredentialEncrypted` + `CREDENTIALS_DIRECTORY`)
is the sole service-credential mechanism; it is not a keyring and is never
treated as one.
