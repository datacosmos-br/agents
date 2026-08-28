---
name: python-development
description: 'python, package development, toolchain detection'
metadata:
  aihub.tags: '["activation:detected","detect:marker:poetry.lock","detect:marker:pyproject.toml","detect:marker:requirements-dev.txt","detect:marker:requirements.txt","detect:marker:uv.lock","provenance:agents-owned","route:project","technology:python","updates:manual","usage:router"]'
---

# Python Development

Apply the active project's Python version, dependency owner, public contracts,
and canonical commands.

- For implementation and refactoring, read
  [engineering.md](references/engineering.md).
- For a defect or unexplained failure, read
  [debugging.md](references/debugging.md).
- For pytest selection, Testmon acceleration, cache preservation, or coverage,
  read [testing.md](references/testing.md).

Use the distinct `python-parallelization` skill for async, thread, process,
vectorization, or throughput changes. Do not impose a tool, framework, or style
threshold that the project has not selected. Runtime behavior and project-owned
configuration are authoritative; generated files remain outputs.
