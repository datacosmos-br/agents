---
description: Bash Guard Lane Execution
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-09-03","route:both"]'
---

# Bash Guard Lane Execution

Lane commands must preserve the isolated checkout and expose output for evidence.
Use these owner-directed forms instead of changing process directories:

- `git -C <worktree> <git-verb>`;
- `env -C <worktree> make <verb> [FILE=<path>]`;
- `bun run --cwd <package-dir> <script>`;
- `gh`, `systemctl --user`, and other provider-selected CLIs from the current city root.

The only allowed directory-changing prefix is `export NAME=value;` before exactly one
governed command. Redirecting stdout or stderr to `/dev/null` is denied: write gate
output to the session scratchpad or let it escape, and preserve the exact command,
working directory, exit code, and decisive output.

Mutations apply with `APPLY=Y` only. `WHAT=` and `PROJECT=` are not agent workflow
controls: invoke the bare canonical verb and add a selector variable only when the
project's own declared make surface documents it for that verb. Invented make forms,
interrogative probes, and ritual re-invocations are defects.

A scoped `make check FILE=`/`make test FILE=` refusal is repaired at its scope owner and
rerun. Only when the same command text is denied after that repair may the operator
repeat that identical bare `make check`/`make test` command once as a deliberate guard
experiment; record the denial and do not use it as a gate substitute.
