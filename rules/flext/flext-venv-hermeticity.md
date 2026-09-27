---
description:
  Python CLI tooling must run in a hermetic venv resolved from the target lock
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# Hermetic venv for multi-worktree Python tooling

A fleet lost a day to wrong-verdict measurements because the shell exported
`VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` pointing at a different project's `.venv`, so
`uv sync`, `make deps`, gate validators, and pytest in one repo silently exercised wheel
installs of another repo. The error repeated across several members and the workspace
root before anyone root-caused it.

- Run every dependency sync, gate, and test with the shell environment neutralized:
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make ...`.
- After any lock change, verify the interpreter actually resolves the intended package:
  compare the installed source (`importlib` or commit line in the wheel's
  `direct_url.json`) against the lock pin before quoting any result.
- Treat any `ModuleNotFoundError` inside fleet-managed tooling (e.g. `flext_cli` missing
  inside a member venv) as a venv desync defect, not a code defect: re-sync from the
  committed lock first, then re-measure.
- `uv lock` inside a directory that is discoverable as a workspace member writes to the
  workspace root, not the member; a missing member lock is a topology fact, confirm with
  `uv lock -v` (DEBUG "Found workspace root") before generating one.

See also: `ruler-consistency.md` (rule file), `observable-runtime.md` (rule file).
