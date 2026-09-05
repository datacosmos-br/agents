---
description: Storage and scratch law
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-28","route:both"]'
---

# Storage and scratch law

This file owns universal storage placement. Project and skill documents point
here and add only narrower local constraints.

Each project declares one typed storage owner. It validates every physical path
before effects and derives deterministic local defaults exactly once. Consumers
do not repeat those defaults through environment variables, settings, arguments,
fixtures, or documentation.

- `/tmp` never contains a repository, worktree, environment, persistent database,
  cache, checkpoint, generated candidate, backup, archive, or report.
- Backups, retirement trees, quarantine copies, `.bak` siblings, and raw archives
  are prohibited. Complete cutover rewires consumers and deletes obsolete
  artifacts; Git history is the recovery authority for tracked source.
- Development subprocesses remain Make/tool owned and propagate nonzero exits,
  timeouts, and signals through their native process API.
- Missing, empty, conflicting, unexpanded, relative, or invalid genuinely
  required external values and configured paths raise immediately. No
  environment variable, setting, parameter, or argument repeats a derivable
  canonical default; no failure selects home, XDG, shell, or `/tmp` as an alternate.
- Preflight selects exactly one physical staging and publication path on the
  destination filesystem. Its failure raises; no alternate primitive is tried.
  Symbolic links and cross-repository mutable references are prohibited.
- A unit test's writes stay inside its `tmp_path` fixture; a test that writes
  to the repository tree, the real home directory, or any path outside
  `tmp_path` is a test defect at its owner, never a skip. See
  `observable-runtime.md` (rule file) for the complete sandboxing contract.

A repository-local `.venv` is a regenerable local runtime artifact, never a
source or shared dependency. It is never copied or reused across checkouts; each
physical repository reconstructs it through its declared setup owner.
