---
name: mle-workflow
description: 'machine learning, model lifecycle, production operations'
metadata:
  aihub.tags: '["activation:detected-or-opt-in","detect:marker:MLproject","detect:marker:dvc.lock","detect:marker:dvc.yaml","detect:opt-in:machine-learning","domain:mle","provenance:agents-owned","route:project","updates:manual","usage:on-demand"]'
---

# Machine Learning Engineering

Use for repositories whose declared artifacts identify an ML system. Do not
project this capability into personal targets or projects without an ML marker.

## Contract

1. Define the product decision, unacceptable mistakes, success metric, guardrail
   metrics, label timing, data snapshot, and baseline.
2. Establish entity grain, point-in-time correctness, split policy, feature
   availability, and train/serve transformation parity before model selection.
3. Keep training, evaluation, artifact packaging, and inference reproducible from
   versioned code, configuration, data identity, and dependency state.
4. Compare the candidate with a simple baseline across relevant slices. Report
   calibration, uncertainty, latency, resource cost, and failure classes rather
   than one aggregate score.
5. Package preprocessing, model identity, schema, and safe loading together.
   Reject incompatible artifacts and unsafe deserialization.
6. Define rollout, monitoring, delayed-label evaluation, drift signals, and
   rollback ownership before production use.

## Boundaries

- Use the repository's existing language, data, experiment, serving, and
  deployment owners; do not introduce an alternate MLOps stack by default.
- Prevent label leakage and future-data access with executable boundary tests.
- Preserve privacy and data-retention contracts in datasets, features, prompts,
  artifacts, predictions, and logs.
- A model-quality gain does not override regressions in safety, protected slices,
  latency, reliability, or cost.
- Runtime inference and artifact loading are proven before test expectations are
  changed.

Deliver the data/model contract, reproducible command, comparison evidence,
artifact identity, runtime proof, and focused project gates.
