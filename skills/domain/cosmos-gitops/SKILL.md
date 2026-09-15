---
name: cosmos-gitops
description: 'cosmos gitops, helm delivery, argocd reconciliation, environment promotion'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:selected-tag:cosmos-gitops","effective:2026-08-29","route:project","subject:argocd","subject:cosmos-gitops","subject:helm","usage:router"]'
---

# Cosmos GitOps

Activate when project selection declares `cosmos-gitops` and work touches Cosmos
charts, Argo CD declarations, GitOps reconciliation, secret delivery, environment
promotion, or their gitlinks. Do not activate for generic deployment work or treat
repository authorization as permission to mutate a cluster.

Read the `delivery procedure` (skill file). Resolve the independent
repository owner, exact staged revision, declared environment, required review,
credentials, native gates, and live-action authority before effects. Prefer
declarative owners and upstream controllers, keep Cosmos-specific policy thin,
serialize Helm, keep secrets opaque, and integrate members before the umbrella.

Missing authorization, credential, deterministic render, known diff, health
evidence, or required check fails closed. Fix the declarative owner forward; never
fall back to a keyring, live patch, alternate context, rollback, or partial
promotion.

## dc-dese release pipeline procedure

Canonical contract:
`cosmos-main/docs/ARCHITECTURE/ARGOCD_GITOPS_RELEASE_CONVERGENCE_PLAN.md` §0.
Chain: R1 charts package+receipt → R2 GitOps import+render → Argo CD `dc-dese`
only → soak 30 min (single window) → cleanup. `develop` is the sole integration
branch; `main`/`dc-prod`/`dc-control` receive no effect without operator order.

- Canonical surface: root `make setup|deps|gen|check|test|fix|fmt`
  only; never invented selectors or raw linters; testmon always via
  `make test`.
- Receipts live in the project tracker; read the current release/import
  receipts from the tracker at activation (commit, package version, OCI
  digest); version drift between charts/GitOps is a blocker, never an accepted
  residual.
- Preserve foreign WIP: commit stray module trees to a named branch before
  any regen; never reset/restore shared work.
- Land one PR per repository, merge `--no-ff` into `develop`, bump root
  submodule pointers in a separate commit, rerun affected gates on the merged
  SHA; delete branch/worktree only after integration evidence.
- Tracker hierarchy follows the canonical-epics rule under
  `rules/coordination/` (rule file): bug/hotfix items stay outside epics;
  tasks attach to the few canonical epics. Keep item status truthful;
  deferred needs a reason and a date.

## Environment channel automation ladder (ADR-144)

Authority: `cosmos-main/docs/ARCHITECTURE/DECISIONS/ADR_144_ENVIRONMENT_CHANNEL_AUTOMATION_LADDER.md`.

- Channels: `develop`→dc-dese (chart channel tag `0.4.141-dese.N.N`,
  resolution by stable channel tag, not SHA pin); `main`→dc-prod/dc-control.
  One Application name `apps-of-apps` in every environment (dual-root suffix
  naming is transitional debt to exterminate).
- dc-dese full automation (`appsetAutomation: true` + `automated.sync` +
  prune + self-heal) is enabled ONLY after `cosmos-release-001` goes green
  with a 30-minute soak. Before that, keep `appsetAutomation: false` and
  Phase-0 preview gating.
- Promotion ladder: bot creates AND merges the `develop→main` PR when the
  dese soak passes; the `main` ruleset keeps 1 human approval; rollout order
  `dc-prod` (rank 2) → `dc-control` (rank 3); stop at the first red
  environment; never promote past first failure; fix-forward only (no code
  rollback); one-off live remediation stays breaking-glass with durable
  root-fix in git afterwards.

## Prune decision protocol (never blind prune)

For each Application flagged with `requiresPruning` (parsed via
`OUTPUT=json LIMIT=<n> make status`):

1. Produce a per-resource diff between live and declared state.
2. Classify into buckets: `orphan` (live-only, no declaration),
   `stale` (declared elsewhere/moved), `keep` (declared under another
   owner/channel), `prune-ok` (safe prune).
3. Record an explicit decision per bucket in the owning bead BEFORE any
   prune. Blind `argocd app prune` / force-sync over an unknown bucket is a
   failure, not a shortcut.
4. Root-fix orphans at the declarative GitOps source; only prune after the
   declaration side converges.

## Reading `make status` buckets

Buckets and heuristic causes surfaced by the status handler:
`orphan` (live resource without declaration), `prune` (declaration wants a
live resource removed), `sync` pending state and the likely cause attached to
each non-green app (ownership drift, channel pin drift, automation disabled).
Treat the bucket as a hypothesis, not a verdict: confirm each with a real
diff before mutating.
