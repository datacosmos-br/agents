---
name: verification-loop
description: "completion evidence, runtime verification, native gates"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-03","usage:router"]'
  version: 1.2.0
---

# Verification Loop

Review claims about PR threads and checks are gated evidence too: use `pr-sheriff` with
AI Hub forge resolution and direct `gh` evidence before repeating them as status.
Activate after behavior changes and before any pass, resolution, readiness, or
completion claim. Read the `complete procedure` (skill file), prove the smallest real
runtime first, and then run the repository-owned gates for the affected scope. Later
edits invalidate earlier evidence where their scopes overlap. Production readiness
adopts every defect in the blast radius, including pre-existing ones; read
`rules/workflow/production-readiness.md` (rule file) before any completion claim over a
red or unresolved base. Tree-wide mechanical rewrites, enforcer/codemod apply cycles,
and bulk migrations additionally obey `rules/workflow/mass-rewrite-discipline.md` (rule
file): bracket the mass with test evidence on both sides, carry scoped commit
boundaries, inventory what the automation applied versus reverted, prove no string
literal was corrupting, and report progress per violation class.

For an increment with a PR, integration proof includes unresolved-thread triage, green
required checks, a no-ff merge commit on the integration branch, rerun of affected gates
on the merged checkout, and measured runtime reconciliation. Never treat “mergeable”, an
open PR, or local-only success as landed. When the repository owns the deployed runtime,
completion also requires installing or reconciling that runtime from the merged
integration SHA and proving the public surface there.

## Investigation protocol delta (evidence 2026-09-11)

- Define the hypothesis and the evidence method BEFORE touching anything: artifacts go
  to files (`difflib.unified_diff` written to a log path), never relied on through
  flooded stdout.
- An experiment that fails silently and yields nothing is NOT evidence. Never relabel
  poorly-instrumented work as "out of scope" or "pre-existing"; re-instrument until the
  diff speaks, or file the defect with the hypothesis and the trigger so the next
  session continues from a real artifact.
- Test budget law (10s/test, 60s slow, 120s full) is enforced by fixing the test
  (fixture isolation, receipt assertions), never by raising the limit. A test that
  executes real provisioning (mise/uv sync) in-line violates the budget by construction.
