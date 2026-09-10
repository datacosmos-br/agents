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

## dc-dese release pipeline procedure (2026-09-10)

Canonical contract:
`cosmos-main/docs/ARCHITECTURE/ARGOCD_GITOPS_RELEASE_CONVERGENCE_PLAN.md` §0.
Chain: R1 charts package+receipt → R2 GitOps import+render → Argo CD `dc-dese`
only → soak 30 min (single window) → cleanup. `develop` is the sole integration
branch; `main`/`dc-prod`/`dc-control` receive no effect without operator order.

- Canonical surface: root `make setup|deps|gen|check|test|fix|fmt APPLY=Y`
  only; never invented selectors or raw linters; testmon always via
  `make test APPLY=Y`.
- Receipts live in the tracker (`cosmos-d57422f2` release, `cosmos-quncg`
  import): commit, package version, OCI digest; version drift between
  charts/GitOps is a blocker, never an accepted residual.
- Preserve foreign WIP: commit stray module trees to a named branch before
  any regen; never reset/restore shared work.
- Land one PR per repository, merge `--no-ff` into `develop`, bump root
  submodule pointers in a separate commit, rerun affected gates on the merged
  SHA; delete branch/worktree only after integration evidence.
- Bug/hotfix tracker items never attach to epics; tasks attach to the few
  canonical epics (`cosmos-yj36e` group). Keep item status truthful; deferred
  needs a reason and a date.
