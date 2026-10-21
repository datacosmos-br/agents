---
description: Authorized parallel work and sequenced publication ownership
capsule_summary: |
  Delegate only under the current operator request or selected role contract.
  Assign bounded, independent work with explicit write ownership and verify
  every result. The main executor retains the task and sequenced publication;
  another agent's output never substitutes for its acceptance evidence.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-20","route:both"]'
---

# Authorized parallel work

The current operator request and selected role contract determine whether work
is delegated or performed inline. Available agents, an old maximum-fan-out
instruction or a broad cleanup request do not by themselves authorize launching
agents. An inline executor retains implementation and closure responsibility;
collaboration with existing writers does not transfer that responsibility.

For authorized delegation, assign one bounded result, its repository and exact
write ownership. Explain that the worker shares the codebase, must preserve
others' changes and must reconcile current WIP. Independent reads may run
concurrently; effects on shared mutable state follow its canonical serializer.
Do not serialize independent work merely by habit, or parallelize a shared
mutation merely because slots exist.

Verify the returned source and native evidence before acceptance. Empty output,
a self-report and a delegated test result without its candidate identity do not
prove completion. The parent retains sequenced effects and the current operator
conversation; merge and tracker permissions follow the active assignment.

Resolve model capabilities and costs through the selected runtime's current
catalog and policy. Do not hardcode model names, prices or effort multipliers
in a universal rule, or invent a substitute when a required capability is absent.

Compose with shared-file coordination, session governance, fix-forward and the
selected tracker's verification contract.
