---
name: py-parallel
description: "python concurrency, parallel execution, performance measurement"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:marker:pyproject.toml","detect:marker:requirements-dev.txt","detect:marker:requirements.txt","effective:2026-08-29","route:project","subject:python","supersedes:skill:python-parallelization","usage:router"]'
---

# Python Parallelization

Read `the selection and proof procedure` (skill file) before changing Python
concurrency, parallelism, or throughput behavior.

This skill owns workload classification, bounded execution, cancellation, cleanup, and
measured speedup. Use `py-dev` for general Python implementation, typing, debugging,
testing, and packaging. Never select async, threads, processes, or vectorization without
repository and workload evidence.
