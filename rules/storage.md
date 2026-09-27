---
description: Storage and scratch law
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-28","route:both"]'
---

# Storage and scratch law

This file owns universal storage placement. Project and skill documents point here and
add only narrower local constraints.

Each project declares one typed storage owner. It validates every physical path before
effects and derives deterministic local defaults exactly once. Consumers do not repeat
those defaults through environment variables, settings, arguments, fixtures, or
documentation.

- `/tmp` never contains a repository, worktree, environment, persistent database, cache,
  checkpoint, generated candidate, backup, archive, or report.
- Backups, retirement trees, quarantine copies, `.bak` siblings, and raw archives are
  prohibited. Complete cutover rewires consumers and deletes obsolete artifacts; Git
  history is the recovery authority for tracked source.
- Development subprocesses remain Make/tool owned and propagate nonzero exits, timeouts,
  and signals through their native process API.
- Missing, empty, conflicting, unexpanded, relative, or invalid genuinely required
  external values and configured paths raise immediately. No environment variable,
  setting, parameter, or argument repeats a derivable canonical default; no failure
  selects the home directory, a user-config directory, the shell, or `/tmp` as an
  alternate.
- Preflight selects exactly one physical staging and publication path on the destination
  filesystem. Its failure raises; no alternate primitive is tried. Cross-repository
  mutable references are prohibited. A symbolic link exists only as the compatibility
  link a declared migration leaves at a tool's fixed path after moving its store, named
  in that migration's declaration and recorded in its receipt; an ad hoc link, or one
  a migration did not declare, is a defect at the storage owner.
- A unit test's writes stay inside its `tmp_path` fixture; a test that writes to the
  repository tree, the real home directory, or any path outside `tmp_path` is a test
  defect at its owner, never a skip. See `observable-runtime.md` (rule file) for the
  complete sandboxing contract.

A repository-local `.venv` is a regenerable local runtime artifact, never a source or
shared dependency. It is never copied or reused across checkouts; each physical
repository reconstructs it through its declared setup owner.

## Scratch root is user-home-scoped, never `/tmp` or in-tree (operator ruling, 2026-09-12)

<!-- Why: registers 2026-09-12 operator ruling A' on this file, the existing storage-placement owner -->

`TMPDIR`, `GOTMPDIR`, the pytest `basetemp`, and tool staging live under the platform
home plus `tmp`, at `.flext-runtime<absolute project root>/scratch` — never `/tmp` and
never inside the checked-out tree. The journal, testmon cache, and `__pycache__` stay
beside the checkout, not under scratch. A `clean` verb that only sweeps an in-tree
`.test-tmp` while scratch actually lives at the platform home plus `tmp` root is
incomplete and leaks; it is corrected at its Make/codegen owner to sweep the real
location.
