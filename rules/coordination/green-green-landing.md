---
description: Green/green always — integration landings at green points, runtime applied
capsule_summary: |
  Universal law (operator ruling 2026-09-16): keep the project green/green at
  all times — local AND CI — landing on the integration branch as soon as a
  100% green point exists, and applying it to runtime without delay.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:both"]'
---

# Green/green always; land and apply at every green point (universal)

1. Local and CI stay green/green; a red state is triaged before new scope.
2. As soon as a 100% green point exists, land it on the integration branch
   (incremental landings, scoped commits) and apply to runtime.
3. Do not delay landings to batch bigger waves: small green points land and
   apply continuously.
