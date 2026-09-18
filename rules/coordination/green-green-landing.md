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

The `full landing cycle` rule owns the delivery path and proof. This rule adds only
cadence: keep local and CI green, repair a red state before new scope, and land each
independently complete green increment instead of batching it into a larger long-lived
lane. Apply runtime only when the declared cycle requires it.
