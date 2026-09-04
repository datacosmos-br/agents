---
globs: hooks/**/*.sh
---

# Hooks must default to the venv interpreter, not system python

System python lacks `flext_cli`, so a hook that shells to bare `python` crashes
silently and disables the guard. Default to the project venv:

`${AI_HUB_PYTHON:-$HOME/.ai-hub/.venv/bin/python}`

After editing a hook, run it live (feed real JSON, check the decision) — static
gates do not catch a dead hook.
