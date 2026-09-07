---
name: python-development
description: 'python, package development, toolchain detection'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:marker:poetry.lock","detect:marker:pyproject.toml","detect:marker:requirements-dev.txt","detect:marker:requirements.txt","detect:marker:uv.lock","effective:2026-08-29","extends:solid","route:project","subject:python","usage:router"]'
---

# Python Development

Apply the active project's Python version, dependency owner, public contracts,
and canonical commands.

For responsibility, abstraction, or dependency-direction changes, apply
`$solid` first and keep only the Python-specific delta here.

Read the `single owner procedure` (skill file) for implementation,
debugging, testing, packaging, and native-gate evidence.

Use the distinct `python-parallelization` skill for async, thread, process,
vectorization, or throughput changes. Do not impose a tool, framework, or style
threshold that the project has not selected. Runtime behavior and project-owned
configuration are authoritative; generated files remain outputs.
