# Storage and scratch law

This file owns universal storage placement. Project and skill documents point
here and add only narrower local constraints.

- `/tmp` is limited to small, bounded operating-system ephemera. Never place a
  repository, worktree, virtual environment, persistent database, build cache,
  checkpoint, backup, or report there.
- Run test and build commands through `agentsctl temp run -- <command>`. Each
  run owns a physical `<repo>/.test-tmp/run.*` directory created by `mktemp` and
  receives distinct `TMPDIR`, `GOTMPDIR`, and `GOCACHE` paths.
- Reusable caches belong to `${XDG_CACHE_HOME:-$HOME/.cache}/<tool>`.
  Node compile caches use `NODE_COMPILE_CACHE` under this hierarchy.
  `GOMODCACHE` is shared; execution/build scratch is not.
- Persistent evidence belongs to
  `${XDG_STATE_HOME:-$HOME/.local/state}/<tool>`. Shells use only the bounded
  agents fallback there; managed commands replace it with repository-local
  per-run paths.
- GC is fail-closed. Preserve runs younger than seven days and anything with a
  live lock, process ownership evidence, Git/venv/database content, symlink, or
  unknown entry. Never use `rm -rf`, `git clean`, reset, or stash for GC.
- Default limits are warning at 1 GiB and owned-process failure at 5 GiB. A
  limiter may signal only the child process group it created.
- A successful owned child is not an orphan: after its report is persisted, its
  marked run tree is removed immediately. Failed/interrupted runs remain for GC.
- Linux copies request `cp --reflink=auto`. Copies remain independent physical
  trees; symbolic links and cross-repository references are prohibited.

Canonical surface:

```text
agentsctl temp audit [--json]
agentsctl temp status [--json]
agentsctl temp run -- <command>
agentsctl temp gc --dry-run|--apply
```
