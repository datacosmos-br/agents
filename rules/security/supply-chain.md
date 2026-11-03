---
description: Dependency cooldown, frozen resolution, containers and interpreter input
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Supply chain

Dependency updates wait a rolling cooldown of at least seven days, set in the owning
package-manager and Dependabot configuration, never a fixed date that silently expires.
`exclude-newer`, in any form, freezes resolution against a date instead of a reviewed
lock and is removed at its owner; locks change only as
[canonical-commands](../workflow/canonical-commands.md) states. Final container stages
run as a dedicated non-root user on a compatible base with no reproducible scanner
findings. Input entering LDAP, SQL, shell, templates or any other interpreter passes the
owner's typed validation and escaping primitive, never string concatenation.
