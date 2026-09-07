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
