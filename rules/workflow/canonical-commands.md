# Run work through canonical Make verbs or the documented CLI

Do not bypass the command surface with ad-hoc `uv run ruff/pytest/...`. Use
`make <verb> WHAT=<x>` (or the documented CLI) so guards, locks, dry-run, and
evidence apply.

A broken or out-of-pattern canonical command is a defect to FIX at its owner
(file a bead, repair it, rerun through it) — never a reason to route around it.

Use and prefer MCP tools and skills alongside the Make verbs for every
action. Large-scale refactors run through `make mod` and ast-grep
search-and-replace, never manual file-by-file edits. Hooks detect raw-command
bypasses of these surfaces and emit a command warning naming the canonical
verb.
