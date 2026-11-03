---
description: Required environment values, service credentials and the operator's keyring
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Required environment

Only values no typed owner can derive are required. Each is read once from the process
environment at the typed boundary; an absent, blank, conflicting, unexpanded, invalid or
unauthorized value fails before any effect, never trimmed, repaired, substituted or
defaulted, and evidence never shows a secret, fingerprint or whole environment. An
external service has one credential variable for every project and tool; a missing
credential is the tool's declared failure, never a degraded mode. A service gets
credentials only from its encrypted store (`LoadCredentialEncrypted=` under systemd), a
unit missing it fails at startup until the unit is fixed, and no session variable such
as `XDG_RUNTIME_DIR` is exported statically. No application code, configuration, test or
document uses the operator's OS keyring; agents touch only entries the operator names.
