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
credential is the tool's declared failure, never a degraded mode. Services receive only
their declared credential subset through their deployment owner and encrypted storage
(`LoadCredentialEncrypted=` under systemd); a missing credential fails the unit at startup,
and services never open the operator's keyring or statically export session variables.

The AI Hub credential owner reconciles only enrolled entries with the native keyring
in the operator's unlocked session. It keeps the last confirmed OAuth or API revision,
applies updates from either side against the confirmed predecessor, and stops on
conflicting revisions. Revocation cannot restore an older value. A locked keyring
leaves synchronization pending without prompting from a daemon.
