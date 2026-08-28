# Storage and scratch law

This file owns universal storage placement. Project and skill documents point
here and add only narrower local constraints.

`config/storage.toml` is the sole writable owner of storage paths and runtime
thresholds. Code and documentation consume its stable keys; they do not carry
independent operational defaults.

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
  path selected by `policy.shell_temp`; managed commands replace it with
  repository-local per-run paths.
- GC is fail-closed. Preserve runs younger than `policy.orphan_age_days` and
  anything with a live lock, process ownership evidence, Git/venv/database
  content, symlink, or unknown entry. The configured retention may never be
  shorter than the universal seven-day safety invariant. Never use `rm -rf`,
  `git clean`, reset, or stash for GC.
- `policy.warning_bytes` and `policy.failure_bytes` bound each owned run. A
  limiter may signal only the child process group it created.
- `policy.report_max_bytes` bounds report publication. Capacity failure keeps
  prior reports and the current scratch evidence; it never prunes evidence.
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
