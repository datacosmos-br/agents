---
description: Dependency cooldown, frozen resolution, containers and interpreter input
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Supply chain

Every resolver, uv included, waits one rolling cooldown of at least seven days, set
once in the owning package-manager and Dependabot configuration as a relative span,
never a fixed date that silently expires. The project's own packages and its forks are
exempt, and a CVE or critical fix is exempted only by a declared, typed exception;
locks change only as [canonical-commands](../workflow/canonical-commands.md) states. Final container stages
run as a dedicated non-root user on a compatible base with no reproducible scanner
findings. Input entering LDAP, SQL, shell, templates or any other interpreter passes the
owner's typed validation and escaping primitive, never string concatenation.
