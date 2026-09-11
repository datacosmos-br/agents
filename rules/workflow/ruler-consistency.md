---
description: A gate count is only comparable under one validator SHA plus one config
metadata:
  aihub.tags: '["effective:2026-09-11","route:both"]'
---

# Freeze the ruler before comparing gate counts

Gate/red counts measured under different validator versions, rule
configurations, or scan scopes are not the same measurement. The
cosmos-3flk9 sweep twice read a "reduced" error count that later
re-exploded when the owner validator tip moved, and twice re-greened when
config owners changed `scan_dirs` — each time treating the numbers as one
series.

- Every phase opens with a **frozen-ruler baseline**: record the validator
  SHA (owner package), its config (`scan_dirs`, thresholds, strict modes),
  and the target repo SHA together in the tracker note.
- Never quote a stale count as current state; new SHA ⇒ new baseline row,
  supersedes, does not compare.
- When the owner validator changes, re-baseline the fleet numbers BEFORE
  using them to prioritize fixes or to claim progress.
- CI and local runs must log which validator SHA produced their gate
  output; a green CI run under an older validator is not proof against a
  newer rule-set.

See also: `runtime-is-reality.md` (rule file), `gate-budget.md` (rule file).
