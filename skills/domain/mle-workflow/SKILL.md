---
name: mle-workflow
description: 'machine learning, model lifecycle, production operations'
metadata:
  aihub.tags: '["activation:detected-or-opt-in","decision:ADR-0008","detect:marker:MLproject","detect:marker:dvc.lock","detect:marker:dvc.yaml","detect:opt-in:machine-learning","domain:mle","effective:2026-08-28","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:project","updates:manual","usage:on-demand"]'
---

# Machine Learning Engineering

Activate only for a repository with a declared ML marker or an explicit
machine-learning request. Deterministic data processing does not activate it.

Before training, resolve the decision, unacceptable mistakes, metrics, label
timing, entity grain, point-in-time snapshot, feature availability, split,
baseline, train/serve transformations, project owners, resource/cost authority,
and non-derivable current-process credentials. The first missing, future,
conflicting, unsafe, or unexpanded input stops before effects.

Use one declared data-to-deployment path. Compare only predeclared candidates
with the baseline across required aggregate, slice, calibration, uncertainty,
latency, resource, privacy, and failure evidence. Never switch model, provider,
data, credential, or stack after failure. Keyrings and profiles are forbidden
credential sources. Never deserialize unsafely or normalize errors into defaults,
retries, skips, warnings, or findings.

Package exact code, dependency, data, preprocessing, model, and schema identity.
Prove safe loading, train/serve parity, monitoring, delayed-label evaluation,
drift boundaries, and rollback ownership before publication or deployment.

The first child, timeout, signal, artifact, registry, or deployment failure
propagates unchanged. Publish validated artifact and rollout state atomically.
Cleanup attaches secondary failure, re-raises the first cause, and removes all
partial artifact, registry, and deployment residue. Report observed evidence only.
