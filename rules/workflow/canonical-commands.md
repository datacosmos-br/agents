---
description: Declared verbs call native tools; locks, heavy runs, deadlines, test verbs
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Canonical commands

Every operation runs through the repository's declared verbs, each a thin call to its
native tool that does only its own operation ([law](../law.md)); a change is validated by
its owner's scoped command, and gates cover every tier (source, tests, examples, scripts)
alike. Configuration declares the newest versions and only the
upgrade verb locks them; every other verb installs from the committed locks, offline.
Each machine runs one heavy job at a time, and a pull-request gate fits
`gates.pr_budget_minutes` (`config/governance.json`). Every command runs under a deadline, the
120-second bound of `operator-order-2026-10-24-make-always-with-timeout` unless its
project declares a tighter one, and a timeout is a failure fixed at its cause. Each
catalog names its test verbs: the incremental verb runs Testmon on its persistent
database, never deleted or replaced except by Testmon's own schema migration, the full
verb runs once without it, locally, and a
run that executes nothing counts only as an integrity-checked cache hit. A generated file
names its writer and regeneration command, and a block written by a tool changes only
through that tool and loses to any rule it contradicts. Text published to a forge or
tracker comes from a file.
