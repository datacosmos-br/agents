# Run work through canonical Make verbs or the documented CLI

Do not bypass the command surface with ad-hoc `uv run ruff/pytest/...`. Use
`make <verb> WHAT=<x>` (or the documented CLI) so guards, locks, dry-run, and
evidence apply.

A broken or out-of-pattern canonical command is a defect to fix at its owner
and rerun through the same surface—never a reason to route around it. While the
tracker is suspended, preserve the exact blocker in Git/PR/CI evidence and keep
the repository-declared manual ledger current and the phase open.

Use available declared tools and skills alongside Make verbs. Large-scale
refactors run through the repository's declared structural-editing surface and ast-grep
search-and-replace, never manual file-by-file edits. Hooks detect raw-command
bypasses of these surfaces and emit a command warning naming the canonical
verb.
