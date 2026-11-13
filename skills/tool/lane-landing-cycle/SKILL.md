---
name: lane-landing-cycle
description: "beads, git worktree, landing cycle, pr merge, ci generation, lane retirement"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0021","detect:opt-in:lane-landing-cycle","effective:2026-10-29","route:agent","subject:beads","subject:git","subject:github","usage:router"]'
---

# Lane landing cycle

The verified mechanical cycle for one work unit on a governed repository lane,
from authorized placement to any authorized retirement, under `rules/law.md` item 10.

## 1. Lane and bead first

Placement follows `rules/git/gitflow-branch-pr.md`, the environment `rules/storage.md`,
and WIP is kept (`rules/law.md` item 11). The tracker, the coordination channel and the
Bead/branch/PR declaration follow `rules/workflow/beads-traceability.md` and
`rules/coordination/inter-session-mail.md`; loading this skill selects no mail command
or append-notes loop.

## 2. The gate, in order

First complete documented alignment, implementation and real public-runtime proof
(`rules/law.md` items 9 and 12). Only then enter this validation sequence or change
regression tests; validation is not permission for test-first work.

Discover public verbs, contexts, population and evidence requirements from the selected
repository's root Make catalog. `rules/workflow/canonical-commands.md` owns operation
boundaries, deadlines and test selection. Use its current test-verb contract rather
than a fixed test/full alias or mandatory targeted-before-full sequence. Prove any
required generation fixed point through its owner; no hidden repeated lifecycle.
Keep the physical environment selected by its owner. A red invocation requires causal
repair and revalidation in the same phase; recording it alone never clears acceptance.

## 3. Classify generated outputs by owner

Read the project generator declaration and inspect each changed output before
staging. A generated file belongs in the PR when its tracked source changed and
the canonical generator produced it. Elect generated paths and their versioning
from the repository's current declaration, not a remembered artifact list.
Regenerate through that project's declared CI context where required and verify the fixed
point. Preserve unrelated worktree changes and repair source drift at its owner.

## 4. Land, prove, retire

Resolve repository, remote identity, working branch, integration base and PR through
`rules/git/gitflow-branch-pr.md`; its existing pipeline owns publication and reviewed
landing. Do not copy a sibling repository/base, select a PR by number alone or build
another merge-command workflow here. Follow its divergence, current-head CI/review,
merged-revision and required runtime proof before tracker closure.

Assess retirement only through that owner's explicit disposable-lane authority,
fresh ancestry and complete preservation/runtime-reference proof. Integration ancestry
alone authorizes no removal. Preserve adopted primary, integration, shared and foreign
contexts. A clean or stable checkout is not a development prerequisite; unresolved preservation
evidence blocks the destructive retirement only, never authorizes forced removal.

## 5. Judgment calls this cycle encodes

- Before starting: research branches, PRs, and beads for prior art; adopt the
  survivor, never re-implement (`rules/coordination/inter-session-mail.md`).
- Environmental timeouts require the profile and measured-cause repair prescribed by
  `rules/workflow/canonical-commands.md`; host load never authorizes an unchanged rerun.
- Historical cycle reports are evidence for their recorded revision and scope, not
  a command catalog or current execution permission for another project.
