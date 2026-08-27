---
globs: hooks/**/*.sh
---

# Hooks use the repository-owned interpreter

Never reference another repository's virtual environment. A Python hook runs
through the active repository's documented runner, normally:

`uv run python <hook>`

After editing a hook, run it live (feed real JSON, check the decision) — static
gates do not catch a dead hook.
