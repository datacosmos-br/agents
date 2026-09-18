---
name: dmux-workflows
description: "dmux, terminal orchestration, agent coordination"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:dmux","effective:2026-08-28","route:agent","subject:dmux","usage:on-demand"]'
---

# dmux Workflows

Activate only when the operator explicitly requests dmux or parallel agent panes. Keep
small or dependent work sequential.

Before starting a pane, prove that each slice is independent, has a complete input and
output contract, and has non-overlapping ownership. Resolve the installed dmux
interface, current orchestration permission, selected harness, required current-process
credentials, resource limits, and synthesis order. File-changing panes additionally
require the repository's declared isolation owner. Do not create branches, worktrees, or
substitute isolation locally.

While orchestration runtime is suspended, do not invoke dmux or any harness; produce a
read-only plan only. After restoration, use exactly the selected interface and harness.
Never switch provider, model, harness, pane role, or execution path after failure.

Dependent synthesis starts only after every prerequisite pane succeeds and its output is
reviewed. The first pane, timeout, signal, or merge-input failure propagates unchanged,
cancels dependent work, and publishes no partial synthesis. Cleanup must remove pane
artifacts while preserving the first cause.
