---
name: python-parallelization
description: 'python concurrency, parallel execution, performance measurement'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:marker:poetry.lock","detect:marker:pyproject.toml","detect:marker:requirements-dev.txt","detect:marker:requirements.txt","detect:marker:uv.lock","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:project","technology:python","updates:manual","usage:router"]'
---

# Python Parallelization

Read `the selection and proof procedure` (skill file) before changing
Python concurrency, parallelism, or throughput behavior.

This skill owns workload classification, bounded execution, cancellation,
cleanup, and measured speedup. Use `python-development` for general Python
implementation, typing, debugging, testing, and packaging. Never select async,
threads, processes, or vectorization without repository and workload evidence.
