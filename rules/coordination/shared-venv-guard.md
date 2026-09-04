# Lane environments follow Makefile RUNTIME_ROOT

SSOT: generated `Makefile` (`RUNTIME_ROOT`, `SETUP_ENVIRONMENT_RECIPE`,
`BORROW_RUNTIME_VENV_RECIPE`). See `docs/worktrees.md`.

- **Isolated git worktree:** `RUNTIME_ROOT == PROJECT_ROOT`. Run `make setup`
  in the lane — it recreates a **real** `<lane>/.venv` (symlink borrow is
  removed first). Use `<lane>/.venv/bin/python` and `make <verb>` from the lane.
- **Nested workspace checkout with a distinct principal:** setup delegates to
  `RUNTIME_ROOT`, then `BORROW_RUNTIME_VENV_RECIPE` may symlink
  `PROJECT_ROOT/.venv` → `RUNTIME_ROOT/.venv`. Never replace a real local env.
- Do **not** point a lane at the primary `.venv` via ad-hoc `PYTHONPATH` +
  primary interpreter as a substitute for lane setup — that loads the wrong
  editable `.pth` and is how shared-env outages happen.
- Never clear a present real `.venv` while another process may be using it.
