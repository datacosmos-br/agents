---
description: Required environment values, service credentials and the operator's keyring
capsule_summary: |
  Every AI Hub daemon and spawner runs the latest integrated binary. AI Hub
  delivers CRG and OpenViking triggers and MCP to every configured agent,
  repository and worktree. A failing runtime, hook or MCP blocks other work
  until verified at its real consumer.
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

Only the AI Hub credential owner reconciles enrolled proxy accounts with the native
keyring in the operator's unlocked session. The keyring retains the last confirmed
OAuth or API revision; the proxy owns operational use and renewal. Updates from either
side require the confirmed predecessor; conflicting revisions stop reconciliation.
Revocation cannot restore an older value. A locked keyring leaves synchronization
pending without prompting from a daemon.

All agents in every session and project use the installed system AI Hub at the
current integration tip for all operations. The operator grants standing
authorization for operations through AI Hub. Every daemon and spawner must run
the latest integrated AI Hub binary. AI Hub propagates CRG and OpenViking triggers
and MCP access to every configured agent, repository and worktree. Verify the
serving revision, each hook event and each MCP at its real consumer. A runtime,
hook or MCP failure blocks other work until repaired at its owner.
