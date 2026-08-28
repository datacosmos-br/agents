---
name: python-parallelization
description: 'Design Python concurrency when a detected Python project needs measured parallel execution.'
metadata:
  aihub.tags: '["activation:detected","detect:marker:poetry.lock","detect:marker:pyproject.toml","detect:marker:requirements-dev.txt","detect:marker:requirements.txt","detect:marker:uv.lock","provenance:agents-owned","route:project","technology:python","updates:manual","usage:router"]'
---

# Python Parallelization

Read [the selection and proof procedure](references/procedure.md) before changing
Python concurrency, parallelism, or throughput behavior.

This skill owns workload classification, bounded execution, cancellation,
cleanup, and measured speedup. Use `python-development` for general Python
implementation, typing, debugging, testing, and packaging. Never select async,
threads, processes, or vectorization without repository and workload evidence.
